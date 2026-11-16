extends Node3D
## Stage 03 garage equipment: two functional, oversized hero work cells.
## The shop shell and circulation remain authored by the earlier stages.

const INK := Color("101c29")
const GRAPHITE := Color("233443")
const BODY := Color("40596a")
const EDGE := Color("8296a0")
const METAL := Color("b2c1c7")
const CYAN := Color("40d8ed")
const CYAN_DARK := Color("187f96")
const AMBER := Color("ff9b43")
const GLASS := Color("153c4e")
const PANEL := Color("0b1721")
const FLOOR := Color("354b59")

var _materials: Dictionary = {}
var _batch_tools: Dictionary = {}

func _ready() -> void:
	_create_materials()
	_build_battery_exchange()
	_build_upgrade_bay()
	_build_battery_storage()
	_build_zone_markers()
	_commit_batches()

func _create_materials() -> void:
	_materials = {
		"ink": _mat(INK, 0.3, 0.42),
		"graphite": _mat(GRAPHITE, 0.45, 0.34),
		"body": _mat(BODY, 0.55, 0.30),
		"edge": _mat(EDGE, 0.74, 0.23),
		"metal": _mat(METAL, 0.82, 0.19),
		"cyan": _mat(CYAN, 0.22, 0.20, 1.3),
		"cyan_dark": _mat(CYAN_DARK, 0.42, 0.28, 0.35),
		"amber": _mat(AMBER, 0.32, 0.25, 0.8),
		"glass": _mat(GLASS, 0.48, 0.16, 0.28),
		"panel": _mat(PANEL, 0.18, 0.28),
		"floor": _mat(FLOOR, 0.32, 0.48)
	}

func _mat(color: Color, metalness: float, roughness: float, emission: float = 0.0) -> StandardMaterial3D:
	var result := StandardMaterial3D.new()
	result.albedo_color = color
	result.metallic = metalness
	result.roughness = roughness
	if emission > 0.0:
		result.emission_enabled = true
		result.emission = color
		result.emission_energy_multiplier = emission
	return result

func _box(parent: Node3D, _name: String, p: Vector3, size: Vector3, material_id: String,
		rotation_y: float = 0.0) -> void:
	var mesh := BoxMesh.new()
	mesh.size = size
	var transform := parent.transform * Transform3D(Basis(Vector3.UP, rotation_y), p)
	_append_mesh(material_id, mesh, transform)

func _cylinder(parent: Node3D, name: String, p: Vector3, radius: float, height: float,
		material_id: String, radial_segments: int = 20, axis: Vector3 = Vector3.UP) -> void:
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius
	mesh.bottom_radius = radius
	mesh.height = height
	mesh.radial_segments = radial_segments
	var orientation := Quaternion(Vector3.UP, axis.normalized())
	var transform := parent.transform * Transform3D(Basis(orientation), p)
	_append_mesh(material_id, mesh, transform)

func _rod(parent: Node3D, name: String, a: Vector3, b: Vector3, radius: float,
		material_id: String) -> void:
	var delta := b - a
	_cylinder(parent, name, (a + b) * 0.5, radius, delta.length(), material_id, 12, delta.normalized())

func _append_mesh(material_id: String, source: Mesh, transform: Transform3D) -> void:
	if not _batch_tools.has(material_id):
		var tool := SurfaceTool.new()
		tool.begin(Mesh.PRIMITIVE_TRIANGLES)
		_batch_tools[material_id] = tool
	var batch: SurfaceTool = _batch_tools[material_id]
	batch.append_from(source, 0, transform)

func _commit_batches() -> void:
	for material_id in _batch_tools:
		var batch: SurfaceTool = _batch_tools[material_id]
		batch.generate_normals()
		var mesh: ArrayMesh = batch.commit()
		var instance := MeshInstance3D.new()
		instance.name = "EquipmentBatch_" + str(material_id)
		instance.mesh = mesh
		instance.material_override = _materials[material_id]
		instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		add_child(instance)
	_batch_tools.clear()

