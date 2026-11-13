#!/usr/bin/env python3
"""Forge V20 calibration diagnostic on the owner's ORIGINAL orthographic artwork.

Only analysis: no geometry edits. Uses V16's fixed camera registration and a
conservative GrabCut mask that can be inspected with the generated overlays.
Reference silhouettes are *approximate*, not authoritative segmentation.
"""
from pathlib import Path
import json

import numpy as np
import cv2
from PIL import Image, ImageDraw
import trimesh

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"art/hero_01/experiments/V19/FORGE_V19_CurvatureStudy.glb"
REFERENCE=ROOT/"art/hero_01/references/forge_8view_original.jpg"
OUT=ROOT/"build/forge_v20_diagnostic"
OUT.mkdir(parents=True,exist_ok=True)
scene=trimesh.load(SOURCE,force="scene",process=False)
original=np.array(Image.open(REFERENCE).convert("RGB"))
assert original.shape==(857,1536,3)
views={
 "side":(806,89,1508,278),
 "top":(66,329,359,832),
 "front":(35,90,385,273),
 "rear":(410,90,756,273),
}
def ref_mask(ref,view):
    rgb=ref.astype(np.uint8)
    h,w=rgb.shape[:2]
    maxv=np.max(rgb,axis=2)
    # Background is a charcoal studio slate, brighter grid lines excluded.
    mask=np.where(maxv>=82,cv2.GC_PR_FGD,cv2.GC_PR_BGD).astype(np.uint8)
    mask[maxv>=133]=cv2.GC_FGD
    edge=7 if view in ("side","top") else 4
    mask[:edge,:]=cv2.GC_BGD
    mask[-edge:,:]=cv2.GC_BGD
    mask[:,:edge]=cv2.GC_BGD
    mask[:,-edge:]=cv2.GC_BGD
    # Add a well-inside-center sure-foreground region for challenging dark scenes.
    # Sure foreground is already supplied by the bright armor; do not prepaint.
    if not np.any(mask==cv2.GC_FGD): raise ValueError("reference lacks bright FG")
    bg=np.zeros((1,65),np.float64); fg=np.zeros((1,65),np.float64)
    cv2.grabCut(rgb,mask,None,bg,fg,6,cv2.GC_INIT_WITH_MASK)
    result=np.isin(mask,(cv2.GC_FGD,cv2.GC_PR_FGD)).astype(np.uint8)
    # Remove isolated gridline fragments then bridge dark recesses.
    result=cv2.morphologyEx(result,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    count,labels,stats,centers=cv2.connectedComponentsWithStats(result,8)
    minimum={"side":180,"top":160,"front":90,"rear":90}[view]
    keep=np.zeros((h,w),dtype=np.uint8)
    for k in range(1,count):
        if stats[k,cv2.CC_STAT_AREA]>=minimum:
            keep[labels==k]=1
    contours,_=cv2.findContours(keep,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    filled=np.zeros((h,w),dtype=np.uint8)
    cv2.drawContours(filled,contours,-1,1,thickness=cv2.FILLED)
    return filled.astype(bool)

def projected(scene,view,shape,part_names=None):
    h,w=shape
    binary=np.zeros((h,w),np.uint8)
    for node in scene.graph.nodes_geometry:
        if part_names is not None and node not in part_names: continue
        t,geo=scene.graph.get(node)
        mesh=scene.geometry[geo]
        vertices=np.asarray(mesh.vertices)@t[:3,:3].T+t[:3,3]
        x,y,z=vertices.T
        if view=="side":
            p=np.column_stack((29+(3.90-z)*78.6,163-(y-.065)*78.6))
        elif view=="top":
            p=np.column_stack((145+x*58.6,7+(3.9-z)*58.6))
        elif view in ("front","rear"):
            p=np.column_stack((w/2+x*64.7,164-(y-.065)*64.7))
        else: raise ValueError(view)
        p=np.rint(p).astype(np.int32)
        for f in mesh.faces:
            cv2.fillConvexPoly(binary,p[f],1)
    return binary.astype(bool)

def metrics(ref,model):
    shared=ref&model
    precision=float(shared.sum()/max(model.sum(),1))
    recall=float(shared.sum()/max(ref.sum(),1))
    iou=float(shared.sum()/max((ref|model).sum(),1))
    return {"reference_area_px":int(ref.sum()),"model_area_px":int(model.sum()),
      "intersection_over_union":round(iou,5),"recall":round(recall,5),
      "precision":round(precision,5),"missing_reference_px":int((ref&~model).sum()),
      "excess_model_px":int((model&~ref).sum())}

report={"source":str(SOURCE.relative_to(ROOT)),
        "reference":str(REFERENCE.relative_to(ROOT)),
        "method":"Original owner's reference, approximate GrabCut, fixed V16 camera",
        "warning":"Reference sheet can have perspective differences, dark parts omitted, and inconsistent artwork proportions. Scoring is diagnostic, not automatic approval.",
        "views":{}}
for v,box in views.items():
    crop=original[box[1]:box[3],box[0]:box[2]]
    rm=ref_mask(crop,v)
    mm=projected(scene,v,rm.shape)
    values=metrics(rm,mm)
    report["views"][v]=values
    color=np.zeros((*rm.shape,3),np.uint8)
    color[rm&mm]=[186,192,197]
    color[rm&~mm]=[242,91,86]
    color[~rm&mm]=[77,195,231]
    # Panel: photograph, extracted reference silhouette, model, difference.
    panels=[]
    for x in (crop,np.repeat((rm*255)[:,:,None],3,axis=2),
              np.repeat((mm*255)[:,:,None],3,axis=2),color):
        panels.append(Image.fromarray(x.astype(np.uint8),"RGB"))
    w,h=panels[0].size
    sheet=Image.new("RGB",(2*w+20,2*h+66),(29,33,41))
    d=ImageDraw.Draw(sheet)
    for i,p in enumerate(panels):
        px=10+(i%2)*w;py=28+(i//2)*(h+23)
        sheet.paste(p,(px,py))
        d.text((px,py-16),("Reference artwork","Estimated ref mask","V19 real mesh","Mismatch: red missing; blue excess")[i],fill="white")
    sheet.save(OUT/("FORGE_V20_DIAG_"+v+".png"))
    print("NFR_V20_VIEW",v,json.dumps(values),flush=True)
(OUT/"FORGE_V20_DIAGNOSTIC.json").write_text(json.dumps(report,indent=2)+"\n")
print("NFR_V20_DIAGNOSTIC_COMPLETE",flush=True)
