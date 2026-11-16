#!/usr/bin/env python3
"""TripoSR V24: two same-camera Forge V23 inputs, neural renders and threshold sweep.
Reuses the predicted density grid across five thresholds, with no extra training.
Experimental geometry only; does not replace production or editable V23 meshes.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import io
import json
import os
import traceback
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/"art/hero_01/references/forge_v23_blockout_threequarter_q80.webp.b64"
EXPECTED="f01171f4c8c76da5b550dcd7e8d00b3242af9dacb1949ee0578381b2e407e41a"
OUT=ROOT/"build/triposr_v24_quality"
THRESHOLDS=(15.,20.,25.,30.,35.)
RESOLUTION=256
OUTPUT_REPORT=OUT/"V24_REPORT.json"

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+"\n")

def prepare():
    if not REF.is_file():raise RuntimeError("V23_SOURCE_MISSING")
    payload=base64.b64decode(REF.read_text().strip(),validate=True)
    sha=hashlib.sha256(payload).hexdigest()
    if sha!=EXPECTED:raise RuntimeError("V23_SOURCE_SHA_MISMATCH "+sha)
    im=Image.open(io.BytesIO(payload)).convert("RGB")
    if im.size!=(512,512):raise RuntimeError("V23_SOURCE_SIZE_INVALID "+str(im.size))
    x=np.asarray(im,dtype=np.float32)
    borders=np.concatenate([x[:5,:,:].reshape(-1,3),x[-5:,:,:].reshape(-1,3),x[:,:5,:].reshape(-1,3),x[:,-5:,:].reshape(-1,3)])
    if np.mean(np.max(np.abs(borders-128),axis=1)<=6)<0.98:
        raise RuntimeError("NON_NEUTRAL_BORDER")
    # Original actual V23 render (flat/faceted clay), unchanged.
    OUT.mkdir(parents=True,exist_ok=True)
    im.save(OUT/"flat.png")
    # Same camera, same silhouette: strengthen existing face lighting only.
    # This is a shading/contrast variant, NOT a new physically rendered camera.
    m=np.max(x,axis=2)>156
    lum=np.mean(x,axis=2)
    enhanced=np.clip(211.+(lum-211.)*1.70,136,248)
    blended=x*0.28+enhanced[...,None]*0.72
    output=np.where(m[...,None],blended,x).clip(0,255).astype(np.uint8)
    Image.fromarray(output).save(OUT/"contrast.png")
    assert np.mean(np.max(np.abs(output[:5]-128),axis=2)<=6)>.98
    write_json(OUT/"INPUT_REPORT.json",{
       "source":str(REF.relative_to(ROOT)),"decoded_input_sha256":sha,
       "source_model":"FORGE V23 (original eleven-part handmade blockout)",
       "inputs":["flat.png","contrast.png"],
       "contrast_variant":"Same camera and silhouette, strengthened existing rendered face luminance",
       "original_resolution":[512,512],
       "neutral_gray_background":True,
       "tripo_weights":"stabilityai/TripoSR","mesh_extractor":"original native torchmcubes",
       "thresholds":THRESHOLDS,"resolution":RESOLUTION,"chunk_size":2048,
       "ground_truth_model_not_reconstructed":True
    })
    print("V24_PREPARE_OK",sha,flush=True)

def run():
    import torch
    import trimesh
    from tsr.system import TSR
    from tsr.utils import scale_tensor
    from tsr.models.isosurface import MarchingCubeHelper
    from tsr.bake_texture import bake_texture
    if not (OUT/"INPUT_REPORT.json").exists():
        raise RuntimeError("RUN_PREPARE_FIRST")
    model=TSR.from_pretrained("stabilityai/TripoSR",config_name="config.yaml",weight_name="model.ckpt")
    model.renderer.set_chunk_size(2048)
    model.to("cpu")
    model.eval()
    print("V24_OFFICIAL_TRIPOSR_READY",flush=True)
    report={"status":"RUNNING","inputs":{},"bake_attempt":{},"notes":[
        "Density sampled once per input at resolution 256, reused for 5 threshold values.",
        "Neural renders come directly from model.render, not from mesh extraction.",
        "No independent cross-view or ground-truth alignment is performed in this step."
    ]}
    for key in ("flat","contrast"):
        print("V24_BEGIN",key,flush=True)
        path=OUT/f"{key}.png"
        im=Image.open(path).convert("RGB")
        with torch.no_grad():
            scene_codes=model([im],device="cpu")
        result={"status":"INFERRED","meshes":{}}
        report["inputs"][key]=result
        # NeRF-style neural preview: optionally record inability, do not block mesh.
        try:
            print("V24_NEURAL_RENDER_BEGIN",key,flush=True)
            imgs=model.render(scene_codes,n_views=4,elevation_deg=20.,
                              height=144,width=144,return_type="pil")
            for idx,frame in enumerate(imgs[0]):
                frame.save(OUT/f"{key}_neural_{idx:02d}.png")
            result["neural_render"]={"status":"ok","views":len(imgs[0]),"resolution":[144,144]}
            print("V24_NEURAL_RENDER_OK",key,flush=True)
        except Exception as e:
            result["neural_render"]={"status":"failed","error":str(e)[:350]}
            print("V24_NEURAL_RENDER_FAILED",key,str(e)[:250],flush=True)
        helper=MarchingCubeHelper(RESOLUTION)
        with torch.no_grad():
            # Exactly the same density sampling code as official TSR.extract_mesh.
            samples=scale_tensor(helper.grid_vertices.to("cpu"),helper.points_range,
                                  (-model.renderer.cfg.radius,model.renderer.cfg.radius))
            density=model.renderer.query_triplane(model.decoder,samples,scene_codes[0])["density_act"]
        del samples
        d=density.detach().cpu().numpy()
        result["density"]={"min":float(d.min()),"max":float(d.max()),
                           "mean":float(d.mean()),"p50":float(np.percentile(d,50)),
                           "p99":float(np.percentile(d,99)),
                           "grid_resolution":RESOLUTION}
        for th in THRESHOLDS:
            name=f"{int(th):02d}"
            print("V24_MC_BEGIN",key,name,flush=True)
            try:
                with torch.no_grad():
                    pos,faces=helper(-(density-th))
                    pos=scale_tensor(pos,helper.points_range,
                                     (-model.renderer.cfg.radius,model.renderer.cfg.radius))
                if faces.numel()<3:
                    raise RuntimeError("EMPTY_ISOSURFACE")
                rgb=None
                if th==25.:
                    with torch.no_grad():
                        rgb=model.renderer.query_triplane(model.decoder,pos,scene_codes[0])["color"].cpu().numpy()
                mesh=trimesh.Trimesh(vertices=pos.cpu().numpy(),faces=faces.cpu().numpy(),
                                     vertex_colors=rgb,process=False)
                if not np.isfinite(mesh.vertices).all():raise RuntimeError("NONFINITE_VERTICES")
                p=OUT/f"{key}_threshold_{name}.glb"
                mesh.export(p)
                loaded=trimesh.load(p,force="scene",process=False)
                g=loaded.dump(concatenate=True)
                if len(g.faces)!=len(mesh.faces):raise RuntimeError("ROUNDTRIP_FACES_MISMATCH")
                size=mesh.extents
                length=float(size.max())
                result["meshes"][name]={
                   "status":"ok","file":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
                   "triangles":int(len(mesh.faces)),"vertices":int(len(mesh.vertices)),
                   "watertight":bool(mesh.is_watertight),
                   "bounds":np.asarray(mesh.bounds).round(5).tolist(),
                   "normalized_sorted_extents":np.sort(size/length).round(6).tolist(),
                   "vertex_colors":rgb is not None}
                print("V24_MC_OK",key,name,len(mesh.faces),flush=True)
            except Exception as e:
                result["meshes"][name]={"status":"failed","error":str(e)[:350]}
                print("V24_MC_FAIL",key,name,str(e)[:250],flush=True)
            write_json(OUTPUT_REPORT,report)
        # Attempt official optional texture baking for 25 only, with no effect on baseline.
        result["bake"]={"status":"not_attempted"}
        if result["meshes"].get("25",{}).get("status")=="ok":
            try:
                print("V24_BAKE_BEGIN",key,flush=True)
                mesh=trimesh.load(OUT/f"{key}_threshold_25.glb",force="scene",process=False).dump(concatenate=True)
                baked=bake_texture(mesh,model,scene_codes[0],512)
                rgba=np.clip(baked["colors"]*255,0,255).astype(np.uint8)
                tex=Image.fromarray(rgba).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                tex.save(OUT/f"{key}_texture_512.png")
                uv=np.asarray(baked["uvs"],dtype=np.float64)
                v=np.asarray(mesh.vertices)[baked["vmapping"]]
                f=np.asarray(baked["indices"],dtype=np.int64)
                bakedmesh=trimesh.Trimesh(vertices=v,faces=f,process=False)
                bakedmesh.visual=trimesh.visual.texture.TextureVisuals(uv=uv,image=tex)
                bp=OUT/f"{key}_baked_512.glb"
                bakedmesh.export(bp)
                back=trimesh.load(bp,force="scene",process=False)
                result["bake"]={"status":"ok","atlas":f"{key}_texture_512.png",
                   "glb":bp.name,"meshes":len(back.geometry)}
                print("V24_BAKE_OK",key,flush=True)
            except Exception as e:
                result["bake"]={"status":"failed","error":str(e)[:450],
                                "trace":traceback.format_exc(limit=2)[-600:]}
                print("V24_BAKE_FAILED",key,str(e)[:300],flush=True)
        result["status"]="COMPLETED"
        write_json(OUTPUT_REPORT,report)
        del scene_codes,density
    report["status"]="COMPLETED"
    write_json(OUTPUT_REPORT,report)
    print("V24_SUCCESS",json.dumps({
      k:{"render":v["neural_render"],"meshes":{n:m.get("triangles") for n,m in v["meshes"].items()},"bake":v["bake"]["status"]}
      for k,v in report["inputs"].items()}),flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("action",choices=("prepare","run"))
    args=ap.parse_args()
    {"prepare":prepare,"run":run}[args.action]()
