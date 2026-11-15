#!/usr/bin/env python3
"""Isolated, auditable TripoSR image-to-3D trial for the Forge hero craft.

Outputs are experimental GLB inspection assets, never promoted to the game.
Input artwork: the user's existing checked-in 8-view Forge reference.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "forge_triposr_trial"
REF = ROOT / "art" / "hero_01" / "references" / "forge_8view_original.jpg"
# Calibrated using the existing art AI pipeline (tools/forge_reference_ai.py).
CROP = (773, 505, 1140, 819)

def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    if not REF.is_file():
        raise SystemExit("Missing Forge eight-view artwork: " + str(REF))
    original = Image.open(REF).convert("RGB")
    if original.size != (1536, 857):
        raise SystemExit("Artwork size changed; do not use stale crop coordinates.")
    crop = original.crop(CROP)
    # Input must contain the vehicle, not a pasted square with two backgrounds.
    # TripoSR's official rembg preprocessing will remove the underlying dark grid
    # and then composite the foreground onto uniform neutral gray.
    image_path = OUT / "forge_front_three_quarter_input.png"
    crop.save(image_path)
    meta = {
        "input_file": str(REF.relative_to(ROOT)),
        "input_sha256": hashlib.sha256(REF.read_bytes()).hexdigest(),
        "crop_bbox": list(CROP),
        "crop_type": "front_three_quarter",
        "crop_size_pixels": list(crop.size),
        "preprocessing": "TripoSR default rembg (U2Net), foreground ratio 0.85",
        "background_removal_enabled": True,
        "generator": "VAST-AI-Research/TripoSR",
        "weights": "stabilityai/TripoSR",
        "inference": "CPU, single image, 128 marching-cubes resolution",
        "status": "INPUT_ONLY_NOT_AI_MESH",
        "source_model_modified": False,
        "production_export": False,
    }
    (OUT / "trial_provenance.json").write_text(json.dumps(meta, indent=2)+"\n")
    print("FORGE_TRIPOSR_INPUT_READY", image_path, flush=True)

def audit():
    import trimesh
    import numpy as np
    model = OUT / "0" / "mesh.glb"
    if not model.is_file() or model.stat().st_size < 1024:
        raise SystemExit("AI inference did not create a valid mesh.glb.")
    # With rembg enabled, upstream saves the actual isolated image here.
    processed = OUT / "0" / "input.png"
    if not processed.is_file():
        raise SystemExit("Missing rembg-prepared input image; do not accept an unsegmented square.")
    ready = np.asarray(Image.open(processed).convert("RGB"), dtype=np.int16)
    border = np.concatenate((
        ready[:8].reshape(-1, 3), ready[-8:].reshape(-1, 3),
        ready[:, :8].reshape(-1, 3), ready[:, -8:].reshape(-1, 3)
    ))
    neutral_border = float(np.mean(np.max(np.abs(border - 128), axis=1) <= 7))
    occupied = float(np.mean(np.max(np.abs(ready - 128), axis=2) > 20))
    if neutral_border < 0.85 or not (0.08 <= occupied <= 0.78):
        raise SystemExit(
            f"FOREGROUND_PREPROCESS_GATE_FAILED neutral_border={neutral_border:.3f} "
            f"occupied={occupied:.3f}; inspect output/0/input.png."
        )
    scene = trimesh.load(model, force="scene", process=False)
    meshes = [g for g in scene.geometry.values() if isinstance(g, trimesh.Trimesh)]
    if not meshes or not sum(len(m.faces) for m in meshes):
        raise SystemExit("AI output has zero triangle faces.")
    # Detect the exact previous failure: broad rectangular image plane with
    # sculptural noise stuck to its front. Valid GLB != good reconstruction.
    primary = max(meshes, key=lambda m: m.area)
    ext = np.asarray(primary.extents, dtype=float)
    normal_area = float(primary.area_faces[
        np.abs(primary.face_normals[:, 2]) >= 0.98
    ].sum() / max(primary.area, 1e-9))
    square_ratio = float(min(ext[0], ext[1]) / max(ext[0], ext[1], 1e-9))
    thickness_ratio = float(ext[2] / max(min(ext[0], ext[1]), 1e-9))
    board_like = square_ratio >= 0.75 and thickness_ratio <= 0.55 and normal_area >= 0.28
    if board_like:
        raise SystemExit(
            f"SLAB_RECONSTRUCTION_REJECTED square_ratio={square_ratio:.3f} "
            f"thickness_ratio={thickness_ratio:.3f} plane_area={normal_area:.3f}; "
            "GLB is geometry-valid but visually wrong."
        )
    result = OUT / "FORGE_AI_TRIPOSR_INSPECTION.glb"
    result.write_bytes(scene.export(file_type="glb"))
    readback = trimesh.load(result, force="scene", process=False)
    geometries = list(readback.geometry.values())
    report = json.loads((OUT / "trial_provenance.json").read_text())
    report.update({
        "status": "AI_MESH_GENERATED_AND_GLB_RELOADED",
        "output": result.name,
        "output_sha256": hashlib.sha256(result.read_bytes()).hexdigest(),
        "output_bytes": result.stat().st_size,
        "mesh_count": len(geometries),
        "vertices": sum(len(m.vertices) for m in geometries),
        "triangles": sum(len(m.faces) for m in geometries),
        "preprocess_neutral_border_fraction": round(neutral_border, 4),
        "preprocess_foreground_occupancy": round(occupied, 4),
        "slab_detector": {
            "square_ratio": round(square_ratio, 4),
            "thickness_ratio": round(thickness_ratio, 4),
            "axis_aligned_plane_area_fraction": round(normal_area, 4),
            "rejected": False
        },
        "visual_quality": "NOT VERIFIED; requires owner inspection of actual geometry",
        "bounds": readback.bounds.tolist(),
        "limitations": [
            "single-view geometry is inferred and cannot guarantee rear or underside fidelity",
            "not a replacement for existing engineered multipart Forge assembly",
            "unapproved inspection-only geometry; no Godot integration",
            "AI output must pass visual multi-view review and license provenance audit"
        ]
    })
    (OUT / "TRIPOSR_FORGE_REPORT.json").write_text(json.dumps(report, indent=2)+"\n")
    print("FORGE_TRIPOSR_REAL_GLB_VERIFIED", json.dumps({
        "triangles": report["triangles"], "meshes": report["mesh_count"],
        "bytes": report["output_bytes"]
    }), flush=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["prepare", "audit"])
    args = ap.parse_args()
    (prepare if args.mode == "prepare" else audit)()
