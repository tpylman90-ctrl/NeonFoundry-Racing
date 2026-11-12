# NF-H01 / FORGE V15 — eight-view reference-guided geometry experiment

**Status:** Standalone Gate 02 **inspection experiment only**. Do not mark any craft approval gate complete, import into production game, or replace the baseline V14 geometry without owner visual approval.

## Inputs and verified AI evidence

- The owner's full-resolution eight-view reference is tracked at `art/hero_01/references/forge_8view_original.jpg`.
- Genuine DINOv2-small and Depth Anything V2 Small inference on all eight artwork crops was verified by the [original-artwork Actions run](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/43144569174).
- DINOv2 side-view feature cosine (left vs right): **0.871**, which is visual similarity, **not** a real-world measurement or proof of correct part correspondence.
- Depth Anything V2 maps are **relative depth per image**, not meters and not uniquely recoverable 3D geometry.

## Geometric approach

V15 is a new standalone, physically modeled GLB experiment from the V14 exported GLB. The workflow uses the artwork's approximate orthographic silhouettes to constrain proportions. DINO maps and relative-depth visualizations inform inspection of visible canopy, wings, intake, and aft assemblies. Blender/mesh construction follows those interpreted constraints; this is **not** automatic trained image-to-3D reconstruction.

The experiment retains independently modeled V14 main thrusters, upper auxiliary exhausts, lift modules, and visible lower machinery. It rebuilds the continuous chassis, nose hood, side intake shrouds, lower machinery frames, shifted and tapered greenhouse, cab-to-rear roof, large side armor, aft shoulder/fin surfaces, and swept front/rear wing geometry. Closed mirrored mesh winding was checked so port-side faces remain visible in single-sided GLB viewers.

## Results: fixed-scale orthographic silhouette IoU

Reference masks were extracted with OpenCV GrabCut; GLB faces were orthographically projected onto the same source-artwork pixel scale. Values are **silhouette intersection-over-union**, not visual similarity judgments or production quality.

| View | V14 | V15 | Change (points) |
| --- | ---: | ---: | ---: |
| Left side | 0.664 | 0.776 | +11.25 |
| Top | 0.721 | 0.782 | +6.05 |
| Front | 0.637 | 0.670 | +3.29 |
| Rear | 0.666 | 0.696 | +2.99 |

V14 overall height/length ratio: **0.287**; V15: **0.236**; approximate side-view reference: **0.229**.

V14 span/length ratio: **0.603**; V15: **0.560**; approximate top-view reference: **0.557**.

V15 export checked in trimesh and VTK GLB importer: **227 independent mesh objects, 11,244 triangles**. The two intentionally open intake bore interiors are not expected to be watertight. The remainder of newly constructed closed pieces are watertight with outward-facing normals.

## Limitations and user review

This is a **real geometry** advance in coarse silhouette only. It does **not** yet faithfully reproduce every mechanical recess, micro-layer, trim, texture, vehicle design annotation, or hidden underside component from the artwork. Reference segmentation and camera framing can produce errors, so the reported scores must be supplemented by side, top, rear, front and oblique visual inspection, ideally on the owner's Android GLB viewer.

No dedicated DINOv2 optimization loop against newly rendered V15 images was completed. The next experimental phase is camera-aligned reference/mesh feature correspondence and iterative per-part edits, while preserving this Gate 02 review gate.

**Artifacts:** A separate experimental V15 GLB, source reconstruction script, masks, comparison images and report were created in the conversation's artifact workspace; they have not been imported into the game repo as production assets.
