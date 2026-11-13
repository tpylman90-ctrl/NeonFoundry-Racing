#!/usr/bin/env python3
"""FORGE V20 / actual reference-guided assembly shape correction.

Stage 02 inspection-only experiment. Uses the V19 REAL GLB, the owner's
8-view photo sheet and the published V20 diagnostic. Implements distinct,
reproducible geometric adjustments:
- shorten the too-long greenhouse towards its front bulkhead, with all frames;
- reshape nose/intake width smoothly to a tighter forebody taper;
- move sculpted forewings toward the front intake mount zone;
- increase rear fin sweep without lifting or deleting engine/wing assemblies.

It is neither AI-derived dimensional reconstruction nor production approval.
All existing objects and materials remain. Owner reviews the new REAL GLB.
"""
from __future__ import annotations
import json
from pathlib import Path
import math
import numpy as np
import trimesh
from PIL import Image, ImageDraw

from forge_v20_reference_diagnostics import (
    original as reference_board, views, ref_mask, projected, metrics
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"art/hero_01/experiments/V19/FORGE_V19_CurvatureStudy.glb"
OUT=ROOT/"build/forge_v20_shape_fit"
OUT.mkdir(parents=True,exist_ok=True)
OUTPUT=OUT/"FORGE_V20_ReferenceShapeFit.glb"

baseline=trimesh.load(SOURCE,force="scene",process=False)
candidate=trimesh.load(SOURCE,force="scene",process=False)
assert len(baseline.geometry)==330
assert set(baseline.geometry)==set(candidate.geometry)

protect={
 "V15_320_PORT_IntegratedSweptRearSideWing",
 "V15_320_STBD_IntegratedSweptRearSideWing",
 "THRUST_PORT_HollowMainNozzle",
 "THRUST_STBD_HollowMainNozzle",
}
assert protect.issubset(candidate.geometry)
canopy_nodes=[k for k in candidate.geometry if (
    k.startswith("V15_200_") or k.startswith("V15_211_") or
    k.startswith("V15_212_") or k.startswith("V15_213_") or
    k.startswith("V15_215_")
)]
assert len(canopy_nodes)>20
forewing_nodes=[k for k in candidate.geometry if "ForeWingSculptedRoot" in k]
rearfin_nodes=[k for k in candidate.geometry if "SweepbackFin" in k]
assert len(forewing_nodes)==2 and len(rearfin_nodes)==2
assert len(candidate.geometry["V15_200_ReferenceAlignedOnePieceGreenhouse"].faces)>=200

changed=[]
groups={"greenhouse":[], "forewing":[], "rearfin":[], "forebody_taper":[]}
def smoothstep(t):
    t=np.clip(t,0.,1.)
    return t*t*(3.-2.*t)

for key,g in candidate.geometry.items():
    if key in protect or key.startswith("THRUST_"):
        continue
    before=np.array(g.vertices,copy=True)
    if key in canopy_nodes:
        v=before.copy()
        # Geometric start of owner's canopy matches existing front windshield;
        # excess rearward extension is shortened to meet the V19 rear roof.
        oldz=v[:,2].copy()
        v[:,2]=.45+(oldz-.45)*.735
        q=np.clip((.45-oldz)/3.12,0,1)
        v[:,1]+=.155*np.sin(math.pi*q)**1.5
        v[:,0]*=1.+.025*np.sin(math.pi*q)
        groups["greenhouse"].append(key)
    elif key in forewing_nodes:
        v=before.copy()
        v[:,2]+=.70
        side=np.sign(v[:,0])
        v[:,0]=side*(1.50+np.maximum(np.abs(v[:,0])-1.50,0)*1.26)
        groups["forewing"].append(key)
    elif key in rearfin_nodes:
        v=before.copy()
        # Pitch back TOP only; lower attachment remains at its existing base.
        q=smoothstep((v[:,1]-1.26)/(.90))
        v[:,2]-=.62*q
        groups["rearfin"].append(key)
    else:
        v=before.copy()
        # Cross-section guided tapered forebody; keep centerline and rear intact.
        # x is width; z grows toward nose. Smooth field avoids hard kinks.
        q=smoothstep((v[:,2]-.72)/(3.88-.72))
        v[:,0]*=(1.-.16*q)
        if np.max(np.abs(v-before))<1e-8:
            continue
        groups["forebody_taper"].append(key)

    assert np.isfinite(v).all(),key
    assert np.max(np.abs(v-before))<.9,key
    if not np.array_equal(v,before):
        watertight=bool(g.is_watertight)
        g.vertices=v
        if watertight:
            g.fix_normals()
            assert g.is_watertight,key
        changed.append(key)

assert len(changed)>60, "This must alter physical meshes, not just one overlay"
assert len(groups["greenhouse"])>20
assert len(groups["forebody_taper"])>20
assert not any(x in changed for x in protect)
for key in protect:
    assert np.array_equal(candidate.geometry[key].vertices,baseline.geometry[key].vertices),key
    assert np.array_equal(candidate.geometry[key].faces,baseline.geometry[key].faces),key
for key in set(candidate.geometry)-set(changed):
    assert np.array_equal(candidate.geometry[key].vertices,baseline.geometry[key].vertices),key

canopy_old=baseline.geometry["V15_200_ReferenceAlignedOnePieceGreenhouse"]
canopy_new=candidate.geometry["V15_200_ReferenceAlignedOnePieceGreenhouse"]
assert (canopy_old.bounds[1,2]-canopy_old.bounds[0,2])>3
assert (canopy_new.bounds[1,2]-canopy_new.bounds[0,2])<2.45
assert canopy_new.bounds[1,1]>canopy_old.bounds[1,1]+.12

forewing_before=[baseline.geometry[k].bounds for k in forewing_nodes]
forewing_after=[candidate.geometry[k].bounds for k in forewing_nodes]
assert all(a[0,2]>b[0,2]+.65 for a,b in zip(forewing_after,forewing_before))

assert len(candidate.geometry)==len(baseline.geometry)
assert set(candidate.geometry)==set(baseline.geometry)
OUTPUT.write_bytes(trimesh.exchange.gltf.export_glb(candidate))
reopened=trimesh.load(OUTPUT,force="scene",process=False)
assert len(reopened.geometry)==len(baseline.geometry)
assert set(reopened.geometry)==set(baseline.geometry)

# Respect actual owners' original photo sheet and registered camera geometry.
# Metrics are explicitly provisional due the charcoal-colored artwork, unaligned
# front/rear perspective, and imperfect GrabCut of dark intakes/engine bores.
compare={}
for view,box in views.items():
    crop=reference_board[box[1]:box[3],box[0]:box[2]]
    ref=ref_mask(crop,view)
    previous=projected(baseline,view,ref.shape)
    actual=projected(reopened,view,ref.shape)
    base_metrics=metrics(ref,previous)
    new_metrics=metrics(ref,actual)
    compare[view]={"V19":base_metrics,"V20":new_metrics,
        "delta_iou":round(new_metrics["intersection_over_union"]-base_metrics["intersection_over_union"],5),
        "delta_recall":round(new_metrics["recall"]-base_metrics["recall"],5)}
    h,w=ref.shape
    # Two actual real-mesh-versus-reference overlays, same camera across passes.
    sheet=Image.new("RGB",(w*2+20,h+56),(25,29,36))
    d=ImageDraw.Draw(sheet)
    for i,(name,pred,m) in enumerate((("V19",previous,base_metrics),("V20",actual,new_metrics))):
        rgb=np.zeros((h,w,3),dtype=np.uint8)
        rgb[ref&pred]=[193,198,201]
        rgb[ref&~pred]=[242,91,86]
        rgb[~ref&pred]=[67,194,229]
        sheet.paste(Image.fromarray(rgb),(10+i*w,42))
        d.text((10+i*w,10),f"{name} vs owner artwork / {view}",fill="white")
        d.text((10+i*w,25),f"IoU {m['intersection_over_union']:.3f}  Recall {m['recall']:.3f}",fill="white")
    sheet.save(OUT/("FORGE_V20_REFERENCE_AB_"+view+".png"))
    print("NFR_V20_REFERENCES",view,compare[view],flush=True)

report={
 "status":"Owner inspection / shape-fit experimental GLB; not game-approved",
 "source":str(SOURCE.relative_to(ROOT)),
 "reference":"art/hero_01/references/forge_8view_original.jpg",
 "output":str(OUTPUT.relative_to(ROOT)),
 "technique":"Curvature-smoothed width taper, assembly-coherent greenhouse longitudinal shortening and height lift, forewing relocation, upper fin sweep",
 "purpose":"Match gross reference landmarks rather than decorate the existing body",
 "warning":"Crop masks are automatic approximations and the reference art is not certified orthographic CAD; automated IoU is diagnostic, not proof of fidelity",
 "original_geometry_count":len(baseline.geometry),
 "output_geometry_count":len(reopened.geometry),
 "modified_meshes":len(changed),
 "modified_groups":{k:{"count":len(v),"names":v} for k,v in groups.items()},
 "main_greenhouse_before_bounds_m":np.round(canopy_old.bounds,4).tolist(),
 "main_greenhouse_after_bounds_m":np.round(canopy_new.bounds,4).tolist(),
 "rear_wings_unchanged":True,
 "main_thrusters_unchanged":True,
 "reference_metrics":compare,
 "automated_owner_approval":False,
 "production_asset_replaced":False,
}
(OUT/"FORGE_V20_SHAPE_FIT_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
print("NFR_V20_REAL_SHAPE_FIT_OK",len(changed),OUTPUT.stat().st_size,flush=True)
