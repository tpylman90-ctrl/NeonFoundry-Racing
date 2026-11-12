#!/usr/bin/env python3
"""FORGE V19: controlled longitudinal surfacing of REAL V17 geometry.

Experimental inspection pass only. This does not claim AI 3D reconstruction,
Class-A certification, reference approval, or production/game integration.
Keeps all existing modules and substitutes three coarse rear shells with
C2 cubic-interpolated station lofts. Produces a new GLB, a mesh audit and
fixed-camera silhouette differences for a meaningful A/B test.

Run: python tools/build_forge_v19_surfaces.py
"""
from __future__ import annotations
import copy
import json
from pathlib import Path

import numpy as np
import trimesh
from scipy.interpolate import CubicSpline
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "art/hero_01/experiments/V17/FORGE_V17_ConnectedPanels.glb"
DEST = ROOT / "build/forge_v19_surfaces"
DEST.mkdir(parents=True, exist_ok=True)
OUTPUT = DEST / "FORGE_V19_CurvatureStudy.glb"

TARGETS = (
    "V16_FabricatedDorsalCowlHollowUSection",
    "V16_PORT_IntegratedRearCowlHaunch",
    "V16_STBD_IntegratedRearCowlHaunch",
)
PROTECTED = (
    "V15_320_PORT_IntegratedSweptRearSideWing",
    "V15_320_STBD_IntegratedSweptRearSideWing",
)
scene = trimesh.load(SOURCE, force="scene", process=False)
original = trimesh.load(SOURCE, force="scene", process=False)
assert len(scene.geometry) == 330, "Unexpected V17 source; review geometry before running"
assert set(TARGETS).issubset(scene.geometry)
assert set(PROTECTED).issubset(scene.geometry)
# All existing propulsion parts are protected by the full unmodified-mesh
# regression below; do not assume any particular booster naming convention.
# V17's canonical geometry keys are the authoritative inventory.
assert len(scene.geometry) >= 330

before = {key: {"vertices": int(len(scene.geometry[key].vertices)),
                "faces": int(len(scene.geometry[key].faces)),
                "watertight": bool(scene.geometry[key].is_watertight),
                "bounds": np.round(scene.geometry[key].bounds, 4).tolist()}
          for key in TARGETS}
protected_before = {
    key: (scene.geometry[key].vertices.copy(), scene.geometry[key].faces.copy())
    for key in PROTECTED
}

def resample_station_data(rows, steps=31):
    """C2 interpolation of engineered cross-section controls, not AI dimensions."""
    raw = np.asarray(rows, dtype=float)
    assert raw.shape[1] in (5, 6)
    order = np.argsort(raw[:, 0])
    raw = raw[order]
    assert np.all(np.diff(raw[:, 0]) > 0)
    z = np.linspace(raw[0, 0], raw[-1, 0], steps)
    fields = [CubicSpline(raw[:, 0], raw[:, k], bc_type="natural")(z)
              for k in range(1, raw.shape[1])]
    return np.column_stack([z, *fields])

def roof_ring(z, half, top, bottom, inner, inner_top):
    assert 0.12 < inner < half and bottom + .05 < inner_top < top - .05
    # Twelve distinct external + four inner rail positions, preserving the
    # actual hollow U channel, not closing it into a plain solid box.
    return [
        (-half*.65, top, z), (half*.65, top, z),
        (half*.94, top-.043, z), (half, top-.16, z),
        (half, bottom+.11, z), (half*.85, bottom, z),
        (inner, bottom, z), (inner, inner_top-.05, z),
        (inner*.70, inner_top, z), (-inner*.70, inner_top, z),
        (-inner, inner_top-.05, z), (-inner, bottom, z),
        (-half*.85, bottom, z), (-half, bottom+.11, z),
        (-half, top-.16, z), (-half*.94, top-.043, z)
    ]

def haunch_ring(z, center, half_width, top, bottom, sign):
    assert center > half_width > 0.08 and top > bottom + .15
    x0, x1 = center-half_width, center+half_width
    t = (x1-x0)*.19
    v = (top-bottom)*.18
    # A formed closed 8-face shoulder: real mass, individual port/starboard.
    ring = [
        (x0+t, top, z), (x1-t, top, z),
        (x1, top-v, z), (x1, bottom+v, z),
        (x1-t, bottom, z), (x0+t, bottom, z),
        (x0, bottom+v, z), (x0, top-v, z)
    ]
    if sign < 0:
        ring = [(-x, y, z) for x, y, z in ring[::-1]]
    return ring

