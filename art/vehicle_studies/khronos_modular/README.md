# Khronos CarConcept — NFR modular conversion, Stage 01

**Experimental modular vehicle / NOT the approved FORGE production craft.**

## Source, permission and scope

- Source: KhronosGroup/glTF-Sample-Assets / Models/CarConcept / GLB/CarConcept.glb.
- License: **CC BY 4.0** for the model, except Khronos marks/logos and other associated trademarks, excluded from that license. Credit original source in all derived releases.
- The input is pinned by SHA-256 in the builder. No source is silently replaced by an unrelated model.
- Imported 109 GLB meshes / 213,347 triangles. The prototype strips identified conventional wheel, brake, hub, axle and trademark-bearing nodes and switches the remainder to unbranded clay materials. Remaining **82 independently modeled donor geometry meshes / 147,775 triangles**.
- The original body/canopy geometry is deliberately preserved without cutting holes or forcing topology changes.

## Tested first-stage customization

Permanent base donor vehicle + nine named socket transforms:

1. `rear_engine` — stock **Foundry Pulse**, **Vortex Twin**, **Titan Vector**, **Nova Overdrive** (three upgrades).
2. `rear_fins` — Street Phantom, Aero Strike, Industrial Forge.
3. `side_intakes` — Street Phantom, Aero Strike, Industrial Forge.
4. `front_splitter` — Street Phantom, Aero Strike, Industrial Forge.
5. `side_skirts` — Street Phantom, Aero Strike, Industrial Forge.
6–9. Factory lift/hover hardware at two front and two rear locations.

These are actual separate GLB modules, not textures or scaled versions of the original wheel meshes. Four engines share one fixed cassette hardpoint and each provides different thruster internals and a separate performance-data entry. Three named style presets can be mixed by installing parts from different families in each slot.

## Reproduce and test

```sh
mkdir -p build/khronos_donor game/assets/vehicle_modular
curl -fL https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/CarConcept/GLB/CarConcept.glb -o build/khronos_donor/CarConcept_ORIGINAL.glb
python -m pip install numpy trimesh networkx scipy
python tools/build_khronos_customization_pilot.py --source build/khronos_donor/CarConcept_ORIGINAL.glb --out game/assets/vehicle_modular
# Godot 4.7.2

godot --headless --path game --editor --import --quit
godot --headless --path game --script res://tests/modular_vehicle_smoke_test.gd
```

The headless Godot test instantiates the donor and stock modules, switches through engine and kit choices, verifies the hardpoint transforms, checks invalid-part rejection, and confirms there is exactly one active module per socket after each swap.

## Remaining work before game integration

The original rear wheel arches remain open; **seamless retopology still needs to be built and reviewed**. Side intake accessories are external to the donor panels and will ultimately require engineering the duct openings into replaceable skins. The preview is **not optimized for an ARM64 Vulkan Mobile race** (147k triangles before modules; visual LOD and collision decomposition are not yet in place). No production garage, player save, pricing/earnings, vehicle physics, or signing workflow has been changed in this stage.

This experiment is built around a licensable donor; no Khronos marks should be carried into a final release. Artist verification is required beyond the named-node and material removal.
