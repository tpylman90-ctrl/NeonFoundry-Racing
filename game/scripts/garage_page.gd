extends Control
## Full-screen 3D Foundry Lot. Experimental Forge is a preview, not an approved race craft.
signal return_to_hub
signal request_race_control

const CYAN: Color = Color("62d8e8")
const ORANGE: Color = Color("ff8059")
const WHITE: Color = Color("eef4f6")
const MUTED: Color = Color("9aafc0")
const PREVIEW_PATH: String = "res://assets/garage/forge_preview.glb"
const WorkshopScript = preload("res://scripts/garage_workshop.gd")
const Stage03EquipmentScript = preload("res://scripts/garage_stage03_equipment.gd")
const DualJoystickScript = preload("res://scripts/garage_dual_joystick.gd")
const SHELL_STAGE01_PATH: String = "res://assets/garage/shell/shell_stage01.glb"
const DECK_STAGE02_PATH: String = "res://assets/garage/shell/observation_deck_stage02.glb"
const PARTITIONS_STAGE02C_PATH: String = "res://assets/garage/shell/interior_partitions_stage02c.glb"
# The viewing deck is above the front-left diagnostics and cell-swap zone.
const DECK_X0: float = -26.82
const DECK_X1: float = -11.14
const DECK_Z0: float = 3.25
const DECK_Z1: float = 12.05
const DECK_SURFACE_Y: float = 7.20
const DECK_STAIR_X0: float = -26.55
const DECK_STAIR_X1: float = -23.85
const DECK_STAIR_TOP_Z: float = 12.05
const DECK_STAIR_BOTTOM_Z: float = 19.95
const WALK_EYE_HEIGHT: float = 1.75
const INTERNAL_PARTITION_HEIGHT: float = 7.2
const STAGE01_REVIEW: bool = true
const SHELL_HALF_WIDTH: float = 27.0
const SHELL_REAR: float = -23.75
const SHELL_FRONT: float = 20.25
const WALL_WALK_CLEARANCE: float = 2.2

var _world: Node3D
var _camera: Camera3D
var _vehicle_holder: Node3D
var _yaw: float = 2.78
var _pitch: float = 0.21
var _distance: float = 15.0
var _target_yaw: float = 2.78
var _target_pitch: float = 0.21
var _target_distance: float = 15.0
var _dragging: bool = false
var _vehicle_loaded: bool = false
var _detail: Label
var _bay_state: String = "inspect"
var _view_button: Button
var _stage_status: Label
var _walk_mode: bool = false
var _walk_position: Vector3 = Vector3(0, 1.75, 11)
var _walk_yaw: float = 0.0
var _walk_pitch: float = 0.0
var _walk_joysticks: Control
var _walk_toggle: Button
var _workshop: Node3D
var _equipment_panel: PanelContainer
var _equipment_status: Label
var _title_panel: PanelContainer
var _tools_panel: PanelContainer
var _performance_label: Label
var _performance_samples: int = 0
var _garage_viewport: SubViewport
var _quality_detail: bool = false
var _quality_button: Button
var _hero_key: SpotLight3D
var _accent_lights: Array[OmniLight3D] = []
var _garage_environment: Environment
var _reflection_probe: ReflectionProbe
var _contact_shadow_material: ShaderMaterial
var _legacy_room: Node3D
var _shell_stage: Node3D
var _observation_deck: Node3D
var _interior_partitions: Node3D

func _ready() -> void:
	_build_3d_stage()
	_build_overlay()
	_set_graphics_detail(false)
	_refresh_camera(0.016)
	set_process(true)

func _process(delta: float) -> void:
	_performance_samples += 1
	if _performance_label != null and _performance_samples % 18 == 0:
		_performance_label.text = "MOBILE VULKAN  /  FPS %d" % Engine.get_frames_per_second()
	if _walk_mode:
		var move_axis: Vector2 = _walk_joysticks.get("move_axis")
		var look_axis: Vector2 = _walk_joysticks.get("look_axis")
		# WASD/arrow keys remain useful in the Godot editor and desktop CI.
		var keyboard: Vector2 = Vector2.ZERO
		if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
			keyboard.y -= 1.0
		if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN):
			keyboard.y += 1.0
		if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
			keyboard.x -= 1.0
		if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
			keyboard.x += 1.0
		var direction: Vector2 = (move_axis + keyboard).limit_length(1.0)
		# Independent right thumb changes yaw AND vertical eye angle.
		_walk_yaw -= look_axis.x * delta * 2.30
		_walk_pitch = clampf(_walk_pitch - look_axis.y * delta * 1.55, -1.10, 1.10)
		var forward: Vector3 = Vector3(-sin(_walk_yaw), 0.0, -cos(_walk_yaw))
		var strafe: Vector3 = Vector3(cos(_walk_yaw), 0.0, -sin(_walk_yaw))
		var old_walk_position: Vector3 = _walk_position
		_walk_position += (strafe * direction.x - forward * direction.y) * delta * 4.6
		var in_stair_approach: bool = STAGE01_REVIEW and \
			_walk_position.x >= DECK_STAIR_X0 - 0.25 and \
			_walk_position.x <= DECK_STAIR_X1 + 0.25 and \
			_walk_position.z >= DECK_STAIR_TOP_Z - 0.35 and \
			_walk_position.z <= DECK_STAIR_BOTTOM_Z
		var on_upper_deck: bool = STAGE01_REVIEW and old_walk_position.y > WALK_EYE_HEIGHT + 0.2
		var min_x: float = -SHELL_HALF_WIDTH + WALL_WALK_CLEARANCE
		var max_z: float = SHELL_FRONT - WALL_WALK_CLEARANCE
		if in_stair_approach:
			min_x = DECK_STAIR_X0 + 0.15
			max_z = DECK_STAIR_BOTTOM_Z
		elif on_upper_deck:
			min_x = DECK_X0 + 0.35
			max_z = DECK_Z1 - 0.20
		_walk_position.x = clampf(
			_walk_position.x, min_x,
			SHELL_HALF_WIDTH - WALL_WALK_CLEARANCE
		) if STAGE01_REVIEW else clampf(_walk_position.x, -17.0, 17.0)
		_walk_position.z = clampf(
			_walk_position.z, SHELL_REAR + WALL_WALK_CLEARANCE,
			max_z
		) if STAGE01_REVIEW else clampf(_walk_position.z, -15.0, 13.8)
		# The old showroom turntable is hidden during Stage 01. Let testers
		# walk freely across the empty floor. Restore its radius guard later.
		if not STAGE01_REVIEW:
			var ground_radius: float = Vector2(_walk_position.x, _walk_position.z).length()
			if ground_radius < 6.35:
				var safe: Vector2 = Vector2(_walk_position.x, _walk_position.z).normalized() * 6.35
				if ground_radius < 0.01:
					safe = Vector2(0, 6.35)
				_walk_position.x = safe.x
				_walk_position.z = safe.y
		_resolve_deck_walk(old_walk_position)
		_resolve_partition_walk(old_walk_position)
	_refresh_camera(delta)

