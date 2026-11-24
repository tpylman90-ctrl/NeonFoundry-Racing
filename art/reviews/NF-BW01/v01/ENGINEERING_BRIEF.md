# NF-BW01 — Aegis Battery Exchange Workstation
## Gate 01: art direction and engineering brief | v0.1 | REVIEW PENDING

**Status:** DESIGN PROPOSAL — NOT OWNER-APPROVED. Do not begin high-poly production, baking or Unity placement until Gate 01 is approved.  
**Asset ID:** NF-BW01  
**Category:** Large inspectable workshop machine / robot-assisted power cassette exchange cell  
**Target:** Neon Foundry Racing Unity 6 garage battery works; isolated Blender review first  
**Authorship:** Original project design; references cited for industrial *principles* only; no copied proprietary geometry  
**Governing process:** [Production Standard](../../../../docs/PRODUCTION_STANDARD.md) and [Asset Review Template](../../../../docs/ASSET_REVIEW_TEMPLATE.md).  
**Gate 01 evidence:** [orthographic proposed dimensions](ORTHOGRAPHIC_BLUEPRINT.svg), this brief, review record.  
**Next gate:** Gate 02 high-poly master *after explicit approval*.

---

## 1. Purpose and production-camera promise

NF-BW01 is the first **quality-calibration asset**, not another block-built background prop. Its job is to show what happens when an owned hovercraft receives a modular power-cell swap in an upscale industrial service garage.

From the player's normal eye height, the asset must immediately read as an actual working automated cell: an anchored industrial robot, a guided extraction/insertion cradle, an accepted cassette rack, mechanically plausible toolhead, cable management and an operator/HMI service console. Up close, the robot's joints, fasteners, mounting plates, carriage guides, latches, cooling connectors and service covers must hold up to inspection.

**Hero hierarchy:** 
1. Readable orange/graphite robot silhouette with a distinctly articulated shoulder, elbow and wrist.
2. Captive cassette visible inside a **recessed**, supported shuttle/cradle (not a cube resting on top of a box).
3. Darkened HMI and power cabinet visibly connected to the machine, with restrained cyan status light.
4. Bracing, hoses, panel gaps, service access, safety markings, small fasteners.

The workstation reads more as an **industrial battery works** than a consumer charging kiosk. Physically plausible support and access take precedence over gratuitous glowing strips.

## 2. Proposed outside dimensions — all in meters

Use Blender meters with local **X right, Y rear, Z up**, with semantic **FRONT = -Y**. Proposed dimensions are design targets, not measurements of existing real machines.

| Component | Width X | Depth Y | Height Z | Purpose |
|---|---:|---:|---:|---|
| Whole anchored cell (including passive guards) | 3.80 | 2.40 | 3.40 max | Fits the current 5m-pitch garage service bay |
| Welded foundation + undercarriage | 3.64 | 2.24 | 0.18 | Visible load path through floor plates |
| Central guided cassette cradle | 1.12 | 1.34 | 0.94 deck height | Real guide rails, locking pins, powered slide |
| Cassette — one prop | 0.68 | 0.86 | 0.34 | Insulated shell, two grip sockets, power/thermal blind-mate interface |
| Fixed articulated robot pedestal | 0.72 | 0.76 | 0.70 | Four structural mounting feet, bolted bearing and motor housing |
| Robot shoulder + forearm lengths | approx. 0.88 / 0.78 | — | working envelope up to 3.40 | Proposed six-joint appearance; actual sweep to be verified |
| Exchange cassette dock | 0.88 | 1.07 | 1.52 | Rack at right/rear with nested guide/alignment details |
| HMI/diagnostic panel | 0.62 | 0.25 | 1.10 | Separately mounted at right/front; readable operator interface |
| Rear cooling + DC link cabinet | 0.50 | 0.46 | 2.30 | Vent passages, service doors, visible incoming conduits |

### Proposed local anchors and zones

- Base/workcell center: **(0,0,0)** on finished garage floor. Body X: **[-1.90,+1.90]**, Y: **[-1.20,+1.20]**, Z: **[0,3.40]**.
- Robot pedestal nominal center: **(-0.90,+0.65,0)**. The articulated arm must reach both cradle and exchange rack without sweeping through the player-facing aisle.
- Guided cradle nominal center: **(-0.10,-0.30,0.94 deck)**.
- Store/exchange dock center: **(+0.96,+0.38,0.9)**.
- HMI at **(+1.30,-0.78,1.6)**, tipped toward the aisle.
- DC/cooling cabinet rear right with cable/duct path hidden behind removable access panels.
- Visual robot parked pose reaches high enough to create a machine silhouette but remains beneath **3.40m**.
- Reserve minimum **0.18m internal moving-component clearance** as a *design target* pending a proper swept-volume check. Do not assume this is a real industrial safety clearance.

