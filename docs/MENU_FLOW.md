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

Visual QA pass: lift/service metallic surfaces now carry deterministic, locally generated brushed PBR microtextures; the camera opens wider for a larger view of the room; workshop light balance is more neutral and the robotic arm is repositioned near the back of the turntable to keep it visible despite mobile UI overlays. This does not substitute a path-traced showroom for the live scene.

## CC0 PBR materials and provenance

`tools/stage_garage_cc0.py` downloads **1K true albedo, OpenGL normal, roughness, metallic and ambient-occlusion maps** from four verified CC0 ambientCG materials (Metal010, MetalPlates001, Metal050A and PaintedMetal010) into the build's `game/assets/garage/pbr/` staging directory, with a machine-readable `provenance.json`. These CC0 materials may be distributed in a commercial game, with credit optional; source: https://docs.ambientcg.com/license/ . The native Godot PBR shader uses real-world-scaled UVs, material normal mapping, roughness, metalness, and AO. When the asset host cannot be reached, the game still compiles using the original local fallback textures; logs explicitly report which maps were actually staged. This is build-time dependency only and does not access the network on user devices. 

## Kenney Factory Kit — curated CC0 3D meshes

The garage also stages eight **real independently modeled factory props** from Kenney Factory Kit 3.0 (machines, scanner, crane-lift, piston, gear, hanging screen and conveyor). Unlike the in-house batched workshop, these are originally authored mesh assets. `tools/stage_garage_factory_props.py` downloads only the named original OBJ, MTL, shared color-map PNG and CC0 license file from a public source mirror with retained attribution and records `provenance.json`. The Godot scene adds these only when imported assets are present; if sources cannot be reached the environment still renders. See https://kenney.nl/assets/factory-kit (license: Creative Commons CC0).

The initial real PBR capture revealed overactive dark microtexture noise on the floor. The deck's CC0 diamond/plate surface is now assigned to localized silver mechanical props while the broad floor tiles receive a cleaner CC0 aluminum material with reduced normal strength and greater roughness. This is an authored adjustment based on actual captured Godot output, not a simulated render.

A single shadow-casting hero spotlight now anchors the Forge craft and its mechanical assemblies to the illuminated turntable. All decorative work lights and emissive strips remain shadow-free to avoid multiplying GPU shadow-map costs on Android. On-device FPS should be checked with the new visible Vulkan FPS overlay.

## Runtime material correction and mobile performance
Based on Android's ~20 FPS screenshot and visible black patches on large engine components, the major PBR defect was applying ambientCG stock-material AO, metallic masks and distressed maps indiscriminately to giant procgen parts, without tangent vectors on those procedural meshes. The corrective pass disables AO/masks, applies clean metal to structural assemblies, uses distressed paint only on selected cabinets and diamond plate only on small physical treads, and calls SurfaceTool.generate_tangents() before mesh commit. The normal-map detail can now be switched between balanced (off) and detail (on), preserving the original assets. Nonessential tiny rod caps are omitted, without deleting visible props. On-device FPS must still be measured to confirm the gain.

## Android graphics profile A/B test
The garage now defaults to **Balanced**: SubViewport 3D scaling=0.72 (approximately 48% fewer 3D fragment pixels than native), one primary workshop omni plus one unshadowed task lamp, no spotlight shadow pass and no normal-map sampling on generated workshop meshes. The scene geometry, car and separately sourced CC0 workshop props are unchanged. **Graphics / Detail** enables native 3D scaling=1.0, extra accent/task lights, one shadowed key and the verified tangent-space normal maps. Both profiles are available in the equipment panel; the FPS counter stays visible during use. The comparison is deliberately user-testable rather than claiming 60 FPS without profiling on the actual Android GPU. Godot documents per-viewport render scaling and the tangents prerequisite for procedural normal maps.

## Bench surface correction, material hygiene (Android screenshot review)

The real underlying issue was an **inward-facing triangle winding order** in `_add_quad()`: it authored CCW triangles even though Godot culls CW fronts. This primarily hid top/outside faces of workbenches, cabinets, and machinery. The normals themselves were authored outward, creating a mismatch between shading and visible faces. The generator now reverses the emitted triangle and UV order while preserving outward normals; generated rod end-cap normals also match the correct faces. A headless geometry regression test checks CW top faces independently of art.

The broad chipped-metal albedo maps were also overused on cabinets. Factory floor and large powder-coated bodies now use smooth, subtly varied authored PBR finishes, and CC0 normal maps remain restricted to appropriate metallic/tread components. The worktop has a separate BENCH material, mechanical edging, and spaced fastener geometry. Keep Balanced as default for Android because user-reported garage FPS improved from ~20 to **78–90** before this bench fix.

For visual QA, Android Actions captures `NeonFoundry-WorkbenchQC.png` from a targeted in-engine viewpoint in addition to the full garage and walkaround views. Do not assume phone FPS until tested on device.

## Cinematic garage lighting — Mobile/Vulkan first pass

