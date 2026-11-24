# Neon Foundry Racing — Asset/Scene Review Record (Template)

Copy this file to `art/reviews/<asset_id>/<version>/review.md` (or an equivalent scene-specific location). Complete it for every **production** asset or environment. The governing workflow is [PRODUCTION_STANDARD](PRODUCTION_STANDARD.md); NF-H01's locked [twelve-gate build order](HERO_CRAFT_BUILD_ORDER.md) takes precedence.

## Identity and accountability

- **Asset/scene ID:**
- **Human-readable name:**
- **Version / git commit:**
- **Category:** Craft / interactive equipment / architecture / environment / character / track
- **Status:** BLOCKOUT / EXPERIMENT / PREVIEW / PRODUCTION CANDIDATE / PRODUCTION APPROVED
- **Target use:** Garage-close / garage-background / race-close / race-distant / other
- **Blender source:** 
- **Reference and asset provenance:** URL, author, license (or wholly original)
- **Unity prefab/scene or game export:** 
- **Review owner and date:**
- **Changes since prior version:**

## Gate ledger

Use `NOT_STARTED`, `IN_PROGRESS`, `NEEDS_REVISION`, `BLOCKED` or `APPROVED` and provide the actual evidence location. Only owner acceptance can certify a visual gate.

| Gate | Status | Evidence URLs / local paths | Owner decision/date |
| --- | --- | --- | --- |
| 01 Engineering/visual brief | NOT_STARTED | | |
| 02 High-poly master | NOT_STARTED | | |
| 03 Optimized game mesh/LOD/UV | NOT_STARTED | | |
| 04 PBR + baking | NOT_STARTED | | |
| 05 Blender-vs-Unity visual comparison | NOT_STARTED | | |
| 06 Runtime prefab and interaction | NOT_STARTED | | |
| 07 Android perf and owner approval | NOT_STARTED | | |

## Evidence checklist

- [ ] Dimensioned front/side/top references and original mechanical design brief
- [ ] Saved `.blend` master with named editable parts, valid pivots and transforms
- [ ] Actual-model orthographic and 3/4 clay renders
- [ ] Actual-model wireframe and detailed mechanism/negative-space views
- [ ] No unintentional intersections, clipping, shaded wrinkles or unsupported assemblies
- [ ] Retopologized game mesh, clear material slots, correct normals and UV layout
- [ ] Visual silhouette comparison: high-poly vs game mesh/LODs
- [ ] High-to-low normal/AO bake validation; tangent-space and seams checked
- [ ] Metallic/roughness/smoothness packing documented for Unity URP
- [ ] Studio beauty render and matching Unity in-engine screenshot
- [ ] Baked/probe lighting, materials and reflections validated on the target presentation camera
- [ ] Spatial culling, LOD, static/interactive separation, and sensible colliders checked
- [ ] APK generated and verified, with build/run/release URL
- [ ] Real Android device tested for quality and sustained frame pacing
- [ ] Explicit owner approval recorded for applicable gates

## Optimization and technical audit

| Measurement | LOD0 | LOD1 | LOD2 | Notes |
| --- | ---: | ---: | ---: | --- |
| Triangles | TBD | TBD | TBD | |
| Vertices | TBD | TBD | TBD | |
| Renderer/material slots | TBD | TBD | TBD | |
| Texture resolution/memory | TBD | TBD | TBD | |
| Collision primitives | TBD | TBD | TBD | |

- **UV/lightmap strategy:**
- **Material map convention:** For URP Lit, identify base map, normal map, metallic channel, smoothness alpha, AO map, and emission.
- **Compression/mipmap settings:**
- **Render scale and quality level:**
- **Draw calls/overdraw notes:**

## Android device evidence (Gate 07)

- **Phone/SoC and Android version:**
- **APK/release URL / commit SHA:**
- **Scene and inspection route:**
- **Graphics API / quality level / render resolution:**
- **Cold-start and loading behavior:**
- **Warm-device runtime length:**
- **Median/p95 FPS or frame-time distribution:**
- **CPU main/render thread ms:**
- **GPU frame ms:**
- **RAM/texture usage:**
- **Draw calls / triangles:**
- **Thermal stability:**
- **Screenshot/video evidence:**
- **Result:** PASS / REVISE / BLOCKED
- **Remaining issues and next action:**

## Owner verdict

- **Decision:** APPROVED / NEEDS_REVISION / BLOCKED
- **Decision date:**
- **Approved gate:**
- **Evidence considered:**
- **Required corrections:**

> Do not fill undecided metrics with invented numbers. A passed CI check is not an owner-signed visual approval. An “approved” status must point to a real review decision.
