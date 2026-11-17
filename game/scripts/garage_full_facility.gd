extends Node3D
## Full Foundry Lot dressing. All fixed architecture props are merged into a
## handful of material batches so the walkable garage stays light on mobile.
## The three vehicle lift pads are deliberately kept empty.

const MAT_IDS := ["graphite", "alloy", "paint", "cyan", "amber", "screen", "glass", "rubber", "white"]
var _mat: Dictionary = {}
var _surface: Dictionary = {}
var _lights: Array[OmniLight3D] = []

func _ready() -> void:
	_make_materials()
	for key in MAT_IDS:
		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		_surface[key] = st
	_bays()
	_assembly()
	_command()
	_parts_depot()
	_gallery()
	_ceiling_lights()
	_commit()
	_add_lights()
	print("NEON_FOUNDRY_FULL_GARAGE_READY zones=6 empty_vehicle_bays=3")

func _make_materials() -> void:
	_mat = {
		"graphite": _material(Color("101b27"), .46, .49),
		"alloy": _material(Color("8195a2"), .72, .30),
		"paint": _material(Color("263d4c"), .42, .39),
		"cyan": _material(Color("48d9eb"), .18, .24, Color("28bfdc"), 1.4),
		"amber": _material(Color("ffad56"), .28, .28, Color("ed692c"), 1.2),
		"screen": _material(Color("06202c"), .08, .24, Color("1ca0bd"), .6),
		"glass": _material(Color("16404d"), .48, .18),
		"rubber": _material(Color("080e14"), .04, .75),
		"white": _material(Color("d9e6e9"), .38, .28)
	}

