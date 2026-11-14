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

var _world: Node3D
var _camera: Camera3D
var _vehicle_holder: Node3D
var _yaw: float = 0.68
var _pitch: float = 0.21
var _distance: float = 14.5
var _target_yaw: float = 0.68
var _target_pitch: float = 0.21
var _target_distance: float = 14.5
var _dragging: bool = false
var _vehicle_loaded: bool = false
var _detail: Label
var _bay_state: String = "inspect"
var _view_button: Button
var _stage_status: Label
var _walk_mode: bool = false
var _walk_position: Vector3 = Vector3(0, 1.75, 11)
var _walk_yaw: float = 0.0
var _walk_forward: float = 0.0
var _walk_turn: float = 0.0
var _walk_pad: PanelContainer
var _walk_toggle: Button
var _workshop: Node3D
var _equipment_panel: PanelContainer
var _equipment_status: Label
var _title_panel: PanelContainer
var _tools_panel: PanelContainer

func _ready() -> void:
	_build_3d_stage()
	_build_overlay()
	_refresh_camera(0.016)
	set_process(true)

func _process(delta: float) -> void:
	if _walk_mode:
		_walk_yaw += _walk_turn * delta * 1.75
		_walk_position += Vector3(-sin(_walk_yaw), 0, -cos(_walk_yaw)) * _walk_forward * delta * 4.6
		_walk_position.x = clampf(_walk_position.x, -17.0, 17.0)
		_walk_position.z = clampf(_walk_position.z, -15.0, 14.0)
		var ground_radius: float = Vector2(_walk_position.x, _walk_position.z).length()
		if ground_radius < 6.35:
			var safe: Vector2 = Vector2(_walk_position.x, _walk_position.z).normalized() * 6.35
			if ground_radius < 0.01:
				safe = Vector2(0, 6.35)
			_walk_position.x = safe.x
			_walk_position.z = safe.y
	_refresh_camera(delta)

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
	environment.ambient_light_color = Color("a8c3d1")
	environment.ambient_light_energy = 0.84
	environment.reflected_light_source = Environment.REFLECTION_SOURCE_BG
	environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	environment_node.environment = environment
	_world.add_child(environment_node)

	var graphite := _material(Color("304354"), 0.37, 0.44)
	var tile := _material(Color("384e5e"), 0.44, 0.43)
	var beams := _material(Color("516675"), 0.55, 0.34)
	var cyan := _material(Color("2b97b3"), 0.15, 0.27, true)
	var orange := _material(Color("c14f30"), 0.15, 0.34, true)
	var black := _material(Color("0b141e"), 0.3, 0.6)
	var glass := _material(Color("103c4c"), 0.6, 0.22)

	_box(_world, "WorkshopFloor", Vector3(0, -0.36, -3), Vector3(46, 0.5, 34), graphite)
	_box(_world, "BackWall", Vector3(0, 7.4, -18), Vector3(46, 15, 0.8), tile)
	_box(_world, "LeftWall", Vector3(-20, 7.4, -3), Vector3(0.8, 15, 34), graphite)
	_box(_world, "RightWall", Vector3(20, 7.4, -3), Vector3(0.8, 15, 34), graphite)
	_box(_world, "Ceiling", Vector3(0, 14.9, -3), Vector3(46, 0.6, 34), graphite)
	for i in range(9):
		var grid_z: float = -17.0 + float(i) * 4.0
		_box(_world, "FloorGuide_%02d" % i, Vector3(0, -0.094, grid_z), Vector3(44, 0.015, 0.035), beams)
		_box(_world, "CeilingRib_%02d" % i, Vector3(0, 14.4, grid_z), Vector3(43, 0.4, 0.5), beams)
	for i in range(11):
		var grid_x: float = -20.0 + float(i) * 4.0
		_box(_world, "Crossfloor_%02d" % i, Vector3(grid_x, -0.083, -3.5), Vector3(0.035, 0.016, 31), beams)
	for side in [-1, 1]:
		var x: float = float(side) * 13.2
		for segment in range(5):
			var z: float = -15.0 + float(segment) * 6.2
			_box(_world, "Support_%d_%d" % [side, segment], Vector3(x, 7.3, z), Vector3(0.65, 14, 0.65), beams)
			_box(_world, "SupportStrip_%d_%d" % [side, segment], Vector3(x - float(side) * 0.35, 4.7, z), Vector3(0.08, 8.2, 0.12), cyan)
		_box(_world, "UpperCatwalk_%d" % side, Vector3(x + float(side) * 2.8, 6.0, -6.6), Vector3(5.1, 0.45, 18), tile)
		_box(_world, "CatwalkRail_%d" % side, Vector3(x + float(side) * 0.3, 7.0, -6.6), Vector3(0.12, 1.8, 18), beams)

	for index in range(6):
		var x: float = -15.0 + float(index) * 6.0
		_box(_world, "WallLightBase_%d" % index, Vector3(x, 9.2, -17.45), Vector3(2.3, 3.2, 0.1), glass)
		_box(_world, "WallLight_%d" % index, Vector3(x, 9.2, -17.37), Vector3(0.1, 2.8, 0.07), cyan)
	_box(_world, "BackWallBanner", Vector3(0, 12, -17.5), Vector3(17.4, 1.1, 0.12), black)
	_box(_world, "BackWallAccent", Vector3(0, 11.3, -17.4), Vector3(17.4, 0.07, 0.12), orange)

	_cylinder(_world, "TurntableFoundation", Vector3(0, -0.06, 0), 6.2, 0.34, black)
	_cylinder(_world, "TurntableDeck", Vector3(0, 0.17, 0), 5.8, 0.22, tile)
	_ring(_world, "InspectionLightRing", Vector3(0, 0.31, 0), 5.55, 5.75, cyan)
	_ring(_world, "OuterGuideRing", Vector3(0, -0.015, 0), 6.55, 6.62, orange)
	for i in range(24):
		var angle: float = TAU * float(i) / 24.0
		var point := Vector3(cos(angle) * 5.98, 0.27, sin(angle) * 5.98)
		var marker := _box(_world, "DeckMarker_%02d" % i, point, Vector3(0.12, 0.02, 0.39), orange if i % 6 == 0 else beams)
		marker.rotation.y = -angle
	_vehicle_holder = Node3D.new()
	_vehicle_holder.name = "VehicleDisplay"
	_vehicle_holder.position.y = 0.33
	_world.add_child(_vehicle_holder)
	_load_craft_preview()
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
	sunlight.light_energy = 1.43
	sunlight.light_color = Color("d2e6ff")
	_world.add_child(sunlight)
	for light_spec in [
		{"pos": Vector3(-5, 9, 6), "color": Color("e3f1ff"), "energy": 4.0},
		{"pos": Vector3(6, 11, -4), "color": Color("ffd5ad"), "energy": 3.4},
		{"pos": Vector3(1, 10, 8), "color": Color("a5def4"), "energy": 3.3}
	]:
		var omni := OmniLight3D.new()
		omni.position = light_spec["pos"]
		omni.light_color = light_spec["color"]
		omni.light_energy = light_spec["energy"]
		omni.omni_range = 23.0
		_world.add_child(omni)

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
		_camera.look_at(_walk_position + Vector3(-sin(_walk_yaw), -0.09, -cos(_walk_yaw)), Vector3.UP)
		return
	var blend: float = clampf(delta * 9.0, 0.0, 1.0)
	_yaw = lerp_angle(_yaw, _target_yaw, blend)
	_pitch = lerpf(_pitch, _target_pitch, blend)
	_distance = lerpf(_distance, _target_distance, blend)
	var aim := Vector3(0, 2.45, 0)
	_camera.position = aim + Vector3(sin(_yaw) * cos(_pitch), sin(_pitch), cos(_yaw) * cos(_pitch)) * _distance
	_camera.look_at(aim, Vector3.UP)

