# Neon Foundry Racing — menu navigation framework

This is an **interactive UI skeleton**, not a production racing gameplay loop. Existing Blender title art, menu art fallback, and offline device settings are retained.

## Route map

- Title / splash -> Main Hub.
- Hub -> Garage -> Craft Select, Tuning, Appearance. Garage -> Race Mode quick jump.
- Hub -> Dealership -> Vehicles, Parts, Currency Bundles, Featured. All checkout disabled.
- Hub -> Driver Profile -> Controls/Assists, Audio/Graphics (existing device settings), Stats/Achievements.
- Hub -> Race Control -> Mode (Surface / Hybrid / Aerial) -> compatible Track -> Pre-race Lobby -> Loading -> In-Race HUD Demo -> Results -> Restart/Next Event/Hub.
- Lobby -> Garage quick jump, Track select back navigation.
- Race demo -> Pause (Resume, Restart Demo, Quit).
- Android hardware Back and Escape traverse navigation history; menus are touch-sized.

## Prototype vs. actual game data

- The NF-H01 test mule is **only a UI placeholder**; it does not import or substitute for the still-pending approved 3D craft.
- Neon Cross, Crimson Serpent, and Skyfall Run are **named track entries**, not loaded racing levels. Mode compatibility tags are planning metadata.
- Eligibility text is not a class validator until real craft specs and event rules exist. Lobby launch is labeled UI FLOW DEMO.
- Loading is a short **interface transition**, not asset preloading.
- Speed/Lap/Boost/HUD values and results are intentionally nonfunctional; XP and credits remain +0 and **never mutate a save**.
- No purchases, network calls, analytics, or payment integrations.
- Shared section screen is in `game/scripts/flow_screen.gd`, kept separate from `title_menu.gd`.

## Acceptance

`game/tests/menu_smoke_test.gd` exercises the title, hub, device settings, garage, store, profile, mode, tracks, lobby, loading, race-demo, pause, results, and return-to-menu sequence. Godot 4.5.1 headless import/startup and this smoke script run in CI. The actual Android Vulkan device review remains required.

Automated Android workflow screenshots now include garage, store, mode selection, lobby, and results alongside the title, hub, and settings. They are generated through Godot Mobile/Vulkan under software Vulkan CI, not concept-art mockups.
