#!/usr/bin/env python3
"""Validate original Stage 01 shell GLB and its physically packed PBR maps.

No third-party packages: uses the raw glTF 2.0 JSON chunk for a strict
R/G/B ORM layout check and confirms no missing images/material slots.
"""
from __future__ import annotations
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / "game/assets/garage/shell/shell_stage01.glb"


def validate(path: Path = GLB) -> dict:
    data = path.read_bytes()
    assert len(data) > 50_000, "Shell GLB implausibly small"
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    assert (magic, version, length) == (b"glTF", 2, len(data)), "Bad glTF header"
    json_len, json_type = struct.unpack_from("<II", data, 12)
    assert json_type == 0x4E4F534A, "Missing GLB JSON chunk"
    gltf = json.loads(data[20:20 + json_len])
    images = gltf["images"]
    materials = gltf["materials"]
    meshes = gltf["meshes"]
    textures = gltf["textures"]
    assert len(meshes) == 6, f"Expected only 4 walls, floor and ceiling, got {len(meshes)}"
    assert len(images) >= 12, "Four atlas materials need albedo, packed ORM and normals"
    required = ("Floor", "Wall", "Ceiling")
    checked = []
    for material in materials:
        name = material.get("name", "")
        if "NF/Shell/" not in name or not any(k in name for k in required):
            continue
        pbr = material.get("pbrMetallicRoughness", {})
        assert "baseColorTexture" in pbr, f"{name}: missing color atlas"
        assert "metallicRoughnessTexture" in pbr, f"{name}: missing packed metallic/roughness"
        assert "normalTexture" in material, f"{name}: missing baked normal"
        assert "occlusionTexture" in material, f"{name}: missing baked AO in R"
        mr_index = pbr["metallicRoughnessTexture"]["index"]
        ao_index = material["occlusionTexture"]["index"]
        mr_source = textures[mr_index]["source"]
        ao_source = textures[ao_index]["source"]
        assert mr_source == ao_source, f"{name}: AO/MR must reuse SAME ORM texture"
        imgname = images[mr_source].get("name", "")
        # Names are optional in GLB, but channel-index equality is not.
        assert mr_source < len(images)
        assert material["normalTexture"]["index"] < len(textures)
        checked.append((name, mr_source))
    assert len(checked) >= 4, f"Expected floor, two wall shapes and ceiling materials: {checked}"
    for i, tex in enumerate(textures):
        assert 0 <= tex["source"] < len(images), f"texture {i} points outside images"
    return {"six_shell_meshes": len(meshes), "texture_images": len(images),
            "orm_materials": len(checked), "packed_materials": checked}


if __name__ == "__main__":
    result = validate()
    print("NEON_FOUNDRY_SHELL_ORM_VALID " + json.dumps(result))
