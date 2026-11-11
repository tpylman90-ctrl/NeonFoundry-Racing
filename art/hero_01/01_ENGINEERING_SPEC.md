# NF-H01 / Forge One — Gate 01 Engineering & Proportion Specification

**Design revision:** G01-R1 — **approved for Gate 02 clay blockout** by the user’s explicit “Ok proceed to the model for visual inspection” on 2026-11-11. Numeric dimensions remain tentative for the Gate 02 visual silhouette review.  
**Project:** Neon Foundry Racing · Android-first Godot Mobile/Vulkan + Blender  
**Source:** Three user-supplied reference images in conversation (rear-three-quarter, front-three-quarter, top).  
**Gate constraint:** No Blender mesh, material pass, cockpit construction, or Godot vehicle scene may start until the owner explicitly accepts this specification.  
**Purpose:** Lock credible, original spatial architecture before spending time on surface detail.

## 1. Reference interpretation and design decisions

These images are treated as a **visual engineering reference**, not as a licensed asset or a mesh to reconstruct. Angles provide useful silhouette information; they do not reveal exact dimensions, underside clearance, internal mechanisms or full cockpit geometry. All numerical sizes below are **proposals** for a new original craft, not measurements taken from the reference.

| Camera | Features that must survive reinterpretation | What cannot be confidently inferred |
| --- | --- | --- |
| Front three-quarter | Long armored wedge nose; slightly raised single-seat/tandem-style canopy; inset hood vents; broad overlapping side shoulders; deeply recessed side intake mouths; small forward-mounted aerodynamic planes; visibly independent side channels | Actual intake internal construction, number and geometry of underside lift cells, precise cabin dimensions |
| Rear three-quarter | Engine-heavy tail; **two very large cylindrical rear exhaust modules**; independent shrouds/braces; angular tail stabilizers; strong rear mechanical depth and distinct side cladding; narrow raised canopy volume ahead of engines | Physical propulsion technology, articulation axes, actual powertrain mounting and exhaust internals |
| Top | Nose / canopy / tail aligned along one strong centerline; narrowing forward silhouette versus wide side shoulders; cockpit shape carved into the central mass; front/rear fins and outboard masses forming a wider overall planform | True 1:1 breadth/length ratio (perspective and orthographic projection unknown), underside visibility, exact pivot locations |

### Preserve

- Looks first like a **designed aircraft/racing machine**, not a conventional sports car without wheels.
- Long, sloped, multilayer forward hull with a recognizable beak/armored impact wedge.
- Body grows broad toward the mid-to-rear shoulders, tapering again at the exposed rear exhausts.
- Raised *integrated* transparent canopy (not a standalone geometric box).
- Each side intake/thruster housing has visible wall thickness and an actual tunnel/negative space when we reach Gate 04.
- Twin rear engines are visually substantial—cannot be tiny cosmetic rings.
- Aerospace construction vocabulary: structural load paths, mechanical overlaps, serviceable parts.

### Must change to make our own

- **No reproduction of** visible "FORGE" lettering, number 07, sponsor trademarks, labels or copied panel placement.
- Replace the reference's side graphic blocks with an NF-H01 **split-chevron shoulder structure**, distinctive forward-facing open intake geometry and a central dual-keel nose.
- Give the rear exhausts **hexagonal protective mounting collars** and individually mounted circular inner stages (later Gates 05/07), creating a distinct rear signature.
- Use a **three-rail canopy frame** and outboard lift-cell housings instead of an exact copy of the reference roof/pods.
- Develop original panel rhythm, seams and insignia at the appropriate late stages.

## 2. Shared Blender spatial convention

