# Full-screen destination architecture — Neon Foundry Racing

The initial shared left-panel/tab-like navigation has been replaced by distinct Godot scenes:

- `game/scenes/garage.tscn` — **3D Foundry Lot**. Dedicated viewport, modeled hangar, illuminated turntable, camera orbit/zoom and front/side/top presets. An experimental original Forge GLB is staged into `game/assets/garage/forge_preview.glb` at build time from `art/hero_01/experiments/V18_Stage04/`. It is **not** the production-approved craft.
- `game/scenes/dealership.tscn` — full-screen showroom layout and disabled transaction/catalog placeholders.
- `game/scenes/driver_profile.tscn` — full-screen driver terminal, control configuration/planned achievements.
- `game/scenes/race_control.tscn` — mode -> track -> lobby -> loading -> HUD demo -> pause -> results. Stylized course display, not gameplay.
- `game/scenes/title_menu.tscn` — cinematic splash/hub/settings shell, routes between independent destinations and releases prior scene on exit.

All destination scenes use full-screen camera/backdrops rather than translucent tabs superimposed on the title art. The three 2D destinations reuse a renderer/controller in `flow_screen.gd` but are independently instantiated scenes with different stage graphics from `page_backdrop.gd`.

## Garage controls
- Drag across the **unobstructed 3D viewport** to rotate the camera on Android or mouse desktop.
- Use dedicated **3/4**, **SIDE**, and **TOP** camera presets and **ZOOM** controls.
- Inspector, craft select, performance/tuning and cosmetic buttons display state-specific diagnostics in the hangar. Functional vehicle physics, upgrade parameters, purchases, cosmetics and official fleet selection remain future milestones.
- **MAIN HUB**, **RESET VIEW** and **RACE CONTROL** are accessible without exiting the 3D scene via small tabs.

## Source-to-runtime vehicle staging
Run `python3 tools/stage_garage_preview.py` before first Godot import if developing locally. CI and Android build workflows perform the staging automatically. The source asset is original to this repository, without a new paid dependency. If staging is absent, the 3D garage still opens, displaying an empty turntable labeled awaiting craft.

## Acceptance
Godot 4.5.1 import/startup and smoke validation cover each destination, garage viewport/camera controls, device settings, race UI sequence, and return to hub. Android build captures title, hub, settings, garage, dealership, mode, lobby and results for Vulkan device review.
