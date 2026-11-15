#!/usr/bin/env python3
"""Official TripoSR chair benchmark + CPU marching-cubes extractor parity.

Experimental only. Uses official examples/chair.png from VAST-AI-Research/TripoSR,
the official stabilityai/TripoSR weights, and our isolated CPU extractor.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/triposr_official_benchmark"
OFFICIAL = Path("/tmp/triposr/examples/chair.png")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mesh_stats(path):
    import numpy as np
    import trimesh
    sc = trimesh.load(path, force="scene", process=False)
    meshes = [m for m in sc.geometry.values() if isinstance(m, trimesh.Trimesh)]
    if not meshes or sum(len(m.faces) for m in meshes) < 100:
        raise RuntimeError("BENCHMARK_EMPTY_OR_INVALID_MESH: " + str(path))
    extents = np.asarray(sc.bounds[1] - sc.bounds[0], dtype=float)
    longest = float(extents.max())
    return {
        "name": Path(path).name,
        "sha256": sha256(path),
        "bytes": Path(path).stat().st_size,
        "mesh_count": len(meshes),
        "vertices": int(sum(len(m.vertices) for m in meshes)),
        "triangles": int(sum(len(m.faces) for m in meshes)),
        "watertight": bool(all(m.is_watertight for m in meshes)),
        "nondegenerate_face_fraction": round(float(
            sum((m.area_faces > 1e-12).sum() for m in meshes) /
            max(1, sum(len(m.faces) for m in meshes))), 6),
        "normalized_extents": [round(float(x / longest), 6) for x in extents],
        "bounds": sc.bounds.tolist(),
    }


def shade_preview(scene_file, angle, elevate, size=500):
    import cv2
    import numpy as np
    import trimesh
    sc = trimesh.load(scene_file, force="scene", process=False)
    tri = sc.dump(concatenate=True)
    pts = np.asarray(tri.vertices, dtype=np.float32)
    faces = np.asarray(tri.faces, dtype=np.int32)
    # Repeatable camera, no 3D rendering engine or misleading texture tricks.
    a, b = math.radians(angle), math.radians(elevate)
    cz, sz, cx, sx = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]], dtype=np.float32)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]], dtype=np.float32)
    r = rx @ rz
    p = (pts - (pts.max(0) + pts.min(0)) / 2) @ r.T
    span = max(float(np.ptp(p[:, 0])), float(np.ptp(p[:, 1])), 1e-6)
    s = size * 0.79 / span
    xy = np.stack([p[:, 0] * s + size/2, -p[:, 1] * s + size/2], axis=1).astype(np.int32)
    depth = p[:, 2][faces].mean(axis=1)
    face_normals = np.asarray(tri.face_normals, dtype=np.float32) @ r.T
    light = np.array([0.35, -0.55, 0.76], dtype=np.float32)
    light /= np.linalg.norm(light)
    intensity = (0.58 + 0.42 * np.clip(face_normals @ light, -0.5, 1.0)).clip(0,1)
    bg = np.full((size, size, 3), 224, np.uint8)
    # Painter's algorithm: farthest faces first; individual triangles use normals.
    order = np.argsort(depth)
    for idx in order:
        col = int(48 + 174 * float(intensity[idx]))
        cv2.fillConvexPoly(bg, xy[faces[idx]], (col, col, col), cv2.LINE_AA)
    return bg


def audit():
    from PIL import Image, ImageDraw
    import numpy as np
    OUT.mkdir(parents=True, exist_ok=True)
    official_sha = subprocess.check_output(
        ["git", "-C", "/tmp/triposr", "hash-object", str(OFFICIAL)], text=True
    ).strip()
    if official_sha != "fee2a21d1c9bbdf707631060f110539401265a1d":
        raise RuntimeError("OFFICIAL_EXAMPLE_CHANGED_SHA: " + official_sha)
    meshes = {}
    for res in (128, 256):
        p = OUT / f"chair_{res}/0/mesh.glb"
        if not p.is_file():
            raise RuntimeError("OFFICIAL_CHAIR_MESH_MISSING: " + str(p))
        meshes[str(res)] = mesh_stats(p)
    report = {
        "benchmark": "Official TripoSR examples/chair.png",
        "reference_repo": "https://github.com/VAST-AI-Research/TripoSR",
        "reference_git_blob": official_sha,
        "reference_sha256": sha256(OFFICIAL),
        "upstream_git_head": subprocess.check_output(
            ["git", "-C", "/tmp/triposr", "rev-parse", "HEAD"], text=True
        ).strip(),
        "pretrained_model": "stabilityai/TripoSR",
        "device": "cpu",
        "marching_cubes": "scikit-image 0.22.0 CPU adapter, NOT original native torchmcubes",
        "preprocessing": "official rembg + resize_foreground(ratio=0.85)",
        "inference": "official run.py; same pretrained model, two fresh invocations",
        "chunk_size": 2048,
        "density_threshold": 25.0,
        "resolutions": meshes,
        "quality_note": "This is a structural and visual benchmark, not a ground-truth reconstruction score.",
    }
    (OUT/"OFFICIAL_CHAIR_BENCH_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
    n=480
    preview = Image.new("RGB",(n*3, n*2+70),(240,240,240))
    draw=ImageDraw.Draw(preview)
    input_im=Image.open(OFFICIAL).convert("RGB")
    input_im.thumbnail((n-30,n-45))
    preview.paste(input_im,((n-input_im.width)//2,(n-input_im.height)//2+40))
    draw.text((16, 12), "Official chair source", fill="black")
    for j,res in enumerate((128,256),start=1):
        image=Image.fromarray(shade_preview(OUT/f"chair_{res}/0/mesh.glb",35,26,n))
        preview.paste(image,(j*n,0))
        draw.text((j*n+14,12),f"TripoSR chair: mc={res}",fill="black")
    for j,res in enumerate((128,256)):
        image=Image.fromarray(shade_preview(OUT/f"chair_{res}/0/mesh.glb",126,5,n))
        preview.paste(image,(j*n,(n+70)))
        draw.text((j*n+14,n+40),f"Alternate view: mc={res}",fill="black")
    preview.save(OUT/"OFFICIAL_CHAIR_BENCH_PREVIEW.png")
    print("TRIPOSR_OFFICIAL_BENCHMARK_COMPLETE",json.dumps({
        res: {"triangles":m["triangles"],"watertight":m["watertight"],
              "normalized_extents":m["normalized_extents"]}
        for res,m in meshes.items()}),flush=True)


def parity():
    """Compare our marching-cubes adapter with native torchmcubes, when installed."""
    import numpy as np
    import torch
    from scipy.spatial import cKDTree
    from importlib.machinery import SourceFileLoader
    from importlib.util import spec_from_loader, module_from_spec
    p = ROOT/"tools/triposr_cpu_marching_cubes.py"
    loader=SourceFileLoader("forge_mc",str(p))
    spec=spec_from_loader(loader.name,loader)
    adapter=module_from_spec(spec)
    loader.exec_module(adapter)
    report={"native_available":False,
            "test_field":"asymmetric displaced ellipsoid with unequal radii at 48^3 grid",
            "benchmark_purpose":"detect native-vs-adapter axis swaps and coordinate errors"}
    n=48
    xyz=torch.linspace(-1,1,n)
    i,j,k=torch.meshgrid(xyz,xyz,xyz,indexing="ij")
    field=((i-0.22)/0.51)**2+((j+0.10)/0.32)**2+((k-0.17)/0.66)**2-1.
    fv, ff=adapter.marching_cubes(field,0.)
    report["fallback_verts"]=int(fv.shape[0])
    report["fallback_faces"]=int(ff.shape[0])
    try:
        from torchmcubes import marching_cubes as native
        nv,nf=native(field,0.)
        report["native_available"]=True
        nv=nv.detach().cpu().numpy()
        fv=fv.detach().cpu().numpy()
        report["native_verts"]=int(nv.shape[0])
        report["native_faces"]=int(nf.shape[0])
        combos=[]
        for perm in itertools.permutations([0,1,2]):
            t=fv[:,list(perm)]
            distances=cKDTree(nv).query(t,k=1)[0]
            reverse=cKDTree(t).query(nv,k=1)[0]
            combos.append({"permutation":list(perm),
                           "median_distance_voxels":round(float(np.median(distances)),6),
                           "p95_distance_voxels":round(float(np.percentile(distances,95)),6),
                           "reverse_median_distance_voxels":round(float(np.median(reverse)),6)})
        combos.sort(key=lambda t:t["median_distance_voxels"]+t["reverse_median_distance_voxels"])
        report["best_match"]=combos[0]
        report["all_permutations"]=combos
        # 0.1 voxel accuracy is a conservative check of near-identical surfaces.
        report["same_surface_with_best_axis_order"]=bool(
            combos[0]["p95_distance_voxels"]<0.1)
    except (ImportError, OSError) as exc:
        report["native_error"]=str(exc)[:350]
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"EXTRACTOR_PARITY_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
    print("EXTRACTOR_PARITY_RESULT",json.dumps(report),flush=True)


if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("mode",choices=["audit","parity"])
    {"audit":audit,"parity":parity}[ap.parse_args().mode]()
