#!/usr/bin/env python3
"""Stage selected Kenney Factory Kit CC0 props, in their original geometry.

Kenney Factory Kit (3.0) is CC0 (see original Kenney LICENSE.txt).
This stages only named models from a mirror containing their original OBJ+MTL
source and one common colormap; no login, paid tool or runtime network needed.
Optional: failures are logged and procedurally authored props remain usable.
"""
from __future__ import annotations
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "game/assets/garage/kenney_factory"
SOURCE = "https://raw.githubusercontent.com/Mcamento8/omnimod-3d-library/main/models/kenney/factory-kit"
MODELS = (
    "machine-window",
    "machine-fortified",
    "scanner-high",
    "crane-lift",
    "piston-round",
    "cog-e",
    "screen-hanging-wide",
    "conveyor-bars-stripe-sides",
)
DEST.mkdir(parents=True, exist_ok=True)


def download(relative: str, max_bytes: int = 2_000_000) -> bytes:
    url = SOURCE + "/" + relative
    with urlopen(Request(url, headers={"User-Agent": "NeonFoundryRacing-CC0-stage/1.0"}),
                 timeout=15) as response:
        data = response.read(max_bytes + 1)
    if not data or len(data) > max_bytes:
        raise ValueError("Wrong asset size for " + relative)
    return data


def stage(relative: str) -> bool:
    target = DEST / relative
    if target.exists() and target.stat().st_size > 30:
        return True
    data = download(relative)
    if relative.endswith(".obj") and b"# Created by Kenney" not in data[:220]:
        raise ValueError("OBJ lacks expected original Kenney attribution header")
    if relative.endswith(".mtl") and b"newmtl" not in data:
        raise ValueError("Invalid material file")
    if relative.endswith("LICENSE.txt") and b"CC0" not in data:
        raise ValueError("Unexpected license")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return True


def main() -> None:
    manifest = {"license": "CC0-1.0", "author": "Kenney",
        "pack": "Factory Kit 3.0", "origin": "https://kenney.nl/assets/factory-kit",
        "mirror": SOURCE, "models": [], "failed": []}
    try:
        stage("LICENSE.txt")
        stage("Textures/colormap.png")
    except Exception as exc:
        print(f"NEON_FOUNDRY_KENNEY_FALLBACK shared: {exc}")
    for model in MODELS:
        try:
            stage(model + ".obj")
            stage(model + ".mtl")
            manifest["models"].append(model)
            print("NEON_FOUNDRY_KENNEY_CC0_OK " + model)
        except Exception as exc:
            manifest["failed"].append({"model": model, "error": str(exc)[:150]})
            print(f"NEON_FOUNDRY_KENNEY_FALLBACK {model}: {exc}")
    (DEST/"provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("NEON_FOUNDRY_KENNEY_MANIFEST_OK")


if __name__ == "__main__":
    main()
