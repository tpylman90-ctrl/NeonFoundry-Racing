# NF-H01 visual-to-geometry review (free / non-destructive)

The reference-assisted comparison tooling has been added **alongside** the original
Blender construction pipeline. It does **not** reconstruct geometry automatically,
modify any craft mesh, copy a third-party model or advance an approval gate.

Current NF-H01 remains at **Gate 02 — user silhouette review**, using the existing
V12 real Blender craft with its rear cowl, paired inboard boosters and preserved rear
side wings. This is geometry metrology, not texturing or production integration.

## What is operational

1. `tools/blender_vision_masks.py` opens an existing Blender `.blend` read-only
   for purposes of review (does not save it), renders **eight** RGBA silhouette
   masks from the same orthographic camera settings as the clay pipeline, and
   exports per-part evaluated mesh bounds and dimensions in meters.
2. `tools/geometry_vision.py` compares camera-aligned reference and actual
   rendered masks, outputs colored overlay, silhouette IoU, bounding-box errors,
   and five cross-section width measurements. Reference-only = red;
   model-only = cyan; overlapping = light gray.
3. An optional landmark JSON can describe points marked on the original photo
   and on the actual model render. For a calibrated orthographic view **only**,
   projected pixel deltas are converted to meters using a **known** span.
4. Optional `--dino` uses Meta's free Apache-2.0 `facebook/dinov2-small`
   model. The global and aligned-patch cosine metrics are **visual similarities**,
   not measured geometry and not approval evidence by themselves.
5. Optional `--depth` runs `depth-anything/Depth-Anything-V2-Small-hf`
   on each image, producing **relative** 8-bit depth maps. Those maps do **not**
   establish dimensions from a single uncalibrated photo.

There is **no external inference API charge**. Both optional neural models
download their publicly available weights and run locally/CPU. CPU model inference
may be slow and is **opt-in**, not part of the default build. The GitHub Actions
job uses an ordinary standard `ubuntu-24.04` runner in the public repo.
Do not switch to billable larger runners.

## Free GitHub Actions entry point

Use [NF-H01 / Vision-Assisted Geometry Review](../.github/workflows/geometry-vision.yml),
the manual **Run workflow** button, or its push-triggered validation.

By default the workflow downloads the existing real Gate 02 V12 Blender artifact
(run `43112335705`, artifact `NF-H01-Gate02-Clay-12`), validates the tools,
renders eight silhouettes, records the mesh measurements, and uploads
`NF-H01-Vision-Geometry-<run-number>` for inspection. No automatic resculpt.

To compare a photo, the workflow also accepts an OPTIONAL `reference_path` that
must already exist in the workflow checkout and a matching `view`.
However, the repository is **public**. Do **not** commit private screenshots,
personal photos, third-party copyrighted references, or unapproved brand art to
make this work. The standard preferred workflow is to provide reference images
here in ChatGPT and run the comparison on a temporary working copy, without
publishing them. The AI options only run when a reference is provided.

### Local / temporary working copy

Dependencies for core comparison:

```bash
python -m pip install 'numpy>=1.26,<3' 'Pillow>=10,<13'
```

Use Blender 4.5.3 with a downloaded existing Gate 02 Blender source:

```bash
blender -b build/hero_01_gate02/NF-H01_Gate02_Clay.blend \
  --python tools/blender_vision_masks.py -- \
  --output-dir build/geometry_vision/masks
```

The Blender source is not overwritten. Then use a reference with either a valid
transparent alpha silhouette or a separate black/white foreground mask:

```bash
python tools/geometry_vision.py \
  --reference /private/rear_reference.png \
  --reference-mask /private/rear_reference_mask.png \
  --render build/hero_01_gate02/02_rear.png \
  --render-mask build/geometry_vision/masks/02_rear.png \
  --out build/geometry_vision/comparison
```

This gives `silhouette_overlay.png` and `geometry_review.json`.
If you lack a reference mask but your reference image has genuinely transparent
alpha, omit `--reference-mask`. **Opaque studio photos are rejected without a
foreground mask**: automatic background segmentation can easily mistake floors,
shadows or body openings for geometry.

Optional AI:

```bash
python -m pip install --index-url https://download.pytorch.org/whl/cpu 'torch==2.6.0'\npython -m pip install 'transformers>=4.44,<5'
python tools/geometry_vision.py \
  --reference /private/rear.png --reference-mask /private/rear_mask.png \
  --render build/hero_01_gate02/02_rear.png \
  --render-mask build/geometry_vision/masks/02_rear.png \
  --out build/geometry_vision/ai_rear --dino --depth
```

### Landmark file format

Provide your **measured** landmarks for the same angle:

```json
{
  "camera": "orthographic",
  "reference": {"nose": [10, 50], "tail": [110, 50], "rear_wing_tip": [85, 20]},
  "render": {"nose": [10, 50], "tail": [110, 50], "rear_wing_tip": [89, 19]},
  "calibration": {"point_a": "nose", "point_b": "tail", "distance_m": 7.2}
}
```

The numbers are **illustrative only**, NOT real FORGE measurements.
Pass `--landmarks path/to/landmarks.json` to compare projected landmark
positions. On perspective views, omit the calibration block: the tool rejects
attempts to convert arbitrary perspective pixel differences into physical meters.
The known span must lie in the calibrated projected image plane.

## Strict review controls

- Compare identical camera directions, framing, perspective/orthographic settings,
  and pixel resolution. If those differ, IoU is misleading.
- Use actual model-generated clay renders and silhouette masks, not AI-generated
  replacement images.
- Keep wings, cowl, and two inboard boosters as distinct real mesh objects.
  Mesh metadata checks fail if any are missing.
- No automatic approvals. Last signed-off gate remains Gate 01; Gate 02 is in
  progress until the owner accepts the specific visual evidence.
- No texture work, game-ready GLB, or Godot import by this tooling.
- The AI depth and DINO features do not uniquely determine hidden surfaces or
  real-world dimensions. Clean Blender geometry still needs original modeling
  and a human automotive-surfacing pass.

## Suggested next pilot

Use the existing Gate 02 V12 rear and rear-three-quarter renders and the
owner's rear-cowl/rear-wing markup as the first calibrated comparison.
Quantify roof continuity, body/wing outline, wingtip placement, and paired
inner booster spacing. Transfer accepted deltas to the *existing* mesh source
only after user inspection of the real multi-view clay and preview GLB.
