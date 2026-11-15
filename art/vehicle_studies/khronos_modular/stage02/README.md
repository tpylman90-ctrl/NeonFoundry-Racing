# NFR Khronos candidate C — Stage 02: fitted aero and engine modules

**STATUS:** actual separate GLB geometry, *for visual inspection*, not integrated into the active garage or race physics. The donor body remains intact and its original 82 named meshes remain unmodified. Commercial credit obligations remain: [KhronosGroup/glTF-Sample-Assets: CarConcept](https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/CarConcept) **CC BY 4.0**; excluded trademarks/logos are not reused. All new engine/fin geometry in this experiment is newly authored.

## Replaces prototype accessories without replacing sculpted car

- **Front-quarter fins:** new independent `front_quarter_fins` slot, mounted on the donor's measured front shoulder (x ±1.03, Y ~0.86 m, Z ~1.30 m), above the forward hover wheelhouse. Street: a low flush wing; Aero: main swept canard plus smaller split blade; Industrial: wide hard-surface wing with upright fence. Both sides have gasketed root shoes and visible mechanical fasteners; Aero/Industrial have distinct load braces.
- **Rear stabilizers:** each fin is raked/swept to follow tail surfaces with a physical pedestal, bolted attachment, load brace, and variants featuring separate horizontal vanes. Replaces prior planar vertical slabs.
- **Four removable rocket cassettes:** Foundry Pulse, Vortex Twin, Titan Vector, Nova Overdrive. Each uses the **unchanged** `rear_engine` socket, independent cradle, paired machined nozzles with *real hollow throats* and inside walls, structural support rails, stepped heat collars, exposed heat channels, exterior armor and model-specific detailing. Nova adds two smaller upper boosters. The sizes and hardware diverge across tiers.
- **No donor paint/body modifications.** The stage is a modular bolt-on engineering study. Existing large rear wheel openings still require proper mesh retopology; closing them with a flat patch would repeat the original mistake.

## Files

- `preview_street_stage02.glb`, `preview_aero_stage02.glb`, `preview_industrial_stage02.glb` are complete inspection assemblies, preserving the established donor base and existing lift/splitter/intake/side-skirt prototypes and **replacing** only engine, tail fin and adding front-quarter fins.
- `quarter_fins_0..2.glb`, `fins_0..2_v2.glb`, and `engine_{stock,vortex,titan,nova}_v2.glb` are **10 independent physical module GLBs**, not combined body variants.
- `module_manifest_stage02.json` is a **second** rig manifest with 10 slots. It does not replace `module_manifest.json`. The original garage, tests and game remain unchanged until visual acceptance.
- `STAGE02_REPORT.json` records part/triangle counts.

## Reproduce

```bash
python -m pip install numpy trimesh scipy networkx Pillow
python tools/build_khronos_stage02.py \
  --root game/assets/vehicle_modular \
  --previews game/assets/vehicle_modular \
  --output build/khronos_stage02
```

Then stage all new module GLBs and `module_manifest_stage02.json` under `game/assets/vehicle_modular/` to run the native Godot test `game/tests/modular_vehicle_stage02_smoke_test.gd`. The new GLBs have physically closed, watertight geometry. A confirmed Android viewer visual acceptance and full mobile LOD optimization remain pending.

## Next acceptance gate

Check actual front three-quarter and rear views of all variants for root contact, clearance to the front lift housings, exhaust coverage, tail rake, and body silhouette. The build is **not yet a finished design**; no claims of real aerodynamic engineering or physics balancing.
