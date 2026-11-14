#!/usr/bin/env python3
"""Stage audited CC0 ambientCG PBR maps for the 3D garage.

Only known asset IDs from ambientCG (CC0 1.0) are downloaded.
Files are generated into game/assets/garage/pbr at build time and packaged
by Godot; no application runtime network call or paid dependency.

Run even when offline: missing downloads are reported as optional and the
scene continues using its deterministic authored fallbacks.
"""
from __future__ import annotations
import io
import json
import os
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen
from zipfile import ZipFile, BadZipFile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "game/assets/garage/pbr"
DEST.mkdir(parents=True, exist_ok=True)
ASSETS = {
    "steel": "Metal010",
    "deck": "MetalPlates001",
    "clean": "Metal050A",
    "paint": "PaintedMetal010",
}
MAPS = {
    "color": ("_Color.", "_Albedo."),
    "normal": ("_NormalGL.", "_Normal_OpenGL.", "_Normal."),
    "roughness": ("_Roughness.",),
    "metallic": ("_Metalness.", "_Metallic."),
    "ao": ("_AmbientOcclusion.", "_AO."),
}
LICENSE_URL = "https://docs.ambientcg.com/license/"
MAX_ZIP_BYTES = 15 * 1024 * 1024


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "NeonFoundryRacing-CC0-asset-build/1.0"})
    with urlopen(request, timeout=32) as response:
        data = response.read(MAX_ZIP_BYTES + 1)
        if len(data) > MAX_ZIP_BYTES:
            raise ValueError("Unexpectedly large ambientCG zip")
        return data


def stage(prefix: str, asset_id: str) -> dict:
    color_path = DEST / f"{prefix}_color.jpg"
    if color_path.is_file() and color_path.stat().st_size > 2000:
        return {"id": asset_id, "state": "cache", "maps": sorted(p.name for p in DEST.glob(prefix + "_*.jpg"))}
    url = f"https://ambientcg.com/get?file={asset_id}_1K-JPG.zip"
    raw = fetch(url)
    if not raw.startswith(b"PK"):
        raise ValueError(f"Not a ZIP: {url}")
    selected: dict[str, bytes] = {}
    with ZipFile(io.BytesIO(raw)) as bundle:
        for entry in bundle.infolist():
            name = Path(entry.filename).name
            if not name.lower().endswith(".jpg") or "__MACOSX" in entry.filename:
                continue
            if entry.file_size > 4 * 1024 * 1024:
                continue
            for key, patterns in MAPS.items():
                if key not in selected and any(pattern.lower() in name.lower() for pattern in patterns):
                    payload = bundle.read(entry)
                    if payload.startswith(b"\xff\xd8") and len(payload) > 2000:
                        selected[key] = payload
                    break
    if "color" not in selected or "normal" not in selected or "roughness" not in selected:
        raise ValueError(f"Incomplete PBR bundle for {asset_id}: {list(selected)}")
    for key, data in selected.items():
        (DEST / f"{prefix}_{key}.jpg").write_bytes(data)
    return {"id": asset_id, "state": "downloaded", "maps": sorted(selected)}


def main() -> None:
    catalog = {"source": "ambientCG", "license": "CC0-1.0", "license_url": LICENSE_URL, "assets": {}}
    for prefix, asset_id in ASSETS.items():
        try:
            catalog["assets"][prefix] = stage(prefix, asset_id)
            print(f"NEON_FOUNDRY_CC0_MATERIAL_OK {prefix}: {asset_id}")
        except (OSError, TimeoutError, BadZipFile, ValueError, Exception) as exc:
            catalog["assets"][prefix] = {"id": asset_id, "state": "fallback", "reason": str(exc)[:220]}
            print(f"NEON_FOUNDRY_CC0_MATERIAL_FALLBACK {prefix}: {exc}", file=sys.stderr)
    (DEST / "provenance.json").write_text(json.dumps(catalog, indent=2) + "\n")
    print("NEON_FOUNDRY_CC0_MANIFEST_OK")


if __name__ == "__main__":
    main()
