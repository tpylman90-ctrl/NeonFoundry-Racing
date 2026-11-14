extends Node3D
## Neon Foundry workshop architecture and equipment. All static geometry is batched
## into one surface per PBR material for low draw calls on Godot Mobile/Vulkan.
## Articulated diagnostic robot remains separately modeled and animatable.
##
## Coordinates: turntable x/z=0, Y=0.3, workshop back wall z=-18.
## Source of truth is real geometry (no baked backdrop inside the garage).

const STEEL := "steel"
const FLOOR := "floor"
const GRAPHITE := "graphite"
const DARK := "dark"
const TRIM := "trim"
const CYAN := "cyan"
const AMBER := "amber"
const YELLOW := "yellow"
const BLACK := "black"
const SCREEN := "screen"
const SILVER := "silver"
const GLASS := "glass"

var _tools: Dictionary = {}
var _materials: Dictionary = {}
var _time: float = 0.0
var _robot: Node3D
var _robot_wrist: Node3D
var _lift_carriages: Array[Node3D] = []
var _lift_height: float = 0.0
var _lift_target: float = 0.0
var _scanner_enabled: bool = true
var _light_rigs: Array[OmniLight3D] = []

func _ready() -> void:
	_create_materials()
	_start_batches()
	_build_floor()
	_build_architecture()
	_build_ceiling()
	_build_platform()
	_build_service_lifts()
	_build_workstations()
	_build_service_bays()
	_build_robot_base()
	_build_signage()
	_commit_batches()
	_build_robot()
	_build_task_lights()
	set_process(true)
	print("NEON_FOUNDRY_WORKSHOP_READY batched_materials=%d lifts=%d" % [_materials.size(), _lift_carriages.size()])

func _process(delta: float) -> void:
	_time += delta
	if _robot != null:
		_robot.rotation.y = 0.08 * sin(_time * 0.45) if _scanner_enabled else 0.0
	if _robot_wrist != null:
		_robot_wrist.rotation.z = 0.18 * sin(_time * 0.84) if _scanner_enabled else 0.0
	_lift_height = move_toward(_lift_height, _lift_target, delta * 1.2)
	for lift in _lift_carriages:
		lift.position.y = _lift_height

func set_scanner_active(enabled: bool) -> void:
	_scanner_enabled = enabled
	for light in _light_rigs:
		light.visible = enabled

func toggle_lifts() -> void:
	_lift_target = 1.6 if _lift_target < 0.8 else 0.0

func reset_equipment() -> void:
	_lift_target = 0.0
	set_scanner_active(true)

func get_equipment_status() -> String:
	return "ROBOT SCANNER  /  %s     •     LIFT DEMO  /  %s" % [
		"ACTIVE" if _scanner_enabled else "STANDBY",
		"RAISED" if _lift_target > 0.8 else "STOWED"
	]

func _material(color: Color, metal: float, rough: float, glow: float = 0.0) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.metallic = metal
	mat.roughness = rough
	if glow > 0:
		mat.emission_enabled = true
		mat.emission = color
		mat.emission_energy_multiplier = glow
	return mat

func _create_materials() -> void:
	_materials = {
		STEEL: _material(Color("3b5260"), 0.80, 0.29),
		FLOOR: _material(Color("263946"), 0.65, 0.27),
		GRAPHITE: _material(Color("182734"), 0.55, 0.40),
		DARK: _material(Color("0c1824"), 0.18, 0.72),
		TRIM: _material(Color("607784"), 0.80, 0.27),
		CYAN: _material(Color("2bd9f0"), 0.18, 0.25, 2.6),
		AMBER: _material(Color("fa7a33"), 0.23, 0.26, 2.3),
		YELLOW: _material(Color("e5a537"), 0.45, 0.33),
		BLACK: _material(Color("111a21"), 0.10, 0.8),
		SCREEN: _material(Color("087c99"), 0.03, 0.25, 1.8),
		SILVER: _material(Color("a5bac3"), 0.84, 0.26),
		GLASS: _material(Color("143347"), 0.63, 0.23)
	}

func _start_batches() -> void:
	for id in _materials:
		var surface := SurfaceTool.new()
		surface.begin(Mesh.PRIMITIVE_TRIANGLES)
		_tools[id] = surface

func _add_quad(id: String, a: Vector3, b: Vector3, c: Vector3, d: Vector3, tiling: float = 1.0) -> void:
	var tool: SurfaceTool = _tools[id]
	var normal: Vector3 = (b - a).cross(c - a).normalized()
	var vertices: Array[Vector3] = [a, b, c, a, c, d]
	var uvs: Array[Vector2] = [
		Vector2.ZERO, Vector2(tiling, 0), Vector2(tiling, tiling),
		Vector2.ZERO, Vector2(tiling, tiling), Vector2(0, tiling)
	]
	for i in range(6):
		tool.set_normal(normal)
		tool.set_uv(uvs[i])
		tool.add_vertex(vertices[i])

