# NF-H01 Hero Craft — LOCKED BUILD ORDER

Status: ORDER LOCKED; gate 01 active, not yet approved.
Asset: NF-H01, working name "Forge One" (not final).
Goal: original production-grade, fully inspectable hover racer for Neon Foundry Racing. The existing menu promo craft is not a production asset.

## User's three photographic references

The project conversation contains a rear three-quarter view, front three-quarter view, and top view. Use these only to understand construction and proportions, not to copy the branded mesh, decals, sponsor logos or exact design.

Primary design DNA: long low wedge/armored fuselage; tapered nose; raised dark framed canopy; widened shoulders and large side intake housings; compact fins; large exposed twin cylindrical rear propulsion; deeply layered mechanical parts; underbody hardware; rugged aerospace-metal finishes.

Critical proportions in this order:
1. Side profile: long front nose, raised canopy placed slightly aft of forward half, broad engine-heavy tail.
2. Top profile: taper forward, articulate cockpit waist, wide shoulders, fins and separate engine masses.
3. Rear: two unambiguously large engine nozzles mounted by visibly functional structure.
4. Canopy/body must be integrated, not a glass box sitting on the roof.
5. Hover lift assemblies and vent clearances must be geometrically real; wings alone are not hover systems.

Blender standard: meters; Z-up; craft forward is -Y. INITIAL proposed blockout dimensions (not image measurements): 7.2 m long; 2.7 m hull width; approximately 4.2 m including fins; 1.8 m height excluding hover clearance. Dimensions are provisional until the silhouette gate is accepted.

## Mandatory numbered gates

| Gate | Allowed implementation | Proof required before progressing |
| --- | --- | --- |
| 01 — Engineering and proportion plan | Study reference, identify original assemblies, component boundaries, scales, pivots and viewing directions; no craft modeling yet | Written dimension/proportion/assembly plan reviewed and approved |
| 02 — Clay silhouette blockout | Only major masses: nose, center hull, cockpit volume, shoulders, rear fuselage, rough fins and nozzle volumes | ACTUAL Blender .blend plus neutral clay front, rear, both sides, top, underside and front/rear 3/4 views; silhouette approved |
| 03 — Main fuselage surfacing | Build clean rounded/creased hull topology, tapered front, roof transitions, rear and proper underbody; keep pieces independent | Real clay/wire review for smooth profiles, correct shading and strong front/side/top proportions |
| 04 — Structural layers and aero | Build separate shoulders, intake ducts, inboard frames, aero fins, brackets, access surfaces and negative spaces | Front/top/oblique clay and exploded assembly review; no flat recessed rectangles masquerading as mechanisms |
| 05 — Propulsion and lift hardware | Model twin rear vector thrust units, nozzle structure, engine mountings and distinct underside hover/lift assemblies | Real rear, side and underside renders demonstrate coherent engineering, proper alignment and clearance |
| 06 — Canopy and cockpit | Shape actual canopy, hinges and seals; interior tub, seat, controls and holographic HUD inside cockpit | Canopy open/closed, driver-eye and clearance views; no intersections |
| 07 — Secondary geometry | Real vent depth, panel geometry, cooling fins, lights, mechanical details, connectors, fasteners | Detailed clay close-ups and actual wireframe showing layered constructed geometry |
| 08 — UV and PBR finish | Unwrap UVs; metal/paint/carbon/glass roughness, detail textures, weathering and original markings | Lit material renders from multiple angles; believable material response, no copied brand decals |
| 09 — High-detail hero audit | Correct geometry, shading, pivots, view-dependent defects; finalize Blender source | Actual Blender scene, wire/clay/beauty front/rear/side/top/3/4/underside/cockpit set approved |
| 10 — Godot export and inspection | Export clean GLB, bring into Mobile/Vulkan Godot scene; assemble interactive parts and inspection camera | GLB + editable Blender source + working Godot inspection; visible geometry matching Blender |
| 11 — Mobile optimization and validation | LODs, simpler collider and draw-call/material/texture optimization; test on target Android phone | Actual device FPS and visual review; comparisons with high-detail asset; no severe flicker or culling |
| 12 — Game integration | Replace menu promo art with approved hero craft; connect to garage display and future vehicle controller interfaces | Signed Android review APK and user approval before beginning a second craft |

## Absolute process rules

- Never advance to a later numbered gate until user explicitly accepts the present gate's evidence and current geometry. "Proceed" means advance only when the current gate has already been accepted.
- Present the same multi-view clay or wireframe evidence from the actual Blender mesh. AI illustration is never accepted as proof a model was built.
- Models must be constructed from independent layered objects with measured transforms, valid normals, and believable mechanical attachments. Never compensate for poor geometry by painting it.
- No detailed texturing before gate 08. No Godot integration before gate 10. No second model or track as a distraction from the first craft.
- A new feature request for a future gate is recorded in art/hero_01/DEFERRED.md and revisited when that gate opens. Point out the specific gate number when redirecting the request.
- If a defect affects an earlier accepted gate, reopen that gate and demote later approvals as required. Fix security or broken build infrastructure promptly without treating the fix as craft-stage advancement.
- The status source of truth is art/hero_01/progress.json; CI runs tools/validate_hero_workflow.py. The script checks sequencing/evidence records, but cannot independently authenticate actual user visual approval.
- Any reorder or bypass requires a fresh explicit user decision and recorded change in docs/DECISIONS.md. No silent reorder.

## Current next action

Gate 01 only: build and obtain sign-off on the engineering/proportion/assembly specification extracted from the three photos. Do not start cockpit polishing, materials, texture work, garage integration, or a second craft.
