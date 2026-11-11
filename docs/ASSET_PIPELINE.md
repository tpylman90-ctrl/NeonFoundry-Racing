# Blender to Godot production standards

## Authoring

- Save editable original Blender sources under art/ and approved GLB exports under game/assets/.
- Use 1 meter per Blender unit, intentional object origins, predictable axes, UVs, correct normals and named individual components.
- Keep parts separate when they must animate or be inspectable (doors, canopy, thrusters, cockpit controls).
- Name exports in lowercase snake_case, with optional _lod0, _lod1, _lod2 suffixes.
- Record source and license for every reference or imported asset; never ship unapproved third-party geometry.

## Two visual budgets

**Garage:** hero-quality geometry and materials, close camera, inspectable cabin/underbody.

**Race:** optimized meshes, LOD, baked material detail, instanced surroundings, bounded shadows and culling. Preserve shape quality while reducing hidden detail.

## Mandatory visual review

Front, rear, side, top, three-quarter and cockpit views for each major craft iteration. Check both neutral clay material and actual Godot Mobile/Vulkan material. Test high-speed camera visibility and see-through/back-face issues.

## Performance principles

Texture mipmaps, ETC2/ASTC-capable imports, lean material counts, conservative transparency and carefully authored collision. Do not pick a universal triangle budget before measuring the first hero craft on the target phone.

## Cinematic main menu artwork

The original main menu is authored by tools/build_menu_hero.py using Blender 4.5.3. The independent layers include a promotional hovercraft, reflective launch platform, illuminated aerial raceways, and modeled city geometry. In CI Blender Cycles renders a 1600 x 900 background PNG at game/assets/menu/launch_scene.png, alongside a source menu_hero.blend in the build artifact. The PNG is cached by Blender-script hash, imported into Godot, and composited as a single inexpensive background texture. Native Godot controls, settings, and animated telemetry run with Mobile/Vulkan. This is real authored/engine-rendered game presentation, not a static visual mockup.

A source checkout without the Blender output shows a procedural fallback; to reproduce the final graphics locally, run Blender 4.5.3 with tools/build_menu_hero.py before Godot import. This promotional hovercraft is not yet the production garage craft.
