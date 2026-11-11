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

### Gate 02 feedback: longer, chunkier forward gray pieces

The owner marked both forward intake housings on a front three-quarter clay render and requested: **"the front gray pieces need to be longer more chunky"**. This is a Gate 02 silhouette correction, *not* Gate 04 duct detailing. The mirrored intake envelope now spans about Y=-3.07 to -1.09 m (versus -2.26 to -1.63 previously), with a 0.48 m maximum half-width and approx. 1.09 m section height. The model generator now exports a **viewer-only GLB** from the exact Blender meshes with all studio objects excluded. This preview is not the optimized Godot export reserved for Gate 10. Owner silhouette sign-off is still pending.

### Gate 02 V7 — owner's industrial FORGE hard-surface direction (2026-11-11)

- **Verified implementation:** `tools/build_hero_01_clay.py` now authors an angular, heavier and wider hard-surface massing: boxy 8-sided side pontoons, flat-deck central fuselage, truncated squared nose, longer faceted canopy, larger block rear deck, extended 16-sided engine volumes, revised downward trapezoidal canards and taller canted rear fin volumes.
- **Real Blender evidence:** [Gate 02 Clay Model run #7](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/43078882117) successfully built Blender 4.5.3 `.blend`, inspection `.glb`, and eight 1200x900 PNG views, with the validation job passing. Artifact: `NF-H01-Gate02-Clay-7` (retained 30 days).
- **Honest limitations:** Rectangular intake ducts, Boolean insets, hood trenches, canopy structural ribs, louver slots, detailed nozzle rings, and hover skids are NOT present in the V7 clay artifact. Those are design features for numbered Gates 03–07, and are recorded in `DEFERRED.md`. No textures or integration are claimed.
- **Gate lock:** `progress.json` remains current stage 2, last approved stage 1. Owner has not approved V7 silhouette; no advancement to stage 3.
- **Revision caveat:** V7 width, tail span and nozzle length deviate from provisional Gate 01 engineering dimensions. These must be accepted or corrected in the Gate 02 visual review; `01_PROPORTIONS.json` is not treated as the new geometry measurement.

**Owner review priority:** squared front nose versus side-pod proportions; canopy footprint and roofline; overhang/tip size of twin nozzle volumes; effective shape and position of thin canards; top-view span and the newly tall tail fins. Silhouette alterations are allowed here; fine surface detailing is not.

### Gate 02 V8–V9 rear silhouette corrections — 2026-11-11

Owner's new reference images and critique identified three deficiencies in V7: the canopy lacked a formed junction into the rear deck, the rear vertical fins were too upright, and the rear side wing flares were absent.

- **V8** (commit `ec009edad2e238673808b6b9a8960380d0e460c3`): Added a separate `BLK_031_CabAftFairing`, swept both rear fins farther backward and outward, and authored two independent rear trapezoid wings (`BLK_082_RearSideWing_PORT`, `BLK_083_RearSideWing_STBD`). Blender run #8 passed. The three-quarter views revealed that the new rear wings still looked like small tabs.
- **V9** (commit `08d00b5789b4333066f8b3629bfe0c7e1fd595eb`): Added separate `BLK_032_CabRearHaunch_PORT` and `BLK_032_CabRearHaunch_STBD` to bridge the aft canopy into the shoulder deck; widened and lengthened both rear side wings; increased the rear stabilizers' outward cant. All are real editable clay masses, without false duct/panel/cockpit claims.
- **Verified build:** [GitHub Actions Gate 02 clay run #9](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/43082533902) completed successfully with a Blender source, an inspection-only GLB containing **19 independent craft meshes**, and all eight 1200x900 clay renders. Artifact `NF-H01-Gate02-Clay-9`, subject to GitHub retention limits.
- **Status:** Still **Gate 02 / awaiting owner silhouette approval**. The owner supplied corrections, not a Gate 02 approval. No Gate 03 geometry or later materials, mechanical ductwork, engine internals, lift units or Godot integration has been authorized.

**Next requested inspection:** compare V9 with V7 from port side, top and rear three-quarter views. Verify that the formed rear cab haunches read as part of the fuselage and both rear flares have adequate span and sweep, then request explicit silhouette approval or precise additional feedback.


### V10 — owner-approved CONCEPT translated to a real Gate 02 clay model (2026-11-11)

The owner approved the eight-panel illustrated target showing a wide armored hover racer with visible high rear flares, canopy surround, a substantial central rear fairing and massive twin rear propulsion. The image is **a design reference only**, never evidence that these complex elements already exist as Blender geometry.

**Actual engineering changes**: commit `bebd3a3a8a5aad94d92aac06b81075aadb1b601e` modifies `tools/build_hero_01_clay.py`. It builds 23 separate real mesh volumes, including raised bilateral rear wing flares, new cockpit/greenhouse shoulder guards, front hood shoulder masses, a refitted cab-to-rear spine and expanded faceted aft thruster outer envelopes.

**Verified build**: [NF-H01 Gate 02 Clay Model #10](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/43093668298) passed its Blender 4.5.3 construction and validation. The downloadable `NF-H01-Gate02-Clay-10` artifact includes editable `.blend`, inspection-only `.glb` and eight 1200 × 900 actual Blender PNG camera views. The GLB is independently inspected for 23 meshes and presence of all new named parts.

**Silhouette not yet approved**: User approval of the *illustration* is the target; proof that the current real mesh matches the target requires user review of the exported GLB and actual eight-angle PNGs. Keep `progress.json` at Gate 02. No subsequent gate was started.

**Explicit differences from concept**: The real clay render currently does not include deep intake ducts, engine internals, finished canopy frames/windows, mechanical belly skids, cooling vent louvers, detailed access panels, or production paint. These belong to Gates 04, 05, 06, 07 and 08. The complete high-detail concept is a multi-gate goal, not a single Gate 02 deliverable.

### V11 — marked rear greenhouse cladding constructed as actual geometry

**Request:** Owner accepted the revised concept of a formed armor roof that wraps over the *rear* of the cockpit/greenhouse and tapers down into the rear deck while maintaining the rear side wings. Owner requested implementation in the 3D model, **not another image**.

**Source change:** `tools/build_hero_01_clay.py`, commit `b4324deebfee4d0c9a02b4ef982c4fcf4fe207f3` authors `BLK_096_GreenhouseAftArmoredCowl`, a fully constructed, closed U-section shell with sixteen profile vertices at each of nine fore-aft stations. Roof, angled shoulder transitions and canopy underside clearance are actual geometry. Bilateral `BLK_094_GreenhouseShoulder_*` volumes have been broadened and shaped to overlap the new roof transitions. Both `BLK_082_RearSideWing_PORT` and `BLK_083_RearSideWing_STBD` remain intact and separate.

**Process:** Still Gate 02 clay silhouette, `progress.json` unchanged. Concept approval does not establish approval of the resulting actual GLB. Detailed cockpit frames, seals, hinge, vents, and production engine hardware remain deferred to their assigned gates. A completed CI build plus multi-view visual owner review is still required.


**V11 verified deliverable:** [GitHub Actions Gate 02 Clay #11](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/43106928380) completed successfully with Blender 4.5.3. The validated `NF-H01-Gate02-Clay-11` artifact contains an editable `.blend`, an inspection-only `.glb` (24 independent craft meshes including `BLK_096_GreenhouseAftArmoredCowl` and both separate rear side wings), and eight 1200 × 900 actual Blender camera renders. The source checks, GLB format validation, and eight-view checks all passed. Silhouette acceptance is **still pending** an actual model review by the owner.