func _point_inside_horizontal(pos: Vector3, xlo: float, xhi: float,
		zlo: float, zhi: float) -> bool:
	return pos.x >= xlo and pos.x <= xhi and pos.z >= zlo and pos.z <= zhi


func _resolve_deck_walk(previous: Vector3) -> void:
	# Floor-level player can pass underneath the mezzanine. No teleport
	# to its platform when crossing the same X/Z from below.
	if _observation_deck == null or not STAGE01_REVIEW:
		return
	var on_stairs: bool = _point_inside_horizontal(_walk_position,
		DECK_STAIR_X0, DECK_STAIR_X1, DECK_STAIR_TOP_Z, DECK_STAIR_BOTTOM_Z)
	var was_on_stairs: bool = _point_inside_horizontal(previous,
		DECK_STAIR_X0, DECK_STAIR_X1, DECK_STAIR_TOP_Z, DECK_STAIR_BOTTOM_Z)
	var on_deck: bool = _point_inside_horizontal(_walk_position,
		DECK_X0, DECK_X1, DECK_Z0, DECK_Z1)
	var from_upper: bool = previous.y > WALK_EYE_HEIGHT + 0.2
	if on_stairs:
		# Guard against entering halfway up from a side: stairs can be
		# mounted from the lower landing or crossed from the upper deck.
		if not from_upper and not was_on_stairs and (
				_walk_position.z < DECK_STAIR_BOTTOM_Z - 0.7):
			_walk_position = previous
			return
		var fraction: float = clampf(
			(DECK_STAIR_BOTTOM_Z - _walk_position.z) /
			(DECK_STAIR_BOTTOM_Z - DECK_STAIR_TOP_Z), 0.0, 1.0
		)
		_walk_position.y = WALK_EYE_HEIGHT + fraction * DECK_SURFACE_Y
	elif on_deck:
		# Stay below the platform unless the player actually climbed up.
		_walk_position.y = WALK_EYE_HEIGHT + (
			DECK_SURFACE_Y if previous.y > WALK_EYE_HEIGHT + DECK_SURFACE_Y - 0.45
			else 0.0
		)
	elif from_upper:
		# Handrail collision proxy: do not step off a five-metre deck.
		_walk_position = previous
	else:
		_walk_position.y = WALK_EYE_HEIGHT


func _material(color: Color, metal: float = 0.0, rough: float = 0.55, glow: bool = false) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.metallic = metal
	mat.roughness = rough
	if glow:
		mat.emission_enabled = true
		mat.emission = color
		mat.emission_energy_multiplier = 2.3
	return mat

func _box(parent: Node3D, name: String, location: Vector3, dimensions: Vector3, surface: Material) -> MeshInstance3D:
	var part := MeshInstance3D.new()
	part.name = name
	var shape := BoxMesh.new()
	shape.size = dimensions
	part.mesh = shape
	part.material_override = surface
	part.position = location
	parent.add_child(part)
	return part

func _cylinder(parent: Node3D, name: String, location: Vector3, radius: float, height: float, surface: Material) -> MeshInstance3D:
	var part := MeshInstance3D.new()
	part.name = name
	var shape := CylinderMesh.new()
	shape.top_radius = radius
	shape.bottom_radius = radius
	shape.height = height
	shape.radial_segments = 72
	part.mesh = shape
	part.material_override = surface
	part.position = location
	parent.add_child(part)
	return part

func _ring(parent: Node3D, name: String, location: Vector3, inner: float, outer: float, surface: Material) -> void:
	var part := MeshInstance3D.new()
	part.name = name
	var shape := TorusMesh.new()
	shape.inner_radius = inner
	shape.outer_radius = outer
	shape.rings = 96
	shape.ring_segments = 12
	part.mesh = shape
	part.material_override = surface
	part.position = location
	parent.add_child(part)