func _material(color: Color, metal: float, rough: float, emission: Color = Color.BLACK,
		energy: float = 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.metallic = metal
	m.roughness = rough
	if energy > 0.0:
		m.emission_enabled = true
		m.emission = emission
		m.emission_energy_multiplier = energy
	return m

func _tri(key: String, a: Vector3, b: Vector3, c: Vector3, n: Vector3) -> void:
	var s: SurfaceTool = _surface[key]
	for v in [a, c, b]:
		s.set_normal(n)
		s.add_vertex(v)

func _quad(key: String, a: Vector3, b: Vector3, c: Vector3, d: Vector3) -> void:
	var n := (b - a).cross(c - a).normalized()
	_tri(key, a, b, c, n)
	_tri(key, a, c, d, n)

func _box(key: String, p: Vector3, size: Vector3, yaw: float = 0.0) -> void:
	var bx := Vector3(cos(yaw), 0, -sin(yaw)) * size.x * .5
	var by := Vector3.UP * size.y * .5
	var bz := Vector3(sin(yaw), 0, cos(yaw)) * size.z * .5
	var a := p - bx - by - bz
	var b := p - bx - by + bz
	var c := p - bx + by - bz
	var d := p - bx + by + bz
	var e := p + bx - by - bz
	var f := p + bx - by + bz
	var g := p + bx + by - bz
	var h := p + bx + by + bz
	_quad(key, e, g, h, f)
	_quad(key, a, b, d, c)
	_quad(key, c, d, h, g)
	_quad(key, a, e, f, b)
	_quad(key, b, f, h, d)
	_quad(key, a, c, g, e)

func _rod(key: String, a: Vector3, b: Vector3, radius: float, segments: int = 10) -> void:
	var axis := b - a
	if axis.length_squared() < .0001:
		return
	var direction := axis.normalized()
	var helper := Vector3.UP if absf(direction.y) < .92 else Vector3.RIGHT
	var tangent := direction.cross(helper).normalized()
	var bitangent := tangent.cross(direction).normalized()
	for i in range(segments):
		var t0 := TAU * float(i) / float(segments)
		var t1 := TAU * float(i + 1) / float(segments)
		var p0 := a + radius * (tangent * cos(t0) + bitangent * sin(t0))
		var p1 := a + radius * (tangent * cos(t1) + bitangent * sin(t1))
		var p2 := b + radius * (tangent * cos(t1) + bitangent * sin(t1))
		var p3 := b + radius * (tangent * cos(t0) + bitangent * sin(t0))
		_quad(key, p0, p1, p2, p3)

func _ring(key: String, center: Vector3, radius: float, width: float, segments: int = 48) -> void:
	for i in range(segments):
		var a := TAU * float(i) / float(segments)
		var b := TAU * float(i + 1) / float(segments)
		var p0 := Vector3(cos(a) * radius, center.y, sin(a) * radius) + center
		var p1 := Vector3(cos(b) * radius, center.y, sin(b) * radius) + center
		_rod(key, p0, p1, width, 6)

func _label(value: String, p: Vector3, size: int = 36, color: Color = Color("a8eff7"),
		face_into_room: bool = false) -> void:
	var label := Label3D.new()
	label.text = value
	label.font_size = size
	label.pixel_size = .008
	label.modulate = color
	label.outline_size = 4
	label.outline_modulate = Color("071019")
	label.position = p
	if face_into_room:
		label.rotation.y = PI
	add_child(label)

func _machine(p: Vector3, title: String, color: String = "cyan", scale: float = 1.0) -> void:
	# Layered enclosure, inset service window, chamfer-like front cheeks,
	# ventilation and a physically modeled operator display.
	var w := 2.4 * scale
	var h := 2.55 * scale
	var d := 1.55 * scale
	_box("graphite", p + Vector3(0, h * .48, 0), Vector3(w + .20, h + .12, d + .16))
	_box("paint", p + Vector3(0, h * .52, d * .5), Vector3(w, h, .09))
	_box("alloy", p + Vector3(-w * .5 + .09, h * .50, d * .5 + .06), Vector3(.12, h * .92, .09))
	_box("alloy", p + Vector3(w * .5 - .09, h * .50, d * .5 + .06), Vector3(.12, h * .92, .09))
	_box("glass", p + Vector3(0, h * .69, d * .5 + .07), Vector3(w * .66, h * .37, .07))
	_box("screen", p + Vector3(0, h * .69, d * .5 + .12), Vector3(w * .56, h * .25, .025))
	_box(color, p + Vector3(0, .18 * scale, d * .5 + .09), Vector3(w * .53, .07 * scale, .025))
	for i in range(5):
		_box("alloy", p + Vector3(-w * .32 + float(i) * w * .16, h * .29, d * .5 + .12),
			Vector3(.045, h * .17, .025))
	for side in [-1.0, 1.0]:
		_box("rubber", p + Vector3(side * w * .34, -.025, 0), Vector3(.18, .16, d * .88))
		_box("amber" if side < 0 else "cyan", p + Vector3(side * w * .41, h * .85, d * .5 + .08),
			Vector3(.12, .08, .04))
	_label(title, p + Vector3(0, h + .35, d * .5), 22, Color("dcf7fb"))

func _robot_arm(base: Vector3, direction: float = 1.0, reach: float = 1.0) -> void:
	# Six-axis industrial manipulator with broad cast base, machined joints,
	# twin actuator rods and a tool head. Kept outside all circulation aisles.
	_box("rubber", base + Vector3(0, .12, 0), Vector3(1.25, .24, 1.18))
	_box("alloy", base + Vector3(0, .28, 0), Vector3(.86, .12, .82))
	_ring("amber", base + Vector3(0, .36, 0), .40, .045, 24)
	var pivot := base + Vector3(0, .52, 0)
	var shoulder := pivot + Vector3(direction * .45, 1.18, 0)
	var elbow := shoulder + Vector3(direction * 1.00 * reach, .28, .12)
	var wrist := elbow + Vector3(direction * .72 * reach, -.35, .08)
	_rod("paint", pivot, shoulder, .24, 8)
	_rod("alloy", pivot + Vector3(0, .08, .16), shoulder + Vector3(0, .08, .16), .064, 8)
	_rod("amber", pivot + Vector3(0, .08, -.16), shoulder + Vector3(0, .08, -.16), .064, 8)
	_ring("alloy", shoulder, .30, .065, 24)
	_rod("paint", shoulder, elbow, .20, 8)
	_rod("cyan", shoulder + Vector3(0, .02, .15), elbow + Vector3(0, .02, .15), .05, 8)
	_ring("alloy", elbow, .24, .052, 24)
	_rod("paint", elbow, wrist, .13, 8)
	_box("alloy", wrist, Vector3(.30, .26, .26))
	for s in [-1.0, 1.0]:
		_rod("white", wrist + Vector3(0, -.07, s * .10), wrist + Vector3(direction * .34, -.24, s * .17), .035, 7)
	_box("cyan", wrist + Vector3(direction * .23, -.22, 0), Vector3(.22, .08, .19))

func _bays() -> void:
	# Three immaculate but visibly empty service footprints. Lifts and scanning
	# gantries flank each pad; the center remains completely clear for craft.
	for bay in range(3):
		var x := -23.0 + float(bay) * 8.0
		var z := -14.5
		for side in [-1.0, 1.0]:
			_box("cyan", Vector3(x + side * 3.28, .025, z), Vector3(.055, .024, 10.8))
		for side in [-1.0, 1.0]:
			_box("amber", Vector3(x, .024, z + side * 5.25), Vector3(6.55, .023, .055))
		# Four compact lift posts remain at the pad edges, leaving an empty center.
		for sx in [-1.0, 1.0]:
			for sz in [-1.0, 1.0]:
				var post := Vector3(x + sx * 3.0, 2.28, z + sz * 4.72)
				_box("graphite", post, Vector3(.38, 4.5, .50))
				_box("alloy", post + Vector3(0, .0, .27), Vector3(.08, 3.7, .045))
				_box("amber", post + Vector3(0, 3.9, .02), Vector3(.44, .09, .52))
				_box("paint", post + Vector3(-sx * .62, .35, 0), Vector3(.95, .12, .22))
				_box("alloy", post + Vector3(-sx * .98, .43, 0), Vector3(.15, .14, .28))
		# Rear gantry and diagnostic arch sit clear of the future vehicle envelope.
		_box("paint", Vector3(x, 5.5, z - 5.35), Vector3(6.6, .34, .42))
		_box("cyan", Vector3(x, 5.29, z - 5.35), Vector3(5.8, .07, .10))
		for dx in [-2.85, 2.85]:
			_box("paint", Vector3(x + dx, 4.3, z - 5.35), Vector3(.25, 2.25, .36))
		for i in range(5):
			_box("white", Vector3(x - 1.6 + float(i) * .8, 5.27, z - 5.35),
				Vector3(.46, .025, .065))
		_label("EMPTY SERVICE PAD  /  %02d" % (bay + 1), Vector3(x, .12, z + 5.65), 23,
			Color("91dce7"))
	# Charge rails and isolated battery carts at rear wall, outside footprints.
	for x in [-25.2, -20.6, -12.2, -8.0, -4.7]:
		_machine(Vector3(x, .06, -22.25), "LIFT / CHARGE" if x < -11 else "CELL TEST", "cyan", .72)

func _assembly() -> void:
	# Two separated robot cells, guarded with transparent wall segments and
	# fed by a low transfer conveyor. The center aisle toward the door stays open.
	for cell in range(2):
		var cx := 1.6 + float(cell) * 8.5
		var cz := -14.5
		_box("rubber", Vector3(cx, .08, cz), Vector3(6.6, .16, 6.6))
		for side in [-1.0, 1.0]:
			_box("amber", Vector3(cx + side * 3.1, 1.85, cz), Vector3(.06, 3.5, 6.2))
			_box("glass", Vector3(cx + side * 3.05, 1.8, cz), Vector3(.035, 3.25, 5.8))
			_box("alloy", Vector3(cx + side * 3.1, 3.55, cz), Vector3(.12, .10, 6.25))
		_robot_arm(Vector3(cx - 1.85, .13, cz), 1.0 if cell == 0 else -1.0, .92)
		_machine(Vector3(cx + 1.7, .10, cz - 1.6), "LASER CELL" if cell == 0 else "SEAM WELD", "amber", .70)
		_box("cyan", Vector3(cx, .22, cz + 2.1), Vector3(3.6, .12, 1.15))
		for i in range(7):
			_box("alloy", Vector3(cx - 1.45 + float(i) * .48, .34, cz + 2.1), Vector3(.07, .12, .9))
	_box("paint", Vector3(5.8, .58, -20.8), Vector3(13.8, 1.0, 1.3))
	_box("alloy", Vector3(5.8, 1.12, -20.8), Vector3(12.9, .12, 1.12))
	for i in range(18):
		var x := -.35 + float(i) * .72
		_rod("rubber", Vector3(x, .36, -20.8), Vector3(x, .78, -20.8), .22, 12)
		_ring("alloy", Vector3(x, .80, -20.8), .21, .025, 14)
	for x in [-1.4, 3.2, 8.1, 13.0]:
		_box("paint", Vector3(x, 4.0, -22.8), Vector3(3.4, 3.4, .30))
		_box("screen", Vector3(x, 4.0, -22.62), Vector3(3.08, 2.65, .05))
		_box("cyan", Vector3(x, 5.26, -22.57), Vector3(2.62, .045, .025))
		_label("ASSEMBLY / LIVE", Vector3(x, 4.85, -22.54), 17, Color("cff9ff"), true)
	_label("ROBOTIC ASSEMBLY  /  AUTOMATED CELL", Vector3(5.5, 7.9, -22.2), 37,
		Color("aff4ff"), true)

func _command() -> void:
	# HQ uses a warm-lit command wall and three individual operator stations,
	# not a mass of identical consoles.
	_box("graphite", Vector3(21.0, 4.7, -23.15), Vector3(10.8, 7.6, .48))
	_box("screen", Vector3(21.0, 5.0, -22.88), Vector3(9.95, 5.25, .08))
	_box("cyan", Vector3(21.0, 7.7, -22.80), Vector3(9.3, .08, .04))
	for i in range(9):
		var x := 16.8 + float(i) * 1.05
		var y := 3.0 + 1.5 * absf(sin(float(i) * .73))
		_box("cyan" if i % 3 else "amber", Vector3(x, y, -22.77), Vector3(.12, .10 + y * .25, .035))
		_box("white", Vector3(x, 2.2, -22.77), Vector3(.045, .42, .03))
	_label("NEON FOUNDRY  /  RACE OPERATIONS", Vector3(21.0, 8.15, -22.73), 31,
		Color("d9f8fb"), true)
	for i in range(3):
		var x := 17.2 + float(i) * 3.8
		_box("paint", Vector3(x, .91, -13.7), Vector3(3.2, 1.6, .95))
		_box("alloy", Vector3(x, 1.74, -13.7), Vector3(3.35, .13, 1.0))
		_box("screen", Vector3(x, 2.48, -14.03), Vector3(2.35, 1.16, .14), -.12)
		_box("cyan", Vector3(x, 2.44, -13.94), Vector3(2.05, .04, .025))
		_box("rubber", Vector3(x, .58, -12.8), Vector3(.82, .32, .78))
		_box("alloy", Vector3(x, .95, -12.8), Vector3(.84, .12, .82))
		_label("OPS  /  0%d" % (i + 1), Vector3(x, 2.0, -13.58), 15, Color("d0f7fb"))
	for i in range(4):
		var x := 16.2 + float(i) * 3.15
		_box("paint", Vector3(x, 5.8, -9.2), Vector3(2.4, 1.65, .15))
		_box("screen", Vector3(x, 5.8, -9.1), Vector3(2.2, 1.42, .035))
		_box("cyan", Vector3(x, 6.45, -9.06), Vector3(1.8, .035, .02))
	_label("CONTROL / STRATEGY", Vector3(21.2, 7.85, -22.75), 32,
		Color("b9f4fb"), true)

func _battery_works() -> void:
	# Battery production/test line beneath the observation deck uses a compact
	# footprint, distinct machines and two robot stations with clear walk lanes.
	var spots: Array[Vector3] = [Vector3(-20.5, .08, 5.2), Vector3(-15.8, .08, 5.2),
		Vector3(-20.5, .08, 9.6), Vector3(-15.8, .08, 9.6)]
	var names: Array[String] = ["CELL SEAL", "COOLANT LOOP", "CAPACITY TEST", "LASER QA"]
	for i in range(spots.size()):
		_machine(spots[i], names[i], "amber" if i % 2 == 0 else "cyan", .76)
	for x in [-19.0, -14.4]:
		_robot_arm(Vector3(x, .12, 14.05), 1.0 if x < -17 else -1.0, .68)
		_box("rubber", Vector3(x, .38, 15.65), Vector3(3.5, .20, 1.2))
		_box("alloy", Vector3(x, .57, 15.65), Vector3(3.3, .12, 1.05))
		for n in range(3):
			_box("screen", Vector3(x - .85 + float(n) * .85, .74, 15.55), Vector3(.68, .18, .04))
		_box("amber", Vector3(x, .17, 16.38), Vector3(3.2, .06, .07))
	# Safe cell storage pod: real framed glass, individually seated modules.
	_box("paint", Vector3(-17.0, 1.55, 18.45), Vector3(9.2, 3.1, .24))
	_box("glass", Vector3(-17.0, 1.65, 18.30), Vector3(8.65, 2.75, .045))
	for i in range(8):
		var x := -20.8 + float(i) * 1.1
		_box("graphite", Vector3(x, .84, 18.18), Vector3(.72, 1.35, .55))
		_box("alloy", Vector3(x, 1.55, 18.48), Vector3(.77, .08, .62))
		_box("cyan" if i % 2 else "amber", Vector3(x, 1.56, 18.12), Vector3(.44, .045, .035))
		_box("graphite", Vector3(x, 2.40, 18.18), Vector3(.72, .62, .55))
		_box("cyan", Vector3(x, 2.56, 18.12), Vector3(.43, .035, .03))
	_label("ENERGY STORAGE  /  ISOLATED CELLS", Vector3(-17.0, 3.65, 18.32), 22)
	_label("CELL SWAP  /  POWER SYSTEMS", Vector3(-18.0, 4.45, 2.7), 28)

func _parts_depot() -> void:
	# Deep storage shelves sit against the perimeter and keep a broad central aisle.
	for rack in range(3):
		var x := -8.3 + float(rack) * 5.8
		for side in [-.1, .1]:
			_box("alloy", Vector3(x + side, 2.55, 17.55), Vector3(.13, 4.9, .20))
		for y in [0.58, 1.75, 2.92, 4.09]:
			_box("paint", Vector3(x, y, 17.55), Vector3(5.15, .12, 1.0))
			_box("cyan", Vector3(x, y + .09, 17.04), Vector3(4.90, .04, .055))
		for tier in range(3):
			for bin in range(5):
				var bx := x - 1.88 + float(bin) * .94
				var yy := .95 + float(tier) * 1.17
				_box("graphite", Vector3(bx, yy, 17.45), Vector3(.82, .60, .66))
				_box("amber" if (bin + tier) % 4 == 0 else "screen",
					Vector3(bx, yy, 17.105), Vector3(.68, .36, .04))
				_box("white", Vector3(bx, yy + .12, 17.077), Vector3(.40, .035, .018))
	_label("PARTS DEPOT  /  INVENTORY CONTROL", Vector3(-2.5, 6.8, 19.7), 28)
	# Mobile robot carts / low materials trolleys parked against the end bay.
	for p in [Vector3(-8.8, .58, 5.2), Vector3(3.8, .58, 5.2)]:
		_box("rubber", p, Vector3(1.55, .94, 1.15))
		_box("alloy", p + Vector3(0, .53, 0), Vector3(1.68, .12, 1.22))
		for dx in [-.53, .53]:
			_ring("alloy", p + Vector3(dx, -.39, .55), .13, .035, 16)
		_box("cyan", p + Vector3(0, .35, .61), Vector3(.85, .07, .04))

func _gallery() -> void:
	# The front showroom is intentionally an empty presentation floor: no car,
	# placeholder silhouette or occupied stand. Atmosphere comes from the room.
	for x in [8.5, 13.0, 17.5, 22.0, 26.0]:
		_box("paint", Vector3(x, 6.5, 19.48), Vector3(3.8, 7.2, .22))
		_box("glass", Vector3(x, 6.5, 19.33), Vector3(3.35, 6.7, .035))
		_box("cyan", Vector3(x, 10.1, 19.27), Vector3(2.95, .06, .03))
		for y in [4.5, 5.5, 6.5, 7.5, 8.5]:
			_box("screen", Vector3(x, y, 19.27), Vector3(2.7, .028, .024))
	_label("NEON FOUNDRY  /  DRIVER EXPERIENCE", Vector3(17.4, 11.3, 19.20), 38,
		Color("e4fbfd"), true)
	# Low, comfortable seating at gallery edges; viewing route remains clear.
	for x in [8.8, 24.2]:
		_box("graphite", Vector3(x, .56, 4.1), Vector3(3.5, .72, 1.0))
		_box("paint", Vector3(x, .96, 4.52), Vector3(3.4, .80, .18))
		for dx in [-1.25, 1.25]:
			_box("alloy", Vector3(x + dx, .28, 3.85), Vector3(.10, .50, .10))
	for x in [8.6, 25.0]:
		_box("paint", Vector3(x, 1.35, 16.2), Vector3(2.6, 2.7, .65))
		_box("screen", Vector3(x, 1.48, 15.85), Vector3(2.25, 1.75, .045))
		_box("amber", Vector3(x, .12, 15.55), Vector3(1.8, .04, .07))
		_label("WELCOME  /  01" if x < 12 else "RACE INFO", Vector3(x, 2.36, 15.79), 17)
	# Thin luminous routes only around the perimeter; center remains open.
	for side in [-1.0, 1.0]:
		_box("cyan", Vector3(16.5, .026, 2.75), Vector3(19.0, .018, .035))
		_box("amber", Vector3(16.5, .026, 19.95), Vector3(19.0, .018, .035))

func _ceiling_lights() -> void:
	# Recessed luminous blades, repeated with deliberate rhythm across zones.
	for z in [-21.3, -17.6, -13.9, -10.2, -6.5, -2.8, 2.0, 6.0, 10.0, 14.0, 18.0]:
		for x in [-18.0, -10.0, -2.0, 6.0, 14.0, 22.0]:
			_box("graphite", Vector3(x, 15.65, z), Vector3(5.4, .24, .74))
			_box("white", Vector3(x, 15.50, z), Vector3(4.55, .055, .25))
			_box("cyan", Vector3(x, 15.45, z + .18), Vector3(3.55, .035, .045))
	# A few darker bridge girders make the long-span room feel engineered.
	for x in [-25.2, -13.0, -.8, 11.4, 23.6]:
		_box("graphite", Vector3(x, 15.82, -1.75), Vector3(.38, .34, 43.2))
		_box("alloy", Vector3(x, 15.58, -1.75), Vector3(.09, .06, 42.0))

func _add_lights() -> void:
	var specs: Array[Dictionary] = [
		{"p": Vector3(-20, 10.2, -14), "c": Color("6ddcf7"), "e": 1.4, "r": 11.0},
		{"p": Vector3(5, 10.1, -15), "c": Color("ffc486"), "e": 1.3, "r": 10.0},
		{"p": Vector3(20, 9.5, -14), "c": Color("79d8ff"), "e": 1.4, "r": 10.0},
		{"p": Vector3(-18, 8.0, 7), "c": Color("62ddf2"), "e": 1.0, "r": 9.0},
		{"p": Vector3(-16, 8.0, 16), "c": Color("ffb76d"), "e": 1.0, "r": 8.0},
		{"p": Vector3(-2, 8.0, 11), "c": Color("63d7eb"), "e": .9, "r": 9.0},
		{"p": Vector3(17, 8.0, 11), "c": Color("ffca9c"), "e": 1.1, "r": 10.0}
	]
	for s in specs:
		var light := OmniLight3D.new()
		light.position = s["p"]
		light.light_color = s["c"]
		light.light_energy = s["e"]
		light.omni_range = s["r"]
		light.shadow_enabled = false
		add_child(light)
		_lights.append(light)

func _commit() -> void:
	for key in MAT_IDS:
		var st: SurfaceTool = _surface[key]
		var mesh := st.commit()
		if mesh.get_surface_count() == 0:
			continue
		var node := MeshInstance3D.new()
		node.name = "Facility_%s" % key
		node.mesh = mesh
		node.material_override = _mat[key]
		node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(node)

func set_mobile_quality(detail: bool) -> void:
	for i in range(_lights.size()):
		_lights[i].visible = detail or i == 0 or i == 2 or i == 4
		_lights[i].light_energy = 1.4 if detail else .9