func _label(parent: Node3D, text_value: String, p: Vector3, size: float = 0.30,
		color: Color = Color("d8f7fc")) -> void:
	var label := Label3D.new()
	label.name = "ID_" + text_value.replace(" ", "_").replace("/", "_")
	label.text = text_value
	label.font_size = int(size * 96.0)
	label.pixel_size = 0.004
	label.modulate = color
	label.outline_size = 5
	label.outline_modulate = Color("07111a")
	label.position = p
	label.no_depth_test = false
	parent.add_child(label)

func _build_battery_exchange() -> void:
	# 8.8 × 5.8 m service cell centered under the 5.2 m observation deck.
	# The full 4.45 m silhouette leaves clearance to the deck above.
	var cell := Node3D.new()
	cell.name = "PowerCellExchangeCell_Zone04"
	cell.position = Vector3(-18.8, -0.065, 7.2)
	add_child(cell)

	# Load-spreading floor plinth with chamfer-like tiered armor, service seams,
	# perimeter light channels, tie-downs and grounded safety bands.
	_box(cell, "LoadBearingBase", Vector3(0, 0.16, 0), Vector3(8.7, 0.30, 5.75), "ink")
	_box(cell, "RaisedWorkDeck", Vector3(0, 0.36, 0), Vector3(8.34, 0.16, 5.38), "body")
	_box(cell, "CenterServiceInsert", Vector3(0, 0.46, 0), Vector3(4.45, 0.055, 2.38), "graphite")
	for side in [-1.0, 1.0]:
		_box(cell, "CyanDeckGuide", Vector3(side * 4.14, 0.47, 0), Vector3(0.075, 0.035, 4.9), "cyan")
		_box(cell, "AmberEdgeStripe", Vector3(side * 4.34, 0.325, 0), Vector3(0.11, 0.035, 5.2), "amber")
		for z in [-2.55, 2.55]:
			_box(cell, "CornerFoot", Vector3(side * 3.98, 0.62, z), Vector3(0.36, 0.35, 0.38), "metal")
			_cylinder(cell, "DeckLock", Vector3(side * 3.98, 0.81, z), 0.13, 0.08, "amber", 16)
	for z in [-2.30, 2.30]:
		_box(cell, "DockLine", Vector3(0, 0.477, z), Vector3(6.95, 0.024, 0.045), "cyan_dark")
		for x in [-3.6, 3.6]:
			_box(cell, "CellStop", Vector3(x, 0.58, z), Vector3(0.12, 0.18, 0.38), "amber")

	# Twin structural towers and the double-track overhead manipulator frame.
	for side in [-1.0, 1.0]:
		var x: float = side * 3.74
		_box(cell, "TowerFoot_%.0f" % side, Vector3(x, 0.73, -1.75), Vector3(0.92, 0.46, 1.00), "ink")
		_box(cell, "ArmoredTower_%.0f" % side, Vector3(x, 2.33, -1.75), Vector3(0.72, 2.9, 0.76), "body")
		_box(cell, "TowerFace_%.0f" % side, Vector3(x - side * 0.37, 2.36, -1.75), Vector3(0.055, 2.35, 0.48), "graphite")
		_box(cell, "TowerStatus_%.0f" % side, Vector3(x - side * 0.405, 3.58, -1.75), Vector3(0.035, 0.42, 0.34), "cyan")
		_box(cell, "LinearGuide_%.0f" % side, Vector3(x - side * 0.40, 2.20, -1.25), Vector3(0.10, 2.35, 0.11), "metal")
		for y in [1.15, 1.55, 1.95, 2.35, 2.75, 3.15]:
			_box(cell, "TowerCoolingFin", Vector3(x, y, -1.34), Vector3(0.79, 0.06, 0.11), "ink")
		for z in [-2.05, -1.45]:
			_box(cell, "TowerAnchorPlate", Vector3(x, 0.98, z), Vector3(1.0, 0.10, 0.10), "metal")
	_box(cell, "GantryUpperBeam", Vector3(0, 4.03, -1.76), Vector3(8.12, 0.42, 0.94), "ink")
	_box(cell, "GantryArmorCap", Vector3(0, 4.28, -1.76), Vector3(7.72, 0.13, 0.82), "body")
	_box(cell, "GantryCyanIndex", Vector3(0, 4.356, -1.76), Vector3(5.95, 0.027, 0.07), "cyan")
	_box(cell, "GantryAmberEnd", Vector3(-3.62, 4.36, -1.76), Vector3(0.24, 0.045, 0.80), "amber")
	_box(cell, "GantryAmberEnd", Vector3(3.62, 4.36, -1.76), Vector3(0.24, 0.045, 0.80), "amber")
	for x in [-2.7, -1.35, 0.0, 1.35, 2.7]:
		_box(cell, "GantryUndersideSegment", Vector3(x, 3.78, -1.76), Vector3(1.05, 0.10, 0.71), "graphite")
		_cylinder(cell, "TrackRoller", Vector3(x, 3.67, -1.76), 0.12, 0.10, "metal", 12)
	# Suspended lift head with four guided actuator shafts and a mechanical quick coupler.
	_box(cell, "LiftHeadArmor", Vector3(0, 3.35, -1.76), Vector3(2.45, 0.38, 1.48), "body")
	_box(cell, "LiftHeadLowerPlate", Vector3(0, 3.12, -1.76), Vector3(2.12, 0.11, 1.18), "metal")
	for x in [-0.78, 0.78]:
		for z in [-0.40, 0.40]:
			_rod(cell, "ActuatorRod", Vector3(x, 2.64, -1.76 + z), Vector3(x, 3.11, -1.76 + z), 0.075, "metal")
			_cylinder(cell, "ActuatorCollar", Vector3(x, 2.78, -1.76 + z), 0.14, 0.16, "cyan_dark", 14)
	_box(cell, "CouplerSocket", Vector3(0, 2.99, -1.76), Vector3(0.66, 0.20, 0.68), "ink")
	_cylinder(cell, "CouplerRing", Vector3(0, 2.84, -1.76), 0.31, 0.10, "cyan", 24)

	# Removable high-voltage power cell: layered shell, end caps, recessed
	# inspection window, cooling fins and circular blind-mate connectors.
	_box(cell, "PowerCellLowerSkid", Vector3(0, 1.02, 0.23), Vector3(3.05, 0.34, 1.82), "ink")
	_box(cell, "CellMainForgedHousing", Vector3(0, 1.63, 0.23), Vector3(2.82, 0.91, 1.56), "body")
	_box(cell, "CellTopArmor", Vector3(0, 2.11, 0.23), Vector3(2.36, 0.14, 1.29), "edge")
	_box(cell, "CellFrontRecess", Vector3(0, 1.62, 1.025), Vector3(1.66, 0.57, 0.048), "ink")
	_box(cell, "CellStatusGlass", Vector3(0, 1.68, 1.058), Vector3(1.38, 0.37, 0.025), "glass")
	for x in [-0.50, -0.22, 0.06, 0.34]:
		_box(cell, "CellChargeBar", Vector3(x, 1.68, 1.078), Vector3(0.14, 0.09, 0.018), "cyan")
	for side in [-1.0, 1.0]:
		_box(cell, "CellEndPlate", Vector3(side * 1.43, 1.62, 0.23), Vector3(0.12, 0.68, 1.44), "graphite")
		_box(cell, "CellAmberLatch", Vector3(side * 1.51, 1.58, 0.23), Vector3(0.08, 0.30, 0.34), "amber")
		_cylinder(cell, "CellBlindMatePort", Vector3(side * 1.53, 1.62, -0.33), 0.22, 0.16, "metal", 18, Vector3.RIGHT)
		_cylinder(cell, "PortLuminousCore", Vector3(side * 1.625, 1.62, -0.33), 0.12, 0.08, "cyan", 18, Vector3.RIGHT)
		for fin in range(7):
			_box(cell, "CellCoolingFin", Vector3(side * 0.95, 1.74, -0.53 + fin * 0.245), Vector3(0.10, 0.66, 0.095), "ink")
		for y in [1.28, 1.98]:
			_box(cell, "CellArmorRib", Vector3(side * 1.40, y, 0.24), Vector3(0.06, 0.07, 1.18), "metal")
	# Tail-side cable looms terminate at the coupler rail, not loose on the floor.
	for side in [-1.0, 1.0]:
		_rod(cell, "PowerCableDrop", Vector3(side * 3.35, 2.0, -2.2), Vector3(side * 3.35, 1.15, -1.95), 0.085, "cyan_dark")
		_rod(cell, "PowerCableReturn", Vector3(side * 3.35, 1.15, -1.95), Vector3(side * 2.6, 0.92, -1.25), 0.085, "cyan_dark")
	# Operator station and a recessed, purpose-placed service display on the front rail.
	_box(cell, "OperatorPedestal", Vector3(0, 1.04, 2.17), Vector3(2.95, 1.86, 0.55), "ink")
	_box(cell, "OperatorArmor", Vector3(0, 1.92, 2.10), Vector3(3.12, 0.22, 0.72), "body")
	_box(cell, "TouchscreenHousing", Vector3(0, 2.68, 1.94), Vector3(2.64, 1.22, 0.16), "ink")
	_box(cell, "CellHealthDisplay", Vector3(0, 2.69, 1.835), Vector3(2.38, 0.94, 0.045), "glass")
	for i in range(6):
		_box(cell, "ScreenTelemetryRow", Vector3(-0.78 + i * 0.30, 2.42, 1.805), Vector3(0.22, 0.045 + (i % 3) * 0.045, 0.012), "cyan" if i < 5 else "amber")
	for side in [-1.0, 1.0]:
		_box(cell, "StatusLouver", Vector3(side * 1.32, 2.69, 1.825), Vector3(0.10, 0.73, 0.028), "metal")
	_label(cell, "POWER CELL / EXCHANGE", Vector3(0, 3.40, 1.78), 0.23, Color("80e9f4"))
	_label(cell, "HIGH VOLTAGE  •  LOCKED", Vector3(0, 0.74, 2.48), 0.14, Color("ffad62"))