func _build_3d_stage() -> void:
	var viewport_frame := SubViewportContainer.new()
	viewport_frame.name = "Garage3D"
	viewport_frame.stretch = true
	viewport_frame.mouse_filter = Control.MOUSE_FILTER_PASS
	viewport_frame.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(viewport_frame)

	var viewport := SubViewport.new()
	viewport.name = "GarageViewport"
	viewport.size = Vector2i(1280, 720)
	viewport.scaling_3d_scale = 0.85 if STAGE01_REVIEW else 0.72
	viewport.msaa_3d = Viewport.MSAA_DISABLED if STAGE01_REVIEW else Viewport.MSAA_2X
	viewport.anisotropic_filtering_level = Viewport.ANISOTROPY_4X
	_garage_viewport = viewport
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	viewport_frame.add_child(viewport)

	_world = Node3D.new()
	_world.name = "FoundryLot"
	viewport.add_child(_world)

	var environment_node := WorldEnvironment.new()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("0a1622")
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("b4c5d0")
	environment.ambient_light_energy = 0.56 if STAGE01_REVIEW else 0.48
	environment.reflected_light_source = Environment.REFLECTION_SOURCE_BG
	environment.tonemap_mode = Environment.TONE_MAPPER_ACES
	environment.tonemap_exposure = 0.96
	environment.tonemap_white = 1.6
	environment.fog_enabled = not STAGE01_REVIEW
	environment.fog_mode = Environment.FOG_MODE_DEPTH
	environment.fog_light_color = Color("1a2c3c")
	environment.fog_density = 0.15
	environment.fog_depth_begin = 13.0
	environment.fog_depth_end = 47.0
	environment.fog_depth_curve = 1.25
	environment.glow_enabled = not STAGE01_REVIEW
	environment.glow_hdr_threshold = 0.92
	environment.glow_intensity = 0.70
	environment.glow_bloom = 0.05
	_garage_environment = environment
	environment_node.environment = environment
	_world.add_child(environment_node)

	# Retain old equipment and placements under a separate hidden root.
	# Stage 01 displays only the six new Blender-authored shell surfaces.
	_legacy_room = Node3D.new()
	_legacy_room.name = "LegacyRoomReservedForFutureStages"
	_world.add_child(_legacy_room)
	var graphite := _material(Color("304354"), 0.37, 0.44)
	var tile := _material(Color("384e5e"), 0.44, 0.43)
	var beams := _material(Color("516675"), 0.55, 0.34)
	var cyan := _material(Color("2b97b3"), 0.15, 0.27, true)
	var orange := _material(Color("c14f30"), 0.15, 0.34, true)
	var black := _material(Color("0b141e"), 0.3, 0.6)
	var glass := _material(Color("103c4c"), 0.6, 0.22)

	_box(_legacy_room, "WorkshopFloor", Vector3(0, -0.36, -3), Vector3(46, 0.5, 34), graphite)
	_box(_legacy_room, "BackWall", Vector3(0, 7.4, -18), Vector3(46, 15, 0.8), tile)
	_box(_legacy_room, "LeftWall", Vector3(-20, 7.4, -3), Vector3(0.8, 15, 34), graphite)
	_box(_legacy_room, "RightWall", Vector3(20, 7.4, -3), Vector3(0.8, 15, 34), graphite)
	_box(_legacy_room, "Ceiling", Vector3(0, 14.9, -3), Vector3(46, 0.6, 34), graphite)
	for i in range(9):
		var grid_z: float = -17.0 + float(i) * 4.0
		_box(_legacy_room, "FloorGuide_%02d" % i, Vector3(0, -0.094, grid_z), Vector3(44, 0.015, 0.035), beams)
		_box(_legacy_room, "CeilingRib_%02d" % i, Vector3(0, 14.4, grid_z), Vector3(43, 0.4, 0.5), beams)
	for i in range(11):
		var grid_x: float = -20.0 + float(i) * 4.0
		_box(_legacy_room, "Crossfloor_%02d" % i, Vector3(grid_x, -0.083, -3.5), Vector3(0.035, 0.016, 31), beams)
	for side in [-1, 1]:
		var x: float = float(side) * 13.2
		for segment in range(5):
			var z: float = -15.0 + float(segment) * 6.2
			_box(_legacy_room, "Support_%d_%d" % [side, segment], Vector3(x, 7.3, z), Vector3(0.65, 14, 0.65), beams)
			_box(_legacy_room, "SupportStrip_%d_%d" % [side, segment], Vector3(x - float(side) * 0.35, 4.7, z), Vector3(0.08, 8.2, 0.12), cyan)
		_box(_legacy_room, "UpperCatwalk_%d" % side, Vector3(x + float(side) * 2.8, 6.0, -6.6), Vector3(5.1, 0.45, 18), tile)
		_box(_legacy_room, "CatwalkRail_%d" % side, Vector3(x + float(side) * 0.3, 7.0, -6.6), Vector3(0.12, 1.8, 18), beams)

	for index in range(6):
		var x: float = -15.0 + float(index) * 6.0
		_box(_legacy_room, "WallLightBase_%d" % index, Vector3(x, 9.2, -17.45), Vector3(2.3, 3.2, 0.1), glass)
		_box(_legacy_room, "WallLight_%d" % index, Vector3(x, 9.2, -17.37), Vector3(0.1, 2.8, 0.07), cyan)
	_box(_legacy_room, "BackWallBanner", Vector3(0, 12, -17.5), Vector3(17.4, 1.1, 0.12), black)
	_box(_legacy_room, "BackWallAccent", Vector3(0, 11.3, -17.4), Vector3(17.4, 0.07, 0.12), orange)

	_cylinder(_legacy_room, "TurntableFoundation", Vector3(0, -0.06, 0), 6.2, 0.34, black)
	_cylinder(_legacy_room, "TurntableDeck", Vector3(0, 0.17, 0), 5.8, 0.22, tile)
	_ring(_legacy_room, "InspectionLightRing", Vector3(0, 0.31, 0), 5.55, 5.75, cyan)
	_ring(_legacy_room, "OuterGuideRing", Vector3(0, -0.015, 0), 6.55, 6.62, orange)
	for i in range(24):
		var angle: float = TAU * float(i) / 24.0
		var point := Vector3(cos(angle) * 5.98, 0.27, sin(angle) * 5.98)
		var marker := _box(_legacy_room, "DeckMarker_%02d" % i, point, Vector3(0.12, 0.02, 0.39), orange if i % 6 == 0 else beams)
		marker.rotation.y = -angle
	_vehicle_holder = Node3D.new()
	_vehicle_holder.name = "VehicleDisplay"
	_vehicle_holder.position.y = 0.33
	_world.add_child(_vehicle_holder)
	_load_craft_preview()
	_add_contact_shadow("ChassisContactShadow", Vector3(0, 0.333, 0),
		Vector2(8.7, 7.4), 0.34)
	_add_contact_shadow("PlatformContactShadow", Vector3(0, -0.042, 0),
		Vector2(15.7, 15.7), 0.25)
	_workshop = Node3D.new()
	_workshop.name = "LiveWorkshopEquipment"
	_workshop.set_script(WorkshopScript)
	_world.add_child(_workshop)

	_camera = Camera3D.new()
	_camera.name = "InspectionCamera"
	_camera.fov = 60.0
	_camera.near = 0.08
	_camera.far = 175.0
	_camera.current = true
	_world.add_child(_camera)

	var sunlight := DirectionalLight3D.new()
	sunlight.rotation_degrees = Vector3(-58, -22, 0)
	sunlight.light_energy = 0.83
	sunlight.light_color = Color("d2e6ff")
	_world.add_child(sunlight)
	# One focused shadow-casting key light: real mesh-to-ground and self shadows.
	# The many decorative emissive strips stay shadow-free for mobile.
	var hero_key := SpotLight3D.new()
	hero_key.name = "ForgeHeroShadowKey"
	hero_key.position = Vector3(2.7, 10.2, 3.0)
	hero_key.rotation_degrees = Vector3(-90, 0, 0)
	hero_key.spot_range = 17.5
	hero_key.spot_angle = 67.0
	hero_key.light_energy = 2.2
	hero_key.light_color = Color("e5efff")
	hero_key.shadow_enabled = false
	hero_key.visible = true
	_hero_key = hero_key
	_world.add_child(hero_key)
	for light_spec in [
		{"pos": Vector3(-5, 9, 6), "color": Color("e3f1ff"), "energy": 4.0},
		{"pos": Vector3(6, 11, -4), "color": Color("ffd5ad"), "energy": 3.4},
		{"pos": Vector3(1, 10, 8), "color": Color("a5def4"), "energy": 3.3}
	]:
		var omni := OmniLight3D.new()
		omni.position = light_spec["pos"]
		omni.light_color = light_spec["color"]
		omni.light_energy = light_spec["energy"]
		omni.omni_range = 13.0
		omni.shadow_enabled = false
		omni.visible = _accent_lights.size() == 0
		_accent_lights.append(omni)
		_world.add_child(omni)
	# One-shot box projected reflections only in Detail (never per-frame).
	_reflection_probe = ReflectionProbe.new()
	_reflection_probe.name = "InspectionBayReflection"
	_reflection_probe.position = Vector3(0, 5.6, -2.0)
	_reflection_probe.size = Vector3(19, 11, 20)
	_reflection_probe.box_projection = true
	_reflection_probe.update_mode = ReflectionProbe.UPDATE_ONCE
	_reflection_probe.intensity = 0.48
	_reflection_probe.visible = false
	_world.add_child(_reflection_probe)
	_activate_stage01_shell()
	_activate_stage02_deck()
	_activate_stage02c_partitions()
	_activate_stage03_equipment()

