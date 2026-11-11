# NF-H01 — Gate 02 / Clay Silhouette Review

**Status: BUILT, RENDERED, AWAITING USER VISUAL APPROVAL.** Do not proceed to Gate 03.

- Source generator: \`tools/build_hero_01_clay.py\`
- Successfully completed Blender build: [NF-H01 Gate 02 Clay Model — run #4](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/43044549421)
- Original editable model: \`NF-H01_Gate02_Clay.blend\` in the downloadable **NF-H01-Gate02-Clay-4** CI artifact.
- Eight real Blender camera renders: front, rear, port side, starboard side, top, underside, front 3/4 and rear 3/4, 1200x900 each.
- Engineering plan: [Gate 01 spec](01_ENGINEERING_SPEC.md) and [dimension map](01_PROPORTIONS.json).

### What the actual clay model does establish

An original continuous tapered nose, separately swept central fuselage, curved raised canopy envelope, independent left/right shoulders and forward intake volumes, aft machinery placeholder, paired large main nozzle cylinders, plus separate forward winglets and rear stabilizers. These are independent, named Blender mesh objects; this is not generated illustration material.

### What requires owner's silhouette judgment

1. Is the armored nose still too tapered/pointed compared with the reference's broader blunt front?
2. Are the side shoulder/intake masses prominent enough, or should they stand farther proud of the central hull?
3. Does the canopy need to stretch fore-aft and sit lower, or is the current height/proportion close?
4. Are the twin rear nozzle masses broad and long enough to anchor the silhouette, viewed from behind and above?
5. Are the little front planes and rear fins correctly proportioned to keep a compact hover-racer outline?

### NOT completed — explicitly deferred

- True intake tunnels and structural ribs: Gate 04.
- Hollow jet interiors, actual thruster support and underside hover/lift hardware: Gate 05.
- Transparent articulated canopy, cockpit and interior HUD: Gate 06.
- Panels, detailed vents, screws, wear: Gate 07.
- UVs, PBR metal textures and original livery: Gate 08.
- **Production GLB**, interactive Godot garage inspection, Android race LOD: Gates 10–12. **Inspection-only GLB** is now required for future review packages beginning at Gate 02, per owner request.

The first render had cropped planform views and washed-out clay. The corrected run #4 has full planform framing, revised intake volumes and improved tonal contrast. No claim is made that this silhouette is accepted.

### Next step

Obtain direct visual feedback on the eight camera renders. Iterate **within Gate 02** until explicitly approved. Do not advance the progress manifest as a side effect of CI success.
