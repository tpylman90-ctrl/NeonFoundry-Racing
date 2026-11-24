# Neon Foundry Racing — Production Standard

**Status:** Adopted by project owner on 2026-11-23. This is the default method for future **production-quality** assets, scenes and releases in Neon Foundry Racing. It applies to the Unity 6 development lane and adapts to any retained Godot work. Amend this standard explicitly; do not bypass it silently.

**Directive:** A successful APK only proves that a project compiled and launched. It does **not** prove an asset is production-quality, visually approved, optimally rendered, or performance-validated.

## 1. Product and platform constraints

- **Experience:** Premium futuristic hover-racing game with owned and inspectable craft, an immersive walkable garage, upgrade/battery works, conventional/hybrid races, and genuine free-flight courses.
- **Production tools:** Blender for high- and low-poly authored 3D assets; Unity 6 Universal Render Pipeline (URP) for the current Android game lane. Preserve the original Godot lane rather than modifying it opportunistically.
- **Android-first:** ARM64, Vulkan where supported, OpenGLES3 fallback; real-device testing controls performance approval.
- **Cost and provenance:** Prefer free tools and legal original/CC0 content. Log origin, creator, link, authoring tool/version and license for all sourced content. Never assume a public download grants reuse rights. No paid tools or content without owner approval.
- **Never replace authored geometry with an AI image.** Concept art is a reference, not evidence of the actual built mesh.

## 2. Two distinct rendering budgets

### Garage, inspection and cinematic presentation

Designed for near-field scrutiny. Prioritize hero-grade surface continuity, visible mechanical attachment and negative space, accessible cockpits/underbody, carefully placed highlight reflections, credible PBR materials, baked static architectural lighting, Light Probes and Reflection Probes. Use limited dynamic lights and effects where genuinely interactive. Static room assets should be individually reviewable, not arbitrary primitive clutter.

### Races, tracks, city and landscape

Designed for rapid movement and broad visibility. Prioritize silhouettes, authored roads/bridges/terrain/buildings, distance-detail tiers, culling, LODs, texture streaming, batching by spatial cell and lighting budgets. Near trackside buildings have credible facades/roofs; distant skyline assets can be lightweight. Airborne flight must use real physical forces and controllable altitude—not hidden road surfaces or scripted height.

Garage and race assets may derive from a common master but need separate inspection/render budgets and LOD selection.

## 3. Mandatory production gates

Complete the gate in sequence for each **production** asset or scene. **Blocked** or **needs revision** means do not mark it complete or advance. A technical experiment may bypass these gates only if clearly labeled `EXPERIMENT / NON-PRODUCTION` and never silently promoted to production.

| Gate | Required work | Acceptance evidence |
| --- | --- | --- |
| **01 — Art direction and engineering brief** | Define purpose, dimensions, scale, silhouettes, mechanisms, component boundaries, reference rights, desired material language and integration needs | Approved brief, orthographic/multi-view references, constraints and version |
| **02 — High-poly master** | Author real form with appropriate topology, clean shading, controlled bevels, panel seams, genuine recesses, structural supports, mechanical logic; save editable source | `.blend`, clay + wireframe front/rear/left/right/top/bottom/3/4 and detailed close-ups as applicable |
| **03 — Optimized game mesh** | Retopologize or simplify while preserving silhouette; separate animating/inspectable pieces; build suitable LODs, UV sets, pivots and simple colliders | High-poly vs low-poly renders, UV/LOD audit, triangle/material counts and rationale |
| **04 — PBR and texture baking** | Bake high-poly details to low-poly tangent-space normals/AO; author base color, metallic, roughness and masks; validate texel density, tangent space, material response and legal sources | Texture maps and manifest, lit comparisons and close-ups, identified channel packing |
| **05 — Studio and engine visual validation** | Review in a controlled Blender studio, then in a matched Unity URP inspection scene with reflections and deliberate lighting | Same-angle side-by-side clay/wire/beauty/engine captures; no obvious shape, shading or material mismatch |
| **06 — Runtime integration** | Make prefabs, collision, LODGroups, interactive pivots, light/reflection probes, culling cells and scene loading behavior | Playable/interactable scene, functional checklist, no major intersections or broken navigation |
| **07 — Android performance and owner approval** | Build native APK with CI, test representative views and thermal duration on actual hardware; revise if budget exceeded | Verifiable APK/build URL, device, settings, CPU/GPU frame times, FPS distribution, memory, draw calls, visual screenshots, owner decision |