func _activate_stage01_shell() -> void:
	if not STAGE01_REVIEW:
		return
	if not ResourceLoader.exists(SHELL_STAGE01_PATH):
		push_error("STAGE_01_SHELL_MISSING: " + SHELL_STAGE01_PATH)
		return
	var pack: PackedScene = load(SHELL_STAGE01_PATH) as PackedScene
	if pack == null:
		push_error("STAGE_01_SHELL_INVALID_GLTF")
		return
	_shell_stage = pack.instantiate() as Node3D
	_shell_stage.name = "ArchitecturalShell_Stage01"
	_world.add_child(_shell_stage)
	_legacy_room.visible = false
	_vehicle_holder.visible = false
	_workshop.visible = false
	# The previous dramatic grade/post effects caused the last FPS regression;
	# this comparison isolates material and bevel quality only.
	_garage_environment.glow_enabled = false
	_garage_environment.fog_enabled = false
	_garage_environment.ambient_light_energy = 0.56
	_hero_key.visible = false
	_hero_key.shadow_enabled = false
	_reflection_probe.visible = false
	for index in range(_accent_lights.size()):
		_accent_lights[index].visible = index == 0
		_accent_lights[index].omni_range = 25.0
		_accent_lights[index].light_energy = 2.8
	print("NEON_FOUNDRY_STAGE01_SHELL_OK visible=6 surfaces props=hidden")

