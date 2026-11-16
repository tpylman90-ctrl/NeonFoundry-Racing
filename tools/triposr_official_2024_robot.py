#!/usr/bin/env python3
"""Repeat the actual original 2024 TripoSR demo on examples/robot.png.

Ground truth: upstream VAST-AI-Research/TripoSR, gradio_app.run_example.
This program uses the exact example-input compositing behavior with the same
stabilityai/TripoSR weights and native torchmcubes extraction at resolution 256.
It captures raw vertex-color GLB, Android-oriented official-demo GLB, and direct
neural render views; UV baking is optional and must not invalidate the comparison.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
import torch
import trimesh

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path("/tmp/triposr/examples/robot.png")
OUT=ROOT/"build/triposr_official_robot_2024"
OUT.mkdir(parents=True,exist_ok=True)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def stats(mesh):
    e=np.asarray(mesh.extents,dtype=float)
    length=max(float(e.max()),1e-9)
    return {
        "vertices":int(len(mesh.vertices)),
        "triangles":int(len(mesh.faces)),
        "is_watertight":bool(mesh.is_watertight),
        "bounds":np.asarray(mesh.bounds).round(6).tolist(),
        "normalized_extents":np.round(e/length,6).tolist(),
        "volume_signed":float(mesh.volume)
    }

def main():
    from tsr.system import TSR
    from tsr.utils import to_gradio_3d_orientation
    from tsr.bake_texture import bake_texture
    import subprocess
    assert SOURCE.is_file(),"UPSTREAM_OFFICIAL_EXAMPLE_MISSING"
    src=Image.open(SOURCE)
    rgba=np.asarray(src.convert("RGBA"),dtype=np.float32)/255.
    composite=rgba[:,:,:3]*rgba[:,:,3:4]+(1-rgba[:,:,3:4])*0.5
    pil=Image.fromarray(np.clip(composite*255,0,255).astype(np.uint8),"RGB")
    # This mirrors gradio_app.preprocess(..., False, .9): no rembg, fill gray alpha.
    input_path=OUT/"official_robot_demo_input.png"
    pil.save(input_path)
    report={
      "source":"https://github.com/VAST-AI-Research/TripoSR/blob/main/examples/robot.png",
      "official_2024_example":True,
      "upstream_commit":subprocess.check_output(
         ["git","-C","/tmp/triposr","rev-parse","HEAD"],text=True).strip(),
      "upstream_source_git_blob":subprocess.check_output(
         ["git","-C","/tmp/triposr","hash-object",str(SOURCE)],text=True).strip(),
      "source_sha256":digest(SOURCE),
      "source_mode":src.mode,"source_size":list(src.size),
      "source_alpha_transparent_fraction":float(np.mean(rgba[:,:,3]<.99)),
      "preprocessed_image_sha256":digest(input_path),
      "preprocessing":"upstream gradio_app.run_example: preprocess(input,False,0.9); gray alpha compositing; NO automatic rembg and NO foreground resizing",
      "pretrained_weights":"stabilityai/TripoSR",
      "native_extractor":"torchmcubes original; no scikit-image fallback",
      "mc_resolution":256,"chunk_size":2048,"device":"cpu",
      "official_demo_extraction":"model.extract_mesh(scene_codes, True, resolution=256)",
      "production_modified":False,
      "neural_render":None,"texture_bake":None,
      "status":"RUNNING"
    }
    (OUT/"benchmark_report.json").write_text(json.dumps(report,indent=2)+"\n")
    print("ORIGINAL_ROBOT_INPUT_VERIFIED",report["upstream_source_git_blob"],flush=True)
    model=TSR.from_pretrained("stabilityai/TripoSR",config_name="config.yaml",weight_name="model.ckpt")
    model.renderer.set_chunk_size(2048)
    model.to("cpu").eval()
    with torch.no_grad():
        scene_code=model(pil,device="cpu")
    print("OFFICIAL_ROBOT_INFERENCE_OK",flush=True)
    try:
        with torch.no_grad():
            frames=model.render(scene_code,n_views=4,elevation_deg=20.,
                                height=192,width=192,return_type="pil")
        for i,frame in enumerate(frames[0]):
            frame.save(OUT/f"neural_{i:02d}.png")
        report["neural_render"]={"status":"success","views":4,
                                  "resolution":[192,192],"elevation_deg":20}
        print("OFFICIAL_ROBOT_NEURAL_RENDER_OK",flush=True)
    except Exception as exc:
        report["neural_render"]={"status":"failed","error":str(exc)[:350]}
        print("OFFICIAL_ROBOT_NEURAL_RENDER_FAIL",str(exc)[:200],flush=True)
    with torch.no_grad():
        raw=model.extract_mesh(scene_code,True,resolution=256)[0]
    rawpath=OUT/"TripoSR_Official_Robot_Raw_256.glb"
    raw.export(rawpath)
    check=trimesh.load(rawpath,force="scene",process=False)
    g=check.dump(concatenate=True)
    assert len(g.faces)==len(raw.faces) and len(g.faces)>1000,"GLB_ROUNDTRIP_FAIL"
    report["raw_glb"]={"file":rawpath.name,"sha256":digest(rawpath),**stats(g)}
    demo=to_gradio_3d_orientation(raw.copy())
    demopath=OUT/"TripoSR_Official_Robot_Demo_Android.glb"
    demo.export(demopath)
    read=trimesh.load(demopath,force="scene",process=False)
    assert len(read.dump(concatenate=True).faces)==len(raw.faces),"DEMO_EXPORT_INVALID"
    report["demo_glb"]={"file":demopath.name,"sha256":digest(demopath),**stats(read.dump(concatenate=True))}
    print("OFFICIAL_ROBOT_NATIVE_MESH_OK",report["raw_glb"]["triangles"],flush=True)
    # Optional original bake code - this may require an X11/GL context.
    try:
        b=bake_texture(raw,model,scene_code[0],512)
        rgba=np.clip(b["colors"]*255,0,255).astype(np.uint8)
        atlas=Image.fromarray(rgba).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        atlas.save(OUT/"robot_texture_512.png")
        textured=trimesh.Trimesh(
            vertices=raw.vertices[b["vmapping"]],
            faces=b["indices"],
            process=False)
        textured.visual=trimesh.visual.texture.TextureVisuals(
            uv=b["uvs"],image=atlas)
        tpath=OUT/"TripoSR_Official_Robot_UV_512.glb"
        textured.export(tpath)
        reread=trimesh.load(tpath,force="scene",process=False)
        assert len(reread.dump(concatenate=True).faces)>1000
        report["texture_bake"]={"status":"success","file":tpath.name,
                                "atlas":"robot_texture_512.png",
                                "sha256":digest(tpath)}
        print("OFFICIAL_ROBOT_UV_BAKE_OK",flush=True)
    except Exception as exc:
        report["texture_bake"]={"status":"failed","error":str(exc)[:500]}
        print("OFFICIAL_ROBOT_UV_BAKE_FAILED",str(exc)[:200],flush=True)
    report["status"]="COMPLETED"
    (OUT/"benchmark_report.json").write_text(json.dumps(report,indent=2)+"\n")
    print("OFFICIAL_TRIPOSR_ROBOT_BENCHMARK_COMPLETE",json.dumps({
        "triangles":report["raw_glb"]["triangles"],
        "vertices":report["raw_glb"]["vertices"],
        "neural":report["neural_render"]["status"],
        "bake":report["texture_bake"]["status"],
    }),flush=True)

if __name__=="__main__":
    main()
