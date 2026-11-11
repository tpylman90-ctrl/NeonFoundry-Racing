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
