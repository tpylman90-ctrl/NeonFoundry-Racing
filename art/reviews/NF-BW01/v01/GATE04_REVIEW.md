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

## Visual inspection findings — 2026-11-24 (Gate 04 not approved)

**Inspected actual files:** `NF_BW01_GATE04_THREE_QUARTER.png`, `NF_BW01_GATE04_REAR_THREE_QUARTER.png`, `NF_BW01_GATE04_ROBOT_DETAIL.png` from `nf-bw01-gate04-lookdev-1`, and all three actual Cycles-baked AO/normal pairs from `nf-bw01-gate04-bake-pilot-2`. These are inspected outputs, not hypothetical references.

**Visual strengths (accept as artistic direction, not final technical approval):** warning-orange robot armor reads cleanly against graphite base and silvery machined joint faces. Distinct housings, open crate cradle, protected hose loops and composed silhouette remain legible under soft key/rim lighting. Studio reflections are restrained, and the design remains consistent across front/rear views.

**Required corrections / risks before Gate 04 acceptance:**
1. **AO UV backgrounds:** black unused regions are conspicuous in the actual AO PNGs, and many occupied regions have strong dark borders. Do not treat black unoccupied texels as valid ambient occlusion. Bake to an explicit neutral-white AO background, verify adequate island padding/dilation at mip levels and avoid dark seams.
2. **AO sampling:** AO shows visible grain at full 512px view; increase Cycles samples/denoise appropriately and inspect 1:1 closeups. Pilot generated at 8 Cycles samples; unsuitable as a signed-off final bake.
3. **Incomplete coverage:** selected-to-active detail and AO are demonstrated for only **3** material/assembly groups, not all 68 LOD0 renderers. Complete matching group plan and UV bake pages before claiming the whole machine has normal/AO detail.
4. **Normal map subtlety:** geometry-baked tangent normal maps appear close to flat purple apart from fine edges (global means R/G ~0.501, B ~1.000). This is consistent with a high-fidelity LOD0 retaining much of the source geometry; visually verify that detail transfer is meaningful and no ray hits are missing. Do not mistake a flat-looking map for completed detail transfer.
5. **Material highlights:** robot paint is clean, sometimes broad/flat, and the material-class boundaries are visually effective. Inspect close-up roughness/grain and fine panel edging at 100% zoom before claiming photorealistic materials. Unity URP comparisons remain Gate 05.

**Pixel inspection diagnostic (counts are entire image, including unused UV space):** near-black pixel share (RGB max < 0.04) robot AO 60.6%, cassette AO 80.4%, shuttle AO 57.6%. These statistics do not distinguish valid dark interior occlusion from unoccupied UV texels, but reinforce the need for AO background and coverage inspection.

**Disposition:** `MATERIAL LOOKDEV PROMISING / BAKE REVISION REQUIRED`; visual Gate 04 **NOT APPROVED**. Do not advance to Gate 05 or game placement based on this inspection. Preserve all three camera views as baseline for bake iteration.

## Gate 04 R2 continuation — authorized 2026-11-25

The owner reviewed three actual Cycles beauty views and approved continuing refinement: “This is looking really good continue refinement.” This is **approval of the art direction and of continued Gate 04 work**, not signoff to start Gate 05.

**R2 source improvements pushed:**
- [Actual geometry bake pilot](prove_gate04_highlow_bakes.py) now writes explicit neutral white AO unused UV texels and tangent-neutral unused normal texels; margin increased to 20px and Cycles samples to 48. CI uses image pixel checks for black AO background and rejects uniform white AO.
- [Actual PBR material renders](build_gate04_materials.py) use Cycles 32-sample output and include two new model-based inspection close-ups, gripper and battery cassette, alongside the established front/rear/robot views.
- The baseline R2 approved mechanical geometry, the eight material families, and the original studio camera positions remain the visual reference.
- **Pending verification:** both Actions workflows must finish and their output PNGs must be inspected for seams, grain and metallic roughness. Do not mark the re-bake successful until results are checked. Full 68-group bake coverage is still required and outside this three-group R2 pilot.

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
