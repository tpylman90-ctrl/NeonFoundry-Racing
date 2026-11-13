#!/usr/bin/env python3
"""Forge V20: actual GLB geometry inventory and neutral shaded previews.

CPU triangle painter. Not a final path-traced render or reference-aligned
comparison; only visual engineering inspection of the SOURCE GLB.
"""
from pathlib import Path
import json
import numpy as np
import cv2
import trimesh

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"art/hero_01/experiments/V19/FORGE_V19_CurvatureStudy.glb"
OUT=ROOT/"build/forge_v20_preview"
OUT.mkdir(parents=True,exist_ok=True)
scene=trimesh.load(FILE,force="scene",process=False)
reported=[]
triangles=[]
for node in scene.graph.nodes_geometry:
    T,geom_name=scene.graph.get(node)
    g=scene.geometry[geom_name]
    v=g.vertices@T[:3,:3].T+T[:3,3]
    name=node
    bounds=[np.round(v.min(axis=0),3).tolist(),np.round(v.max(axis=0),3).tolist()]
    reported.append({"name":name,"faces":int(len(g.faces)),"bounds":bounds})
    material=getattr(g.visual,"material",None)
    rgb=np.array([151,147,141],float)
    if material is not None:
        try:
            rgb=np.array(material.baseColorFactor[:3],dtype=float)
            if float(rgb.max())<=1.2:rgb*=255
        except (AttributeError,TypeError,ValueError): pass
    rgb=np.clip(rgb,19,240)
    verts=v[g.faces]
    norms=np.cross(verts[:,1]-verts[:,0],verts[:,2]-verts[:,0])
    n=np.linalg.norm(norms,axis=1)
    good=n>1e-8
    verts=verts[good]
    norms=norms[good]/n[good,None]
    triangles.append((verts,norms,rgb))

inventory={"source":str(FILE.relative_to(ROOT)),"mesh_count":len(reported),
           "total_triangles":sum(v["faces"] for v in reported),
           "parts":sorted(reported,key=lambda x:x["name"])}
(OUT/"part_inventory.json").write_text(json.dumps(inventory,indent=2)+"\n")
for p in sorted(reported,key=lambda x:-x["faces"])[:35]:
    print("PART",p["faces"],p["name"],p["bounds"],flush=True)
tris=np.concatenate([x[0] for x in triangles],axis=0)
normals=np.concatenate([x[1] for x in triangles],axis=0)
colors=np.concatenate([np.repeat(x[2].reshape(1,3),len(x[0]),axis=0) for x in triangles],axis=0)
light=np.array([.4,.8,.45],float);light/=np.linalg.norm(light)
lambert=np.clip(normals@light,0,1)
shade=.38+.62*lambert
palette=np.uint8(np.clip(colors*shade[:,None],0,255))
W,H=1100,720
views={
 "side":([-13,6,0],[0,1.12,0],10.5),
 "top":([0,16,0],[0,0,-.25],10.0),
 "front_three_quarter":([-10,6.0,12],[0,1.10,0],10.5),
 "rear_three_quarter":([10,7,-12],[0,1.1,0],10.5),
 "rear":([0,4,-17],[0,1.15,0],7.5),
}
from PIL import Image,ImageDraw
for name,(eye,center,scale) in views.items():
    eye=np.asarray(eye,float);center=np.asarray(center,float)
    fw=center-eye;fw/=np.linalg.norm(fw)
    right=np.cross(fw,[0,1,0])
    if np.linalg.norm(right)<.001:
        right=np.array([1.,0.,0.])
    right/=np.linalg.norm(right)
    up=np.cross(right,fw)
    projected=tris-center
    # Coordinates in camera plane, with dynamic aspect correction.
    xs=np.einsum("ijk,k->ij",projected,right)
    ys=np.einsum("ijk,k->ij",projected,up)
    pixel=np.stack([W*.5+xs*H/scale,H*.5-ys*H/scale],axis=2)
    depth=np.einsum("ijk,k->ij",tris-eye,fw).mean(axis=1)
    order=np.argsort(-depth)
    canvas=np.full((H,W,3),(30,34,42),dtype=np.uint8)
    for i in order:
        p=np.rint(pixel[i]).astype(np.int32)
        if np.all((p[:,0]<-10)|(p[:,0]>W+10)|(p[:,1]<-10)|(p[:,1]>H+10)):
            continue
        cv2.fillConvexPoly(canvas,p,palette[i].tolist())
    im=Image.fromarray(canvas,"RGB")
    dr=ImageDraw.Draw(im)
    dr.rectangle((18,18,410,52),fill=(20,23,30))
    dr.text((28,27),"FORGE V19 / actual GLB mesh / "+name,fill=(240,240,240))
    im.save(OUT/("FORGE_V20_GLB_"+name+".png"))
print("NFR_V20_PREVIEW_OK",len(reported),len(tris),flush=True)
