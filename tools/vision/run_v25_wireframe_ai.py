#!/usr/bin/env python3
"""Actual pretrained DINOv2 and Depth Anything V2 on Forge owner's wireframe.

Side/top cells from owner's 4240 wireframe and *real* V25 GLB rendering.
The 400x288 compact atlas is deliberately compressed; inference is diagnostic.
Never count feature/depth similarity as 90% geometric correspondence.
"""
from pathlib import Path
import base64,io,hashlib,json
import numpy as np
from PIL import Image,ImageDraw
import torch
import torch.nn.functional as F
from transformers import AutoImageProcessor,AutoModel,AutoModelForDepthEstimation

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"build/forge_v25_wireframe_ai"
OUT.mkdir(parents=True,exist_ok=True)
src=ROOT/"tools/vision/v25-wireframe-actual-atlas.b64"
raw=base64.b64decode(src.read_text().strip(),validate=True)
assert hashlib.sha256(raw).hexdigest()=="1bf9559649ba4c23412acefc296c72d93069b19982903f0be8eaa115b989d137", "Atlas checksum mismatch"
atlas=Image.open(io.BytesIO(raw)).convert("RGB")
assert atlas.size==(400,288)
torch.set_num_threads(2)
views={
    "side":(atlas.crop((0,0,200,144)),atlas.crop((200,0,400,144))),
    "top":(atlas.crop((0,144,200,288)),atlas.crop((200,144,400,288)))
}
result={
 "source":"User's 4240.jpg basic 5-view wireframe sheet, paired with actual FORGE_V25_side.png and FORGE_V25_top.png rendered from V25 GLB",
 "atlas_sha256":hashlib.sha256(raw).hexdigest(),
 "models":{"dino":"facebook/dinov2-small","depth":"depth-anything/Depth-Anything-V2-Small-hf"},
 "pretrained_inference_completed":False,
 "reference_images_are_wireframe_drawings":True,
 "camera_calibrated":False,
 "geometry_changed":False,
 "limitations":"2D grayscale wireframe plus compressed art is out-of-domain for monocular depth; relative depth maps are not metric or ground truth. DINO cosine is not an accuracy percentage; not a pass/fail geometry metric.",
 "views":{}
}
for label,(ref,render) in views.items():
 ref.save(OUT/f"{label}_reference_wireframe.jpg")
 render.save(OUT/f"{label}_actual_v25_glb.jpg")
proc=AutoImageProcessor.from_pretrained(result["models"]["dino"])
net=AutoModel.from_pretrained(result["models"]["dino"]).eval()
for label,(ref,render) in views.items():
 inp=proc(images=[ref,render],return_tensors="pt")
 with torch.inference_mode():
  tokens=net(**inp).last_hidden_state.float()
  cls=F.normalize(tokens[:,0,:],dim=-1)
  patch=F.normalize(tokens[:,1:,:],dim=-1)
 aligned=torch.sum(patch[0]*patch[1],dim=1)
 cosine=float((cls[0]*cls[1]).sum().item())
 spatial=float(aligned.mean().item())
 count=patch.shape[1]
 grid=int(np.sqrt(count))
 if grid*grid!=count:raise RuntimeError("Unexpected DINO patch layout")
 sim=aligned.reshape(grid,grid).cpu().numpy()
 sim=np.uint8(np.clip((sim+1)/2,0,1)*255)
 heat=Image.fromarray(sim).resize((200,144),Image.Resampling.BICUBIC)
 heat.save(OUT/f"{label}_DINO_aligned_patch_agreement.png")
 result["views"][label]={
  "dino_cls_cosine":round(cosine,5),
  "dino_spatial_patch_cosine":round(spatial,5),
  "patch_count":int(count),
  "reference_vs_render":"Wireframe drawing vs neutral gray GLB; texture/domain differences affect DINO comparison"
 }
 print("FORGE_WIRE_DINO_PRETRAINED",label,result["views"][label],flush=True)
del proc,net
proc=AutoImageProcessor.from_pretrained(result["models"]["depth"])
net=AutoModelForDepthEstimation.from_pretrained(result["models"]["depth"]).eval()
for label,(ref,render) in views.items():
 maps=[]
 for kind,img in (("reference_wireframe",ref),("actual_v25_glb",render)):
  inp=proc(images=img,return_tensors="pt")
  with torch.inference_mode():
   pred=net(**inp).predicted_depth
   pred=F.interpolate(pred.unsqueeze(1),size=(144,200),mode="bicubic",align_corners=False)[:,0]
  dep=pred[0].cpu().numpy().astype(np.float64)
  assert np.isfinite(dep).all() and dep.max()>dep.min()
  a,b=np.percentile(dep,[2,98])
  norm=np.clip((dep-a)/max(b-a,1.e-8),0,1)
  Image.fromarray(np.uint8(norm*255)).save(OUT/f"{label}_{kind}_depth_anything_v2.png")
  maps.append(norm)
 corr=float(np.corrcoef(maps[0].reshape(-1),maps[1].reshape(-1))[0,1])
 result["views"][label]["relative_depth_correlation"]=round(corr,5)
 result["views"][label]["depth_warning"]="Monocular estimates on wireframe art can be inaccurate and are independently normalized; correlation is not shape accuracy."
 print("FORGE_WIRE_DEPTH_PRETRAINED",label,corr,flush=True)
result["pretrained_inference_completed"]=True
(OUT/"FORGE_V25_Wireframe_DINO_Depth_Report.json").write_text(json.dumps(result,indent=2)+"\n")
print("FORGE_V25_WIREFRAME_BOTH_REAL_MODELS_COMPLETED",flush=True)
