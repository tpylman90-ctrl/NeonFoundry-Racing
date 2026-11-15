#!/usr/bin/env python3
"""Validate the separately exported Stage 02C garage partition GLB."""
from __future__ import annotations
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / "game/assets/garage/shell/interior_partitions_stage02c.glb"


def validate(path: Path = GLB) -> dict:
    raw = path.read_bytes()
    assert len(raw) > 20_000, "Expected authored partition geometry"
    magic, version, total = struct.unpack_from("<4sII", raw, 0)
    assert (magic, version, total) == (b"glTF", 2, len(raw)), "Bad glTF 2.0 header"
    chunk_len, chunk_type = struct.unpack_from("<II", raw, 12)
    assert chunk_type == 0x4E4F534A
    gltf = json.loads(raw[20:20 + chunk_len])
    meshes = gltf.get("meshes", [])
    assert len(meshes) == 4, f"expected 4 material batches, got {len(meshes)}"
    names = {node.get("name", "") for node in gltf.get("nodes", []) if "mesh" in node}
    for expected in ("INT_WALL_Structure", "INT_WALL_Cladding",
                     "INT_WALL_Portals", "INT_WALL_Safety"):
        assert expected in names, (expected, names)
    assert len(gltf.get("materials", [])) == 4
    vertices = sum(
        gltf["accessors"][primitive["attributes"]["POSITION"]]["count"]
        for mesh in meshes for primitive in mesh.get("primitives", [])
    )
    assert 1000 < vertices < 500_000, f"unexpected partition vertex count: {vertices}"
    return {"meshes": len(meshes), "materials": len(gltf["materials"]),
            "vertices": vertices, "bytes": len(raw)}


if __name__ == "__main__":
    print("NEON_FOUNDRY_PARTITIONS_GLB_VALID", json.dumps(validate()))
