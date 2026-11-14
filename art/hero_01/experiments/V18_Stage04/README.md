# FORGE V18.04 — independently modeled cockpit & rear-cowl assembly

**Status:** owner-inspection experiment; V18.03 hood/intakes and V18.02 frame are preserved, untouched. Not a production craft or a full completed FORGE body.

## Construction sequence

1. **Physical attachment hardpoints:** ten machined sill clamps + bracing, separate bonnet hinges and bolts (not merely bounding-box intersections).
2. **Individual canopy glazing:** left/right curved windscreen halves; four door side windows and four roof panes. Each surface has real edge thickness and GLB alpha-blend materials.
3. **Canopy structure:** formed transverse arches, continuous extruded roof rails, A-pillars, molded glass perimeter seals, door seams, gas struts, latch and hinge pins.
4. **Cabin interior:** a mounted seat with independent bolsters and harnesses, front instrument beam, HUD and steering yoke.
5. **Formed rear roof:** three longitudinal aerodynamic panels (central deck and paired side shoulders), split upper armor with service seams, spline ridges, structural saddles, bracing, and open booster-pocket framing.
6. **Lower fairing adapters:** paired pressed pieces physically tie the glass sill down to the known V18.02 chassis rails, rather than float above the spaceframe.

## Verified geometry

- Exactly **396 preserved V18.03 meshes**, including the accepted V18.02 chassis and real front intake assemblies.
- **161 new independently named parts** across seven fabrication groups.
- **557 total separate meshes / 38,596 triangles** in the inspection GLB.
- Every part is a closed watertight, consistently wound individual component. This **does not mean the entire vehicle is one welded/manifold solid**.
- Ten independent cross-sectional intersections were measured at physically relevant front, lower-door, rear canopy and aft cowl mounts (five per side). Contact areas are recorded in `V18_04_Contact_QA.json`.
- Real GLB loaded by `trimesh` and the VTK glTF importer; four camera renders saved in the conversation workspace for visual review.
- Existing Stage 03 source geometry was checked exactly unchanged. **No game repo production craft was replaced.**

## Reproducibility

```bash
python -m pip install numpy==2.3.5 scipy==1.17.0 trimesh==4.11.1 networkx==3.6.1 shapely==2.1.2
python tools/build_forge_v18_stage04.py
python tools/check_forge_v18_stage04.py \
  --base art/hero_01/experiments/V18_Stage03/FORGE_V18_03_Hood_Intakes_Modular.glb \
  --model build/forge_v18_stage04/FORGE_V18_04_Cockpit_Assembly.glb \
  --out build/forge_v18_stage04/V18_04_Contact_QA.json
```

The actual GLB is at `art/hero_01/experiments/V18_Stage04/FORGE_V18_04_Cockpit_Assembly.glb`.

**Source basis:** FORGE 8-view reference, the new clay render, and owner-provided exploded-parts breakdown. Visual interpretation and procedural modeling drove this geometry. The DINOv2/Depth Anything outputs are *reference diagnostics*, not a trained image-to-3D mesh reconstruction. No fresh DINO optimization run was made for V18.04.

**Review priorities:** verify canopy windshield height/length, rear roof-to-cab join, cockpit sill alignment, Android glass blending and door side-window positions before proceeding to full side armor or detailed rear propulsion. Fine geometry/texture finish and Godot Android runtime testing remain pending.
