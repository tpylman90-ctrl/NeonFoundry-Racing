# NEON FOUNDRY RACING

**Own the craft. Know the machine. Race beyond the road.**

An original, Android-first hover-racing game built in **Godot 4.5.1 (Mobile / Vulkan)** with 3D assets authored in **Blender**. The long-term vision combines detailed vehicle ownership and walkaround inspection with motorsport-inspired progression and circuits that expand from conventional roads into true three-dimensional flight.

> **Status: FOUNDATION / PRE-PRODUCTION.** This repository contains a technical starting point, documentation, and build infrastructure—not a finished game, vehicle roster, or playable race.

[![Repository checks](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/workflows/ci.yml/badge.svg)](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/workflows/ci.yml)
[![Android build](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/workflows/android.yml/badge.svg)](https://github.com/tpylman90-ctrl/NeonFoundry-Racing/actions/workflows/android.yml)

## Game vision

| Pillar | Experience |
| --- | --- |
| **The Foundry** | A navigable garage with owned craft, up-close inspection, cockpit access, and a dedicated upgrade area |
| **Craft ownership** | Earn or purchase original craft; choose, personalize, maintain, and upgrade them |
| **Race control** | Select a racing discipline, track, and event; return to the garage afterward |
| **Three-dimensional racing** | A deliberately designed blend of conventional, hybrid, and aerial courses |
| **Android-first fidelity** | Strong vehicle silhouettes, readable scenery, and stable frame pacing on actual phones |

We aim for the *ownership and inspection depth* associated with premium racing games—not a copy of their vehicles, art, interfaces, or assets.

## Technology

- **Engine:** Godot **4.5.1 stable**, GDScript, Mobile renderer with the **Vulkan** driver.
- **Art:** Blender, with glTF 2.0 / GLB exports and preserved source \`.blend\` files.
- **Target:** Android / ARM64; desktop preview for development.
- **CI:** GitHub Actions for source validation, Godot smoke tests, and signed Android builds.
- **Cost policy:** free-to-use tooling; no paid asset, cloud-render, or proprietary dependency required for development.

## Getting started

1. Install [Godot 4.5.1](https://godotengine.org/download/archive/4.5.1-stable/) and Blender.
2. Open **\`game/project.godot\`** in Godot.
3. Run the **title screen and main menu**. They include working navigation, local audio/visual preferences and marked previews for future Garage and Race Control systems. They are **not** playable gameplay.
4. Review [PROJECT_BRIEF](docs/PROJECT_BRIEF.md), [ARCHITECTURE](docs/ARCHITECTURE.md) and [ROADMAP](docs/ROADMAP.md) before developing systems.
5. Use [BUILD_AND_SIGNING](docs/BUILD_AND_SIGNING.md) for Android CI and release signing.

**Important:** Only the Android **release workflow** uses GitHub signing secrets. Never store keys, password files, or signing ZIPs in the repository.

## Repository map

\`\`\`text
game/                   Godot project, startup scene, future game systems
art/                    Blender source models and asset-authoring conventions
docs/                   Game brief, systems architecture, roadmap, asset pipeline
tools/                  Local and CI validation utilities
.github/workflows/      Automated project checks and Android APK build
.github/ISSUE_TEMPLATE/ Structured development and bug reports
\`\`\`

## Working principles

- **No hidden road masquerading as flight.** The vehicle flight model must eventually support actual altitude, momentum, and controllable recovery.
- **Garage detail and race detail are different budgets.** Garage craft may be high fidelity; race assets need LODs and visibility limits.
- **Validate on a physical Android device.** CI's software rendering is a correctness check, not a phone FPS benchmark.
- **No unverified claims.** Separate implemented, tested, planned, and blocked milestones.
- **Protect release credentials.** The signing keystore remains external to this public repository.
- **Original work only.** Reference other games for quality and interaction, not for proprietary meshes or copied art.

## Project management

Start with the [roadmap](docs/ROADMAP.md). **The first hero craft has a [locked twelve-gate implementation order](docs/HERO_CRAFT_BUILD_ORDER.md)** with explicit visual user approval at each stage. Its authoritative progress record is [NF-H01 progress](art/hero_01/progress.json); an automated validator checks sequencing in CI. Use the [issue templates](.github/ISSUE_TEMPLATE) to scope other work. Every pull request should include the test evidence and screenshots where relevant.

**Licensing:** No code or asset license has been selected yet. Public visibility is not an open-source license; obtain the repository owner's decision before distributing or reusing project content.

---

**Current milestone:** Title/main menu vertical slice, then first detailed hovercraft + walkaround garage.

## Cinematic menu production

The V2 title/main menu is a real Godot UI composited over an original Blender Cycles 3D presentation scene. See docs/ASSET_PIPELINE.md and tools/build_menu_hero.py; the edited Blender source, screenshots and Android installer are generated by the build workflow, not committed as large binary assets. Garage and race gameplay remain unimplemented.