func _box(id: String, position: Vector3, size: Vector3, angle_y: float = 0.0) -> void:
	if size.x <= 0 or size.y <= 0 or size.z <= 0:
		return
	var bx: Vector3 = Vector3(cos(angle_y), 0, -sin(angle_y)) * size.x * 0.5
	var by := Vector3.UP * size.y * 0.5
	var bz := Vector3(sin(angle_y), 0, cos(angle_y)) * size.z * 0.5
	var a := position - bx - by - bz
	var b := position - bx - by + bz
	var c := position - bx + by - bz
	var d := position - bx + by + bz
	var e := position + bx - by - bz
	var f := position + bx - by + bz
	var g := position + bx + by - bz
	var h := position + bx + by + bz
	_add_quad(id, e, g, h, f)
	_add_quad(id, a, b, d, c)
	_add_quad(id, c, d, h, g)
	_add_quad(id, a, e, f, b)
	_add_quad(id, b, f, h, d)
	_add_quad(id, a, c, g, e)

func _rod(id: String, from: Vector3, to: Vector3, radius: float, segments: int = 12) -> void:
	var axis: Vector3 = to - from
	if axis.length_squared() < 0.00001:
		return
	var direction: Vector3 = axis.normalized()
	var helper := Vector3.UP if absf(direction.y) < 0.94 else Vector3.RIGHT
	var tangent: Vector3 = direction.cross(helper).normalized()
	var bitangent: Vector3 = tangent.cross(direction).normalized()
	for i in range(segments):
		var a: float = TAU * float(i) / float(segments)
		var b: float = TAU * float(i + 1) / float(segments)
		var ca: Vector3 = (tangent * cos(a) + bitangent * sin(a)) * radius
		var cb: Vector3 = (tangent * cos(b) + bitangent * sin(b)) * radius
		_add_quad(id, from + ca, from + cb, to + cb, to + ca)
		var center_bottom := from
		var center_top := to
		var tool: SurfaceTool = _tools[id]
		for pts in [[center_bottom, from + cb, from + ca], [center_top, to + ca, to + cb]]:
			var p0: Vector3 = pts[0]
			var p1: Vector3 = pts[1]
			var p2: Vector3 = pts[2]
			tool.set_normal((p1 - p0).cross(p2 - p0).normalized())
			tool.set_uv(Vector2.ZERO)
			tool.add_vertex(p0)
			tool.set_uv(Vector2(1, 0))
			tool.add_vertex(p1)
			tool.set_uv(Vector2(0, 1))
			tool.add_vertex(p2)

func _disc(id: String, point: Vector3, radius: float, depth: float, segments: int = 48) -> void:
	_rod(id, point + Vector3(0, -depth * 0.5, 0), point + Vector3(0, depth * 0.5, 0), radius, segments)

func _arc(id: String, center: Vector3, radius: float, width: float, y: float, start: float, end: float, steps: int = 72) -> void:
	for i in range(steps):
		var a := lerpf(start, end, float(i) / float(steps))
		var b := lerpf(start, end, float(i + 1) / float(steps))
		var p := Vector3(cos(a) * radius + center.x, center.y + y, sin(a) * radius + center.z)
		var q := Vector3(cos(b) * radius + center.x, center.y + y, sin(b) * radius + center.z)
		_rod(id, p, q, width, 6)

func _commit_batches() -> void:
	for id in _tools:
		var tool: SurfaceTool = _tools[id]
		var mesh: ArrayMesh = tool.commit()
		var node := MeshInstance3D.new()
		node.name = "Batched_%s" % id
		node.mesh = mesh
		node.material_override = _materials[id]
		node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(node)