func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event is InputEventScreenDrag:
		if _walk_mode:
			_walk_yaw -= event.relative.x * 0.006
		else:
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
			_walk_yaw -= event.relative.x * 0.006
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
	var title_panel := _panel(0.025, 0.028, 0.53, 0.16)
	_title_panel = title_panel
	var head := VBoxContainer.new()
	head.add_theme_constant_override("separation", 2)
	title_panel.add_child(head)
	head.add_child(_label("N / F  MOTORSPORT DIVISION   //   FOUNDRY LOT", 15, CYAN))
	head.add_child(_label("GARAGE  /  VEHICLE INSPECTION", 30, WHITE))
	head.add_child(_label("FULL 3D SHOWROOM   •   TOUCH & DRAG TO ORBIT", 14, MUTED))

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
		{"text": "3/4", "a": 0.68, "p": 0.21, "d": 14.5},
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

	_equipment_panel = _panel(0.753, 0.545, 0.974, 0.845)
	var equipment := VBoxContainer.new()
	equipment.add_theme_constant_override("separation", 7)
	_equipment_panel.add_child(equipment)
	equipment.add_child(_label("SERVICE BAY  /  EQUIPMENT", 15, ORANGE))
	equipment.add_child(_button("OPERATE LIFT ARMS", _operate_lifts))
	equipment.add_child(_button("ROBOT SCANNER  /  TOGGLE", _toggle_scanner))
	_equipment_status = _label("AUTO SERVICE  /  STANDBY", 13, MUTED)
	_equipment_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	equipment.add_child(_equipment_status)
	_refresh_equipment_status()

	_walk_pad = _panel(0.753, 0.545, 0.974, 0.855)
	var walk_content := VBoxContainer.new()
	walk_content.add_theme_constant_override("separation", 6)
	_walk_pad.add_child(walk_content)
	walk_content.add_child(_label("FIRST-PERSON WALKAROUND", 15, ORANGE))
	var motion_row := HBoxContainer.new()
	motion_row.add_theme_constant_override("separation", 7)
	walk_content.add_child(motion_row)
	var forwards: Button = _button("▲  FWD", func() -> void: pass)
	var backwards: Button = _button("▼  BACK", func() -> void: pass)
	forwards.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	backwards.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	motion_row.add_child(forwards)
	motion_row.add_child(backwards)
	forwards.button_down.connect(func() -> void: _walk_forward = 1.0)
	forwards.button_up.connect(func() -> void: _walk_forward = 0.0)
	backwards.button_down.connect(func() -> void: _walk_forward = -1.0)
	backwards.button_up.connect(func() -> void: _walk_forward = 0.0)
	var turn_row := HBoxContainer.new()
	turn_row.add_theme_constant_override("separation", 7)
	walk_content.add_child(turn_row)
	var left: Button = _button("◀  TURN", func() -> void: pass)
	var right: Button = _button("TURN  ▶", func() -> void: pass)
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	turn_row.add_child(left)
	turn_row.add_child(right)
	left.button_down.connect(func() -> void: _walk_turn = -1.0)
	left.button_up.connect(func() -> void: _walk_turn = 0.0)
	right.button_down.connect(func() -> void: _walk_turn = 1.0)
	right.button_up.connect(func() -> void: _walk_turn = 0.0)
	walk_content.add_child(_label("HOLD TO MOVE  /  DRAG TO LOOK", 13, MUTED))
	_walk_pad.visible = false

	var bottom := _panel(0.327, 0.89, 0.977, 0.978)
	var action_row := HBoxContainer.new()
	action_row.add_theme_constant_override("separation", 12)
	bottom.add_child(action_row)
	var back := _button("‹   MAIN HUB", func() -> void: return_to_hub.emit())
	var spin := _button("⟳   RESET VIEW", func() -> void: _move_view(0.68, 0.21, 14.5))
	var race := _button("RACE CONTROL   ›", func() -> void: request_race_control.emit())
	for b in [back, spin, race]:
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		action_row.add_child(b)
	_inspect()

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
	_walk_forward = 0.0
	_walk_turn = 0.0
	_walk_pad.visible = _walk_mode
	_equipment_panel.visible = not _walk_mode
	_title_panel.visible = not _walk_mode
	_tools_panel.visible = not _walk_mode
	_walk_toggle.text = "RETURN TO INSPECTION" if _walk_mode else "WALK THE GARAGE"
	_detail.text = "WALKAROUND MODE\nHold the movement and turn buttons to tour the Foundry Lot. Drag across the open 3D view to turn the camera." if _walk_mode else "INSPECTION MODE\nTouch-drag to orbit around the model. Use the camera presets for detail study."

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

func _zoom(amount: float) -> void:
	_target_distance = clampf(_target_distance + amount, 6.8, 20.0)

func navigate_back() -> void:
	return_to_hub.emit()