**Approval rule:** For hero vehicles, named rooms and other important visual assets, require explicit owner acceptance of the evidence before declaring a visual gate complete. Do not infer acceptance from “the script ran,” “APK opens,” a concept illustration, or technical CI success. Record decision as `APPROVED`, `NEEDS_REVISION`, or `BLOCKED`, with date and evidence URLs.

### Existing hero-craft precedence

`docs/HERO_CRAFT_BUILD_ORDER.md` defines a **locked twelve-gate sequence** for `NF-H01`; it remains authoritative and must not be reordered or overridden by this general seven-gate standard. Apply this document's topology, PBR, studio and Android acceptance criteria **inside the matching existing hero gates**, not in lieu of them. The hero status record `art/hero_01/progress.json` continues as the source of truth.

## 4. Asset modeling quality bar

- Establish scale in meters and correct forward/up axes; prove shape at front/rear/side/top/underside and three-quarter views before adding detail.
- Automotive forms use measured cross-sections, clean panel transitions and deliberate curvature; avoid primitive-stacking, unsupported “floating” armor, rubbery/inflated metal edges and unintentional self-intersections.
- All vents, intakes, thrusters, hover pods and robotic joints must read as engineered assemblies: outer shell → attachment/clearance → recessed mechanism → fasteners/seals → functional center.
- Use subdivision and support topology only where appropriate; hard-surface bevels/weighted normals must have predictable shading after export.
- Preserve original `.blend` files and separate mechanical components with logical pivots and names.
- Keep separate high-poly, low-poly, LOD, and collision representations; no automatic destructive joining of editable masters.
- Preserve actual-model inspection and comparison renders for review. Use images only as concept references, never as substitute for mesh evidence.

## 5. Materials, lighting and texture standards

- Physically motivated finish categories: painted bodywork, anodized or brushed steel/aluminum, carbon, rubber, tinted glazing, lens covers, ceramic/heat-stained thrusters, energy-cassette ceramics.
- Author PBR variation at appropriate scale. Small shared color textures alone are **layout/prototype** quality; they do not satisfy production material review.
- Bake/reproject fine master geometry to appropriate normal/AO detail maps before game export; support independent metallic/roughness review.
- **Unity URP channel mapping matters:** the default URP Lit metallic workflow expects metallic in the metallic map's R and smoothness (1 - roughness) commonly in its A; AO is assigned through the occlusion map. Do not blindly assign an ORM map directly and assume it renders correctly. Validate importer settings and normal-map type.
- Use baked lighting for mostly static garage architecture; use Light Probes for moving objects and Reflection Probes for glossy vehicles; restrict real-time light/shadow passes on Android.
- Provide controlled studio turntables under neutral key/fill/rim lighting as well as the in-scene environment. Verify glass readability, metal reflections, panel-line thickness, highlight continuity and bloom restraint.
- For Android, use appropriate ASTC compression on supported devices, mipmaps, resolution tiers, and measure memory use. Free CC0 libraries such as Poly Haven/ambientCG are permitted only with source recording.

## 6. Unity scene and optimization rules

- **Spatial batching, not a monolithic garage mesh.** Partition the hangar into logical render/culling cells: craft bay, battery works, overhead shell, side walls, observation deck and stores. A giant joined mesh sharing one material can prevent per-area culling.
- Prefer reused meshes, deliberate submesh/material limits, instancing or SRP Batcher-friendly materials where applicable, and LODGroups for changing distance.
- Separate heavy static world geometry from animating/interactable pieces. Keep collision primitives simpler than display meshes.
- Measure overdraw, transparency, shadow cascades, postprocess bandwidth, shader variants and texture memory. Do not raise budgets by guesswork.
- Use controlled scene transitions/loading and asset lifetime. Evaluate Addressables when scene/asset volume justifies it; do not add it simply for appearance.
- Race tracks use modular building/road kits, horizon silhouettes and authored Blender terrain; validate both low camera and aerial perspectives.
- Maintain Vulkan/OpenGLES3 compatibility and test quality tiers on real devices.

