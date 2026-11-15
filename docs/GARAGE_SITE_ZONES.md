# Foundry Lot — proposed functional floor plan

**Reference:** User-provided "Futuristic Hover & Assembly Garage — Site Layout" blueprint in the November 2026 project discussion.

**Status:** Planning reference only. No room geometry, textures, object positions, or stage-number commitments are changed by this document.

The existing Stage 01 envelope is approximately **39.8 m X (width) × 32.3 m Z (depth)**, with a **14.7 m ceiling**. The four walls and surface textures are currently under review; preserve them. The blueprint is a conceptual placement/zoning suggestion, NOT verified to scale.

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
- Back boundary around Z = -17.9 m, front around Z = +14.4 m.
- Left boundary around X = -19.9 m, right around X = +19.9 m.
- Zones above are **relative areas**, not locked object coordinates.
- The existing show platform currently uses a central layout. The blueprint suggests moving it to front-right; **do not relocate** or remove it without a subsequent approved layout stage.

## Controlled order

1. **Current** — approve the walls, floor, ceiling, PBR/ORM and stable walkaround controls.
2. **Future** — place structural girders, ceiling framework, and controlled wall separations.
3. **Future** — establish the internal zone boundaries and functional paths.
4. **Future** — add equipment one bay at a time; verify visibility, lighting and Android FPS between additions.

The previously modeled workshop remains a source of reusable equipment assets, not an instruction to bring everything back at once.