func _activate_stage02_deck() -> void:
	# Deck is a separately exported glTF scene so our six-wall shell
	# remains immutable, and equipment stays hidden in this stage.
	if not STAGE01_REVIEW:
		return
	if not ResourceLoader.exists(DECK_STAGE02_PATH):
		push_error("STAGE02_VIEWING_DECK_MISSING: " + DECK_STAGE02_PATH)
		return
	var packed: PackedScene = load(DECK_STAGE02_PATH) as PackedScene
	if packed == null:
		push_error("STAGE02_VIEWING_DECK_INVALID_GLTF")
		return
	_observation_deck = packed.instantiate() as Node3D
	_observation_deck.name = "PowerCellSwapObservationDeck"
	_world.add_child(_observation_deck)
	print("NEON_FOUNDRY_STAGE02_DECK_LOADED height=7.20 wall_flush=true door_clear=true location=power-cell-swap")

func _activate_stage02c_partitions() -> void:
	# Internal zone walls are a separate GLB so the authored perimeter shell
	# and its surface materials remain independently rebuildable.
	if not STAGE01_REVIEW:
		return
	if not ResourceLoader.exists(PARTITIONS_STAGE02C_PATH):
		push_error("STAGE02C_PARTITIONS_MISSING: " + PARTITIONS_STAGE02C_PATH)
		return
	var packed: PackedScene = load(PARTITIONS_STAGE02C_PATH) as PackedScene
	if packed == null:
		push_error("STAGE02C_PARTITIONS_INVALID_GLTF")
		return
	_interior_partitions = packed.instantiate() as Node3D
	_interior_partitions.name = "GarageZonePartitionsStage02C"
	_world.add_child(_interior_partitions)
	print("NEON_FOUNDRY_STAGE02C_PARTITIONS_LOADED zones=6 height=7.20 vehicle_portals=8")

func _activate_stage03_equipment() -> void:
	# Equipment is authored as its own procedural layer so the approved shell,
	# deck and partitions remain independently rebuildable.
	var equipment := Node3D.new()
	equipment.name = "GarageEquipment_Stage03"
	equipment.set_script(Stage03EquipmentScript)
	_world.add_child(equipment)
	print("NEON_FOUNDRY_STAGE03_EQUIPMENT_LOADED battery_exchange=zone04 upgrade_bay=zone05")

func _partition_blocks_crossing(previous: Vector3, current: Vector3,
		axis: String, fixed: float, start: float, finish: float,
		portals: PackedVector2Array) -> bool:
	var from_axis: float = previous.x if axis == "x" else previous.z
	var to_axis: float = current.x if axis == "x" else current.z
	var crossed: bool = (from_axis < fixed and to_axis >= fixed) or (
		from_axis > fixed and to_axis <= fixed
	)
	if not crossed or is_equal_approx(from_axis, to_axis):
		return false
	var t: float = (fixed - from_axis) / (to_axis - from_axis)
	var intersection: Vector3 = previous.lerp(current, t)
	var along: float = intersection.z if axis == "x" else intersection.x
	if along < start or along > finish:
		return false
	for opening: Vector2 in portals:
		if along >= opening.x and along <= opening.y:
			return false
	return true

func _resolve_partition_walk(previous: Vector3) -> void:
	if _interior_partitions == null:
		return
	if _walk_position.y >= INTERNAL_PARTITION_HEIGHT + WALK_EYE_HEIGHT:
		return
	var current: Vector3 = _walk_position
	var barriers: Array[Dictionary] = [
		{"axis": "z", "fixed": -5.75, "start": -27.0, "end": 27.0,
			"portals": PackedVector2Array([
				Vector2(-25.9, -20.1), Vector2(-17.9, -12.1), Vector2(-9.9, -4.1),
				Vector2(2.0, 10.0), Vector2(18.0, 24.0)])},
		{"axis": "z", "fixed": 1.25, "start": -27.0, "end": 27.0,
			"portals": PackedVector2Array([
				Vector2(-22.0, -16.0), Vector2(-7.0, 2.0), Vector2(12.0, 19.0)])},
		{"axis": "x", "fixed": -3.0, "start": -23.75, "end": -5.75,
			"portals": PackedVector2Array([Vector2(-12.3, -7.7)])},
		{"axis": "x", "fixed": 15.0, "start": -23.75, "end": -5.75,
			"portals": PackedVector2Array([Vector2(-11.6, -8.4)])},
		{"axis": "x", "fixed": -11.0, "start": 1.25, "end": 20.25,
			"portals": PackedVector2Array([Vector2(10.9, 13.1)])},
		{"axis": "x", "fixed": 6.0, "start": 1.25, "end": 20.25,
			"portals": PackedVector2Array([Vector2(10.9, 13.1)])}
	]
	for wall: Dictionary in barriers:
		if _partition_blocks_crossing(previous, current, wall["axis"],
				wall["fixed"], wall["start"], wall["end"], wall["portals"]):
			_walk_position = previous
			return


func _add_contact_shadow(name: String, location: Vector3,
		dimensions: Vector2, darkness: float) -> void:
	# Mobile lacks SSAO; a single small radial alpha plane is inexpensive.
	if _contact_shadow_material == null:
		_contact_shadow_material = ShaderMaterial.new()
		_contact_shadow_material.shader = load("res://shaders/garage_contact_shadow.gdshader")
	var instance := MeshInstance3D.new()
	instance.name = name
	var plane := PlaneMesh.new()
	plane.size = dimensions
	instance.mesh = plane
	var mat: ShaderMaterial = _contact_shadow_material.duplicate() as ShaderMaterial
	mat.set_shader_parameter("strength", darkness)
	instance.material_override = mat
	instance.position = location
	instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_world.add_child(instance)