## 3. Existing garage integration constraints

The current Blender preview `generate_assets.py` creates a 35 × 37 m garage, with rear workstation centers at X = **-11.6, -6.6, -1.6, +3.4**, Y = **+12.25** (Blender Z-up coordinates). NF-BW01 is **proposed** to replace the station at **(-6.6,+12.25)**; it must **not** simply be added on top of the existing workstation.

- With 5.0m bay pitch and a 3.8m outside width, 1.2m remains **between adjacent proposed same-sized cell outlines**, before considering columns, movable doors, or neighbors' robot sweep.
- Front of machine: Y = 11.05; central craft cradle ends at approx. Y = +5.9. This gives roughly **5.15m of open approach depth** in the current plan, subject to all other machines and routes.
- Maintain a clearly marked **walkable front access/service region**. Enclose the powered robot motion inside the machine, never in the open player walkway. Any deployable guard must be part of the mechanism.
- Existing deck/stair geometry occupies the right-side workshop area. NF-BW01's chosen bay is left of this and should not obstruct the deck sightline.
- World placement under Unity's export axis convention is expected near **X -6.6, Z -12.25**, but final transform must be inspected against the real imported asset at Gate 06. Do not mark as verified now.
- For this gate, **no asset is placed in the game** and no production source geometry is altered.

## 4. Mechanical system and authored module boundaries

| ID | Independent module | Required visible construction / use | Future pivot or movement |
|---|---|---|---|
| BW01_00 | Welded base and isolation plinth | Bolted corners, anchor brackets, gussets, lowered foot pads; never floats | Static |
| BW01_10 | Main shuttle cassette cradle | Twin rails, lead-screw/linear actuator housing, bronze guides, locking dogs | Slide along Y with a bounded stroke |
| BW01_20 | Dummy cassette shell | Corners, lifting points, latch recesses, insulated bus and cooling couplings | Independent inspectable/replaceable prop |
| BW01_30 | Robot shoulder pedestal | Turntable ring, drive cover, rear cable feed, heavy mounting plate | Rotates about vertical Z |
| BW01_31 | Robot upper arm | Two-piece articulated armor with exposed joint bearing | Rotates about local joint |
| BW01_32 | Robot forearm | Engineered tapered housing and elbow cover | Rotates about local joint |
| BW01_33 | Wrist and gripper | Two parallel jaws engage *physical cassette sockets*, cable hose tracks | Wrist rotations + jaw motion |
| BW01_40 | Charged/spent cassette dock | Separate supported receiving slots, sprung pins, telescoping stop | Static rack; cassette remains movable |
| BW01_50 | DC link and cooling module | Power entry, louvres, fasteners, hoses/quick-connects, radiator channels | Static cabinet; service door hinged |
| BW01_60 | Operator diagnostic/HMI | Angled display, E-stop for story realism, exposed arm, frame-mounted wiring | Hinged service screen optional |
| BW01_70 | Safety machine envelope | Transparent or framed shielding with orange warning indicators; not an invisible open sweep | Sliding or hinged guard; limits animation |
| BW01_80 | Facility interface | Bolted power trunk and conduit to wall/overhead, supported by brackets | Scene adapter, not detached dangling tubes |

The machine must exhibit continuous force paths. Bearings connect limbs to motors; tubing connects power/cooling sources to their loads; lifting sockets line up with gripper jaws. Screw heads and etched text alone cannot disguise an unsupported mechanism.

## 5. Intended operation — storyboard, not verified kinematics

1. **Idle / ready:** robot parks in overhead folded pose; amber safety frame static; one spent cassette locked in central cradle. Operator can inspect.
2. **Interlock:** visible stop/door lock engages; status transitions and the cell becomes inaccessible to player movement while operating.
3. **Release:** cradle locking dogs retract, plug and coolant connections separate in correct order, cassette is supported by rails.
4. **Transfer:** cradle slides cassette out along guide rails; gripper aligns to keyed sockets and closes over real handles.
5. **Exchange:** arm raises a small controlled distance, places the spent cassette in its bounded dock, retrieves charged cassette.
6. **Insertion:** cradle re-centers and seats the new cassette; physical locks and blind-mate interface engage.
7. **Verification:** HMI changes to green/cyan; safety guard opens and the player can resume inspection.

