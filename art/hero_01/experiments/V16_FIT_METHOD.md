# FORGE V16 — revised reference-to-geometry fitting method

**Status:** Method improvement, not a finished V16 mesh or a gate approval. The existing V14 and V15 experimental GLBs remain unchanged.

## Why change the method?

Our V15 reconstruction scored higher on silhouette IoU but reduced reference coverage (recall) substantially. Four-view, fixed-projection diagnostic comparison:

| Metric | V14 | V15 | Interpretation |
| --- | ---: | ---: | --- |
| Mean intersection-over-union | 0.6720 | 0.7309 | V15 overlaps a higher fraction of the silhouette union |
| Mean precision | 0.7261 | 0.8803 | V15 has fewer extraneous/oversized projected regions |
| Mean reference recall | **0.9005** | **0.8138** | V15 omits more of the artwork silhouette |
| Mean recall-weighted F2 | **0.8588** | **0.8250** | A more conservative metric penalizes the lost coverage |
| Mean symmetric 95th-percentile contour error | 58.4 px | **29.1 px** | V15 has more consistently aligned outline boundaries |

The mean values are the arithmetic average of front, rear, top and left-side projections. Existing 2D alignment was manually calibrated and reference artwork foreground masks were obtained by GrabCut. These are prototype metrics, not ground-truth depth or absolute measurements.

The critical failure was treating IoU as the only success criterion. When the whole vehicle is slightly oversized, shrinking it can improve IoU while losing real detail (especially fins, wings, shoulders, nose and engine contour).

## New evaluation gates

1. **Reference registration first.** Keep a camera manifest of each source view, pixel crop, orthographic scale, projection origin, and axis convention. Never tune the reference camera independently for each candidate; reject perspective mismatch or unreliable source segmentation.
2. **Segment major parts.** Label nose, two front intake shrouds, canopy, dorsal rear cowl, aft shoulders, side armor, left/right wings, fins and both propulsion tiers. Use user-confirmed landmarks or manually supervised masks for ambiguous geometry. Do not mistake FORGE lettering or texture contrast for structural depth.
3. **Replace single-metric optimization.** Track per-view IoU + precision + **recall**, recall-weighted F2, symmetric contour distance, section widths and landmark offsets. Track errors separately at nose, greenhouse and rear, in addition to the whole silhouette. Any gain in IoU accompanied by a substantial recall drop is a warning, not a validated improvement.
4. **Use DINOv2 for feature correspondence.** Compare the exact camera-aligned Blender render against the corresponding owner-artwork tile. Use mutual nearest-neighbor patch matches, geometric consistency filters and manual landmark verification. Do **not** interpret global cosine score as recovered CAD dimensions.
5. **Use Depth Anything V2 for relative shape.** Compare depth ordering of canopy, intakes, shoulders, fins and thrusters within the same view; ignore global depth scale and studio floor. Treat it as a visual cue, not a metric 3D point cloud.
6. **Optimize surfaces in groups.** First tune longitudinal cross-sections on side/top views; then front/rear width and height sections; only then remodel individually layered intakes, cabin frames and rear machinery. Maintain left/right mirror constraints unless the owner's reference shows an intentional exception.
7. **Accept only tested geometry.** Generate actual GLBs and matched 8-view renders, run regression checks on preserved engines, wings, cowl and mechanical assemblies, and obtain owner inspection in the Android A/B viewer. Do not advance the Gate 02 signoff automatically.

## Target V16 priority

- **Highest priority:** recover cockpit/cowl and front/rear missing coverage without returning to V14's bloated outline.
- Next: distinct front intake bores and layered shoulder geometry (the screenshot shows V15's nose still reads as shallow/simple).
- Then: rear wing/fins and dual-tier boosters, preserving unique mesh identities and checking rear and top projections.

## Implemented now

The existing public `tools/geometry_vision.py` now reports reference recall and a recall-weighted F2 score beside IoU, including missing/excess pixels. `tools/tests/test_geometry_vision.py` includes a regression test where an undersized render has perfect precision but poor coverage.

This is the diagnostic foundation for V16; no claim is made that a trained network automatically reconstructed the mesh.