func _load_craft_preview() -> void:
	if not ResourceLoader.exists(PREVIEW_PATH):
		_vehicle_loaded = false
		return
	var resource: Resource = load(PREVIEW_PATH)
	if not resource is PackedScene:
		push_warning("Garage experimental craft GLB cannot be instantiated.")
		return
	var model: Node3D = (resource as PackedScene).instantiate() as Node3D
	if model == null:
		push_warning("Garage GLB root is not Node3D.")
		return
	_vehicle_holder.add_child(model)
	model.name = "ForgeExperimental"
	var bb_min := Vector3(100000, 100000, 100000)
	var bb_max := Vector3(-100000, -100000, -100000)
	var mesh_count: int = 0
	for child in model.find_children("*", "MeshInstance3D", true, false):
		var mesh_node := child as MeshInstance3D
		if mesh_node.mesh == null:
			continue
		mesh_count += 1
		var aabb: AABB = mesh_node.get_aabb()
		var local_to_model: Transform3D = model.global_transform.affine_inverse() * mesh_node.global_transform
		for x in range(2):
			for y in range(2):
				for z in range(2):
					var v: Vector3 = local_to_model * (aabb.position + aabb.size * Vector3(float(x), float(y), float(z)))
					bb_min = bb_min.min(v)
					bb_max = bb_max.max(v)
	if mesh_count == 0:
		model.queue_free()
		return
	var extent: Vector3 = bb_max - bb_min
	var widest: float = maxf(extent.x, extent.z)
	var factor: float = clampf(8.25 / maxf(widest, 0.01), 0.10, 3.0)
	model.scale = Vector3.ONE * factor
	var center: Vector3 = (bb_min + bb_max) * 0.5
	model.position = Vector3(-center.x * factor, -bb_min.y * factor + 0.05, -center.z * factor)
	_vehicle_loaded = true
	print("NEON_FOUNDRY_GARAGE_PREVIEW_READY parts=%d" % mesh_count)

func _refresh_camera(delta: float) -> void:
	if _camera == null:
		return
	if _walk_mode:
		_camera.position = _walk_position
		var eye: Vector3 = Vector3(
			-sin(_walk_yaw) * cos(_walk_pitch),
			sin(_walk_pitch),
			-cos(_walk_yaw) * cos(_walk_pitch)
		)
		_camera.look_at(_walk_position + eye, Vector3.UP)
		return
	var blend: float = clampf(delta * 9.0, 0.0, 1.0)
	_yaw = lerp_angle(_yaw, _target_yaw, blend)
	_pitch = lerpf(_pitch, _target_pitch, blend)
	_distance = lerpf(_distance, _target_distance, blend)
	var aim := Vector3(0, 2.45, 0)
	_camera.position = aim + Vector3(sin(_yaw) * cos(_pitch), sin(_pitch), cos(_yaw) * cos(_pitch)) * _distance
	_camera.look_at(aim, Vector3.UP)

func _input(event: InputEvent) -> void:
	if not visible or not _walk_mode or _walk_joysticks == null:
		return
	# ScreenTouch/ScreenDrag events carry independent finger IDs, so using
	# one thumb never steals or releases the other thumb's joystick.
	if event is InputEventScreenTouch or event is InputEventScreenDrag:
		if bool(_walk_joysticks.call("handle_screen_event", event)):
			_dragging = false
			get_viewport().set_input_as_handled()


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event is InputEventScreenDrag:
		# First-person touch-look is now owned by the right joystick, NOT
		# arbitrary swipes which previously conflicted with move touches.
		if _walk_mode:
			return
		_target_yaw -= event.relative.x * 0.007
		_target_pitch = clampf(_target_pitch + event.relative.y * 0.005, -0.15, 1.1)
		get_viewport().set_input_as_handled()
	elif event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			_dragging = event.pressed
		elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_target_distance = maxf(6.8, _target_distance - 1.0)
		elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_target_distance = minf(20.0, _target_distance + 1.0)
	elif event is InputEventMouseMotion and _dragging:
		if _walk_mode:
			if _walk_joysticks != null and (
					int(_walk_joysticks.get("move_finger")) >= 0 or
					int(_walk_joysticks.get("look_finger")) >= 0):
				return
			_walk_yaw -= event.relative.x * 0.006
			_walk_pitch = clampf(_walk_pitch - event.relative.y * 0.004, -1.10, 1.10)
		else:
			_target_yaw -= event.relative.x * 0.007
			_target_pitch = clampf(_target_pitch + event.relative.y * 0.005, -0.15, 1.1)

func _label(value: String, size_px: int, color: Color) -> Label:
	var label := Label.new()
	label.text = value
	label.add_theme_color_override("font_color", color)
	label.add_theme_font_size_override("font_size", size_px)
	return label

func _button(text_value: String, callback: Callable) -> Button:
	var button := Button.new()
	button.text = text_value
	button.custom_minimum_size.y = 52
	button.add_theme_font_size_override("font_size", 17)
	button.add_theme_color_override("font_color", WHITE)
	button.add_theme_color_override("font_hover_color", Color.WHITE)
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.03, 0.15, 0.2, 0.94)
	style.border_width_left = 3
	style.border_color = CYAN
	style.content_margin_left = 15
	style.content_margin_right = 15
	style.set_corner_radius_all(4)
	button.add_theme_stylebox_override("normal", style)
	var hover: StyleBoxFlat = style.duplicate()
	hover.bg_color = Color(0.09, 0.31, 0.39, 1)
	button.add_theme_stylebox_override("hover", hover)
	button.pressed.connect(callback)
	return button