func _build_floor() -> void:
	# High-gloss graphite floor panels, clean CNC seams and orange maintenance lanes.
	for x in range(-8, 9):
		for z in range(-6, 7):
			var cx := float(x) * 2.35
			var cz := float(z) * 2.42 - 3.0
			if Vector2(cx, cz).length() < 6.72:
				continue
			_box(FLOOR if (x + z) % 3 == 0 else GRAPHITE,
				Vector3(cx, -0.073, cz), Vector3(2.325, 0.018, 2.395))
			if x % 3 == 0:
				_box(TRIM, Vector3(cx - 1.16, -0.056, cz), Vector3(0.014, 0.009, 2.38))
			if z % 3 == 0:
				_box(TRIM, Vector3(cx, -0.055, cz - 1.18), Vector3(2.3, 0.009, 0.014))
	for side in [-1.0, 1.0]:
		# Recessed trench drain with steel grating, workshop access safety band.
		var x: float = side * 9.0
		_box(BLACK, Vector3(x, -0.035, -4.0), Vector3(0.72, 0.05, 24.0))
		for i in range(56):
			_box(STEEL, Vector3(x, -0.005, -15.7 + float(i) * 0.42),
				Vector3(0.71, 0.04, 0.074))
		_box(YELLOW, Vector3(x + side * 0.55, -0.015, -4.0), Vector3(0.12, 0.02, 24.0))
	for x in [-14.0, 14.0]:
		for z in [-13.0, -3.0, 7.0]:
			for k in range(9):
				var dx: float = float(k) * 0.50
				_box(YELLOW, Vector3(x - 2.0 + dx, 0.0, z), Vector3(0.28, 0.018, 0.19), -0.45)

func _build_architecture() -> void:
	# Double wall skin and exposed structural reinforced bays.
	for side in [-1.0, 1.0]:
		var x: float = 18.6 * side
		_box(STEEL, Vector3(x, 6.9, -2.0), Vector3(0.32, 13.8, 30.0))
		for k in range(7):
			var z := -16.0 + float(k) * 4.7
			_box(GRAPHITE, Vector3(x - side * 0.30, 6.5, z), Vector3(0.34, 12.7, 0.8))
			_box(CYAN, Vector3(x - side * 0.50, 7.1, z), Vector3(0.06, 9.0, 0.08))
			_box(TRIM, Vector3(x - side * 0.46, 13.2, z), Vector3(0.13, 0.18, 3.2))
		# Real mezzanine supports, guard rails and hanging cable trays.
		_box(STEEL, Vector3(side * 13.5, 5.8, -8.7), Vector3(6.4, 0.46, 16.8))
		_box(BLACK, Vector3(side * 13.5, 6.05, -8.7), Vector3(6.35, 0.04, 16.6))
		for i in range(11):
			var z := -16.5 + float(i) * 1.55
			_rod(TRIM, Vector3(side * 10.45, 6.1, z), Vector3(side * 10.45, 7.5, z), 0.045, 8)
		_rod(STEEL, Vector3(side * 10.45, 7.55, -16.8), Vector3(side * 10.45, 7.55, -0.5), 0.07, 9)
		_box(CYAN, Vector3(side * 10.48, 6.06, -8.7), Vector3(0.09, 0.10, 16.0))
	# Back wall armor segmented around work stations.
	for i in range(11):
		var x: float = -18.0 + float(i) * 3.6
		_box(GRAPHITE, Vector3(x, 6.4, -17.53), Vector3(3.50, 11.75, 0.18))
		_box(STEEL, Vector3(x - 1.72, 6.4, -17.36), Vector3(0.1, 11.3, 0.30))
		_box(CYAN if i % 2 == 0 else AMBER, Vector3(x, 10.25, -17.38), Vector3(2.78, 0.065, 0.08))
		for h in [1.5, 11.5]:
			_box(TRIM, Vector3(x, h, -17.31), Vector3(2.92, 0.11, 0.06))
	for column_x in [-17.0, -8.5, 8.5, 17.0]:
		_box(STEEL, Vector3(column_x, 6.9, -16.6), Vector3(0.66, 13.8, 0.72))
		_box(CYAN, Vector3(column_x + 0.37, 6.7, -16.15), Vector3(0.06, 8.0, 0.06))
	# Hazard-striped vertical door surrounds for two maintenance bays.
	for bx in [-13.2, 13.2]:
		for side in [-1.0, 1.0]:
			var x: float = bx + side * 3.15
			_box(TRIM, Vector3(x, 3.5, -16.98), Vector3(0.36, 6.8, 0.20))
			for k in range(11):
				_box(YELLOW, Vector3(x, 0.62 + float(k) * 0.54, -16.84),
					Vector3(0.36, 0.16, 0.09), 0.0)
		_box(STEEL, Vector3(bx, 7.0, -16.98), Vector3(6.8, 0.48, 0.22))
		_box(CYAN, Vector3(bx, 6.8, -16.84), Vector3(6.6, 0.07, 0.08))

