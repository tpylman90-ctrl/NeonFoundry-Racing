# FORGE V17 – Connected Armor Attachment Experiment

This is a **Gate 02 inspection-only** successor to V16. The owner's feedback was that parts, especially the hood, looked disconnected. The goal was to improve **physical attachment geometry**, not add decorative mesh count.

- Extended the existing closed hood shell **0.31 m** behind its original leading cockpit seam.
- Added a closed, physically overlapping hood-to-windshield load bridge.
- Added left/right formed hood-to-front-intake deck webs, and three additional structural support ribs on each side.
- Added structural saddles connecting the rear roof haunches to the main hull.
- Retained both front intake housings, the main rear propulsion units, the smaller boosters, wings, fins, and cockpit glazing.
- Every new component is watertight. Actual 2D transverse sections (not only axis-aligned bounding boxes) confirm positive cross-sectional overlap between hood, chassis and both front intake housings at six stations per side; rear saddle contact was checked at four stations per side.

**Source:** `art/hero_01/experiments/V16/FORGE_V16_ReferenceFit.glb`

**Rebuild:** `python tools/build_forge_v17_connections.py` (requires numpy, trimesh, networkx, shapely, scipy).

**Output:** `art/hero_01/experiments/V17/FORGE_V17_ConnectedPanels.glb` – 330 mesh objects, 13,836 triangles. Machine-readable contact audit accompanies the GLB.

**Important limitation:** This remains a layered, overlapping assembly with distinct solid panels, not a globally boolean-unioned, fully manifold chassis. Final integration, collision, and owner visual acceptance remain pending.

The V16 reference asset is preserved and the game craft is not replaced automatically.
