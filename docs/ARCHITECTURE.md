# Architecture — future system boundaries

## Technical baseline

Godot 4.5.1 stable, GDScript, Mobile/Vulkan, Android ARM64, landscape orientation, 60 physics ticks per second. Blender sources export glTF/GLB. CI checks correctness, not actual phone GPU performance.

## System modules (not yet implemented)

| System | Responsibility |
| --- | --- |
| App shell | Scene transitions, loading, options and save versioning |
| Garage | Walkable showroom, owned craft slots, active craft |
| Inspection | Close exterior/cockpit viewing and independently articulated parts |
| Craft data | Versioned resource specifications, upgrades and cosmetic variants |
| Craft controller | Hover physics, 6-DoF flight interfaces, collision, assists and camera |
| Race control | Event discipline, selected track, craft eligibility, difficulty |
| Course runtime | Real surfaces, terrain, obstacles, flight gates, checkpoints |
| Economy | Rewards, purchases, upgrades and persistent garage ownership |
| Quality manager | LOD, material budgets, culling, resolution scaling and device tests |

Never combine all systems into one race-scene script. Use small reusable scenes and typed resources.

## Physics requirements

A hovercraft has grounded and airborne operating modes, with deliberate transitions. Ground hover uses distance-to-surface, stabilization and bank; flight uses lift, thrust, speed-dependent forces, pitch/yaw, controllable altitude and recovery. Assists may exist but must not secretly attach the craft to a phantom road.

## Visual standards

Garage craft can use closer-detail geometry; race craft must have a lower-cost LOD family. Prioritize clear normals and correct face winding, compressed textures with mipmaps, few transparent layers, instancing and distance culling. Measure frame pacing on a real Android phone. Vulkan is an API, not a guarantee of realism.

## Planned directory extensions

Under game/, introduce modules named garage, craft, race, courses, progression and ui as features are approved. Keep Blender source assets under art/ and authored runtime exports under game/assets/.

No networking or personal analytics in the foundation; privacy-sensitive features need explicit review.
