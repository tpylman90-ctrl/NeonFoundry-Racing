# Foundry Lot — proposed functional floor plan

**Reference:** User-provided "Futuristic Hover & Assembly Garage — Site Layout" blueprint in the November 2026 project discussion.

**Status:** Planning reference only. No room geometry, textures, object positions, or stage-number commitments are changed by this document.

Stage 01 has been enlarged from 39.8 × 32.3 m to **54.0 m X (width) × 44.0 m Z (depth)**, with a **16.2 m ceiling** to make room for three full-size hovercar lifts, assembly machinery and separate visitor/showroom paths. The six mesh objects and original roughness/ORM materials remain; preserve them. The blueprint is a conceptual placement/zoning suggestion, NOT verified to scale.

## Proposed activity zones (viewed from above)

| Zone | Blueprint location | Function |
|---|---|---|
| Robotic lift bays | Back-left | Three magnetic levitation lift stations and articulating service arms |
| Automated assembly | Back-middle | Heavy robotic welding, gantries and modular 3D fabrication |
| AI control / HQ | Back-right | Control center, monitoring and operator workstations |
| Diagnostics & re-power | Front-left | Holographic diagnostic station, swappable power-cell racks |
| Tool repositories | Front-middle | Automated parts dispensers, storage, mobile carts |
| Rotating showroom | Front-right | Hovercraft showcase, circular viewing platform, customer inspection |
| Vehicle ingress / egress | Front central access | Hangar doors, arrival lane, controlled traffic flow |
| Visitor observation | Along right / showroom edge | Screens and safe viewing positions |

## Coordinate convention for future work

- Godot X increases to the right; Z increases toward the visitor/front side.
- Back boundary Z = -23.75 m, front Z = +20.25 m.
- Left boundary X = -27.0 m, right X = +27.0 m.
- Zones above are **relative areas**, not locked object coordinates.
- The existing show platform currently uses a central layout. The blueprint suggests moving it to front-right; **do not relocate** or remove it without a subsequent approved layout stage.

## Controlled order

1. **Current** — approve the walls, floor, ceiling, PBR/ORM and stable walkaround controls.
2. **Future** — place structural girders, ceiling framework, and controlled wall separations.
3. **Future** — establish the internal zone boundaries and functional paths.
4. **Future** — add equipment one bay at a time; verify visibility, lighting and Android FPS between additions.

The previously modeled workshop remains a source of reusable equipment assets, not an instruction to bring everything back at once.

## Stage 01 controlled footprint expansion — November 2026

The user's Stage 01 screenshot showed approximately **99 FPS** with two-thumb controls and approved the shell materials, but raised a valid clearance concern with the proposed three-bay/assembly/HQ/showroom layout. In response the shell is expanded symmetrically (X: ±27 m, Z center preserved at -1.75 m). The height increases 1.5 m for overhead cranes. Internal objects, girders and partitions remain hidden and are NOT added.

- Three 8.4 m-long Forge-sized craft can fit with side access in the back-left; back-middle assembly and back-right HQ occupy the remaining width.
- Reuse the existing two-joystick Android UI, original material composition and central hazard-ring painting.
- Maintain approximately 3.9–4.1 m panels by increasing floor/ceiling tile layout to 14 × 11 and wall tier layout to 4, with aligned atlas normal/ORM seam patterns. Avoid merely stretching the old 10×8 wall grid.
- Change no texture resolution, dynamic lights, bloom, or fog. Keeping the previous texture GPU budget makes the FPS comparison more meaningful.
- Tests enforce all six mesh world bounds, room heights and camera collision bounds, plus the simultaneous two-touch control behavior. The previous device FPS is a reference only; re-measure the enlarged room.
- No fixed bay coordinates or showroom relocation until the footprint is approved.
