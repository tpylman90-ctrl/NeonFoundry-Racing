#!/usr/bin/env python3
"""Static validation for the independently exported Stage 02A deck."""
from __future__ import annotations
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / "game/assets/garage/shell/observation_deck_stage02.glb"

def validate(path: Path=GLB) -> dict:
    raw=path.read_bytes()
    assert len(raw)>8000, "Expected an authored structural GLB"
    magic,version,length=struct.unpack_from("<4sII",raw,0)
    assert (magic,version,length)==(b"glTF",2,len(raw)), "Bad glTF 2.0 header"
    chunk_len,chunk_type=struct.unpack_from("<II",raw,12)
    assert chunk_type==0x4e4f534a
    gltf=json.loads(raw[20:20+chunk_len])
    meshes=gltf.get("meshes",[])
    assert len(meshes)==4, f"expected four batched material meshes, got {len(meshes)}"
    names={m.get("name","") for m in meshes}
    for expected in ["OBS_DECK_Structure","OBS_DECK_WalkSurface",
                     "OBS_DECK_TrimRails","OBS_DECK_SafetyPaint"]:
        assert expected in names, (expected,names)
    assert len(gltf.get("materials",[]))==4
    vertices=0
    for mesh in meshes:
        for primitive in mesh.get("primitives",[]):
            accessor=gltf["accessors"][primitive["attributes"]["POSITION"]]
            vertices+=accessor["count"]
            assert "min" in accessor and "max" in accessor
            assert accessor["count"]>=36
    assert vertices<300000, f"deck unexpectedly dense: {vertices} vertices"
    return {"meshes":len(meshes),"materials":len(gltf["materials"]),"vertices":vertices,
            "bytes":len(raw)}
if __name__=="__main__":
    print("NEON_FOUNDRY_DECK_GLB_VALID",json.dumps(validate()))
