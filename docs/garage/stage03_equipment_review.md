# Garage Stage 03 equipment build

## Current pass

The current build uses distinct footprints across zone 04: the power-cell exchange gantry under the mezzanine, a four-cabinet formation bank beyond its front edge, a thermal conditioning chamber in the west-rear pocket, and a laser metrology bench at the east-front edge. The pod upgrade/calibration bay remains in zone 05. The spare-cell rack was removed from this pass because its footprint crowded the exchange station. The authored equipment retains the graphite, cool-metal, cyan, and amber material language.

The exchange cell has a twin-tower service gantry, guided lift head, blind-mate connectors, detailed high-voltage pack, operator console, grounded deck, and safety lighting. The upgrade cell has a removable vector pod on a cradle, louvered housings, visible coil hardware, paired controls, telemetry, and a calibration bridge.

## Placement contract

- Keep the exchange gantry below the 7.20 m deck surface. The gantry top is about 4.32 m, leaving about 2.88 m of overhead clearance.
- Keep the zone 05 bay west of the 9 m ingress lane. The bay ends at X=-7.50 m, leaving 0.50 m to the lane boundary at X=-7.00 m.
- Keep the 7 m transverse aisle (Z=-5.75..1.25 m) clear.
- Reserve the stairwell opening at X=-16.00..-13.30 and Z=+9.05..+12.05. Keep at least 1.2 m clear from the stair toe to the formation bank and at least 2.0 m from the lower landing to the front wall.

## Opening view

The opening 3/4 camera frames the zone 04 work area. The equipment is split into front, center and rear pockets around a reserved stair corridor rather than grouped on one pad. The HUD identifies this build as Stage 03.

## Review state

The equipment is wired into the existing garage scene as a separate Stage 03 node. The stair geometry and movement bounds share the same coordinates, and the Android CI scene capture is the next visual verification step. The separate prop review catalog remains intact; the two hero stations here are custom meshes so their silhouette and scale fit this garage rather than relying on generic sourced workshop props.

See [stage03_equipment_manifest.json](stage03_equipment_manifest.json) for measured centers, dimensions, clearances, and provenance.