func _build_ceiling() -> void:
	# Suspended segmented engineering halo and articulated ceiling rail system.
	for spec in [
		{"y": 9.2, "r": 6.2, "id": GRAPHITE, "w": 0.33},
		{"y": 9.0, "r": 5.75, "id": CYAN, "w": 0.085},
		{"y": 8.74, "r": 5.1, "id": STEEL, "w": 0.28},
		{"y": 8.52, "r": 4.79, "id": AMBER, "w": 0.075},
		{"y": 8.34, "r": 4.30, "id": TRIM, "w": 0.12}
	]:
		_arc(str(spec["id"]), Vector3(0, 0, -0.8),
			float(spec["r"]), float(spec["w"]), float(spec["y"]), 0, TAU, 84)
	for i in range(18):
		var a := TAU * float(i) / 18.0
		var x: float = cos(a) * 5.6
		var z := sin(a) * 5.6 - 0.8
		_rod(STEEL, Vector3(x, 9.0, z), Vector3(x, 11.0, z), 0.13, 8)
		_box(AMBER if i % 3 == 0 else TRIM, Vector3(x, 8.79, z),
			Vector3(0.27, 0.13, 0.19), -a)
	for i in range(6):
		var a := TAU * float(i) / 6.0
		_rod(STEEL, Vector3(cos(a) * 5.8, 11.1, sin(a) * 5.8 - 0.8),
			Vector3(cos(a) * 5.8, 14.0, sin(a) * 5.8 - 0.8), 0.18, 10)
	for z in [-14.0, -7.0, 1.0, 8.0]:
		_box(STEEL, Vector3(0, 12.9, z), Vector3(37.2, 0.55, 0.55))
		_box(AMBER, Vector3(0, 12.53, z), Vector3(30.0, 0.07, 0.07))
		for x in [-13.0, -9.0, 9.0, 13.0]:
			_box(CYAN, Vector3(x, 11.92, z), Vector3(2.4, 0.1, 0.22))
	# Cable bundles and overhead service track over the robot.
	for x in [-9.0, 9.0]:
		_box(GRAPHITE, Vector3(x, 12.9, -2.8), Vector3(1.3, 0.34, 23.0))
		_box(TRIM, Vector3(x - 0.42, 12.64, -2.8), Vector3(0.09, 0.09, 23.0))
		_box(AMBER, Vector3(x + 0.42, 12.64, -2.8), Vector3(0.09, 0.09, 23.0))
		for k in range(18):
			var z := -13.4 + float(k) * 1.25
			_rod(BLACK, Vector3(x - 0.17, 12.6, z), Vector3(x - 0.17, 11.3, z - 0.24), 0.04, 6)

func _build_platform() -> void:
	# Retrofit the existing stage with tiered ring modules, vent banks, clamps,
	# bumper edges, bolts and maintenance hatch covers.
	_arc(STEEL, Vector3.ZERO, 6.05, 0.11, 0.11, 0, TAU, 96)
	_arc(CYAN, Vector3.ZERO, 5.92, 0.045, 0.36, 0, TAU, 96)
	_arc(BLACK, Vector3.ZERO, 6.33, 0.16, 0.09, 0, TAU, 96)
	_arc(AMBER, Vector3.ZERO, 6.42, 0.048, 0.17, 0, TAU, 96)
	for i in range(48):
		var a := TAU * float(i) / 48.0
		var r := 6.13
		var p := Vector3(cos(a) * r, 0.12, sin(a) * r)
		_box(STEEL, p, Vector3(0.36, 0.22, 0.75), -a)
		if i % 2 == 0:
			_box(CYAN, Vector3(cos(a) * 6.27, 0.13, sin(a) * 6.27),
				Vector3(0.12, 0.08, 0.38), -a)
		if i % 6 == 0:
			_box(AMBER, Vector3(cos(a) * 6.30, 0.20, sin(a) * 6.30),
				Vector3(0.17, 0.04, 0.42), -a)
	for i in range(16):
		var a := TAU * float(i) / 16.0
		var x: float = cos(a) * 6.75
		var z := sin(a) * 6.75
		_box(DARK, Vector3(x, 0.01, z), Vector3(0.8, 0.08, 0.52), -a)
		for j in range(4):
			_box(TRIM, Vector3(x + cos(a) * 0.01, 0.060,
				z + sin(a) * 0.01 + (float(j) - 1.5) * 0.085),
				Vector3(0.43, 0.018, 0.025), -a)
	# HUD-style floor pointers near crew access.
	for side in [-1.0, 1.0]:
		for i in range(4):
			_box(YELLOW, Vector3(side * 7.5, 0.02, 1.6 + float(i) * 0.43),
				Vector3(0.36, 0.012, 0.16), -0.28)

