#!/usr/bin/env python3
"""Run real DINOv2 + Depth Anything V2 on the owner's 8-view FORGE artwork.

This is a reference-processing experiment, NOT 3D reconstruction. Output:
8 cropped reference views, DINOv2 patch-PCA maps, real cross-view matches,
8 relative depth images, and one machine-readable report.
No model meshes, geometry-gate decisions or art are overwritten.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps
import torch
import torch.nn.functional as F
from transformers import AutoImageProcessor, AutoModel, AutoModelForDepthEstimation

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "art/hero_01/references/forge_8view_original.jpg"
DEST = Path(os.environ.get("NFR_ART_AI_OUTPUT", str(ROOT / "build/forge_artwork_ai")))
DEST.mkdir(parents=True, exist_ok=True)
torch.set_num_threads(2)
torch.manual_seed(0)

# Bounding-box crops EXCLUDE almost all sheet headings, while keeping some
# context around the craft and all visible extremities. RGB artwork only.
CROPS = {
    "front": (35, 90, 385, 273),
    "rear": (410, 90, 756, 273),
    "left_side": (806, 89, 1508, 278),
    "right_side": (798, 291, 1508, 462),
    "top": (66, 329, 359, 832),
    "underside": (436, 329, 733, 832),
    "front_three_quarter": (773, 505, 1140, 819),
    "rear_three_quarter": (1157, 503, 1510, 819),
}
NAMES = list(CROPS)
EXPECTED_SHA256 = "8606398e4935e46b6bc9f3f580ab9f2506318a7c7c0c954d15d103868b0ae9a0"
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256, "Reference source changed unexpectedly"
board = Image.open(SOURCE).convert("RGB")
assert board.size == (1536, 857), "Reference artwork dimensions do not match crop calibration"
images = {name: board.crop(bounds) for name, bounds in CROPS.items()}
for name, image in images.items():
    image.save(DEST / (name + "_reference.png"))
print("NFR_REAL_REFERENCE_CROPS_OK views=8", flush=True)


def heatmap(matrix, names, path):
    cell = 74
    padleft = 153
    top = 58
    size = len(names)
    im = Image.new("RGB", (padleft + size*cell + 14, top + size*cell + 16), (23, 27, 36))
    draw = ImageDraw.Draw(im)
    for i, name in enumerate(names):
        draw.text((4, top + i*cell + 30), name[:23], fill=(240, 240, 240))
        draw.text((padleft+i*cell + 2, 14), name.replace("_", " ")[:10], fill=(240, 240, 240))
    for i in range(size):
        for j in range(size):
            v = float(matrix[i][j])
            t = max(0.0, min(1.0, (v + 1)/2))
            col = (int(18+60*t), int(35+155*t), int(80+130*t))
            x0 = padleft+j*cell
            y0 = top+i*cell
            draw.rectangle((x0+2,y0+2,x0+cell-3,y0+cell-3),fill=col)
            draw.text((x0+10,y0+28),f"{v:.3f}",fill=(255,255,255))
    im.save(path)


def patch_matches(a, b, features):
    aa = F.normalize(features[a].float(), dim=-1)
    bb = F.normalize(features[b].float(), dim=-1)
    similarities = (aa @ bb.T).cpu().numpy()
    ai_to_b = np.argmax(similarities, axis=1)
    bi_to_a = np.argmax(similarities, axis=0)
    side = math.isqrt(len(ai_to_b))
    assert side*side == len(ai_to_b), "DINO image tokens not in expected square patch layout"
    candidates = []
    for x, y in enumerate(ai_to_b):
        y = int(y)
        similarity = float(similarities[x, y])
        if int(bi_to_a[y]) == x and similarity > .45:
            candidates.append((similarity, int(x), int(y)))
    candidates.sort(reverse=True)
    chosen = []
    for similarity, x, y in candidates:
        ax,ay=x%side,x//side
        bx,by=y%side,y//side
        # Avoid overcrowding feature plots with multiple nearby neighbors.
        if any((ax-xx)**2+(ay-yy)**2 < 4 or (bx-xxx)**2+(by-yyy)**2 < 4
               for _,xx,yy,xxx,yyy in chosen):
            continue
        chosen.append((similarity, ax, ay, bx, by))
        if len(chosen)>=16:
            break
    return [{"cosine":round(float(s),4),
             "a_patch":[int(x),int(y)],"b_patch":[int(bx),int(by)],
             "a_xy_normalized":[round((x+.5)/side,4),round((y+.5)/side,4)],
             "b_xy_normalized":[round((bx+.5)/side,4),round((by+.5)/side,4)]}
            for s,x,y,bx,by in chosen]


def match_image(a, b, matches, file):
    left = images[a].resize((336,336),Image.Resampling.LANCZOS)
    right = images[b].resize((336,336),Image.Resampling.LANCZOS)
    img=Image.new("RGB",(700,368),(25,28,33))
    img.paste(left,(6,26))
    img.paste(right,(358,26))
    dr=ImageDraw.Draw(img)
    dr.text((8,8),a,fill="white")
    dr.text((362,8),b,fill="white")
    for idx,p in enumerate(matches):
        ax,ay=p["a_xy_normalized"]
        bx,by=p["b_xy_normalized"]
        start=(6+round(ax*336),26+round(ay*336))
        end=(358+round(bx*336),26+round(by*336))
        col=(80+idx*4,230-idx*6,130+idx*3)
        dr.line((start,end),fill=col,width=1)
        dr.ellipse((start[0]-3,start[1]-3,start[0]+3,start[1]+3),fill=col)
        dr.ellipse((end[0]-3,end[1]-3,end[0]+3,end[1]+3),fill=col)
    img.save(file)


DINO_ID = "facebook/dinov2-small"
dino_processor = AutoImageProcessor.from_pretrained(DINO_ID)
dino = AutoModel.from_pretrained(DINO_ID).eval()
with torch.inference_mode():
    # All 8 original artwork tiles, NOT the previous Blender renders.
    x = dino_processor(images=[images[n] for n in NAMES],return_tensors="pt")
    tokens = dino(**x).last_hidden_state
    class_tokens = F.normalize(tokens[:,0,:].float(), dim=-1)
    patch_tokens = F.normalize(tokens[:,1:,:].float(), dim=-1)
    sims = (class_tokens@class_tokens.T).cpu().numpy()
sims = np.clip(sims,-1,1)
assert sims.shape == (8,8) and np.isfinite(sims).all()
sim_json = {a:{b:round(float(sims[i,j]),6)
              for j,b in enumerate(NAMES)} for i,a in enumerate(NAMES)}
heatmap(sims,NAMES,DEST/"dinov2_global_similarity.png")
print("NFR_ARTWORK_DINOV2_OK", flush=True)

# One PCA color embedding shared across all 8 views, making visual feature
# groups comparable across the views. Not a semantic-part segmenter.
p=patch_tokens.cpu().numpy()
side = math.isqrt(p.shape[1])
assert side*side==p.shape[1]
flat=p.reshape(-1,p.shape[-1]).astype("float32")
centered=flat-flat.mean(axis=0,keepdims=True)
_,_,basis=np.linalg.svd(centered,full_matrices=False)
scores=centered@basis[:3].T
lo=np.percentile(scores,2,axis=0)
hi=np.percentile(scores,98,axis=0)
rgb=np.uint8(np.clip((scores-lo)/(hi-lo+1e-7),0,1)*255)
for i,name in enumerate(NAMES):
    feat=rgb[i*p.shape[1]:(i+1)*p.shape[1]].reshape(side,side,3)
    Image.fromarray(feat,"RGB").resize((336,336),Image.Resampling.NEAREST).save(
        DEST/(name+"_dinov2_features.png"))

pairs=[
    ("left_side","right_side"),
    ("front","front_three_quarter"),
    ("rear","rear_three_quarter"),
    ("top","front_three_quarter"),
    ("top","rear_three_quarter"),
]
feature_map={name:patch_tokens[i] for i,name in enumerate(NAMES)}
matches={}
for a,b in pairs:
    result=patch_matches(a,b,feature_map)
    matches[a+"__"+b]=result
    match_image(a,b,result,DEST/("dino_matches_"+a+"__"+b+".png"))
del dino, dino_processor, x, tokens, patch_tokens, class_tokens, feature_map

DEPTH_ID = "depth-anything/Depth-Anything-V2-Small-hf"
depth_processor = AutoImageProcessor.from_pretrained(DEPTH_ID)
depth_model = AutoModelForDepthEstimation.from_pretrained(DEPTH_ID).eval()
depth_reports={}
for name in NAMES:
    im=images[name]
    with torch.inference_mode():
        input_tensors=depth_processor(images=im,return_tensors="pt")
        output=depth_model(**input_tensors)
        depth=depth_processor.post_process_depth_estimation(
            output,target_sizes=[(im.height,im.width)]
        )[0]["predicted_depth"].cpu().numpy()
    assert np.isfinite(depth).all() and float(np.ptp(depth)) > 1e-6,name
    low,high=(float(v) for v in np.percentile(depth,(2,98)))
    normalized=np.uint8(np.clip((depth-low)/max(high-low,1e-8)*255,0,255))
    # Grayscale means relative near/far only; not meters.
    Image.fromarray(normalized,"L").save(DEST/(name+"_relative_depth.png"))
    depth_reports[name]={
        "height":int(im.height),"width":int(im.width),
        "relative_range":round(float(np.ptp(depth)),6),
        "relative_p02":round(low,6),"relative_p98":round(high,6),
    }
    print("NFR_ARTWORK_DEPTH_VIEW_OK",name,flush=True)
del depth_model,depth_processor

# 8-depth-map contact sheet for quick user review.
sheet=Image.new("RGB",(1050,1000),(23,27,33))
dr=ImageDraw.Draw(sheet)
for i,name in enumerate(NAMES):
    d=Image.open(DEST/(name+"_relative_depth.png")).convert("RGB")
    d.thumbnail((500,215),Image.Resampling.LANCZOS)
    left=15+(i%2)*520+(500-d.width)//2
    top=15+(i//2)*248
    sheet.paste(d,(left,top+19))
    dr.text((15+(i%2)*520,top),name,fill="white")
sheet.save(DEST/"depth_all_8_views.jpg",quality=90)
report={
    "asset":"NF-H01 FORGE eight-view owner reference",
    "reference_sha256":hashlib.sha256(raw).hexdigest(),
    "reference_resolution_px":list(board.size),
    "reference_used":True,
    "view_crop_boxes_px":{name:list(rect) for name,rect in CROPS.items()},
    "dino_model":DINO_ID,
    "dino_global_cosine_similarity":sim_json,
    "dino_patch_grid":side,
    "dino_mutual_nearest_neighbor_patch_examples":matches,
    "dino_interpretation":"Image feature similarities and candidate patch correspondences; NOT physical dimension or reliable 3D feature identification.",
    "depth_model":DEPTH_ID,
    "relative_depth_statistics":depth_reports,
    "depth_interpretation":"Relative monocular depth on artwork crops; not physical meters, not a unique 3D surface or consistent scale across views.",
    "source_blender_model_modified":False,
    "geometry_reconstruction_performed":False,
    "owner_gate_approval":"unchanged",
    "validated_on":"owner-uploaded original 8-view reference artwork, not Blender render substitute",
}
(DEST/"ARTWORK_AI_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
assert len(depth_reports)==8 and len(matches)==5
print("NFR_REAL_ARTWORK_BOTH_MODELS_COMPLETE views=8",flush=True)
