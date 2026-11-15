# Toolchain Upgrade Trial (non-production branch)

Date: November 14, 2026

Test Godot **4.7.2 stable** and Blender **5.2.4 LTS** before changing production on main.

## Verified upstream
- Godot official archive: https://godotengine.org/download/archive/ (4.7.2 stable; 4.8 beta)
- Godot migration 4.5 to 4.6: https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html
- Godot migration 4.6 to 4.7: https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html
- Blender official 5.2.4 LTS: https://www.blender.org/download/lts/
- Blender 5.3 is newer, but 5.2 LTS provides long-term support and reproducible CI.

## Promotion gates
1. Leave production main and the verified signed APK intact until checks pass.
2. Import, startup, and garage/menu smoke test under Godot 4.7.2.
3. Render the original Blender menu scene under Blender 5.2.4, validate PNG and .blend outputs.
4. Capture all UI screens with Godot Mobile/Vulkan software rendering.
5. Export and verify Android APK with matching official 4.7.2 templates, without changing package IDs, signing keys or user save data.
6. Compare device FPS/garage materials: version upgrades do not inherently fix GPU cost.

These changes are isolated to an upgrade branch for evaluation.
