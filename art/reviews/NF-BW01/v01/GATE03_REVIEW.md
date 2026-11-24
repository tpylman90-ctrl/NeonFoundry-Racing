# NF-BW01 — Gate 03 optimization review

**Asset:** Aegis battery-exchange workstation  
**Approval received:** Gate 02 visual design approved by owner on 2026-11-24 (“These look really awesome”; then “Ok proceed” to Gate 03).  
**Current status:** **GATE 03 IN PROGRESS — NOT OWNER-APPROVED**

## Source of truth
- [Gate 02 reviewed high-poly source](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-container-master-7): 579 independent objects; ~182,600 evaluated triangles; 3.77 × 2.36 × 2.665 m.
- [Gate 02 reviewed real-model clay/wire PNGs](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/releases/tag/nf-bw01-clay-review-5).
- [Gate 03 Blender optimizer source](build_game_mesh.py).

## Gate 03 deliverables being checked
1. **LOD0** preserving high-quality close inspection silhouette with rendered-bevel reduction and independent mechanism groups.
2. **LOD1** reduced mid-distance mesh with subordinate fasteners and fine lines omitted where not silhouette critical.
3. **LOD2** reduced distant machine shape for racing/garage far camera; not expected to hold up to close scrutiny.
4. **UV0** per exported mesh using Blender smart projection with finite-value checks; shared material atlas/bake compatibility still requires Gate 04 consolidation. Across meshes the 0..1 UV square may be reused; do not falsely imply a global non-overlapping atlas.
5. **Colliders** 11 separate simple box candidates: floor, pedestal, table, cabinet, rack, HMI, shield posts and robot arms/toolhead. These are planning primitives, not a validated dynamic mechanism or safety envelope.
6. **Real model comparisons** same-camera clay front-quarter at master / LOD0 / LOD1 / LOD2 plus side master / LOD0, alongside per-LOD triangle and renderer counts.

## Technical decisions
- Leave the approved master untouched. Geometry LODs are **derivative**, generated from evaluated meshes.
- Segment by machine assembly and original pivot group rather than joining a single room-scale mesh; material reuse is maintained.
- Named pivot group boundaries are preserved as grouping metadata, not proof that the GLB can already execute reliable animation.
- Reduction and UV unwrap are computational heuristics. Quality must be judged against actual rendered views before acceptance. Ray cages, bake-ready packed UV atlases, normal/AO maps and final URP materials belong to Gate 04.
- Source dimensions, unit system and player-accessible structure are not changed.
- **No Unity prefab integration or Android APK is permitted until the applicable gates pass.**

## Pending acceptance checks
- [ ] LOD0/1/2 actual GLBs exported without corrupt topology
- [ ] All three have finite UV0 and no missing UV face loops
- [ ] Distinct LODs have strictly decreasing triangle counts
- [ ] No important mechanism or silhouetted arm disappears prematurely
- [ ] Core assembly and proposed pivot boundary names retained
- [ ] Collision primitives aligned on real source views (no physics result assumed)
- [ ] Matched close-up views support quality acceptance
- [ ] Explicit owner approval of Gate 03

## Latest run
[Gate 03 automated LOD/UV review](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/workflows/nf-bw01-gate03.yml). This document intentionally does not assert any build/LOD count until verified.
