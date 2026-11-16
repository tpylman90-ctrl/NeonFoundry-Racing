# Forge V24: Neural rendering vs. extracted 3D mesh

- **Run:** https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/43801989875
- **Source:** Original Forge V23, 11 meshes, 884 triangles; unchanged.
- **TripoSR:** Official weights, native torchmcubes, 256 density grid, CPU-only.
- **Inputs:** Same-camera flat V23 reference and facet-contrast-enhanced version.
- **Outputs:** Four genuine neural renders per input; thresholds 15, 20, 25, 30, 35; 10 GLBs.
- **Texturing:** Both 512px neural bake attempts failed with `(standalone) XOpenDisplay: cannot open display`; no valid UV texture generated.

## Findings

1. The native neural-render previews are visibly smoother and retain a recognizable silhouette and cockpit. The threshold-25 mesh renders at the matching camera angle are much more rippled and uneven.
2. Threshold sweep made very little difference within each input. Flat meshes ranged from 108,800 to 108,972 triangles. Enhanced meshes ranged from 117,920 to 118,156 triangles.
3. A surface-sampling geometric comparison (2,600 samples per mesh, 48 orientation/axis variations, normalized to the V23 8.4m length) gave **approximately 0.486m Chamfer-type bidirectional nearest-surface distance** for the best enhanced threshold-15 model and **approximately 0.486m** for the best flat threshold-30 model. Previous V23 AI baseline reported ~0.474m using a different sampling count, so these differences are not evidence of improved geometry.
4. Mild Taubin smoothing on enhanced threshold 15 (2, 5, 10, 18 iterations) did not improve measured fit, and should not be mistaken for detail recovery.
5. Best enhanced output still distorts Forge's width/height proportions and fuses independent components.

## Next technical decision

Use the neural renderer as a visual guide; do not promote its exported geometry. For higher-quality GLBs, investigate *surface reconstruction* (density field regularization, resampling/smoothing aware of isosurface and sharp boundaries) rather than another arbitrary resolution increase. Texture baking requires a working EGL/Xvfb OpenGL context. Retain the **original editable V23** as the modeling foundation.

**Status:** Benchmark completed; source GLB and production craft untouched.
