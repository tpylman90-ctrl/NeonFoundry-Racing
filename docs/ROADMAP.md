# Milestones

| Phase | Deliverable | Status |
| --- | --- | --- |
| 0 | Professional repository, docs, Vulkan shell, CI, Android signing workflow | **Done — CI and signed Android build #1 verified** |
| 0.5 | Cinematic title, main menu, functional settings, navigation previews | **Implemented — CI and Android build #4 passed; phone review pending** |
| 1 | Walkable Foundry garage + single detailed original hovercraft | Planned |
| 2 | Inspection camera, cockpit and interactable components | Planned |
| 3 | Hover and real free-flight physics on a small proving ground | Planned |
| 4 | Event selection, first hybrid race, results and garage return | Planned |
| 5 | Ownership, upgrades, local save file and economy | Planned |
| 6 | More race courses, rivals, championships and performance polish | Planned |

A milestone is only complete after its code is merged, regression checks pass and relevant visuals and gameplay are tested on the target Android device.

## First engineering backlog

1. Create the real garage shell and walkaround camera.
2. Design one original hero craft with separately modeled body, canopy, cockpit and hover modules.
3. Develop a surface/flight controller in a controlled test arena.
4. Connect event selection, race flow and results.
5. Establish first real Android FPS/temperature benchmark before increasing visual budgets.

Do not start building several tracks or vehicles before the first end-to-end loop is demonstrated.

Foundation evidence: [source checks](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/workflows/ci.yml) and [Android build #1](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/42939925754). This does not imply gameplay or a completed garage.

Menu milestone verification: [Android build #4](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/runs/42941449060) passed, with real Godot Mobile/Vulkan captures of the title and main menu. The Garage and Race Control screens are explicit placeholders, not playable systems.

Menu V2 visual milestone: Blender-produced hero/deck/airway/city, native Godot motorsport UI, and automated Vulkan screenshots. The Android build and device review must confirm quality/performance before final approval.
