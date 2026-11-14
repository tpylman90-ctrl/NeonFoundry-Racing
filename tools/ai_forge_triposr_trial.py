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
    crop.thumbnail((420, 420), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (512, 512), (128, 128, 128))
    canvas.paste(crop, ((512 - crop.width)//2, (512 - crop.height)//2))
    image_path = OUT / "forge_front_three_quarter_input.png"
    canvas.save(image_path)
    meta = {
        "input_file": str(REF.relative_to(ROOT)),
        "input_sha256": hashlib.sha256(REF.read_bytes()).hexdigest(),
        "crop_bbox": list(CROP),
        "crop_type": "front_three_quarter",
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
    model = OUT / "0" / "mesh.glb"
    if not model.is_file() or model.stat().st_size < 1024:
        raise SystemExit("AI inference did not create a valid mesh.glb.")
    scene = trimesh.load(model, force="scene", process=False)
    meshes = [g for g in scene.geometry.values() if isinstance(g, trimesh.Trimesh)]
    if not meshes or not sum(len(m.faces) for m in meshes):
        raise SystemExit("AI output has zero triangle faces.")
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
