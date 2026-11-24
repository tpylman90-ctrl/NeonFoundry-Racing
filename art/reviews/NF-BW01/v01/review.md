# NF-BW01 / v01 — Production Gate Review

**Gate:** 01 — Art direction and engineering brief  
**Status:** IN_PROGRESS / PENDING OWNER REVIEW  
**Asset:** Aegis battery exchange workstation  
**Asset class:** Inspectable industrial workshop equipment  
**Target presentation:** Unity 6 garage cell works (close inspection)  
**Source concept:** Original project design; references are research only  
**Purpose:** First complete quality-calibration asset under `docs/PRODUCTION_STANDARD.md`  
**Revision:** 0.1, 2026-11-23

## Gate evidence

- Proposed dimensions, mechanisms, design DNA, operations and integration: [ENGINEERING_BRIEF.md](ENGINEERING_BRIEF.md).
- Original concept dimension drawing: [ORTHOGRAPHIC_BLUEPRINT.svg](ORTHOGRAPHIC_BLUEPRINT.svg).
- Existing garage integration evidence: `unity/Blender/FoundryPreview/generate_assets.py`; rear service stations on 5m centers and an open central approach.
- External reference only: industrial battery robotic assembly and real industrial safety source URLs within the brief.
- Real Blender asset: **not yet created** (Gate 02).
- Visual owner approval: **not yet received**.

## Mandatory gate ledger

| Gate | Status | Evidence / blockers |
|---|---|---|
| 01 — Art direction and engineering brief | **IN_PROGRESS** | Written engineering brief and concept 3-view SVG; owner signoff still pending |
| 02 — High-poly master | NOT_STARTED | Must not start until Gate 01 is approved |
| 03 — Game mesh, UVs and LODs | NOT_STARTED | Await high-poly approval |
| 04 — PBR and texture baking | NOT_STARTED | Await optimized game mesh |
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
- [ ] Owner approves style, identity, dimensions and concept drawing
- [ ] Any revisions needed for robotics sweep/cassette size resolved in the brief

## Proposed owner decision

**PENDING**. This record becomes `APPROVED` only after the owner clearly accepts Gate 01. Owner may instead request revision. No guessed date or fabricated consent.

## Next stage, ONLY after approval

Create the actual editable Blender high-poly master with separate objects/pivots for pedestal, six-axis arm, gripper, guided cassette shuttle, safety guard, HMI, charge rack, conduit and cabinet. Present clay/wire front/back/side/top/bottom/three-quarter and joint-mechanism close-ups, all rendered from the **actual constructed mesh**.