The garage scene now uses ACES (Godot 4.7), reduced flat ambient/directional fill and a focused, unshadowed hero spot in both modes. Godot Mobile-supported glow and depth fog are conservatively enabled, and a single lightweight shader grounds the vehicle and platform with soft radial alpha contact shadows rather than unsupported SSAO. The dedicated 3D SubViewport explicitly uses 2× MSAA and 4× anisotropic filtering (8× in Detail). The existing Balanced profile retains 0.72 render scale and no dynamic shadow maps; Detail also enables one shadowed spotlight and a box-projected UPDATE_ONCE ReflectionProbe. Probe update is not per-frame, and it is not planar floor reflection. These are rendering targets pending actual device profiling.

**LightmapGI is not yet baked.** The current room is procedurally generated without dedicated editor-baked UV2 charts; simply inserting a LightmapGI node does nothing useful. The next Blender stage must export coherent static-room meshes with UV2 and bevel/weighted normals, bake lighting in the Godot editor, and keep moving lift arms, the robotic scanner and the car outside the static bake. Do not claim GI benefits before a visible verified lightmap exists.

## Stage 01 — six-surface architectural shell, isolated for visual review

Source of truth: `tools/build_garage_shell.py` generates an editable `build/garage_shell_stage01.blend` and the corresponding embedded-PBR `game/assets/garage/shell/shell_stage01.glb`. The scene contains exactly 4 walls, 1 floor, and 1 ceiling (six mesh objects). Dimensions/coordinates match the existing Foundry Lot (~39.8 m wide, 32.3 m long, 14.7 m tall); physical panel cladding and floor/ceiling cassettes create genuine surface seams and small bevel highlights without girders or decorative machinery. Blender creates original albedo, shallow OpenGL normal, and separate physically varying roughness maps. All texture rights are original project work; no CC0 package dependency is needed for this shell.

For this **single-stage review build only**, the previous turntable, Forge vehicle, robot, lifts, props, old room and neon furniture are preserved but hidden; this is intentional so the user can inspect geometry and materials in isolation. Garage navigation and first-person walking remain available. Lighting was reset to a modest one-key, one-fill arrangement; fog, glow, live shadow maps, and repeated texture overlays are disabled. The surface GLB must be generated before Godot imports project resources in CI/Android. Mesh is intended to be reused when subsequent milestones add girders, interior walls, and equipment one at a time.

**Stage 02 is NOT implemented:** no structural girders or partitions are added here. The next construction step requires explicit visual approval of the wall, floor and ceiling material quality and FPS.

### Axis correction discovered by visual inspection

The first Vulkan screenshot exposed a Blender-to-Godot coordinate error: the floor appeared as a giant wall. The Blender generator now pre-rotates its Godot-oriented coordinates by +90° about Blender X before glTF export, compensating for Blender Z-up to Godot Y-up. Added bounding-box assertions for the six imported meshes, including the floor horizontal dimensions and ceiling Y height. The initial Build 96 is NOT approved.

### Surface-material refinement after Android visual capture

The second Android review revealed too much block-like procedural variation in Stage 01's floor/wall finishes. The generator used repeated nearest-neighbor noise cells and incomplete smoothing. It now uses continuous, smooth, periodic bilinear interpolated noise; the epoxy floor is a largely matte, neutral gray, the walls have restrained ceramic/paint grain, and the ceiling uses a subtle dark powder coat. Roughness modulation and micro-normal amplitudes were reduced, with physical panel seams left as distinct Blender geometry. No new machinery or girders were introduced.

## Stage 01 — PBR material correction based on Android 103 FPS screenshot

The user-provided Stage 01 wall screenshot showed 103 FPS but severe repetitive vertical corrugation. The culprit was a high-frequency sinusoidal striae pattern and independent local UVs on each tile. The construction geometry was sound, so the new material pass changes **only the six shell meshes' source texture data and world-space atlas UVs**, leaving every lift/girder/partition absent for this stage.

- Floor: one deterministic 2048×2048 original atlas spanning ~39.8×32.3m, with mostly matte epoxy/concrete roughness, soft glossy oil streaks, understated thruster scuffs, physically painted graphite/amber clearance stripes around the future turntable, and subtle grooves aligned to existing panel junctions. This is a paint marking, not a turntable object.
- Long walls and side walls: separate 1024 atlases with no hard-frequency vertical line pattern. Surface geometry remains broad satin-composite panels with mild color/roughness variation.
- Ceiling: independent 1024 rough powder-coated acoustic-steel atlas.
- All four surfaces: **glTF packed ORM** R=baked cavity occlusion, G=roughness, B=metallic, created offline by Blender and connected to Principled BSDF and Blender's glTF Material Output node. Panel seams, rivet dimples and subtle microroughness are **precomputed high-resolution signed height relief converted into Y+ OpenGL tangent-space normal maps**, not extra meshes or runtime displacement. This is a procedural relief-map bake, not yet a Cycles high-poly-to-low-poly mesh bake.
- UVs: contiguous atlas coordinates derived from the world-space panel positions before Blender's axis conversion, eliminating identical repeated patches on every segment.
- Performance: no additional runtime geometry, no reintroduced dynamic fog/glow/shadows, still a six-surface material review. Original shell .blend, GLB and image maps are retained for inspection.
- Export validation: `tools/validate_shell_pbr.py` inspects the binary GLB and verifies the four real albedo, packed ORM and normal materials, and ensures the AO and metallic/roughness share the exact same GLB image source.

Do not advance to girders and interior wall until this shell appearance and real phone FPS are approved.