def make_loft(rings, key):
    p = np.asarray(rings, dtype=float)
    assert p.ndim == 3 and len(p) >= 20 and p.shape[1] >= 8
    n = p.shape[1]
    faces = []
    for i in range(len(p)-1):
        for j in range(n):
            a, b, c, d = i*n+j, i*n+(j+1)%n, (i+1)*n+(j+1)%n, (i+1)*n+j
            faces.extend(((a,b,c),(a,c,d)))
    for j in range(1, n-1):
        faces.append((0,j+1,j))
        last = (len(p)-1)*n
        faces.append((last,last+j,last+j+1))
    out = trimesh.Trimesh(vertices=p.reshape(-1,3),
                          faces=np.asarray(faces, dtype=np.int64), process=False)
    out.fix_normals()
    assert out.is_watertight and np.isfinite(out.vertices).all(), key
    if out.volume < 0:
        out.invert()
    assert out.volume > 0.001, key
    material = getattr(scene.geometry[key].visual, "material", None)
    if material is not None:
        out.visual = trimesh.visual.TextureVisuals(material=copy.deepcopy(material))
    else:
        out.visual.vertex_colors = [150,142,130,255]
    return out

# V16's 7 sharp longitudinal rings become 31 continuous curvature stations.
# A flatter roof runs aft into the smaller inboard boosters, rather than
# forming an abrupt hump and vertical side wall. User artwork provides the
# intended shape; these measured controls are still a trial, not a CAD fit.
roof_controls = [
    (-1.79,.47,1.735,1.33,.31,1.61),
    (-2.03,.56,1.805,1.32,.355,1.655),
    (-2.34,.675,1.845,1.315,.405,1.702),
    (-2.72,.755,1.87,1.33,.465,1.733),
    (-3.13,.77,1.865,1.34,.483,1.72),
    (-3.52,.73,1.847,1.36,.46,1.70),
    (-3.84,.66,1.83,1.38,.425,1.675),
]
roof_stations = resample_station_data(roof_controls)
for row in roof_stations:
    assert 0.30 < row[1] < .82 and 1.70 < row[2] < 1.92
scene.geometry[TARGETS[0]] = make_loft(
    [roof_ring(*row) for row in roof_stations], TARGETS[0])

shoulder_controls = [
    (-1.72,1.00,.16,1.72,1.23),
    (-2.05,1.08,.20,1.77,1.20),
    (-2.39,1.155,.245,1.75,1.16),
    (-2.83,1.27,.30,1.715,1.14),
    (-3.28,1.32,.32,1.67,1.13),
    (-3.72,1.29,.26,1.59,1.15),
]
shoulder_stations = resample_station_data(shoulder_controls)
for sign, tag in ((-1, "PORT"), (1, "STBD")):
    key = f"V16_{tag}_IntegratedRearCowlHaunch"
    scene.geometry[key] = make_loft(
        [haunch_ring(*row, sign) for row in shoulder_stations], key)

assert len(scene.geometry) == len(original.geometry)
assert set(scene.geometry) == set(original.geometry), "A mechanical module was removed"
assert any(scene.geometry[k].vertices.shape != original.geometry[k].vertices.shape for k in TARGETS)
for key, (vert, faces) in protected_before.items():
    assert np.array_equal(scene.geometry[key].vertices, vert), key + " changed"
    assert np.array_equal(scene.geometry[key].faces, faces), key + " changed"
for name in set(scene.geometry) - set(TARGETS):
    assert np.array_equal(scene.geometry[name].faces, original.geometry[name].faces), name
    assert np.array_equal(scene.geometry[name].vertices, original.geometry[name].vertices), name

baseline_bounds = original.bounds
new_bounds = scene.bounds
assert np.all(np.abs(baseline_bounds-new_bounds) < .15), (baseline_bounds,new_bounds)
assert scene.geometry[TARGETS[1]].bounds[0,0] < 0
assert scene.geometry[TARGETS[2]].bounds[1,0] > 0