func _build_service_lifts() -> void:
	# Two main servo lift columns with telescoping paired support arms.
	for side in [-1.0, 1.0]:
		var x: float = side * 8.2
		var z := -1.75
		_box(BLACK, Vector3(x, 0.19, z), Vector3(1.85, 0.32, 2.6))
		_box(STEEL, Vector3(x, 3.00, z), Vector3(1.16, 5.86, 1.25))
		_box(GRAPHITE, Vector3(x, 3.04, z + 0.65), Vector3(0.96, 5.65, 0.08))
		_box(CYAN, Vector3(x - side * 0.42, 3.0, z + 0.71), Vector3(0.12, 4.95, 0.08))
		_box(STEEL, Vector3(x, 6.0, z), Vector3(1.4, 0.4, 1.46))
		_box(YELLOW, Vector3(x - side * 0.65, 0.40, z), Vector3(0.15, 0.65, 1.15))
		for i in range(11):
			_box(YELLOW if i % 2 == 0 else BLACK,
				Vector3(x, 0.47 + float(i) * 0.43, z + 0.72),
				Vector3(0.64, 0.11, 0.035))
		# A deliberately small carriage: does not move or collide with the craft.
		# Lift animation only actuates these unloaded service arms.
		var carriage := Node3D.new()
		carriage.name = "LiftCarriage_%d" % int(side)
		carriage.position = Vector3(x, 0, z)
		add_child(carriage)
		_lift_carriages.append(carriage)
		_lift_part(carriage, Vector3(0, 1.5, 0.0), Vector3(1.5, 0.5, 1.55), STEEL)
		for oz in [-0.43, 0.43]:
			_lift_part(carriage, Vector3(-side * 1.35, 1.26, oz),
				Vector3(2.5, 0.22, 0.39), YELLOW)
			_lift_part(carriage, Vector3(-side * 2.35, 1.43, oz),
				Vector3(0.52, 0.25, 0.38), BLACK)
		_add_label("LIFT 0%d" % (1 if side < 0 else 2),
			Vector3(x, 5.35, z + 0.80), 30, Color("9ce3ea"), 0.009)

func _lift_part(parent: Node3D, center: Vector3, size: Vector3, id: String) -> void:
	var mesh := BoxMesh.new()
	mesh.size = size
	var node := MeshInstance3D.new()
	node.mesh = mesh
	node.position = center
	node.material_override = _materials[id]
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(node)