func _panel(left: float, top: float, right: float, bottom: float) -> PanelContainer:
	var panel := PanelContainer.new()
	panel.anchor_left = left
	panel.anchor_top = top
	panel.anchor_right = right
	panel.anchor_bottom = bottom
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.012, 0.027, 0.048, 0.88)
	style.border_color = Color(0.24, 0.7, 0.8, 0.7)
	style.border_width_left = 2
	style.border_width_top = 1
	style.content_margin_left = 19
	style.content_margin_top = 15
	style.content_margin_right = 19
	style.content_margin_bottom = 14
	style.set_corner_radius_all(6)
	panel.add_theme_stylebox_override("panel", style)
	add_child(panel)
	return panel

func _build_overlay() -> void:
	var performance_plate := _panel(0.756, 0.040, 0.975, 0.118)
	_performance_label = _label("MOBILE VULKAN  /  FPS --", 15, CYAN)
	_performance_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	performance_plate.add_child(_performance_label)
	var title_panel := _panel(0.025, 0.028, 0.53, 0.16)
	_title_panel = title_panel
	var head := VBoxContainer.new()
	head.add_theme_constant_override("separation", 2)
	title_panel.add_child(head)
	head.add_child(_label("N / F  MOTORSPORT DIVISION   //   FOUNDRY LOT", 15, CYAN))
	head.add_child(_label(
		"STAGE 02C  /  SIX-ZONE INTERIOR" if STAGE01_REVIEW else "GARAGE  /  VEHICLE INSPECTION",
		28, WHITE))
	head.add_child(_label(
		"ZONE WALLS  •  VEHICLE PORTALS  •  CLEAR AISLES" if STAGE01_REVIEW
		else "FULL 3D SHOWROOM   •   TOUCH & DRAG TO ORBIT",
		14, MUTED))

	var tools_panel := _panel(0.025, 0.19, 0.305, 0.89)
	_tools_panel = tools_panel
	var tools := VBoxContainer.new()
	tools.add_theme_constant_override("separation", 9)
	tools_panel.add_child(tools)
	tools.add_child(_label("ACTIVE CRAFT / PROTOTYPE", 15, ORANGE))
	tools.add_child(_label("FORGE  /  NF-H01", 25, WHITE))
	_stage_status = _label("EXPERIMENTAL MODEL  •  NOT APPROVED" if _vehicle_loaded else "AWAITING CRAFT / EMPTY BAY", 14, MUTED)
	_stage_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	tools.add_child(_stage_status)
	tools.add_child(HSeparator.new())
	tools.add_child(_button("01   INSPECT  /  3D VIEW", _inspect))
	tools.add_child(_button("02   SELECT CRAFT", _show_craft))
	tools.add_child(_button("03   PERFORMANCE  /  TUNING", _show_tuning))
	tools.add_child(_button("04   VISUAL CUSTOMIZATION", _show_cosmetic))
	tools.add_child(HSeparator.new())
	_detail = _label("", 15, MUTED)
	_detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_detail.size_flags_vertical = Control.SIZE_EXPAND_FILL
	tools.add_child(_detail)

	var camera_panel := _panel(0.753, 0.19, 0.974, 0.52)
	var views := VBoxContainer.new()
	views.add_theme_constant_override("separation", 7)
	camera_panel.add_child(views)
	views.add_child(_label("CAMERA  /  VIEWPORT", 16, CYAN))
	var angle_row := HBoxContainer.new()
	angle_row.add_theme_constant_override("separation", 6)
	views.add_child(angle_row)
	for spec in [
		{"text": "3/4", "a": 2.78, "p": 0.21, "d": 15.0},
		{"text": "SIDE", "a": 1.57, "p": 0.15, "d": 12.3},
		{"text": "TOP", "a": 0.0, "p": 1.22, "d": 15.4}
	]:
		var b: Button = _button(str(spec["text"]), _move_view.bind(float(spec["a"]), float(spec["p"]), float(spec["d"])))
		b.custom_minimum_size.y = 43
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		angle_row.add_child(b)
	var zoom_row := HBoxContainer.new()
	zoom_row.add_theme_constant_override("separation", 6)
	views.add_child(zoom_row)
	var minus: Button = _button("−  ZOOM", _zoom.bind(1.8))
	var plus: Button = _button("+  ZOOM", _zoom.bind(-1.8))
	zoom_row.add_child(minus)
	zoom_row.add_child(plus)
	minus.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	plus.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_walk_toggle = _button("WALK THE GARAGE", _toggle_walk)
	views.add_child(_walk_toggle)

	_equipment_panel = _panel(0.753, 0.515, 0.974, 0.877)
	var equipment := VBoxContainer.new()
	equipment.add_theme_constant_override("separation", 7)
	_equipment_panel.add_child(equipment)
	equipment.add_child(_label("SERVICE BAY  /  EQUIPMENT", 15, ORANGE))
	equipment.add_child(_button("OPERATE LIFT ARMS", _operate_lifts))
	equipment.add_child(_button("ROBOT SCANNER  /  TOGGLE", _toggle_scanner))
	_quality_button = _button("GRAPHICS  /  BALANCED", _toggle_graphics_quality)
	_quality_button.custom_minimum_size.y = 40
	equipment.add_child(_quality_button)
	_equipment_status = _label("AUTO SERVICE  /  STANDBY", 13, MUTED)
	_equipment_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	equipment.add_child(_equipment_status)
	_refresh_equipment_status()

	# Minimal draw-only overlay: two thumbsticks rather than four buttons.
	# They sit above the bottom navigation bar and outside camera controls.
	_walk_joysticks = DualJoystickScript.new() as Control
	_walk_joysticks.name = "DualThumbWalkControls"
	_walk_joysticks.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_walk_joysticks.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_walk_joysticks)
	_walk_joysticks.visible = false

	var bottom := _panel(0.327, 0.89, 0.977, 0.978)
	var action_row := HBoxContainer.new()
	action_row.add_theme_constant_override("separation", 12)
	bottom.add_child(action_row)
	var back := _button("‹   MAIN HUB", func() -> void: return_to_hub.emit())
	var spin := _button("⟳   RESET VIEW", func() -> void: _move_view(2.78, 0.21, 15.0))
	var race := _button("RACE CONTROL   ›", func() -> void: request_race_control.emit())
	for b in [back, spin, race]:
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		action_row.add_child(b)
	_inspect()
	if STAGE01_REVIEW:
		_tools_panel.visible = false
		_equipment_panel.visible = false