func _build_upgrade_bay() -> void:
	# Zone 05, west of the ingress lane; the complete 3.4 m width stays clear
	# of the specified x=-7..2 vehicle approach.
	var bay := Node3D.new()
	bay.name = "RacerUpgradeConfigurator_Zone05"
	bay.position = Vector3(-9.20, -0.065, 9.3)
	add_child(bay)
	_box(bay, "ConfiguratorFoundation", Vector3(0, 0.15, 0), Vector3(3.40, 0.28, 5.45), "ink")
	_box(bay, "RaisedArmorDeck", Vector3(0, 0.34, 0), Vector3(3.18, 0.13, 5.18), "body")
	for side in [-1.0, 1.0]:
		_box(bay, "DeckLight", Vector3(side * 1.50, 0.43, 0), Vector3(0.055, 0.03, 4.72), "cyan")
		_box(bay, "DeckAmberMark", Vector3(side * 1.61, 0.30, 0), Vector3(0.07, 0.025, 4.95), "amber")
	# Hero pod/craft part on a service cradle, shaped as an engineered module.
	_box(bay, "PodCradleBase", Vector3(0, 0.72, -0.30), Vector3(2.18, 0.52, 2.45), "graphite")
	for x in [-0.80, 0.80]:
		_box(bay, "PodCradleRail", Vector3(x, 1.09, -0.30), Vector3(0.20, 0.30, 2.14), "metal")
		_box(bay, "CradleGrip", Vector3(x, 1.28, -0.38), Vector3(0.26, 0.08, 1.60), "amber")
	_box(bay, "UpgradePodCore", Vector3(0, 1.84, -0.25), Vector3(1.70, 0.88, 1.83), "body")
	_box(bay, "PodTopSpine", Vector3(0, 2.30, -0.25), Vector3(0.82, 0.11, 1.48), "edge")
	for side in [-1.0, 1.0]:
		_box(bay, "PodSideShoulder", Vector3(side * 0.82, 1.90, -0.23), Vector3(0.23, 0.64, 1.47), "graphite")
		_box(bay, "PodIntakeRecess", Vector3(side * 0.945, 1.91, -0.17), Vector3(0.035, 0.42, 0.82), "ink")
		for louver in range(5):
			_box(bay, "PodCoolingLouver", Vector3(side * 0.975, 1.78 + louver * 0.07, -0.17), Vector3(0.04, 0.027, 0.72), "metal")
		_cylinder(bay, "VectorCoilOuter", Vector3(side * 0.60, 1.79, -1.22), 0.40, 0.22, "ink", 24, Vector3.BACK)
		_cylinder(bay, "VectorCoilRing", Vector3(side * 0.60, 1.79, -1.35), 0.31, 0.13, "amber", 24, Vector3.BACK)
		_cylinder(bay, "VectorCoilCore", Vector3(side * 0.60, 1.79, -1.43), 0.19, 0.08, "cyan", 24, Vector3.BACK)
	_box(bay, "PodNoseArmor", Vector3(0, 1.85, 0.72), Vector3(1.24, 0.46, 0.18), "metal")
	_box(bay, "PodIdentificationPanel", Vector3(0, 1.86, 0.83), Vector3(0.75, 0.20, 0.035), "ink")
	_box(bay, "PodIDLight", Vector3(0, 1.88, 0.855), Vector3(0.48, 0.045, 0.02), "cyan")
	# Twin control plinths flank the display cradle without crossing the approach aisle.
	for side in [-1.0, 1.0]:
		var x: float = side * 1.17
		_box(bay, "ControlConsoleBase", Vector3(x, 0.91, 1.58), Vector3(0.88, 1.58, 0.96), "ink")
		_box(bay, "ConsoleArmorLip", Vector3(x, 1.73, 1.42), Vector3(0.98, 0.12, 1.06), "body")
		_box(bay, "ConsoleGlass", Vector3(x, 1.82, 1.10), Vector3(0.70, 0.055, 0.43), "glass", -side * 0.10)
		for i in range(4):
			_box(bay, "ConsoleSlider", Vector3(x - 0.24 + i * 0.16, 1.86, 1.12), Vector3(0.055, 0.022, 0.27), "cyan" if i % 2 == 0 else "amber")
		_box(bay, "ConsoleFrontBadge", Vector3(x, 1.08, 2.071), Vector3(0.50, 0.24, 0.025), "graphite")
		_box(bay, "ConsoleBadgeLight", Vector3(x, 1.08, 2.09), Vector3(0.26, 0.035, 0.012), "cyan")
	# Articulated measurement bridge over the part, with calibrated three-axis rails.
	for side in [-1.0, 1.0]:
		_box(bay, "MetrologyColumn", Vector3(side * 1.50, 2.55, -1.54), Vector3(0.22, 2.42, 0.25), "ink")
		_box(bay, "MetrologyGuide", Vector3(side * 1.50, 2.52, -1.37), Vector3(0.075, 2.05, 0.055), "metal")
	_box(bay, "MetrologyCrossbar", Vector3(0, 3.73, -1.54), Vector3(3.22, 0.20, 0.36), "graphite")
	_box(bay, "CalibrationStrip", Vector3(0, 3.61, -1.34), Vector3(2.70, 0.038, 0.04), "cyan")
	for x in [-1.2, -0.8, -0.4, 0.0, 0.4, 0.8, 1.2]:
		_box(bay, "CalibrationTick", Vector3(x, 3.56, -1.32), Vector3(0.025, 0.09 if int(abs(x) * 10) % 2 == 0 else 0.05, 0.025), "metal")
	_box(bay, "BayTelemetryTower", Vector3(0, 2.82, -2.42), Vector3(2.35, 1.26, 0.16), "ink")
	_box(bay, "UpgradeStatusGlass", Vector3(0, 2.84, -2.325), Vector3(2.10, 0.92, 0.035), "glass")
	for row in range(3):
		_box(bay, "UpgradeGraphLine", Vector3(-0.55 + row * 0.52, 2.68 + row * 0.09, -2.30), Vector3(0.36, 0.035, 0.018), "cyan" if row != 1 else "amber")
	_label(bay, "UPGRADE / CALIBRATION", Vector3(0, 3.44, -2.29), 0.22, Color("8cecf6"))
	_label(bay, "VECTOR POD  /  FIT CHECK", Vector3(0, 0.66, 2.45), 0.15, Color("ffb56a"))
	# Replaceable hardware bins against the inner west end of the work cell.
	for i in range(3):
		var z: float = -1.2 + float(i) * 0.72
		_box(bay, "ModuleDrawer", Vector3(-1.43, 1.26, z), Vector3(0.32, 0.36, 0.56), "ink")
		_box(bay, "DrawerID", Vector3(-1.25, 1.29, z), Vector3(0.018, 0.13, 0.32), "cyan_dark")

