# FORGE V16 — physical geometry trial (Gate 02 inspection)

The source reference is `art/hero_01/references/forge_8view_original.jpg`.
This is an independently inspectable refinement from the earlier V15 experiment, **not** the production-approved craft.

## Actual geometry changes
- Front intake shroud meshes now have **open eight-sided intake mouths**, separate machined rim geometry, structural inner tunnel liners, physically inset rear caps and multiple internal vanes.
- Replaced the massive disconnected dorsal cowl with a formed **U-section** rear roof bridge, separate rear shoulder haunches and blend plates. The greenhouse, rear fins and propulsive assemblies are preserved.
- Added nose cheek armor, center spine, functional-looking cooling slats, roof grilles, aft-wing root support assemblies and independent side machinery.
- Verified face orientation on the open intake shells for strict single-sided Android GLB viewers. All original main thrusters, lift cells, both rear wings and the canopy geometry remain present.

## Quantitative reference review

Four approximately orthographic views were scored using the **same** coarse GrabCut foreground masks and calibrated projection scales as V15. Scores are diagnostic only; they cannot determine real-world surface quality or hidden geometry.

| View | V15 IoU | V16 IoU | V15 recall | V16 recall | V15 F2 | V16 F2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Side | .77629 | .76072 | .82469 | .84616 | .84375 | .85324 |
| Top | .78158 | .78213 | .91710 | .92543 | .90080 | .90575 |
| Front | .66979 | .69477 | .75653 | .81112 | .77417 | .81461 |
| Rear | .69607 | .72125 | .75692 | .80979 | .78124 | .82086 |
| **Mean** | **.73093** | **.73972** | **.81381** | **.84813** | **.82499** | **.84862** |

**Tradeoff:** V16's side IoU decreased 1.56 percentage points because extra forward-shoulder and panel geometry overfills a few regions. Recall and F2 nevertheless increased across every view. V16 should **not** be characterized as a perfect reference match. The next pass should tighten the side shoulder contour while preserving the restored reference coverage.

## Model and inference provenance
- V15 baseline GLB: 227 independent meshes and 11,244 triangles.
- V16 inspection GLB: **319 independent meshes and 13,288 triangles**.
- V16 GLB SHA256: `c35741125b41025b72d480b7a18f9404a611a907bbb988efe3249cce18119643`.
- Actual DINOv2-small and Depth Anything V2-small analysis of owner's eight-view artwork is retained from a previously verified free GitHub Actions run. These results informed feature placement/depth ordering but this build is **not** automated DINO-driven reconstruction, and it has not rerun either network on V16.
- The V16 mesh is programmatically constructed from V15 using `tools/build_forge_v16_geometry.py`, with optional evaluation from `tools/evaluate_forge_v16.py`. `NFR_WORKSPACE` and `NFR_BASE_GLB` allow selecting a working directory/baseline. It produces GLB and mesh manifest; no Blender or production engine is altered.

## Remaining review gate
1. Inspect the actual V16 GLB in the Android A/B viewer, emphasizing front duct depth, cockpit roof-to-aft continuity, fin visibility, and wing-root junctions.
2. Correct side-view overfill while maintaining or increasing front and rear reference recall.
3. Continue controlled part-specific surface passes before adding final PBR textures and production Godot integration.

This release is intended for **visual inspection only**. The owner has not yet approved this version as a production replacement.
