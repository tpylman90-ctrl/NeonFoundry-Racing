# FORGE V18 — assembly-first correction

**Status: Stage 01 / inner chassis and hardpoints prototype (NOT a finished vehicle or game-approved asset).**

## Why this pass differs from V17

V17 contained hundreds of mesh objects, but its silhouette still depended heavily on a continuous, reference-derived lower hull and a one-piece greenhouse mesh. Named objects by themselves do not demonstrate genuine engineering assembly. The owner's exploded reference diagrams show a separate skeletal structure with removable canopy, front intakes, individual side armor plates, dorsal engine covers, detachable rear thrusters, hover modules, undercarriage shields, and skids. We will use the exploded sheet to define part ownership and mounting interfaces before surface detail.

## Ground-truth references

- `art/hero_01/references/forge_8view_original.jpg`: previously approved 8-view overall proportions and silhouette.
- `art/hero_01/references/forge_parts_breakdown.jpg`: new part grid from owner.
- `art/hero_01/references/forge_exploded_assembly.jpg`: new exploded assembly view from owner.

The references are design artwork, not an authoritative measured CAD drawing. The prototype uses dimensions from actual V17 mesh to establish approximate frame coordinates. **No full DINO-to-3D geometry solution has been used**; AI feature matches are not interchangeable with mechanical mount data.

## Stage 01 output

`FORGE_V18_01_Structural_Subframe.glb` contains only newly created **frame structure**:

1. **Ladder chassis:** paired continuous lower rails, upper sills, crossmembers, and side triangulation.
2. **Keel:** separate central longitudinal spine with center-to-sill ties.
3. **Cockpit safety cage:** A-pillar, crown tubes, transverse hoops, and load-bearing aft stays.
4. **Ten armor/intake/wing mounting points:** each with its own welded load arm, separate bracket plate, and fasteners.
5. **Rear propulsion cradle:** two continuous engine rails, transverse bracing, and stays attached to the rear chassis.
6. **Five independently modeled belly panels**, plus selected gusset nodes.

Verification: **191 independent watertight meshes**, **9,060 triangles**, **140 parametric load-member edges**, **75 named frame connection nodes**, and a **single connected structural centerline graph**. A connected line graph is a design check, not a structural stress calculation. The cylinders physically overshoot each centerline intersection by their radii to avoid visible gaps. Actual welded intersections are **not boolean unioned** and loads have **not** been evaluated with FEA.

`FORGE_V18_01_Frame_With_Modules.glb` is only an **assembly placement study**: it includes the new frame and selected V17 intake shells, canopy placeholder, side armor, wings, and rear thrusters, kept as independently selectable meshes. It deliberately omits the V17 one-piece lower hull to reveal the internal structure. **The retained canopy is explicitly temporary** and does not satisfy the final panelized-canopy standard. It is not a finished racer. Some exterior components still require precise fitted attachment interfaces.

## Changed order of operations

1. Frame and hardpoint geometry; inspect mounting positions in real GLB.
2. Separate canopy glazing **per window** with distinct windscreen frame, side rail, hinges, seals, dashboard and seat.
3. Model **each front intake** as an assembly of exterior shroud, structural frame, tapering duct walls, lip, baffle, vanes, attachment bolts, and internal throat (not an intact solid block with a dark rectangle).
4. Develop hood **in layers**: understructure, two cheek panels, central centerline section, radiator/scoop, lip, locking seam, and separate fasteners; remove large continuous top shells only after each replacement part fits.
5. Rear roof: build upper cowl bridge, separate rear shoulder castings, twin inboard boosters and main thruster cradles. Keep rear fins and side wings as separate mounted pieces.
6. Underbody: power coils, conduits, six shield sections, and hover modules with real interfaces.
7. Produce fully assembled and exploded GLBs, part-by-part clay/wire inspection, then PBR material and bake pass.

Every stage must check: (a) actual mesh topology (normals/manifold where applicable), (b) interfaces and intentional clearance, (c) no missing modules, (d) silhouette from all reference directions, and (e) user approval before promoting game assets. **Separate parts, physical connection to support hardware, and coherent body silhouette are all required**. Polygon or object count alone cannot pass the check.

## Rebuild

From repository root, with `numpy`, `trimesh`, `networkx`, and their supported dependencies installed:

```bash
python tools/build_forge_v18_stage01.py
```

The script loads a local V17 experimental inspection GLB at `art/hero_01/experiments/V17/FORGE_V17_ConnectedPanels.glb`, then writes two new diagnostic GLBs and JSON manifests under `build/forge_v18_stage01/`. Do not override or replace V17. Experimental only.