**Metric:** Blender units = meters, scale = 1.00; transforms applied intentionally.  
**Axes:** +Z up, -Y forward/nose, +Y rear/thrusters; +X starboard/right, -X port/left.  
**Visual asset root:** \`NF_H01_ROOT\` at (0,0,0) beneath the craft centerline.  
**Proposed mass center helper:** \`DATUM_COM_EST\` (0,+0.20,+1.07); provisional for a later physical simulation.  
**Ground datum:** z=0 represents the floor/deck; the initial static craft is approximately 0.35–0.50 m clear of it. No physics or hover controller is being added in this gate.  
**Mirroring:** symmetric X silhouette at Gate 02. Deliberate asymmetry may be introduced later when mechanically justified.  
**Export:** GLB handed off only after Gate 10; do not confuse Blender look-dev with game-ready topology.

### Working envelope (NOT measured from reference)

| Dimension | Proposed size | Review consideration |
| --- | ---: | --- |
| Overall length | **7.20 m** | Tip at Y = -3.60; tail lip at Y = +3.60 |
| Central armored fuselage maximum width | **2.80 m** | x = +/-1.40 in thick shoulder / aft mid-body |
| Broadest hull + intake housings | **3.45 m** | x approx. +/-1.725, before aerodynamic fins |
| Total winglet / finspan | **4.20 m** | x = +/-2.10; wings are short and angular |
| Top of canopy | **2.20 m** | Measured from the grounded reference z=0 |
| Main lower belly | **0.48–0.70 m** | Hovercraft needs visible clearance and mechanical underbody |
| Rear primary nozzle outside diameter | **1.02 m each** | Significantly larger than a decorative exhaust |
| Rear nozzle center X | **+/-1.02 m** | Mirrored, leaving a central separation |
| Rear nozzle exit plane Y | **+3.60 m** | Mechanical collar sits forward of this plane |
| Nominal free hover gap | **0.35–0.50 m** | For visualization only; not physics |
| Cockpit canopy length | **2.10 m** | Y approx. -0.70 to +1.40, centered just aft of midpoint |
| Cockpit visible max half-width | **0.69 m** | Retain pronounced shoulder bodywork outside cabin |

The initial overall proportion is **length : finspan ~1.71**, **length : maximum hull ~2.57**. These are authored targets subject to the clay review, not claims about the supplied model.

## 3. Primary hull cross-sections (the Gate 02 blockout contract)

The next gate should build the silhouette from smooth connected longitudinal cross-sections, *not* stacked boxes, and should deliberately separate the shell from its raised shoulders. The following stations are measured from local vehicle origin. A station's \`half_width\` describes only the **central primary shell** (intakes, fins and propulsion extend beyond it); all heights are relative to z=0.

| Station Y (m) | Center half-width X (m) | Upper Z (m) | Lower Z (m) | Intended read |
| ---: | ---: | ---: | ---: | --- |
| -3.60 | 0.23 | 0.93 | 0.72 | Faceted blunt armored beak |
| -3.15 | 0.60 | 1.02 | 0.59 | Sharpened upper nose chine |
| -2.60 | 0.91 | 1.13 | 0.53 | Broadening forebody, recessed hood geometry later |
| -1.70 | 1.11 | 1.24 | 0.49 | Forward shoulders begin; tapered intake aperture zones |
| -0.70 | 1.27 | 1.30 | 0.48 | Canopy root / intake throat separation |
| +0.35 | 1.33 | 1.35 | 0.49 | Thick waist and highest shoulder mass |
| +1.35 | 1.40 | 1.45 | 0.49 | Broad engine cradle connection / aft canopy |
| +2.30 | 1.32 | 1.40 | 0.53 | Rear taper, retained machinery volume |
| +3.10 | 1.11 | 1.28 | 0.60 | Mechanical tail with nozzle housings alongside |
| +3.60 | 0.80 | 1.16 | 0.74 | Narrow central rear spine; engine lips define rear face |

**Blockout shape rule:** No station should be translated directly into an angular extruded rectangle. Use a curved crown, a restrained shoulder chine and a deeper faceted lower wedge. Surface topology/flow gets engineered at Gate 03, *after* Gate 02 silhouette approval.

### Projected outline / width checkpoints

- Nose tip X = +/-0.23, narrow but not needle-sharp.
- At Y=-2.60, central body width 1.82 m; paired outer intake shoulders may begin flaring toward +/-1.43.
- At Y=-0.70, central body 2.54 m wide; independent shoulder housings reach roughly +/-1.55.
- At Y=+1.35, central body reaches 2.80 m; protected outboard propulsion bracing leads toward +/-1.70.
- Short side winglets/planes extend to about +/-2.10 around Y=-1.1 to -0.1; small vertical tail fins near Y=+2.2 to +2.9, not gigantic aircraft wings.
- Rear thruster centers X +/-1.02; each ~1.02 m outside diameter, visually dominant from behind.
- **Top silhouette must show a waist break** where canopy glazing meets outer shoulder structure, even though central hull widens aft.

### Projected side profile

- Nose Z ~0.9 at Y=-3.6 rising progressively toward forward shoulder Z~1.25.
- Canopy front ramp begins around Y=-0.70, rises to roof apex Z~2.20 around Y=+0.35, then slopes to a structural rear collar Z~1.60 by Y=+1.40.
- Side intake housings do not rise above the canopy; they read as a continuous but distinctly layered machine body.
- Rear fins rise roughly to Z~2.0 and lean slightly rearward; they frame, not hide, the canopy from oblique view.
- Tail motor casings sit lower than the cockpit, showing forward thrust load path and rear silhouette depth.
- Bottom isn't flat: a midline belly channel and articulated underbody lift hardware are reserved for Gate 05.

## 4. Component assembly contract and object naming

A professional Blender scene must have **independent objects/collections** for real assemblies. The component contract below defines ownership and approximate occupied volumes; only \`BLOCKOUT\` masses are constructed at Gate 02.

| Collection / part ID | Function / rough space | Construction stage |
| --- | --- | ---: |
| \`NF_H01_ROOT\` | Overall scene parent, local origin at visual datum | 02 |
| \`BLK_010_NosePrimary\` | Tapered impact wedge, Y -3.60 to -1.65 | 02 |
| \`BLK_020_CenterFuselage\` | Continuous main shell, Y -2.60 to +3.60 | 02 |
| \`BLK_030_CanopyEnvelope\` | Separate volume placeholder from Y -0.70 to +1.40 | 02 |
| \`BLK_040_Shoulder_PORT\`, \`BLK_041_Shoulder_STBD\` | Twin outer masses along Y -1.7 to +2.4 | 02 |
| \`BLK_050_AftMachinery\` | Thick central cradle Y +1.35 to +3.3 | 02 |
| \`BLK_060_Nozzle_PORT\`, \`BLK_061_Nozzle_STBD\` | Only cylinder silhouette at stage 02, X +/-1.02 | 02 |
| \`BLK_070_FinFront_PORT/STBD\` | Small sideplanes, total span <=4.2 m | 02 |
| \`BLK_080_FinRear_PORT/STBD\` | Compact rear stabilizer masses | 02 |
| \`HULL_*\` | Proper nose/body panels, continuous surfacing and clean edges | 03 |
| \`AERO_*\`, \`INTAKE_*\`, \`FRAME_*\` | Real ducts, structural ribs, panel layers, supports | 04 |
| \`THRUST_*\`, \`LIFT_*\` | Serviceable engine internals, hover modules, annular rings, undercarriage | 05 |
| \`CANOPY_*\`, \`COCKPIT_*\` | Canopy pivots, framed glass, seat, controls, HUD inside | 06 |
| \`DETAIL_*\`, \`LIGHT_*\` | Mesh-sculpted surface hardware and light fixtures | 07 |
| \`MAT_*\`, \`LIVERY_*\` | Original material and graphics authoring | 08 |

**Coordinate-space and hierarchy rules:** the mirrored port/starboard objects remain separate and consistently named. Future canopy pivot should be anchored approximately at Y=+1.30, Z=+1.6, with opening clearance reviewed at Gate 06; actual hinge axis isn't approved yet. Engine gimbal pivots and hover-lift directions must be physically justified before Gate 05, not guessed now. Pivot aids may be marked as design helpers, never claimed as working machinery.

## 5. Engineering packaging and clearance assumptions

These are important but **not visual facts recovered from the images**.

- **Cockpit:** One pilot as the default; sufficient conceptual shoulder space for seat and controls. Keep a 0.9–1.0 m usable internal width and 1.9 m class canopy longitudinal shell allowance. Internal features are Gate 06.
- **Thrust:** Two outward-visible large rear main nozzles; the engine shrouds must visibly connect to aft side cradles, which then feed loads into the central hull. Avoid nozzles hovering unsupported in space.
- **Lift:** Four planned underside lift modules, two forward around Y=-1.65 and two rear around Y=+1.80 at approximate X +/-1.06. These are **packaging placeholders** until Gate 05, not modeled functional repulsors at Gate 02.
- **Intakes:** Distinct paired front-facing duct mouths toward mid-forward shoulders, with no immediate dead-end geometry. Gate 02 reserves negative-space envelope; Gate 04 creates real intake walls and depth.
- **Access:** Side cladding ought to be removable for garage inspection, but visible functional panel seams and latches belong to Gate 07.
- **Mass distribution:** broad aft engine weight balanced by elongated forward keel; not a claim of physically computed center of mass.
- **Materials:** eventual weathered aerospace alloy palette and graphite, muted burnt-bronze side accents, original NF insignia. NO texture/decals/livery during the clay stage.

## 6. Gate 02 production deliverables, after Gate 01 approval only

Build a real editable Blender file with the primary volumes listed as \`BLK_*\`. Only neutral material; no fake photorealism.

**Required orthographic camera set** (same exact Blender scene):
1. FRONT (looking aft from Y=-, nose fills frame)
2. REAR (looking forward from Y=+, twin nozzles dominate)
3. PORT SIDE (X=-)
4. STARBOARD SIDE (X=+)
5. TOP (+Z)
6. UNDERSIDE (-Z)
7. FRONT 3/4 (nose + side)
8. REAR 3/4 (engines + side)

Output must include an editable \`.blend\` file and independently downloadable PNGs (neutral gray clay). Provide scale dimensions in shots, a part hierarchy summary, and comparison notes keyed to the reference. No "beautiful render" is a substitute for proving the model's proportions.

**Gate 02 acceptance checklist:** aircraft-like original identity; clearly longer than wide; differentiated nose and rear; canopy integrates with body; no blocky truck-cab roof; shoulder taper seen from top; two engines read at rear; no unsupported disconnected appendages. If any viewpoint fails, **stay on Gate 02** and refine before proceeding.

## 7. Gate 01 approval checklist (owner decision)

The owner should approve or adjust:
- [ ] Overall dimensions and profile stations above (especially 7.20 m length, 4.20 m finspan, canopy placement)
- [ ] Twin-engine priority and independent lift system packaging
- [ ] Original split-keel, shoulder and canopy language rather than reproducing reference markings
- [ ] Single-seat cockpit and rear-canopy pivot assumptions
- [ ] **Eight-view clay-only deliverables** before any finer modeling or material work

**Gate 01 state: APPROVED FOR INITIAL CLAY BLOCKOUT.** The user accepted the design as a starting point and authorized Blender silhouette inspection. Gate 02 remains in progress and **is not approved**; do not proceed to surfacing or details until the eight renders are visually accepted.
