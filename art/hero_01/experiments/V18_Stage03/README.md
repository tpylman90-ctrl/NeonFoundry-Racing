# FORGE V18.03 — Modular hood and twin front-intake trial

**Status: Stage 03, real inspectable GLB.** The owner accepted the V18.02 wide/deep frame; the approved 235 geometry parts are preserved without vertex or face edits. No game asset or existing frame is replaced. Cockpit and aft exterior are intentionally incomplete while this assembly is inspected.

## Assembly-first order

1. **Hood mounting structure:** independent deck; four cross-body formers; eight primary carrier brackets with independent fasteners.
2. **Removable hood:** center spine, port and starboard formed skins with edge hems, individual nose anchors, service hinges and pins, separately formed front beak.
3. **Duct architecture:** two genuine open-through extruded/octagonal duct walls with changing stations, machined perimeter lips, deep internal guide vanes and dividers. Mouths are not black rectangles painted on a solid face.
4. **Nacelle structure:** independent low/high triangulation arms and physical clevis brackets at the frame's existing front hardpoints. Three nacelle side armor plates per side plus split fore/aft upper skins.
5. **Hood-to-intake transition:** forward and aft pressed shoulder bridge panels with real cross-sectional overlaps; mechanical braces below.
6. **Hood cooling:** sunken bed, separate frame and five recessed louvers rather than a flat surface texture.

The original FORGE eight-view artwork, new clay image, and owner's exploded parts sheets guide design intent. This model **does not claim a DINOv2-generated CAD mesh**; DINO/depth visual analysis previously supplied reference information, while these parts were built as deterministic procedural geometry.

## Measured construction checks

- Approved V18.02 frame retained: **235** geometry meshes, identical vertex and face arrays.
- New separately editable parts: **161** across 7 modular assembly groups.
- New assembly GLB: **396** independent meshes and **18,056** triangles.
- All parts separately closed/manifold and consistent normals.
- Open air passage validated at the center of each front duct.
- Planar section areas confirm seven physical join interfaces (hood ↔ frame, left/right hood ↔ bridge ↔ intake, and left/right intake ↔ mechanical clevis). Actual intersection areas in `FORGE_V18_03_CONTACT_AUDIT.json`; no claims of pressure- or fatigue-tested structure.

## Rebuild, verification, and owner review

Run from repository root:

```bash
python -m pip install numpy trimesh networkx scipy shapely
NFR_STAGE03_OUT=build/forge_v18_stage03 python tools/build_forge_v18_stage03.py
python tools/check_forge_v18_stage03.py \
  --frame art/hero_01/experiments/V18_Stage02/FORGE_V18_02_WideDeep_Chassis.glb \
  --model build/forge_v18_stage03/FORGE_V18_03_Hood_Intakes_Modular.glb \
  --out build/forge_v18_stage03/FORGE_V18_03_CONTACT_AUDIT.json
```

Inspect `FORGE_V18_03_Hood_Intakes_Modular.glb` in the Android A/B viewer. Specifically review frontal mouth openings, bonnet-to-pod seams, height and width relative to the FORGE clay reference, and future cockpit clearance.

**Next step after owner's visual sign-off:** revisit the intake angle and outer shroud shape with orthographic top and front clay references; then construct the cockpit greenhouse as independently fitted frame, glass and roof armor assemblies. Do not collapse all components into one shell.
