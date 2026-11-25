# NF-BW01 — Gate 04 PBR look-development and geometry bake review

**Current approval:** Gates 01–03 accepted for visual design; Gate 04 **IN PROGRESS**.
**Source:** [Approved LOD review release](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-gate03-review-2) and [high-poly R2 master](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-container-master-7).

## Stage 04A — Industrial look-development

Blender 4.3 [generator](build_gate04_materials.py) creates eight original 512 × 512 reusable surface families, each with:

- **BaseColor:** sRGB PNG (non-physically-derived but authored to plausible finish values).
- **Metallic/Smoothness for Unity URP:** **R = metallic**; **A = smoothness = 1 − roughness**, saved as non-color RGBA. It is *not* a glTF metallicRoughness texture; the two APIs require different conventions.
- **Tangent-space micro normal:** derived from authored microscopic procedural height. This is surface microtexture only; **not a bake of the master geometry.**
- **Look-development:** real Cycles renders of the actual optimised LOD0 mesh, plus editable derivative Blender material file and a standalone candidate GLB.
- **Preservation:** approved Gate02/03 source and all LOD geometry remain untouched; no import into Unity until the next gate.

Materials: graphite powder coat, machined tool steel, bright brushed alloy, near-black polymer, orange formed safety armor, nitrile elastomer, ceramic insulator, dark diagnostic screen glass.

## Stage 04B — Geometry transfer and AO requirements, **not yet satisfied**

Gate 03 UV0 covers each of 68 renderer meshes individually; the UVs reuse their 0–1 coordinates across separate meshes. It is incorrect to run one full-machine high-to-low bake into that overlapping atlas and call it valid. Before Gate 04 approval:

- Establish per-assembly/material unique bake atlases or a robust matching per-component cage-bake workflow. Preserve separate robot pivots and non-destructive source edits.
- Bake actual evaluated high-poly normals onto low meshes with aligned rays/cages; prove matched spatial geometry, correct tangent space, ray hit quality, seam padding and absence of self-projection errors.
- Bake real ambient occlusion into compatible unique UV sets (not a white AO placeholder), validate lighting consistency and seam/padding against close-up views.
- Audit texel density, map memory, mipmapping/ASTC use and Unity URP importer settings. Record exact channels.
- Show *actual* Blender/Cycles finished material review images; obtain owner approval before advancing to matching Unity studio Gate 05.

## Production QA state

- [ ] PBR lookdev material maps and derivative model generated and uploaded by successful GitHub run
- [ ] Base-color and metallic/smoothness channels structurally validated (including per-pixel alpha)
- [ ] Blender beauty images reviewed with owner
- [ ] Unique bake UV strategy verified by geometry test
- [ ] Selected-to-active high-to-low geometry-normal bake completed and checked
- [ ] Actual AO bake completed and checked
- [ ] Bake map seams and tangent normals validated
- [ ] Gate 04 owner review decision

**DO NOT mark Gate 04 approved until Stage 04B is done.** A finished shader palette alone is not a true detail bake.

[Stage 04A GitHub Actions workflow](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/workflows/nf-bw01-gate04.yml)