## 7. Performance acceptance

The **primary target** is sustained **60 FPS** (16.67 ms total frame time) on a designated Android target, with **12–14 ms provisional CPU/GPU working headroom** where practicable. A stable **30 FPS quality fallback** is allowed for slower phones. These are **goals**, not verified current capability.

For every substantive performance claim, capture:
1. Device model, OS, graphics API, resolution/render scale, quality tier, build SHA and test scene.
2. Warm-device and sustained-run FPS/framerate consistency (not just one instantaneous on-screen counter).
3. CPU main/render-thread and GPU frame time, draw calls, triangles, memory/texture footprint, loading/stutter events and thermal behavior where tooling permits.
4. Screenshots or recordings of representative near/far views and each major quality tier.
5. Explicit `PASS`, `REVISE` or `BLOCKED` conclusion and the next corrective action.

Do not set a universal polygon count, texture size, or draw-call ceiling without a measured device benchmark.

## 8. Review packages and release labeling

Every reviewed deliverable should include:
- Asset ID/version; purpose; origin/license; editable Blender source link.
- Actual-model multi-view clay, wireframe, beauty and focused mechanical close-ups.
- Game mesh GLB/FBX and component/LOD/UV/collider metadata where applicable.
- Maps + URP import/channel manifest, alongside controlled Blender vs Unity comparisons.
- Validation checklist with gate decisions; device profile record at Android gate.
- Reproducible build workflow URL and **direct APK release** link when an APK is approved.

Label pre-production material `BLOCKOUT`, `PROTOTYPE`, `PREVIEW`, or `EXPERIMENT`. Do **not** label it `PRODUCTION` or `AAA FINISHED` without completing relevant gates.

## 9. Initial calibrated vertical slice

1. **Do not fill the garage with more placeholder geometry as a substitute for quality.**
2. Choose **one robot-assisted battery exchange workstation** as the quality benchmark.
3. Finish its engineering brief → high-poly → optimized/UV/LOD → PBR bake → studio/Unity comparison → Android device review.
4. After its visual and technical acceptance, establish reusable materials, robot-joint components, lighting fixtures and layout standards from that approved asset.
5. Extend those standards to the battery room, then garage, then a short racing environment and finally a full circuit.

Treat all existing Unity garage R1/R2 builds as **preview baselines** until reviewed under this standard. They remain useful for layout and perf regression comparisons, not proof of art completion.

## 10. Change control / responsibilities

- For each new production task, begin by identifying the **asset/scene, current gate, required evidence and expected deliverable**.
- A changed asset cannot jump ahead because a render looks attractive; technical work may progress only within accepted gate boundaries.
- Store evidence and versioned review records under an asset-specific folder, using `docs/ASSET_REVIEW_TEMPLATE.md` as the starting form.
- Scope changes that impact previously accepted shape, scale or engineering must reopen the affected gate.
- Changes to this standard require a user decision and a documented revision, including why. Do not make silent exceptions.
- CI enforces syntax, file presence and build reproducibility when implemented; **only the owner** can approve visual design and device experience.

### Technical references

- Unity 6 URP performance and material workflow documentation: https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/index.html
- Unity optimizing graphics/Draw calls and culling: https://docs.unity3d.com/Manual/optimizing-graphics-performance.html
- Unity texture import/compression: https://docs.unity3d.com/Manual/class-TextureImporter.html
- Blender baking documentation: https://docs.blender.org/manual/en/latest/render/cycles/baking.html
- Android games performance guidance: https://developer.android.com/games/optimize
- Poly Haven CC0: https://polyhaven.com/license
- ambientCG license: https://ambientcg.com/license

**Guiding standard:** Design → Model → Inspect → Optimize → Bake → Integrate → Profile → Approve. Never skip from rough geometry straight to “finished game asset.”
