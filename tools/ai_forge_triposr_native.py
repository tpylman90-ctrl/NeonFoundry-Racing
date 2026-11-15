#!/usr/bin/env python3
"""Clay-only Forge input and raw TripoSR geometry audit (experimental; not production)."""
from __future__ import annotations
import argparse
import hashlib
import json
import io
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "art/hero_01/references/forge_shadowfree_512_q88.webp.b64"
OUT = ROOT / "build/forge_triposr_native"

def prepare():
    from PIL import Image
    import numpy as np
    if not SOURCE.is_file():
        raise SystemExit("REFERENCE_NOT_COMMITTED: missing shadowfree image data.")
    raw = base64.b64decode(SOURCE.read_text().strip(),validate=True)
    expected = "9265200bd3c8659105440b68870d66e722c7ec3c68c7983906630673b4c6c8af"
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected:
        raise SystemExit("SHADOWFREE_SOURCE_HASH_MISMATCH: " + digest)
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    if im.size != (512, 512):
        raise SystemExit(f"INPUT_REJECTED expected 512x512 got {im.size}")
    pix = np.asarray(im,dtype=np.int16)
    band = np.concatenate([pix[:10].reshape(-1,3),pix[-10:].reshape(-1,3),
                           pix[:,:10].reshape(-1,3),pix[:,-10:].reshape(-1,3)])
    neutral = float(np.mean(np.max(np.abs(band-128),axis=1)<=7))
    foreground = np.max(np.abs(pix-128),axis=2)>30
    occupancy=float(np.mean(foreground))
    if neutral<0.98 or not (0.07<occupancy<0.55):
        raise SystemExit(f"INPUT_REJECTED neutral_border={neutral:.3f} foreground_area={occupancy:.3f}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"0").mkdir(exist_ok=True)
    im.save(OUT/"forge_input.png")
    report={"source":str(SOURCE.relative_to(ROOT)),"source_sha256":hashlib.sha256(raw).hexdigest(),
            "source_type":"shadow-free generated Forge image, 512x512 WebP quality 88",
            "precut_from_owner_clay_render":False,"single_large_vehicle_only":True,
            "background":"neutral mid-gray RGB 128","background_removal":False,"extraction":"official native torchmcubes (NOT scikit-image)",
            "neutral_border_fraction":round(neutral,4),"foreground_fraction":round(occupancy,4),
            "model":"stabilityai/TripoSR","method":"single_view_cpu_original_native_torchmcubes",
            "status":"INPUT_READY_NOT_A_GENERATED_MODEL","production":False}
    (OUT/"INPUT_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
    print("FORGE_CLEAN_INPUT_VALID",report,flush=True)

def audit():
    import numpy as np
    import trimesh
    raw=OUT/"0/mesh.glb"
    if not raw.is_file():
        raise SystemExit("AI_GENERATION_FAILED_MISSING_GLB")
    scene=trimesh.load(raw,force="scene",process=False)
    meshes=[m for m in scene.geometry.values() if isinstance(m,trimesh.Trimesh)]
    if not meshes:
        raise SystemExit("AI_GENERATED_EMPTY_GEOMETRY")
    triangles=sum(len(m.faces) for m in meshes)
    if triangles<500:
        raise SystemExit(f"AI_GENERATED_TOO_FEW_FACES={triangles}")
    geom=max(meshes,key=lambda m:m.area)
    ext=np.asarray(geom.extents,dtype=float)
    planar=float(geom.area_faces[np.max(np.abs(geom.face_normals),axis=1)>.985].sum()/max(geom.area,1e-9))
    dims=sorted(ext)
    # Prevent the previous nearly flat, square image-card reconstruction.
    if dims[0]/max(dims[2],1e-8)<.18 and planar>.40:
        raise SystemExit(f"REJECT_FLAT_IMAGE_CARD dimensions={ext.tolist()} planar={planar:.3f}")
    exported=OUT/"FORGE_NATIVE_TRIPOSR_V5_INSPECTION.glb"
    exported.write_bytes(scene.export(file_type="glb"))
    check=trimesh.load(exported,force="scene",process=False)
    if sum(len(m.faces) for m in check.geometry.values())!=triangles:
        raise SystemExit("GLB_ROUNDTRIP_FACE_MISMATCH")
    report=json.loads((OUT/"INPUT_REPORT.json").read_text())
    report.update({"status":"RAW_GLB_VALID_VISUAL_FIDELITY_UNVERIFIED",
                   "output_sha256":hashlib.sha256(exported.read_bytes()).hexdigest(),
                   "model_glb":exported.name,
                   "mesh_count":len(meshes),"triangles":int(triangles),
                   "bounds_m_unknown":check.bounds.tolist(),
                   "extents_normalized":ext.tolist(),
                   "planar_face_area_fraction":round(planar,5),
                   "fit_to_reference_not_yet_measured":True,
                   "user_visual_approval":False})
    (OUT/"RESULT_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
    print("FORGE_AI_RAW_INSPECTION_READY",json.dumps(report),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("prepare","audit"))
    mode=p.parse_args().mode
    {"prepare":prepare,"audit":audit}[mode]()