func _inspect() -> void:
	_bay_state = "inspect"
	_detail.text = "Rotate with a finger, switch angles, or zoom in to inspect the craft and hangar. The Forge GLB displayed here is an EXPERIMENTAL work-in-progress."

func _show_craft() -> void:
	_bay_state = "select"
	_detail.text = "CRAFT SELECT\nForge / NF-H01 — test slot only. Fleet ownership and car switching will be enabled after approved craft assets are imported."

func _show_tuning() -> void:
	_bay_state = "tuning"
	_detail.text = "TUNING WORKSHOP\nTarget systems: lift, thrust, steering, damping, braking and boost. Live controls will be enabled when performance data and physics exist."

func _show_cosmetic() -> void:
	_bay_state = "customize"
	_detail.text = "CUSTOMIZATION BAY\nFuture systems: paint, material layers, armor accents, decals and propulsion FX. No model textures are changed in this prototype."

func _move_view(yaw: float, pitch: float, distance: float) -> void:
	if _walk_mode:
		_toggle_walk()
	_target_yaw = yaw
	_target_pitch = pitch
	_target_distance = distance

func _toggle_walk() -> void:
	_walk_mode = not _walk_mode
	_walk_joysticks.call("release_all")
	_walk_joysticks.visible = _walk_mode
	_dragging = false
	if _walk_mode:
		_walk_pitch = 0.0
	_equipment_panel.visible = not _walk_mode and not STAGE01_REVIEW
	_title_panel.visible = not _walk_mode
	_tools_panel.visible = not _walk_mode and not STAGE01_REVIEW
	_walk_toggle.text = "RETURN TO INSPECTION" if _walk_mode else "WALK THE GARAGE"
	_detail.text = "WALKAROUND MODE\nLeft thumb moves/strafe; right thumb pans and looks up/down. Both sticks support independent fingers." if _walk_mode else "INSPECTION MODE\nTouch-drag to orbit around the model. Use the camera presets for detail study."

func _refresh_equipment_status() -> void:
	if _workshop != null and _equipment_status != null:
		_equipment_status.text = str(_workshop.call("get_equipment_status"))

func _operate_lifts() -> void:
	if _workshop != null:
		_workshop.call("toggle_lifts")
		_refresh_equipment_status()

func _toggle_scanner() -> void:
	if _workshop != null:
		_workshop.call("set_scanner_active", not bool(_workshop.get("_scanner_enabled")))
		_refresh_equipment_status()

func _set_graphics_detail(enabled: bool) -> void:
	_quality_detail = enabled
	if _garage_viewport != null:
		_garage_viewport.scaling_3d_scale = 1.0 if enabled else (0.85 if STAGE01_REVIEW else 0.72)
		_garage_viewport.msaa_3d = (
			Viewport.MSAA_2X if enabled or not STAGE01_REVIEW
			else Viewport.MSAA_DISABLED
		)
		_garage_viewport.anisotropic_filtering_level = (
			Viewport.ANISOTROPY_8X if enabled else Viewport.ANISOTROPY_4X
		)
	if _garage_environment != null:
		_garage_environment.ambient_light_energy = 0.40 if enabled else 0.48
		_garage_environment.glow_intensity = 1.08 if enabled else 0.70
		_garage_environment.glow_bloom = 0.09 if enabled else 0.05
		_garage_environment.fog_density = 0.25 if enabled else 0.15
		if STAGE01_REVIEW:
			_garage_environment.glow_enabled = false
			_garage_environment.fog_enabled = false
	if _hero_key != null:
		_hero_key.visible = not STAGE01_REVIEW
		_hero_key.shadow_enabled = enabled and not STAGE01_REVIEW
	if _reflection_probe != null:
		_reflection_probe.visible = enabled and not STAGE01_REVIEW
	for index in range(_accent_lights.size()):
		_accent_lights[index].visible = index == 0 if STAGE01_REVIEW else enabled or index == 0
		_accent_lights[index].omni_range = 25.0 if STAGE01_REVIEW else (15.0 if enabled else 13.0)
	if _workshop != null:
		_workshop.call("set_material_detail", enabled)
		_workshop.call("set_mobile_quality", enabled)
	if _quality_button != null:
		_quality_button.text = "GRAPHICS  /  DETAIL" if enabled else "GRAPHICS  /  BALANCED"
	print("NEON_FOUNDRY_GARAGE_GRAPHICS profile=%s scale=%.2f" % [
		"detail" if enabled else "balanced",
		_garage_viewport.scaling_3d_scale
	])

func _toggle_graphics_quality() -> void:
	_set_graphics_detail(not _quality_detail)

func _zoom(amount: float) -> void:
	_target_distance = clampf(_target_distance + amount, 6.8, 20.0)

func navigate_back() -> void:
	return_to_hub.emit()
