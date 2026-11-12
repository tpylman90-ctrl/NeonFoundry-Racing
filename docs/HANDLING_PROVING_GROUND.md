# Hover controls and flight dynamics — SceneForge proving ground

Status: **experimental / phone acceptance pending**. This document records a controller prototype, NOT approval of NF-H01 Gate 01 or permission to skip any of the 12 locked model gates.

## Source of reusable prototypes

The live testbed remains [SceneForge](https://github.com/tpylman90-ctrl/SceneForge), so Neon Foundry Racing keeps its independent project structure and approval gates.

- [game/vehicles/hover_touch_input.gd](https://github.com/tpylman90-ctrl/SceneForge/blob/main/game/vehicles/hover_touch_input.gd) — Android multi-touch decode for large left/right, thrust, brake/reverse, and boost touch zones.
- [game/vehicles/hover_motion.gd](https://github.com/tpylman90-ctrl/SceneForge/blob/main/game/vehicles/hover_motion.gd) — controlled A/B spring suspension and sideways momentum on existing SceneForge tracks. Its spline-provided deck target is a bridge experiment, not the final open-world surface detector.
- [game/vehicles/hover_rig.gd](https://github.com/tpylman90-ctrl/SceneForge/blob/main/game/vehicles/hover_rig.gd) — independent, collision-based RigidBody3D using four RayCast3D surface samples, corner-mounted spring/damper forces, upright stabilization, forward/reverse thrust, rate-limited yaw, lateral damping, and real unsupported airtime.
- [game/hover_lab.tscn](https://github.com/tpylman90-ctrl/SceneForge/blob/main/game/hover_lab.tscn) — temporary physics proving ground with asphalt, raised surface, grass-colored pad, water-colored pad, edge gap, and side barriers. The simple gray box exists only to assess handling, never as a substitute for the authored hero craft.
- [game/tests/hover_handling_test.gd](https://github.com/tpylman90-ctrl/SceneForge/blob/main/game/tests/hover_handling_test.gd) and [game/tests/hover_rigidbody_test.gd](https://github.com/tpylman90-ctrl/SceneForge/blob/main/game/tests/hover_rigidbody_test.gd) — simulation-rate, multi-touch, spring, thrust, and steering assertions. Automated checks alone do not establish Android device feel or FPS.

## Intentional baseline behavior

1. **Touch mapping:** enlarged left and right arrow zones; separate thrust; brake slows to rest and becomes reverse after a deliberate hold; boost remains a separate second-finger action. Neutral input must not create forward thrust.
2. **Steering:** screen-right should actually steer right. Reverse steering should invert its direction when backing up. Lateral velocity must carry briefly through corners, without kart-like immediate heading lock.
3. **Ground hover:** real downward samples determine whether support exists. Independent spring forces react to terrain height and body tilt. Probe contact cannot be inferred from a spline or from colored scenery.
4. **Flight:** when probes lose support, gravity resumes and lateral drift persists. Air steering is weaker, rather than pulling the racer onto an invisible course. Later powered-flight systems will need separate lift and altitude controls.
5. **Collision:** use physical hull/world collisions, low wall friction, controlled bounce-back, and anti-sticking logic. Never quietly reset the craft for a normal glancing contact.
6. **Camera:** both chase and driver-position views should convey lean, lateral momentum, height and speed without excessive camera shake.

Current **starting values**, not approved final tuning: desired hover probe clearance 1.48 m; spring 32 s⁻²; vertical damping 10 s⁻¹; surface yaw limit 1.28 rad/s; grounded lateral damping 2.9 s⁻¹; unsupported lateral damping 0.35 s⁻¹; reverse hold 0.28 s; physics at 60 Hz. A/B track suspension uses an additional gentle visible bob and modest lateral momentum retention. Normalize all behavior to seconds, not frame count.

## Phone acceptance procedure

On a SceneForge Android test APK, choose **TRACKS → HOVER PHYSICS LAB**. Drive straight, stop, reverse, then repeat with single-finger and two-finger steering + thrust. Drive onto the raised surface and across the unsupported gap. Strike a side barrier at a shallow angle and recover without sticking. Switch between chase and seat cameras. In the normal SceneForge race, choose **EVENT → HANDLING: HOVER PHYSICS / CLASSIC** and compare the original track handling with the suspension experiment.

Record: steering direction and responsiveness, coast distance, amount of sideways slip, hover bounce/oscillation, transition into unsupported air, wall contact, camera comfort, touchscreen reach, and sustained FPS/thermal behavior on Android. Failures or regressions must be corrected in the testbed and tested again before the design becomes a canonical Neon Foundry controller.

## Integration hold

**Do not place the SceneForge test-rig body, temporary level, or placeholder meshes in Neon Foundry Racing's production scenes.** NF-H01 must still pass its locked gates and the game must reach the appropriate handling/arena milestone. When approved, port the small input and physics modules behind a craft-control interface, attach the accepted craft's genuine collider/repulsor mount locations, and rerun device and CI checks. This record is architectural preparation, not gameplay implementation or a model-gate exception.
