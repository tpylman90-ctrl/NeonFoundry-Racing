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

## Gate 04 R3 — mechanical finish candidate (2026-11-25)

Owner direction: “Agreed keep pushing this might be our best work yet.” This authorizes further refinement, **not** production signoff.

- R3 source: [gate04_r3_mechanical_detail.py](gate04_r3_mechanical_detail.py), loaded onto the authentic [PBR lookdev-3 Blender source](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-gate04-lookdev-3) as a distinct reversible collection.
- Targeted changes: 96-sided motor sleeves and machined annular retaining races; separate gripper wear pads, tool fasteners and pneumatic service parts; physically separate high-voltage/coolant cassette connections; closeable-look transparent side/rear/front shielding with interlock indicator, and revised HMI controls.
- Exact structural shapes and all approved color/material families remain the visual baseline. This R3 derivative is **not** a replacement for the approved 579-part high-poly source or a final LOD.
- [R3 actual Blender review workflow](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/workflows/nf-bw01-gate04-r3.yml) must pass world-envelope, native Blender, GLB and real four-view Cycles render checks. **Do not assert successful PNG artifacts or polished geometry before validation.**
- Guarding is fictional design only. Door travel, mechanical swept-volume clearances, true interlock response, and the robot's actual cassette pickup have not been simulated.
- Follow-up: inspect glass reflections, motor roundness and gripper/cassette connection alignment at 1:1; if accepted, integrate R3 into high-poly master/LOD and redo any affected UV/normal/AO bakes before Gate 04 approval.
- The most recent three-group corrected AO pilot passed [workflow #45617137206](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/45617137206); **that is not full 68-group AO coverage** and needs visual seam review.

## R4 visibility and detail revision — 2026-11-25

User reviewed **actual R3 full-view and gripper/cassette close-up screenshots** and requested **greater transparency and more mechanical detail**. R3 glass was near-opaque blue in several studio views, obscuring the robot and cassette.

- New [R4 reversible geometry layer](gate04_r4_visibility_detail.py) derives from the [verified R3 source release](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-gate04-r3-1) without replacing it.
- Revised glass: near-neutral color, IOR 1.49, roughness 0.015, transmission 0.97, shader alpha 0.12, with **explicit note that Unity URP opacity is not validated yet**.
- Added physical contact shoes, jaw sensors and routed pneumatic lines, cassette cam-locks and connection labels, radiator service fins and hose adapters, richer HMI signals and door protective edge moldings. Avoids unmotivated random bolt spam.
- The five actual-model review cameras include front/rear enclosed views and gripper, cassette and full-machine **glass-hidden cutaway** views. Geometry in the cutaway is unchanged; only panel visibility is toggled for inspection.
- [R4 GitHub render/GLB build](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/workflows/nf-bw01-gate04-r4.yml). **Do not claim complete until verified.**
- Still needed: assess physical gripper and door clearances, surface/intersecting details, full low-mesh bake, and URP transparent material compatibility. Keep Gate 04 pending owner review.

## Gate 04 R5 precision-detail and surface-texture review — 2026-11-26

The user explicitly requested: “Ok proceed pushing R4 model details and texture.” This authorizes **another non-destructive refinement**, not final Gate 04 acceptance.

- **Editable source of truth:** published real [R4 Blender master](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-gate04-r4-1), unchanged.
- New [R5 additive geometry and texture source](gate04_r5_detail_and_texture.py) introduces independently modeled gripper friction pads, sleeve fasteners, jaw sensor details, cassette HV/contact guards, coolant shields, diagnostic louvers, status lights, and service-guard brackets in a separate collection.
- Includes a real **512×512 image-backed maintenance label texture** with a repeatable print pattern; this is explicitly **surface color artwork, not geometry-transferred normal/AO data**.
- Preserves the base eight industrial PBR surface classes and the clearer R4 glass. Two render modes are required: real closed-glass camera plus actual Blender cutaway views for machine-detail inspection.
- [R5 Blender CI](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/workflows/nf-bw01-gate04-r5.yml) must validate .blend, GLB, texture image and all five model-derived PNG views before a deliverable is treated as finished.
- **Stage remains open:** extra R5 geometry still requires bake-ready UV audit, actual high-to-low normal/AO transfer at production level, in-engine URP review, and rig/clearance checks before Gate 05.

## Verified R5 results and render inspection — 2026-11-26

[Successful Gate04 R5 Blender workflow #45836543773](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/45836543773) (the first run #45835940434 completed actual geometry and 5 renders, but failed a too-high size threshold on a highly compressible texture; fixed in the successful run).

[Download verified R5 native Blender source, inspection GLB and five actual Cycles PNGs](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-gate04-r5-2)

- **95 new independent, editable objects** in their own R5 collection; **294 total derivative export objects**. Actual Blender evaluated bounds of the R5 additions: X = −1.7995 to +1.7995 m; Y = −1.1265 to +0.873 m; Z = +0.354 to +2.403 m. Within approved envelope.
- Successfully exported native **17.28MB .blend** and **22.92MB inspection GLB**; validated five real 1040×780 Cycles renders, a real authored 512×512 surface-color PNG and a release manifest.
- **Real image review:** closed-glass R5 angle is now relatively clear and no longer dominated by cloudy blue panels; the orange arm and cassette remain clearly readable. Open-glass view makes detailed interior accessible. The toolhead has additional service fittings and two long gripper fingers; cassette and HMI display several new micro-details and panel diagrams. Topside arm housing still lacks sophisticated animation and most fine visual improvements cluster at close range, so avoid overstating runtime impact.
- A 512×512 maintenance decal is genuinely UV-applied color texture, **not** an AO or normal geometry bake. R5 new mesh is not yet included in Gate03 performance LODs, so the 22.9MB GLB must not be treated as mobile-ready.
- **Status: visually inspectable R5 candidate, owner signoff pending**. Retain R4 as the immutable comparison reference. Gate 04 requires production UV, full high-to-low normal/AO baking and transparent URP proof before Gate 05.

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
