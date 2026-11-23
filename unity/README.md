# Neon Foundry Racing — Unity 6 Android Preview

This Unity project is isolated under `unity/` in the original Neon Foundry Racing repository.
The prior Godot game and Blender library remain unchanged.

- **Editor:** 6000.3.27f2; Universal Render Pipeline 17.3.0.
- **Target:** Android ARM64; Vulkan with OpenGLES3 fallback.
- **Build:** Shared Eclipse Hollow Sky Unity runner with its existing Unity license secrets.
- **Source models:** `Blender/FoundryPreview/generate_assets.py` creates two OBJ/MTL assets on CI.
- **Build method:** `NeonFoundryUnityBuild.BuildAndroid`.
- **Expected APK:** `unity/Builds/Android/NeonFoundry-Unity-Garage.apk`.

This is a **garage/inspection technology slice**, not a complete game or the final approved hero vehicle.
The model is a geometry review placeholder. It uses a Blender lofted fuselage,
sponsons, machined thruster rims, vent slats and canopy, plus an independent
hangar with cell workstations, chargers, robotic arm fixtures, and an observation
deck reached by an unblocked stair run.

Touch controls:
- ORBIT: one finger rotates, pinch zooms, two fingers pan.
- WALK: left thumb moves, right thumb looks; fixed-height collision-free prototype.
- Header buttons switch focus to Craft, Cell Works, or Overlook. FPS displayed.

**Review limitations:** No save system, race physics, collision-based walking, exact GLB
asset transfer, final PBR bakes, or playable race yet. Material assignment currently
maps Blender material slots onto a reduced URP test palette. This stage is
intentionally separate from production assets until phone performance is verified.
