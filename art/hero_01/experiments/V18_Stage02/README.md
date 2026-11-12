# FORGE V18.02 — Wide, Full-Depth Chassis (inspection)

Owner feedback: original V18.01 tubular frame was too slender, then the side truss walls were too short in vertical elevation. This is an **actual GLB geometry rebuild**, not an edited illustration.

This independent Stage 02 experiment retains the assembly-first engineering approach and raises/deepens the side walls from nose through engine bay. It includes full-length intermediate rails, additional welded-style uprights, full-height triangulated braces, taller cockpit hoops, and relocated mounting brackets.

| Measured frame property (m) | V18.01 | V18.02 |
|---|---:|---:|
| Front port/stbd sidewall vertical span | 0.47 | **0.92** |
| Rear port/stbd sidewall vertical span | 0.64 | **1.12** |
| Front primary rail-to-rail width | 1.42 | **1.76** |
| Rear primary rail-to-rail width | 1.86 | **2.24** |
| Frame mesh count | 191 | **235** |
| Triangle count | 9,060 | **11,460** |

The implementation retains 10 named mounting hardpoints and a single connected **design-graph**, with individual watertight GLB meshes, 7 editable assembly hierarchy groups, 95 structural nodes and 184 beam edges. This is a topology/connectivity prototype, not a structural stress/FEM validation. Tubes meet through physical overlaps at connection nodes, not weld-manufacturing geometry.

The main model `FORGE_V18_02_WideDeep_Chassis.glb` should be inspected in the Android GLB viewer **before** adding outer body panels. A supplementary `Frame_With_Reference_Modules` file is locally available but contains V17 placement placeholders that may not align with the revised frame. The original V18.01 and V17 assets remain untouched.

Reproduce from the checked-in V17 craft with `python tools/build_forge_v18_stage02.py`. Output in `build/forge_v18_stage02/`. The exported GLB was independently validated and reproducibly byte-identical in a clean local repo-style layout. Owner visual approval is pending.
