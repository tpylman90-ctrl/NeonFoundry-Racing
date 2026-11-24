# Neon Foundry Racing — Unity 6 Android Preview

**Mandatory for production assets:** [Production Standard](../docs/PRODUCTION_STANDARD.md) and [Asset Review Template](../docs/ASSET_REVIEW_TEMPLATE.md). The current R1/R2 garage preview is a layout/performance experiment, not an approved production scene. Produce a model-review package and obtain the required sign-offs before promoting geometry or materials into production.

This Unity project is isolated under `unity/` in the original Neon Foundry Racing repository.
The prior Godot game and Blender library remain unchanged.

- **Editor:** 6000.3.27f2; Universal Render Pipeline 17.3.0.
- **Target:** Android ARM64; Vulkan with OpenGLES3 fallback.
- **Build:** Shared Eclipse Hollow Sky Unity runner with its existing Unity license secrets.
- **Source models:** `Blender/FoundryPreview/generate_assets.py` and `upgrade_geometry.py` author geometry, UV-aware surface masks and material batching on CI.
- **Build method:** `NeonFoundryUnityBuild.BuildAndroid`.
- **Expected APK:** `unity/Builds/Android/NeonFoundry-Unity-Garage.apk`.

This is a **garage/inspection technology slice**, not a complete game or the final approved hero vehicle.
The model is a geometry review placeholder. It uses a Blender lofted fuselage,
sponsons, machined thruster rims, vent slats and canopy, plus an independent
hangar with cell workstations, chargers, robotic arm fixtures, and an observation
deck reached by an unblocked stair run.

R2 garage composition:
- Sealed industrial ceiling with acoustic cassettes, architectural ribs, optical housings, improved camera clearance, and cinematic but restrained URP grading.
- Structured floor service lanes, engineered wall bays, machining details, hydraulic cradle, warning inlays, and mirrored hover-pod fasteners.
- Dedicated battery assembly machines, diagnostic readouts, power converters, energy cassettes, robot tooling, and spare maglev coils with separate aisle circulation.
- Functional observation-deck stair ground proxies (not an unrestricted character controller); continuous railings preserve landing access.
- Five procedural 256px tiled detail maps generated using Blender's NumPy; mobile-friendly joining of surface meshes to reduce renderer submission overhead.

Touch controls:
- ORBIT: one finger rotates, pinch zooms, two fingers pan. Camera height avoids clipping through the enclosed roof.
- WALK: left thumb moves, right thumb looks; floor, staircase, and overlook support ground-height tracking. Per-object wall/craft collision is not implemented.
- Header buttons switch focus to Craft, Cell Works, or Overlook. FPS displayed.

**Review limitations:** No save system, race physics, full character controller, exact GLB
asset transfer, final high-resolution authored PBR bakes, or playable race yet. The five
Blender-authored detail textures are intentionally small tiling surface variations—not
photorealistic scanned materials. Material assignment maps Blender material slots onto
shared URP materials. The review craft is not the approved final hero mesh. This stage is
intentionally separate from production assets until phone performance is verified.
