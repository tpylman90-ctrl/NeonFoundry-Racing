#!/usr/bin/env python3
"""Vulkan, export and credential-hygiene checks for the foundation."""
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1]
project = (root / "game/project.godot").read_text()
preset = (root / "game/export_presets.cfg").read_text()
ignore = (root / ".gitignore").read_text()
for setting in [
    'run/main_scene="res://scenes/foundation.tscn"',
    'renderer/rendering_method="mobile"',
    'renderer/rendering_method.mobile="mobile"',
    'rendering_device/driver="vulkan"',
    'rendering_device/driver.android="vulkan"',
    'rendering_device/fallback_to_opengl3=false',
]:
    assert project.splitlines().count(setting) == 1, setting
assert "gl_compatibility" not in project
for setting in ['platform="Android"', 'package/unique_name="com.tpylman.neonfoundryracing.debug"',
                'architectures/arm64-v8a=true', 'package/signed=true']:
    assert setting in preset, setting
for pattern in ["*.keystore", "*.jks", "*.pem", "*.apk", "build/"]:
    assert pattern in ignore, pattern
for name in ["README.md", "SECURITY.md", "game/scripts/foundation.gd",
             "game/scenes/foundation.tscn", "docs/ROADMAP.md",
             "docs/PROJECT_BRIEF.md", "docs/ARCHITECTURE.md", "docs/BUILD_AND_SIGNING.md"]:
    assert (root / name).is_file(), name
try:
    tracked = subprocess.check_output(["git", "ls-files"], cwd=root, text=True).splitlines()
except (OSError, subprocess.CalledProcessError):
    tracked = []
for path in tracked:
    assert not re.search(r"(?i)\.(keystore|jks|p12|pfx|key|pem|der|apk|aab)$", path), path
print("NEON_FOUNDRY_FOUNDATION_OK")
