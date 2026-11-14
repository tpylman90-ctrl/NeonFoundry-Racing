#!/usr/bin/env python3
"""Stage the repo's original experimental Forge GLB for Godot garage preview.

The approved vehicle remains gated; this is explicitly an experimental showroom
asset. Copy to game/assets only at build/import time to avoid duplicate binaries.
"""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
source = root / "art/hero_01/experiments/V18_Stage04/FORGE_V18_04_Cockpit_Assembly.glb"
target = root / "game/assets/garage/forge_preview.glb"
assert source.is_file() and source.stat().st_size > 200_000, source
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(source, target)
assert target.stat().st_size == source.stat().st_size
print("NEON_FOUNDRY_GARAGE_EXPERIMENTAL_GLB_STAGED")
