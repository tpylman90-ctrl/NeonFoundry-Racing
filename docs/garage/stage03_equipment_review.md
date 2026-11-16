# Garage Stage 03 equipment build

## Current pass

The current build adds two large custom work cells to the runtime garage: a power-cell exchange cell under the zone 04 observation deck, and a pod upgrade/calibration bay in zone 05. A three-tier spare-cell cabinet sits along the west edge of the exchange area. The authored assets use the garage's graphite, cool-metal, cyan, and amber material language and keep the existing shell, partition, mezzanine, and stair files separate.

The exchange cell has a twin-tower service gantry, guided lift head, blind-mate connectors, detailed high-voltage pack, operator console, grounded deck, and safety lighting. The upgrade cell has a removable vector pod on a cradle, louvered housings, visible coil hardware, paired controls, telemetry, and a calibration bridge.

## Placement contract

- Keep the zone 04 equipment below the 7.20 m deck surface. The gantry top is at about 4.32 m world height after the 5 mm floor inset, leaving about 2.88 m to the deck surface.
- Keep the zone 05 bay west of the 9 m ingress lane. The bay ends at X=-7.50 m, leaving 0.50 m to the lane boundary at X=-7.00 m.
- Keep the 7 m transverse aisle (Z=-5.75..1.25 m) clear.
- Preserve the stair approach and all previously built walls, doors, mezzanine geometry, and partitions.

## Opening view

The opening 3/4 camera now targets the zone 04 battery exchange and zone 05 upgrade bay from the south/front side of the mezzanine, so the new work cells are visible immediately when Garage opens. The HUD identifies this build as Stage 03.

## Review state

The equipment is wired into the existing garage scene as a separate Stage 03 node. This pass has not been captured in the production runtime or on Android. It is an in-progress equipment layout, not a packaged or released build. The separate prop review catalog remains intact; the two hero stations here are custom meshes so their silhouette and scale fit this garage rather than relying on generic sourced workshop props.

See [stage03_equipment_manifest.json](stage03_equipment_manifest.json) for measured centers, dimensions, clearances, and provenance.