No animation or physics will be asserted correct until reach, interference, joint limits, and player clearance are simulated in Blender/Unity at later gates.

## 6. Art direction, materials and surface quality

**Design DNA:** aerospace race-team pit equipment × high-voltage battery foundry × precision heavy automation.

- **Silhouette:** asymmetrical but balanced: high articulated robot left, low center cradle, tall cooling/service cabinet right; no equal-height stack of cubic blocks.
- **Manufacturing:** cast base and drive housings, formed robot-shell plates with curved transition surfaces, extruded aluminum rails, recessed fasteners, removable maintenance covers, sealed fluid ports.
- **Palette:** restrained charcoal/graphite; desaturated metallic silver; controlled warning orange at robot motion/locks; small cyan/green diagnosis. *Do not illuminate every edge.*
- **Proposed PBR families:** industrial powder coat, worn/anodized aluminum, bead-blasted steel, rubber bellows, ceramic insulating cassettes, heat-sink metal, thick translucent safety glass.
- **Surface inspection:** real rounded transitions where cast, planar flats where machined, mechanically plausible attachment seams; chamfers with measured scale, no plastic-looking inflatable turbines or padded edges.
- **Presentation:** all-gray clay and wire passes first, then later studio key/fill/rim plus matched in-Unity shots. Do not texture as a substitute for bad geometry.

## 7. Reference study and provenance

These are **research references only**. Do not copy proprietary manufacturer geometry, logos, industrial robot CAD, or engineering drawings into the game's asset.

1. ABB IRB 6700 official product material (reach/work-envelope and the visually obvious layered shoulder/forearm architecture): https://one.robotics.abb.com/en/%E6%9C%BA%E5%99%A8%E4%BA%BA/p/IRB-6700
2. Research on EV battery disassembly/automation: https://pmc.ncbi.nlm.nih.gov/articles/PMC12515223/
3. EV battery manufacturing/handling workflow reference: https://sedinengineering.com/case-studies/battery-pack-assembly-line-design/
4. Industrial safety design context, **not an assertion that a fictional game machine is certified:** ISO 10218-1:2025 https://www.iso.org/standard/73933.html and ISO 10218-2:2025 https://www.iso.org/standard/73934.html

No third-party model is authorized for import by this Gate 01 brief. Geometry will be original, Blender-authored.

## 8. Gate 01 review criteria and unresolved risks

### Required before claiming Gate 01 APPROVED

- [ ] Owner accepts **machine identity, aesthetic and hero hierarchy**, rather than generic factory fixture.
- [ ] Owner checks proposed 3.80 × 2.40 × 3.40m dimensions, orientation, cassette dimensions and layout.
- [ ] Owner accepts front/top/side orthographic **concept blueprint**; drawing is only a dimensioned proposal, not actual mesh evidence.
- [ ] Robot/cradle/rack reach and separation are judged feasible at design level; full swept-volume analysis deferred to Gate 02.
- [ ] Provisional garage position avoids replacing/obstructing unrelated stations, railings and walk routes.
- [ ] Provenance reviewed: references only; no proprietary mesh reuse.
- [ ] No modeling, UV, PBR, APK or Unity asset placement erroneously represented as complete.

### Explicit unresolved tasks

- Robot's exact drive sizes, gripper motion and joint-limit envelope require model-based proof; the proposed lengths are provisional.
- Cassette mass/payload and the difference between an exchangeable **module** and a whole-craft battery pack require gameplay-consistent numbers. This concept depicts **one modular cassette**, not an entire vehicle pack.
- Safety guards/interlock visual design must not imply unsafe player proximity during active robot motion.
- Exact garage wall alignment, nearby fixtures and service-rack clearance require the full runtime plan and eventual placement QA.
- Orthographic drawings will be reviewed with the owner; render-quality mood references and mechanical exploded view follow the accepted brief, before high-poly production.

**Gate decision:** PENDING OWNER REVIEW. **Next action:** obtain explicit approval or revision notes; then begin Gate 02 high-poly modeling and actual-model multi-view clay/wire review.
