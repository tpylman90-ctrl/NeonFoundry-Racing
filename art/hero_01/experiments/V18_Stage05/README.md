# FORGE V18.05 — Rear greenhouse/body integration and lower chassis fairings

**Status:** owner-inspection-only experiment. The last approved V18.02 wide/deep frame, V18.03 hood and twin open ducts, and V18.04 canopy/seat are retained **vertex-for-vertex**. No game craft is automatically replaced.

The garage screenshot identified two visual defects: the lower space-frame protruded beyond the body, and the roof armor behind the canopy ended too early, exposing the cockpit-to-rear skeleton.

## Changes to actual 3D geometry

- **Lower and front underframe:** five thin underbody plates (not filled-in cabin blocks); layered full-height port/starboard cheek and rocker covers, three longitudinal armor segments per side, two guarded sub-intake skid pieces per side, and a tucked central nose chin.
- **Service details:** central side engine-service opening remains **real empty volume**, bounded by separate upper-belt and lower-rocker components. Independent internal ribs, conduits, and header rails remain visible.
- **Canopy to aft enclosure:** one longer faceted continuous center roof crown (Z -2.28 to -3.90 meters); separately shaped left/right shoulder armor, two independent aft haunch service covers per side, formed seams, removable access hatches, and 8 new mount/support feet to the original rear cowl hardpoints.
- **Rear face:** two shaped corner-return panels, separate lower transom, top crossmember, central service keel; keeps two empty aft engine-module apertures for the next stage.
- **All prior 557 separate meshes remain unchanged.** 140 newly created separate meshes; total 697 mesh elements, 43,444 triangles.

The rear canopy glass ends near Z=-2.26 m. New armor begins Z=-2.28 m, immediately behind it, without using a giant covering box over the glazing.

## Checks

Test source from repository root:

```bash
python -m pip install numpy==2.3.5 trimesh==4.11.1 networkx==3.6.1 scipy==1.17.0 shapely==2.1.2
NFR_BASE_GLB=art/hero_01/experiments/V18_Stage04/FORGE_V18_04_Cockpit_Assembly.glb \
NFR_OUTPUT_DIR=build/forge_v18_stage05 \
  python tools/build_forge_v18_stage05.py
python tools/check_forge_v18_stage05.py \
  --base art/hero_01/experiments/V18_Stage04/FORGE_V18_04_Cockpit_Assembly.glb \
  --model build/forge_v18_stage05/FORGE_V18_05_Body_Integration.glb \
  --out build/forge_v18_stage05/V18_05_Attachment_Audit.json
```

QA independently checks named meshes, all original vertex/face arrays, closed/winding-consistent components, proper lower fairing coverage, rear roof span, and positive geometric overlap at specific *box-to-box* chassis hardpoints. It is **not** aerodynamic, FEM, or full tolerance verification. Approval requires visual inspection in the Android garage and GLB viewer.

**Remaining work:** full twin rear thruster/booster installations, rear aerodynamic wing and tail structure, UV materials, LOD and performance profiling. Separate game integration after owner accepts the silhouette.