func _build_workstations() -> void:
	# Functional-looking benches, pegboards with correctly oriented hand tools,
	# test monitors, drawers, rolling diagnostic carts, storage and spare turbines.
	for x in [-7.2, 0.0, 7.2]:
		var z := -15.3
		_box(BLACK, Vector3(x, 0.93, z), Vector3(6.25, 0.18, 2.15))
		_box(STEEL, Vector3(x, 0.74, z), Vector3(5.92, 1.45, 1.85))
		_box(TRIM, Vector3(x, 1.04, z + 1.10), Vector3(6.25, 0.07, 0.13))
		for drawer in range(5):
			_box(GRAPHITE, Vector3(x - 2.22 + float(drawer) * 1.1, 0.62, z + 0.96),
				Vector3(1.0, 0.58, 0.08))
			_box(AMBER if drawer % 2 == 0 else TRIM,
				Vector3(x - 2.22 + float(drawer) * 1.1, 0.82, z + 1.02),
				Vector3(0.72, 0.04, 0.04))
		_box(STEEL, Vector3(x, 3.65, -17.03), Vector3(5.4, 3.15, 0.22))
		_box(DARK, Vector3(x, 3.63, -16.91), Vector3(5.15, 2.9, 0.08))
		for k in range(17):
			var tool_x: float = x - 2.44 + float(k) * 0.30
			var tool_y := 2.95 + float(k % 3) * 0.52
			# Wrenches, probes, socket drivers, scribe tools and clamps.
			_rod(SILVER, Vector3(tool_x, tool_y - 0.36, -16.83),
				Vector3(tool_x, tool_y + 0.36, -16.83), 0.042, 8)
			_rod(SILVER if k % 4 else YELLOW,
				Vector3(tool_x - 0.13, tool_y + 0.35, -16.83),
				Vector3(tool_x + 0.13, tool_y + 0.35, -16.83), 0.040, 8)
			if k % 4 == 0:
				_box(YELLOW, Vector3(tool_x, tool_y - 0.25, -16.80),
					Vector3(0.13, 0.35, 0.12))
		_box(CYAN, Vector3(x, 5.30, -16.91), Vector3(5.2, 0.06, 0.08))
		# Slanted diagnostic displays.
		for offset in [-1.76, 1.76]:
			var sx: float = x + offset
			_box(BLACK, Vector3(sx, 1.68, z - 0.60), Vector3(1.48, 1.05, 0.10))
			_box(SCREEN, Vector3(sx, 1.67, z - 0.53), Vector3(1.31, 0.83, 0.04))
			for i in range(5):
				_box(CYAN, Vector3(sx - 0.5, 1.37 + float(i) * 0.12, z - 0.49),
					Vector3(0.12 + float((i * 7) % 5) * 0.13, 0.025, 0.008))
	# Free-standing rolling workshop toolboxes.
	for location in [Vector2(-10.4, 6.1), Vector2(10.5, 6.2),
			Vector2(-11.2, -11.9), Vector2(11.3, -11.9)]:
		var x: float = location.x
		var z: float = location.y
		_box(STEEL, Vector3(x, 0.69, z), Vector3(1.85, 1.32, 1.15))
		_box(BLACK, Vector3(x, 1.42, z), Vector3(2.0, 0.15, 1.34))
		for i in range(5):
			_box(GRAPHITE, Vector3(x, 0.32 + float(i) * 0.21, z + 0.595),
				Vector3(1.62, 0.16, 0.047))
			_box(AMBER, Vector3(x, 0.32 + float(i) * 0.21, z + 0.632),
				Vector3(0.84, 0.025, 0.018))
		for dx in [-0.65, 0.65]:
			for dz in [-0.42, 0.42]:
				_disc(BLACK, Vector3(x + dx, 0.085, z + dz), 0.13, 0.10, 12)
		for i in range(7):
			_box(SILVER, Vector3(x - 0.70 + float(i) * 0.23, 1.56, z),
				Vector3(0.07, 0.16, 0.07))
	# Open shelving at the far right and a spare propulsion module on a stand.
	for side in [-1.0, 1.0]:
		var x: float = side * 16.0
		var z := -12.3
		for dx in [-1.9, 1.9]:
			for dz in [-0.72, 0.72]:
				_box(STEEL, Vector3(x + dx, 3.1, z + dz), Vector3(0.20, 5.9, 0.2))
		for h in [0.65, 2.0, 3.45, 4.9]:
			_box(TRIM, Vector3(x, h, z), Vector3(4.1, 0.14, 1.8))
		for k in range(11):
			var bx: float = x - 1.65 + float(k % 6) * 0.61
			var by := 0.98 + float(k / 6) * 1.5
			_box(GRAPHITE, Vector3(bx, by, z), Vector3(0.51, 0.56, 0.85))
			_box(AMBER if k % 3 == 0 else CYAN,
				Vector3(bx, by + 0.31, z + 0.45), Vector3(0.32, 0.05, 0.018))
		# Large turbine display with stacked concentric industrial rings.
		var px: float = side * 15.1
		var pz := -6.0
		_box(STEEL, Vector3(px, 0.56, pz), Vector3(3.4, 0.4, 2.0))
		_rod(GRAPHITE, Vector3(px, 1.45, pz - 1.0), Vector3(px, 1.45, pz + 1.0), 0.94, 28)
		_rod(TRIM, Vector3(px, 1.45, pz + 0.93), Vector3(px, 1.45, pz + 1.12), 0.76, 28)
		_rod(BLACK, Vector3(px, 1.45, pz + 1.13), Vector3(px, 1.45, pz + 1.18), 0.5, 28)
		for blade in range(10):
			var a := TAU * float(blade) / 10.0
			_rod(SILVER, Vector3(px, 1.45, pz + 1.20),
				Vector3(px + cos(a) * 0.68, 1.45 + sin(a) * 0.68, pz + 1.20), 0.067, 7)

