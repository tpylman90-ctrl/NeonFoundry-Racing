# NF-BW01 / v01 — Production Gate Review

**Gate:** 04 — PBR materials and detail baking  
**Status:** GATES 01–03 VISUALLY APPROVED / GATE 04 IN PROGRESS  
**Asset:** Aegis battery exchange workstation  
**Asset class:** Inspectable industrial workshop equipment  
**Target presentation:** Unity 6 garage cell works (close inspection)  
**Source concept:** Original project design; references are research only  
**Purpose:** First complete quality-calibration asset under `docs/PRODUCTION_STANDARD.md`  
**Revision:** 0.1, 2026-11-23

## Verified Gate 02 master output

- Blender source: [NF_BW01_GATE02_HIGH_POLY_MASTER.blend](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/download/nf-bw01-container-master-4/NF_BW01_GATE02_HIGH_POLY_MASTER.blend)
- High-poly inspection-only GLB: [NF_BW01_GATE02_INSPECTION_ONLY.glb](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/download/nf-bw01-container-master-4/NF_BW01_GATE02_INSPECTION_ONLY.glb)
- Verified container workflow: [Blender master build #45312545027](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/45312545027)
- Actual geometry: **413 independently retained modeled objects**, verified bounds **3.77 × 2.36 × 2.67 m**, from evaluated mesh vertices in Blender 4.3.
- Clay/wireframe multi-view render set: **13 authentic Blender-generated 1400×1000 PNG views verified**, including revised underside, front/rear/side/top, 3/4, robot joints and cassette close-ups.
- [Verified render CI #45313327569](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/45313327569) — all rendering, PNG integrity, artifact upload and publication steps successful.
- [Gate 02 review image release](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-clay-review-2) with key PNG images.
- GitHub Actions artifact: `NF-BW01-Gate02-Actual-Geometry-Renders-2`, full 13-view render set plus inspection model and manifest.
- Source model and inspection GLB are also available in [most recent master release](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-container-master-5).
- **Visual observations (not user approval):** Readable articulated arm, guide rail cassette cradle, cooling/power enclosure and guard posts. Underside is mostly a plain base plate and wireframe is dense in joint close-ups; address if owner requests more mechanical undercarriage detail.
- **NOT approved**: gate 02 visual review, kinematic/clearance checks, UVs, PBR, game-ready optimization, and Unity integration.

## Gate 02 R2 — Mechanical refinement (2026-11-24)

The previous visual review was encouraging, and the owner authorized further work with “Ok proceed.” This is approval to **refine Gate 02**, **not** approval to advance to Gate 03.

- New separate geometry module: [gate02_mechanical_refinement.py](gate02_mechanical_refinement.py), integrated into [build_highpoly.py](build_highpoly.py).
- Scope: open underframe with real load-carrying crossmembers and diagonals, protected distribution casing and service pipes, hydraulic shoulder actuator, forearm drive/retainers, an independently keyed jaw carriage with rack teeth/soft pads and wrist connectors.
- **Verified R2 source:** [Container master workflow #45403414584](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/45403414584), successful, preserving **579 modeled objects** and measured physical envelope **3.77 × 2.36 × 2.665 m**.
- [R2 editable Blender master + high-poly inspection GLB](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-container-master-7).
- The **16-view actual-geometry clay/wire review** passed [render job #45403451511](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/45403451511); 16 PNG images are each 1400×1000. New views 14 (gripper), 15 (underframe), 16 (gripper wire). [Published R2 review PNGs](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-clay-review-5).
- Gripper is **a parked engineered assembly**; stroke endpoints, closed-pose clearance, cassette socket alignment, motor power and joint collision volumes are not yet kinematically verified.
- **Current gate decision:** IN_PROGRESS / AWAITING OWNER'S R2 VISUAL REVIEW. The 579-part mesh is ~182,600 evaluated rendering triangles, deliberately high-poly and **not** an Android LOD. No live animation proof or reach test. No UVs, PBR or Unity placement authorized.

## Gate 03 kickoff (2026-11-24)

- User accepted Gate 02 R2's real 16-view mechanical form and authorized moving to optimization.
- Preserve the 579-object high-poly Blender master unchanged as the source of truth.
- Build LOD0/LOD1/LOD2 as separate review-only exports and keep robot joint/actuator components distinct from static workstation structures.
- UVs must be reviewed for overlaps and degenerate islands; texture baking and actual paint are **Gate 04**, not Gate 03.
- Do not place the asset in Unity, infer game FPS, or claim kinematic clearance certification at this gate.
- Gate 03 will require real model-based triangle/UV/collider audit plus same-view silhouette checks.

## Gate 04 kickoff (2026-11-24)

- Owner accepted actual Blender Gate 03 LOD comparison visuals (“From the images these look great”) and then explicitly requested to proceed.
- Gate 03's geometry, UV0 and collision proxies are approved **visually** for continuing work, not physically benchmarked or proven animatable.
- Gate 04 must distinguish procedural tiling material textures from **genuine** high-to-low normal/AO bake output. Any non-baked maps must be labeled accurately; a procedural normal image is not proof of transferred high-poly geometry.
- Confirm Unity URP metallic R, smoothness alpha (1-roughness), normal import convention, and standalone AO path. Preserve the three established LODs and original Blender master.
- Gate 04 materials and any bake artifacts require review before starting Gate 05 Unity comparison.

## Gate evidence

- Proposed dimensions, mechanisms, design DNA, operations and integration: [ENGINEERING_BRIEF.md](ENGINEERING_BRIEF.md).
- Original concept dimension drawing: [ORTHOGRAPHIC_BLUEPRINT.svg](ORTHOGRAPHIC_BLUEPRINT.svg).
- Existing garage integration evidence: `unity/Blender/FoundryPreview/generate_assets.py`; rear service stations on 5m centers and an open central approach.
- External reference only: industrial battery robotic assembly and real industrial safety source URLs within the brief.
- Real Blender asset: **generated and exported** (Gate 02), see model release below.
- Gate 01 owner approval: **2026-11-23, “Looks good proceed.”**

## Mandatory gate ledger

| Gate | Status | Evidence / blockers |
|---|---|---|
| 01 — Art direction and engineering brief | **APPROVED** | Owner: “Looks good proceed.” (2026-11-23). Engineering brief and orthographic concept accepted |
| 02 — High-poly master | **APPROVED** | Owner reviewed R2 clay views and said “These look really awesome,” then explicitly said “Ok proceed” when invited to move to Gate 03 (2026-11-24). Approved as visual shape, not functional kinematics. |
| 03 — Game mesh, UVs and LODs | **VISUALLY APPROVED** | LOD0/1/2 and UV checks passed run #45406053140; owner said “From the images these look great,” then “Ok perfect proceed” authorizing Gate 04. Animation and device performance remain unverified. |
| 04 — PBR and texture baking | **IN PROGRESS** | Authoring measured metal/paint/rubber/glass finishes and URP-correct packed maps; true high-to-low normal/AO baking must be verified before declaring Gate 04 complete. |
| 05 — Studio/Unity visual comparison | NOT_STARTED | Await Blender/Unity test meshes |
| 06 — Unity integration | NOT_STARTED | No scene placement allowed |
| 07 — Physical Android performance + owner approval | NOT_STARTED | No new APK is claimed |

## Gate 01 review checklist

- [x] Asset name and gameplay/service purpose defined
- [x] Measured conceptual height, width, depth and coordinate axes
- [x] Functional module inventory and designed sequence
- [x] Concept front/top/side orthographics **drawn** (not actual 3D renders)
- [x] Proposed garage location based on current script (not verified against deployed asset)
- [x] Reference/provenance sources recorded; no third-party mesh imported
- [x] Owner approves style, identity, dimensions and concept drawing (2026-11-23)
- [ ] Any revisions needed for robotics sweep/cassette size resolved in the brief

## Proposed owner decision

**Gate 01 APPROVED 2026-11-23. Gate 02 visually APPROVED 2026-11-24** by the user's positive assessment of actual R2 renders followed by “Ok proceed” to the offered Gate 03. The physical robotic operation remains unverified, and Gate 03 is not approved.

## Gate 02 production scope — authorized by owner

Create the actual editable Blender high-poly master with separate objects/pivots for pedestal, six-axis arm, gripper, guided cassette shuttle, safety guard, HMI, charge rack, conduit and cabinet. Present clay/wire front/back/side/top/bottom/three-quarter and joint-mechanism close-ups, all rendered from the **actual constructed mesh**.
