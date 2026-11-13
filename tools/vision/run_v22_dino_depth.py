#!/usr/bin/env python3
"""Real pretrained DINOv2 + Depth Anything V2, FORGE V22 reference vs render.

Input is a small, LOSSY, 2x2 comparison atlas generated from owner 4237 reference
and the actual V22 side/top images. Use features and relative depth as imperfect
diagnostics; neither recovers metric 3D. Geometry edits require independent
3D measurements. All original files remain immutable.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import json, base64, io, hashlib, numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoImageProcessor, AutoModel, AutoModelForDepthEstimation

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"build/forge_v22_actual_ai"
OUT.mkdir(parents=True,exist_ok=True)
payload=(ROOT/"tools/vision/v22-side-top-atlas.b64").read_text().strip()
# Strict validation: reject truncated or malformed embedded reference pairs.
raw=base64.b64decode(payload,validate=True)
Image.open(io.BytesIO(raw)).verify()
atlas=Image.open(io.BytesIO(raw)).convert("RGB")
assert atlas.size==(400,288),atlas.size
views={"side":(0,144),"top":(144,288)}
pairs={}
for k,(ya,yb) in views.items():
    # Each half has a genuinely different provenance: owner 4237 reference
    # at left; rendered V22 BasicClayShape GLB view at right.
    ref=atlas.crop((0,ya,200,yb))
    pred=atlas.crop((200,ya,400,yb))
    ref.save(OUT/(k+"_owner_reference.jpg"),quality=90)
    pred.save(OUT/(k+"_v22_render.jpg"),quality=90)
    pairs[k]=(ref,pred)

torch.set_num_threads(2)
dino_id="facebook/dinov2-small"
processor=AutoImageProcessor.from_pretrained(dino_id)
model=AutoModel.from_pretrained(dino_id).eval()
report={
  "status":"pretrained models executed on new V22 side/top comparison; NOT a reconstructed mesh",
  "input":str((ROOT/"tools/vision/v22-side-top-atlas.b64").relative_to(ROOT)),
  "atlas_sha256":hashlib.sha256(raw).hexdigest(),
  "paired_views":list(pairs),
  "dino_model":dino_id,
  "depth_model":"depth-anything/Depth-Anything-V2-Small-hf",
  "warning":"Input is downscaled and compressed; feature and depth matches are coarse visual diagnostics; not calibrated geometry.",
  "comparison":{},
  "weights_downloaded":True,
  "geometry_modified":False
}
for k,(reference,candidate) in pairs.items():
    batch=processor(images=[reference,candidate],return_tensors="pt")
    with torch.inference_mode():
        tok=model(**batch).last_hidden_state.float()
        cls=F.normalize(tok[:,0,:],dim=-1)
        patch=F.normalize(tok[:,1:,:],dim=-1)
    sims=(patch[0]@patch[1].T).cpu().numpy()
    nearest=np.argmax(sims,axis=1)
    twin=np.argmax(sims,axis=0)
    reciprocal=int(sum(1 for i,j in enumerate(nearest) if int(twin[j])==i))
    aligned=float((patch[0]*patch[1]).sum(-1).mean().item())
    report["comparison"][k]={
      "dino_global_cosine":round(float((cls[0]*cls[1]).sum().item()),5),
      "dino_aligned_patch_cosine":round(aligned,5),
      "dino_reciprocal_matches":reciprocal,
      "patch_count":int(patch.shape[1]),
      "interpretation":"Visual agreement only; features cannot specify target 3D vertex coordinates."
    }
    print("NFR_V22_DINO_PRETRAINED_OK",k,report["comparison"][k],flush=True)
del model,processor

depth_id="depth-anything/Depth-Anything-V2-Small-hf"
depth_proc=AutoImageProcessor.from_pretrained(depth_id)
depth_net=AutoModelForDepthEstimation.from_pretrained(depth_id).eval()
for k,(reference,candidate) in pairs.items():
    depths=[]
    for tag,img in (("owner_reference",reference),("v22_render",candidate)):
        inputs=depth_proc(images=img,return_tensors="pt")
        with torch.inference_mode():
            pred=depth_net(**inputs).predicted_depth
            pred=F.interpolate(pred.unsqueeze(1),size=(img.height,img.width),mode="bicubic",align_corners=False)[:,0]
        depth=pred[0].cpu().numpy()
        assert np.isfinite(depth).all() and np.ptp(depth)>1e-5
        p2,p98=np.percentile(depth,[2,98])
        normal=np.clip((depth-p2)/max(p98-p2,1e-5),0,1)
        Image.fromarray(np.uint8(normal*255)).save(OUT/(k+"_"+tag+"_relative_depth.png"))
        depths.append(normal)
    # Caution: per-image normalization does not calibrate actual 3D depths!
    corr=float(np.corrcoef(depths[0].ravel(),depths[1].ravel())[0,1])
    report["comparison"][k]["relative_depth_map_correlation"]=round(corr,5)
    report["comparison"][k]["relative_depth_note"]="Monocular relative depth: normalized per image and affected by framing; correlation is NOT a surface error in meters."
    print("NFR_V22_DEPTH_PRETRAINED_OK",k,report["comparison"][k]["relative_depth_map_correlation"],flush=True)
report["complete"]=True
(OUT/"V22_PRETRAINED_AI_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
assert len(report["comparison"])==2
print("NFR_V22_TWO_PRETRAINED_MODELS_COMPLETE",flush=True)