func _build_service_bays() -> void:
	# Background service bays read as automotive maintenance (not showroom).
	for side in [-1.0, 1.0]:
		var x: float = side * 13.1
		var z := -9.6
		for column in [-2.18, 2.18]:
			_box(STEEL, Vector3(x + column, 2.48, z), Vector3(0.53, 4.9, 0.73))
			_box(CYAN, Vector3(x + column, 2.55, z + 0.42), Vector3(0.075, 3.7, 0.07))
			_box(YELLOW, Vector3(x + column, 3.6, z + 0.45), Vector3(0.32, 0.14, 0.06))
		_box(STEEL, Vector3(x, 4.82, z), Vector3(4.95, 0.37, 0.65))
		# A spare hover cell undergoing work: standalone mechanical part, not a second craft.
		_box(STEEL, Vector3(x, 1.76, z), Vector3(3.50, 0.27, 1.9))
		for dx in [-1.3, 1.3]:
			_box(YELLOW, Vector3(x + dx, 1.53, z), Vector3(0.46, 0.24, 1.9))
		_rod(TRIM, Vector3(x, 2.05, z - 0.65), Vector3(x, 2.05, z + 0.65), 0.52, 24)
		_rod(BLACK, Vector3(x, 2.05, z + 0.65), Vector3(x, 2.05, z + 0.78), 0.37, 24)
		for k in range(7):
			var a := TAU * float(k) / 7.0
			_rod(SILVER, Vector3(x, 2.05, z + 0.85),
				Vector3(x + cos(a) * 0.44, 2.05 + sin(a) * 0.44, z + 0.85), 0.045, 6)
		# Floor-mounted diagnostics and hoses.
		_box(BLACK, Vector3(x, 0.16, z + 2.85), Vector3(5.0, 0.12, 0.72))
		_box(CYAN, Vector3(x, 0.21, z + 2.85), Vector3(3.7, 0.03, 0.055))
		for k in range(13):
			var t := float(k) / 12.0
			_rod(AMBER, Vector3(x + 1.7 + 0.6 * sin(t * TAU * 2.0), 3.9 - t * 3.1, z - 0.2),
				Vector3(x + 1.7 + 0.6 * sin((t + 0.06) * TAU * 2.0), 3.9 - (t + 0.06) * 3.1, z - 0.2),
				0.07, 6)

func _build_robot_base() -> void:
	# Rails, articulated service anchor and tool charging pedestal.
	_disc(BLACK, Vector3(7.55, 0.27, -3.85), 1.23, 0.42, 42)
	_disc(STEEL, Vector3(7.55, 0.51, -3.85), 1.07, 0.16, 42)
	_arc(AMBER, Vector3(7.55, 0, -3.85), 1.09, 0.065, 0.59, 0, TAU, 42)
	_box(STEEL, Vector3(7.55, 1.15, -3.85), Vector3(1.2, 1.23, 1.2))
	_box(YELLOW, Vector3(7.55, 1.77, -3.85), Vector3(1.35, 0.20, 1.3))
	for i in range(6):
		var a := TAU * float(i) / 6.0
		_box(CYAN, Vector3(7.55 + cos(a) * 1.07, 0.42, -3.85 + sin(a) * 1.07),
			Vector3(0.17, 0.08, 0.15))
	for i in range(5):
		var x: float = 8.6 + float(i) * 0.44
		_box(YELLOW, Vector3(x, 0.025, -4.9), Vector3(0.28, 0.026, 0.15), -0.52)

func _mesh_between(parent: Node3D, a: Vector3, b: Vector3,
		radius: float, id: String, segments: int = 12) -> MeshInstance3D:
	var mesh := CylinderMesh.new()
	mesh.height = a.distance_to(b)
	mesh.top_radius = radius
	mesh.bottom_radius = radius
	mesh.radial_segments = segments
	var node := MeshInstance3D.new()
	node.mesh = mesh
	node.material_override = _materials[id]
	node.position = (a + b) * 0.5
	node.quaternion = Quaternion(Vector3.UP, (b - a).normalized())
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(node)
	return node

func _robot_joint(parent: Node3D, position: Vector3, radius: float) -> void:
	var joint := SphereMesh.new()
	joint.radius = radius
	joint.height = radius * 2.0
	joint.radial_segments = 16
	joint.rings = 8
	var housing := MeshInstance3D.new()
	housing.mesh = joint
	housing.position = position
	housing.material_override = _materials[STEEL]
	housing.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(housing)
	for side in [-1.0, 1.0]:
		_mesh_between(parent, position + Vector3(0, 0, side * 0.30),
			position + Vector3(0, 0, side * 0.43), radius * 0.54, YELLOW)