OUTPUT.write_bytes(trimesh.exchange.gltf.export_glb(scene))
reopened = trimesh.load(OUTPUT, force="scene", process=False)
assert len(reopened.geometry) == len(scene.geometry)
assert set(reopened.geometry) == set(scene.geometry)
for name in TARGETS:
    assert reopened.geometry[name].is_watertight, name

# Camera-registered A/B orthographic silhouette diagnostic. Same projection
# for both versions; NO per-candidate camera fitting. Not reference IoU yet.
def silhouette(asset, view, width=1040, height=700):
    import cv2
    mask = np.zeros((height,width), dtype=np.uint8)
    # x lateral, y vertical, z forward. Match V16 asset convention.
    for node in asset.graph.nodes_geometry:
        transform, geom = asset.graph.get(node)
        mesh = asset.geometry[geom]
        if len(mesh.faces) == 0:
            continue
        xyz = mesh.vertices @ transform[:3,:3].T + transform[:3,3]
        x, y, z = xyz.T
        if view == "side":
            coords = np.column_stack(((3.95-z)*113+42,(2.20-y)*250+45))
        elif view == "top":
            coords = np.column_stack(((x+2.65)*156+65,(3.95-z)*74+36))
        elif view == "rear":
            coords = np.column_stack(((x+2.65)*156+65,(2.20-y)*250+45))
        else:
            raise ValueError(view)
        rounded = np.rint(coords).astype(np.int32)
        for indices in mesh.faces:
            cv2.fillConvexPoly(mask, rounded[indices], 255)
    return mask > 127

silhouettes = {}
for view in ("side","top","rear"):
    a = silhouette(original, view)
    b = silhouette(reopened, view)
    im = np.zeros((*a.shape, 3), dtype=np.uint8)
    im[a & b] = (191,194,197)
    im[~a & b] = (77,201,233)   # geometry gained
    im[a & ~b] = (246,94,89)    # geometry lost
    result = Image.fromarray(im, "RGB")
    draw = ImageDraw.Draw(result)
    draw.rectangle((10,10,620,65), fill=(30,34,41))
    draw.text((19,18), "FORGE V17 baseline vs V19 REAL GLB geometry", fill="white")
    draw.text((19,40), "gray=both   cyan=new outline   red=removed outline", fill=(205,215,220))
    result.save(DEST / f"FORGE_V19_AB_{view}.png")
    silhouettes[view] = {
        "baseline_foreground_px": int(a.sum()),
        "candidate_foreground_px": int(b.sum()),
        "added_pixels": int((~a & b).sum()),
        "removed_pixels": int((a & ~b).sum()),
        "intersection_over_union": round(float((a & b).sum()/max((a | b).sum(),1)),6),
    }

after = {key: {"vertices": int(len(scene.geometry[key].vertices)),
                "faces": int(len(scene.geometry[key].faces)),
                "watertight": bool(scene.geometry[key].is_watertight),
                "bounds": np.round(scene.geometry[key].bounds, 4).tolist()}
         for key in TARGETS}
report = {
    "experiment": "FORGE V19 / C2-interpolated rear roof and shoulder shapes",
    "status": "Inspection-only, requires owner approval",
    "input": str(SOURCE.relative_to(ROOT)),
    "output": str(OUTPUT.relative_to(ROOT)),
    "source_geometry_count": len(original.geometry),
    "result_geometry_count": len(reopened.geometry),
    "changed_components": list(TARGETS),
    "original_panels": before,
    "reworked_panels": after,
    "source_total_triangles": int(sum(len(g.faces) for g in original.geometry.values())),
    "result_total_triangles": int(sum(len(g.faces) for g in scene.geometry.values())),
    "protected_rear_wings": list(PROTECTED),
    "material_strategy": "Keep original GLB materials; only three panel meshes rebuilt",
    "curvature": "Natural cubic spline longitudinal station interpolation; not globally curvature-continuous Class A surfaces",
    "silhouette_comparison": silhouettes,
    "reference_comparison": "Not scored: original artwork has no owner-verified exact projection calibration and segmentation for this GLB",
    "AI_reconstruction_performed": False,
    "promoted_to_game": False,
}
(DEST / "FORGE_V19_REPORT.json").write_text(json.dumps(report, indent=2)+"\n")
print("NFR_V19_REAL_GLB_SURFACE_TRIAL_PASS", OUTPUT, OUTPUT.stat().st_size, flush=True)