func _build_battery_storage() -> void:
	# Visible two-column, six-slot spare-cell cabinet on the deck's far-west edge.
	# Kept outside the stair envelope and clear of the service lane.
	var rack := Node3D.new()
	rack.name = "SparePowerCellCabinet_Zone04"
	rack.position = Vector3(-24.50, -0.065, 5.8)
	add_child(rack)
	_box(rack, "BatteryRackFoot", Vector3(0, 0.18, 0), Vector3(1.75, 0.34, 3.30), "ink")
	for side in [-1.0, 1.0]:
		_box(rack, "RackUpright", Vector3(side * 0.72, 2.08, 0), Vector3(0.18, 3.72, 3.0), "body")
		_box(rack, "RackCyanRail", Vector3(side * 0.62, 2.10, 0), Vector3(0.045, 3.25, 2.72), "cyan_dark")
	for tier in range(3):
		var y: float = 0.78 + float(tier) * 1.18
		_box(rack, "RackShelf", Vector3(0, y, 0), Vector3(1.56, 0.12, 2.86), "metal")
		for side in [-1.0, 1.0]:
			_box(rack, "SpareCellCase", Vector3(side * 0.36, y + 0.36, 0), Vector3(0.60, 0.58, 1.08), "graphite")
			_box(rack, "SpareCellFace", Vector3(side * 0.36, y + 0.36, 0.55), Vector3(0.43, 0.34, 0.045), "ink")
			_box(rack, "SpareCellCharge", Vector3(side * 0.36, y + 0.39, 0.58), Vector3(0.24, 0.055, 0.018), "cyan" if tier < 2 else "amber")
	for side in [-1.0, 1.0]:
		_box(rack, "RackTopArmor", Vector3(side * 0.55, 4.10, 0), Vector3(0.42, 0.18, 3.15), "edge")
	_box(rack, "RackHeader", Vector3(0, 4.32, 1.53), Vector3(1.70, 0.47, 0.12), "ink")
	_box(rack, "RackHeaderLight", Vector3(0, 4.33, 1.455), Vector3(1.30, 0.055, 0.025), "amber")
	_label(rack, "CELL RESERVE", Vector3(0, 4.35, 1.42), 0.13, Color("d6f4f8"))

func _build_zone_markers() -> void:
	# Low, floor-contact wayfinding at each hero cell; the 7 m cross-aisle and
	# 9 m front ingress are deliberately left free of props and overhead clutter.
	var plates: Array[Dictionary] = [
		{"name": "POWER CELL / 04", "p": Vector3(-18.8, -0.039, 10.38), "w": 7.1},
		{"name": "UPGRADES / 05", "p": Vector3(-9.20, -0.039, 12.27), "w": 2.8}
	]
	for entry in plates:
		var p: Vector3 = entry["p"]
		_box(self, "FloorWayfindingPlate_" + str(entry["name"]), p, Vector3(float(entry["w"]), 0.022, 0.19), "ink")
		_box(self, "FloorWayfindingLine_" + str(entry["name"]), p + Vector3(0, 0.006, 0), Vector3(float(entry["w"]) - 0.22, 0.012, 0.035), "amber")