func _build_robot() -> void:
	_robot = Node3D.new()
	_robot.name = "ArticulatedServiceRobot"
	_robot.position = Vector3(7.55, 1.85, -3.85)
	add_child(_robot)
	_robot_joint(_robot, Vector3.ZERO, 0.52)
	_mesh_between(_robot, Vector3(0, 0, 0), Vector3(-1.0, 2.18, 0),
		0.33, YELLOW, 14)
	_mesh_between(_robot, Vector3(-0.08, 0.15, 0.37), Vector3(-1.05, 1.91, 0.37),
		0.095, SILVER)
	_robot_joint(_robot, Vector3(-1.0, 2.18, 0), 0.44)
	_mesh_between(_robot, Vector3(-1.0, 2.18, 0), Vector3(-2.95, 1.72, 0.14),
		0.28, STEEL, 14)
	_mesh_between(_robot, Vector3(-1.25, 2.37, -0.18), Vector3(-2.75, 1.9, -0.13),
		0.065, BLACK)
	_robot_joint(_robot, Vector3(-2.95, 1.72, 0.14), 0.38)
	_robot_wrist = Node3D.new()
	_robot_wrist.name = "ScannerWrist"
	_robot_wrist.position = Vector3(-2.95, 1.72, 0.14)
	_robot.add_child(_robot_wrist)
	_mesh_between(_robot_wrist, Vector3.ZERO, Vector3(-0.66, -0.32, 0),
		0.18, YELLOW)
	var scanner_mesh := CylinderMesh.new()
	scanner_mesh.top_radius = 0.29
	scanner_mesh.bottom_radius = 0.36
	scanner_mesh.height = 0.22
	scanner_mesh.radial_segments = 22
	var scanner := MeshInstance3D.new()
	scanner.name = "ScannerHead"
	scanner.mesh = scanner_mesh
	scanner.material_override = _materials[BLACK]
	scanner.position = Vector3(-0.78, -0.44, 0)
	_robot_wrist.add_child(scanner)
	var light := OmniLight3D.new()
	light.position = Vector3(-0.81, -0.64, 0)
	light.light_color = Color("39dfff")
	light.light_energy = 0.7
	light.omni_range = 2.3
	light.shadow_enabled = false
	_robot_wrist.add_child(light)
	_light_rigs.append(light)
	# Scanner aperture as actual emissive geometry, not an image overlay.
	var lens := MeshInstance3D.new()
	var lens_mesh := CylinderMesh.new()
	lens_mesh.top_radius = 0.19
	lens_mesh.bottom_radius = 0.19
	lens_mesh.height = 0.065
	lens_mesh.radial_segments = 18
	lens.mesh = lens_mesh
	lens.material_override = _materials[CYAN]
	lens.position = Vector3(-0.78, -0.58, 0)
	_robot_wrist.add_child(lens)

func _build_task_lights() -> void:
	# Shadow-free local highlights; avoid per-tool and per-bay real-time lights.
	for spec in [
		{"p": Vector3(0, 7.55, 1.2), "c": Color("a9eeff"), "power": 1.25, "range": 14.0},
		{"p": Vector3(-11.0, 5.4, -11.0), "c": Color("60cfff"), "power": 0.7, "range": 9.0},
		{"p": Vector3(11.0, 5.4, -12.0), "c": Color("ffb076"), "power": 0.55, "range": 9.0}
	]:
		var lamp := OmniLight3D.new()
		lamp.position = spec["p"]
		lamp.light_color = spec["c"]
		lamp.light_energy = spec["power"]
		lamp.omni_range = spec["range"]
		lamp.shadow_enabled = false
		add_child(lamp)

func _add_label(text: String, location: Vector3, font_size: int,
		tint: Color, pixel_size: float) -> void:
	var sign := Label3D.new()
	sign.text = text
	sign.font_size = font_size
	sign.pixel_size = pixel_size
	sign.modulate = tint
	sign.outline_size = 2
	sign.position = location
	add_child(sign)

func _build_signage() -> void:
	_box(DARK, Vector3(0, 10.8, -17.1), Vector3(9.2, 2.9, 0.22))
	_box(CYAN, Vector3(0, 9.38, -16.96), Vector3(8.7, 0.07, 0.08))
	_add_label("N / F   ///", Vector3(0, 11.30, -16.94), 84, Color("b8eff8"), 0.009)
	_add_label("N E O N   F O U N D R Y    /    R A C I N G",
		Vector3(0, 10.35, -16.93), 26, Color("7cbad0"), 0.009)
	for side in [-1.0, 1.0]:
		_add_label("BAY 0%d  /  SERVICE" % (2 if side < 0 else 3),
			Vector3(side * 13.2, 8.0, -16.82), 31, Color("75d8ed"), 0.010)
	# Wall diagnostic panels are real emissive physical screens in the room.
	for x in [-4.6, 4.6]:
		_box(BLACK, Vector3(x, 6.85, -17.22), Vector3(2.4, 1.8, 0.11))
		_box(SCREEN, Vector3(x, 6.85, -17.15), Vector3(2.13, 1.55, 0.035))
		_add_label("NF / SCAN", Vector3(x, 7.3, -17.07), 18, Color("c6f9ff"), 0.008)
		for k in range(8):
			var h := 6.25 + float(k) * 0.13
			_box(CYAN, Vector3(x - 0.67 + float(k % 3) * 0.1, h, -17.08),
				Vector3(0.45 + float(k % 4) * 0.14, 0.02, 0.014))
