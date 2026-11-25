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

## Verified Stage 04A results — 2026-11-24 local / 2026-11-25 UTC

[Successful Blender/Cycles material review build #45518932714](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/45518932714)

[Material release: three authentic Blender rendered PNGs, candidate GLB, editable .blend, all 24 material maps](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-gate04-lookdev-1)

- **68 renderer groups** correctly classified into **8 finish families**. **24** distinct 512×512 PNG maps validated, actual Blender source and 1040×780 Cycles beauty images present.
- **Actual packed pixel readback (not only filenames):** orange ARMOR metallic R ≈0.42/smoothness A ≈0.62; steel ≈0.94/0.65; graphite ≈0.38/0.46; elastomer ≈0.00/0.22. Alpha carries smoothness as required by URP Lit, not roughness.
- These PBR maps are **physically motivated lookdev**, still not validated in Unity URP. The supplied micro-normal images are procedural tiles and are **not** high-to-low geometry bake results.

## Verified Stage 04B pilot — real matched geometry, not whole-asset approval

[Successful true geometry bake workflow #45519436411](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/45519436411)

[Six real geometry-baked PNGs and method report](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-gate04-bake-pilot-2)

Blender Cycles **selected-to-active** baked tangent-space normal maps from matched R2 high-poly components onto corresponding LOD0 UV0 meshes for the **robot shell**, **cassette shell**, and **shuttle frame**. Ambient occlusion was also actually baked on those three target meshes with the other LOD0 parts providing surrounding occlusion. Result: three high-to-low normal maps and three AO maps, each 512×512 PNG. Pixel-level inspection found varying geometry normal values and nonuniform AO; structural checks passed. The normal variation is relatively subtle because LOD0 still retains most of the source surface curvature. This pilot does **not** establish ray-cage clearance/seam quality, whole-workstation coverage, or full material approval.

## Stage 04B — Geometry transfer and AO requirements, **partially demonstrated**

Gate 03 UV0 covers each of 68 renderer meshes individually; the UVs reuse their 0–1 coordinates across separate meshes. It is incorrect to run one full-machine high-to-low bake into that overlapping atlas and call it valid. Before Gate 04 approval:

- Establish per-assembly/material unique bake atlases or a robust matching per-component cage-bake workflow. Preserve separate robot pivots and non-destructive source edits.
- Bake actual evaluated high-poly normals onto low meshes with aligned rays/cages; prove matched spatial geometry, correct tangent space, ray hit quality, seam padding and absence of self-projection errors.
- Bake real ambient occlusion into compatible unique UV sets (not a white AO placeholder), validate lighting consistency and seam/padding against close-up views.
- Audit texel density, map memory, mipmapping/ASTC use and Unity URP importer settings. Record exact channels.
- Show *actual* Blender/Cycles finished material review images; obtain owner approval before advancing to matching Unity studio Gate 05.

## Production QA state

- [x] PBR lookdev material maps and derivative model generated and uploaded by successful GitHub run
- [x] Base-color and metallic/smoothness channels structurally validated (including per-pixel alpha)
- [ ] Blender beauty images reviewed with owner
- [ ] Unique bake UV strategy verified by geometry test
- [ ] **Three-group bake pilot** succeeded; full approved asset coverage and seam quality still pending
- [ ] **Three-group AO pilot** succeeded; full approved asset coverage and halo artifacts still pending
- [ ] Bake map seams and tangent normals validated
- [ ] Gate 04 owner review decision

**DO NOT mark Gate 04 approved until Stage 04B is done.** A finished shader palette alone is not a true detail bake.

[Stage 04A GitHub Actions workflow](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/workflows/nf-bw01-gate04.yml)
