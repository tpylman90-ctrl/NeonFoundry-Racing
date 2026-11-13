#!/usr/bin/env python3
"""Run genuine pretrained DINOv2 and Depth Anything V2 on owner's wireframe.

Paired inputs use IDENTICAL fixed camera positions/scale for V25 and V29.
Wireframe reference and model render both from actual GLB triangle edges.
Image compression, wire topology differences and 2D depth ambiguity remain.
"""
from pathlib import Path
import base64,io,hashlib,json,math
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
from transformers import AutoImageProcessor,AutoModel,AutoModelForDepthEstimation

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"build/forge_v25_wireframe_ai"
OUT.mkdir(parents=True,exist_ok=True)
sources={
 "V25":("tools/vision/v25-wireframe-actual-atlas.b64","f197b18d8a962b1361d525aa37da329ef099886ae1e9b3f8a2d0c86dedc08318"),
 "V29":("tools/vision/v29-wireframe-real-atlas.b64","e9ddbc828c9abb0c552d0f6f6ace88a43ffa4afc5293280f23fb03cc0830128e")
}
pairs={}
for version,(path,digest) in sources.items():
 b64=(ROOT/path).read_text().strip()
 raw=base64.b64decode(b64,validate=True)
 assert hashlib.sha256(raw).hexdigest()==digest,version+" atlas SHA mismatch"
 atlas=Image.open(io.BytesIO(raw)).convert("RGB")
 assert atlas.size==(400,288),(version,atlas.size)
 for view,ya,yb in (("side",0,144),("top",144,288)):
  reference=atlas.crop((0,ya,200,yb))
  candidate=atlas.crop((200,ya,400,yb))
  reference.save(OUT/f"{version}_{view}_owner_wireframe.jpg")
  candidate.save(OUT/f"{version}_{view}_actual_glb_wireframe.jpg")
  pairs[(version,view)]=(reference,candidate)
torch.set_num_threads(2)
report={
 "source":"User-supplied 4240.jpg basic five-view wireframe; V25 and V29 true GLB wireframe renderings in same fixed-side/top camera",
 "model_versions":list(sources),
 "camera_registered":True,
 "pretrained_weights_executed":False,
 "geometry_changed_by_AI":False,
 "notes":["Exact metric camera scale from labeled drawing is approximate, not a calibrated CAD camera",
  "Wireframe drawings create out-of-domain relative-depth maps; DINO features are texture sensitive",
  "DINO similarity and relative depth correlation are not percentages of geometry accuracy",
  "90 percent gate is independently measured 2D side/top silhouette IoU; no five-view 90 percent claim"],
 "models":{"dino":"facebook/dinov2-small","depth":"depth-anything/Depth-Anything-V2-Small-hf"},
 "comparisons":{}
}
proc=AutoImageProcessor.from_pretrained(report["models"]["dino"])
model=AutoModel.from_pretrained(report["models"]["dino"]).eval()
for (version,view),(ref,img) in pairs.items():
 batch=proc(images=[ref,img],return_tensors="pt")
 with torch.inference_mode():
  tokens=model(**batch).last_hidden_state.float()
  cls=F.normalize(tokens[:,0,:],dim=-1)
  patch=F.normalize(tokens[:,1:,:],dim=-1)
 cos=float((cls[0]*cls[1]).sum().item())
 aligned=(patch[0]*patch[1]).sum(-1).cpu().numpy()
 grid=math.isqrt(len(aligned))
 assert grid*grid==len(aligned)
 heat=Image.fromarray(np.uint8(np.clip((aligned.reshape(grid,grid)+1)/2,0,1)*255)).resize((200,144),Image.Resampling.BICUBIC)
 heat.save(OUT/f"{version}_{view}_DINO_patch_similarity.png")
 report["comparisons"].setdefault(version,{})[view]={
  "global_cls_cosine":round(cos,5),
  "spatial_patch_cosine":round(float(aligned.mean()),5),
  "patch_count":len(aligned),
 }
 print("REAL_PRETRAINED_DINO",version,view,report["comparisons"][version][view],flush=True)
del model,proc
proc=AutoImageProcessor.from_pretrained(report["models"]["depth"])
model=AutoModelForDepthEstimation.from_pretrained(report["models"]["depth"]).eval()
for (version,view),(ref,img) in pairs.items():
 depths=[]
 for label,picture in (("owner",ref),("actual",img)):
  batch=proc(images=picture,return_tensors="pt")
  with torch.inference_mode():
   dep=model(**batch).predicted_depth
   dep=F.interpolate(dep.unsqueeze(1),size=(144,200),mode="bicubic",align_corners=False)[:,0]
  depth=dep[0].cpu().numpy()
  assert np.isfinite(depth).all() and np.ptp(depth)>1e-6
  low,high=np.percentile(depth,[2,98])
  norm=np.clip((depth-low)/max(high-low,1e-6),0,1)
  Image.fromarray(np.uint8(norm*255)).save(OUT/f"{version}_{view}_{label}_relative_depth.png")
  depths.append(norm)
 corr=float(np.corrcoef(depths[0].ravel(),depths[1].ravel())[0,1])
 report["comparisons"][version][view]["relative_depth_correlation"]=round(corr,5)
 report["comparisons"][version][view]["depth_interpretation"]="Uncalibrated monocular estimate on line art; correlation is diagnostic only"
 print("REAL_PRETRAINED_DEPTH",version,view,corr,flush=True)
report["pretrained_weights_executed"]=True
report["comparison_deltas"]={}
for v in ("side","top"):
 report["comparison_deltas"][v]={
  "dino_cls_delta":round(report["comparisons"]["V29"][v]["global_cls_cosine"]-report["comparisons"]["V25"][v]["global_cls_cosine"],5),
  "dino_patch_delta":round(report["comparisons"]["V29"][v]["spatial_patch_cosine"]-report["comparisons"]["V25"][v]["spatial_patch_cosine"],5),
  "relative_depth_corr_delta":round(report["comparisons"]["V29"][v]["relative_depth_correlation"]-report["comparisons"]["V25"][v]["relative_depth_correlation"],5),
 }
(OUT/"FORGE_V25_V29_REAL_WIREFRAME_AI_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
print("FORGE_V25_WIREFRAME_BOTH_REAL_MODELS_COMPLETED",flush=True)
