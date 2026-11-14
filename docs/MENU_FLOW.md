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

## Walkaround milestone (initial implementation)
Switch **WALK THE GARAGE** from the 3D inspection toolbar. On-screen hold-to-move and turn buttons provide first-person camera walking in the rendered hangar; touch-drag rotates the view. Position is clamped to the workshop bounds and inspection platform perimeter as an interim collision barrier. This is not a player character or final physics/navmesh system. **RETURN TO INSPECTION** restores the orbiting inspection camera.

## Workshop fidelity pass: true 3D service garage

The approved workshop direction is implemented in `game/scripts/garage_workshop.gd` as runtime 3D geometry, **not an image**. The old stage and original experimental Forge GLB remain usable. The new room includes:

- Multi-ring overhead inspection gantry; warm/cool service light strips, cable rails and mechanical ceiling supports.
- Three-dimensional segmented turntable rim with vents, clamps, clamps' illuminated status strips and warning markers.
- Two instrumented servo lift towers with movable **unloaded** service support arms; separate rear service bays with spare hover-cell displays, no substitute fleet cars.
- A multi-jointed robot scanner with metallic piston links, cable, wrist scanner aperture and working light. Animated idle sweep can be toggled from the UI.
- Workshop workbenches with labeled, individually shaped tools, cabinets and drawers, diagnostic workstations, spare turbine props, shelves, rolling tool trolleys and industrial floor drains.
- Neon Foundry illuminated wall-branding, diagnostic screens, machine stations and directional workshop markings.

All static props are authored as triangles consolidated into material-specific `ArrayMesh` batches, keeping draw calls comparatively low despite rich geometry. Only the actuated service lift arms and robotic scanner are independent animated meshes. PBR materials have controlled metallic and roughness values; geometry uses emission strips but avoids expensive per-object shadowed lights. The menu is still subject to real Android visual and FPS verification.

In the garage's **SERVICE BAY / EQUIPMENT** panel, **OPERATE LIFT ARMS** toggles an unloaded lift carriage movement, while **ROBOT SCANNER / TOGGLE** powers the animated inspection head. Garage UI remains separate from other destinations.
