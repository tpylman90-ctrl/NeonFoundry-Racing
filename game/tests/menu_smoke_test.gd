extends SceneTree
## End-to-end menu routing without fabricated gameplay results.
func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var packed: PackedScene = load("res://scenes/title_menu.tscn")
	assert(packed != null)
	var menu: Variant = packed.instantiate()
	root.add_child(menu)
	await process_frame
	assert(menu.current_page == "title")
	assert(menu.get_node("TitleScreen").visible)
	menu.show_main_menu()
	assert(menu.current_page == "menu")
	menu.open_settings()
	assert(menu.current_page == "settings")
	menu._on_volume_changed(0.35)
	menu._on_motion_changed(false)
	menu._on_fps_changed(true)
	var cfg := ConfigFile.new()
	assert(cfg.load(menu.SETTINGS_FILE) == OK)
	assert(is_equal_approx(float(cfg.get_value("audio", "master")), 0.35))
	assert(not bool(cfg.get_value("menu", "animation")))
	assert(bool(cfg.get_value("menu", "show_fps")))
	menu._restore_defaults()

	menu._open_section("garage")
	assert(menu.current_page == "garage")
	assert(menu._garage_page != null)
	assert(menu._garage_page._performance_label != null)
	assert(menu._garage_page._garage_viewport.msaa_3d == Viewport.MSAA_DISABLED)
	assert(menu._garage_page._garage_environment.tonemap_mode == Environment.TONE_MAPPER_ACES)
	assert(menu._garage_page._garage_environment.glow_enabled == false)
	assert(menu._garage_page._garage_environment.fog_enabled == false)
	assert(menu._garage_page._shell_stage != null)
	assert(menu._garage_page._shell_stage.visible)
	assert(not menu._garage_page._legacy_room.visible)
	assert(not menu._garage_page._workshop.visible)
	assert(not menu._garage_page._vehicle_holder.visible)
	assert(menu._garage_page._shell_stage.find_children("*", "MeshInstance3D", true, false).size() >= 6)
	# Verify actual imported world orientation, not just scene presence.
	var meshes: Array[Node] = menu._garage_page._shell_stage.find_children(
		"SHELL_01_*", "MeshInstance3D", true, false
	)
	assert(meshes.size() == 6)
	var horizontal_surfaces: int = 0
	var vertical_surfaces: int = 0
	for candidate in meshes:
		var node: MeshInstance3D = candidate as MeshInstance3D
		var world_aabb: AABB = node.global_transform * node.get_aabb()
		if node.name == "SHELL_01_FLOOR":
			assert(world_aabb.size.x > 53.0 and world_aabb.size.x < 55.0)
			assert(world_aabb.size.z > 43.0 and world_aabb.size.z < 45.0)
			assert(world_aabb.size.y < 1.0)
			assert(absf(world_aabb.position.y) < 0.8)
			horizontal_surfaces += 1
		elif node.name == "SHELL_01_CEILING":
			assert(world_aabb.size.x > 53.0 and world_aabb.size.x < 55.0)
			assert(world_aabb.size.z > 43.0 and world_aabb.size.z < 45.0)
			assert(world_aabb.size.y < 1.0)
			assert(world_aabb.position.y > 15.2)
			horizontal_surfaces += 1
		else:
			assert(world_aabb.size.y > 15.5)
			vertical_surfaces += 1
	assert(horizontal_surfaces == 2)
	assert(vertical_surfaces == 4)
	# New Stage 02 mezzanine is a distinct glTF, not added to the shell.
	assert(menu._garage_page._observation_deck != null)
	var deck: Node3D = menu._garage_page._observation_deck
	assert(deck.visible)
	var deck_meshes: Array[Node] = deck.find_children(
		"OBS_DECK_*", "MeshInstance3D", true, false
	)
	assert(deck_meshes.size() == 4)
	# Front-left mezzanine at about 5.2m overlooks lift bays; top of
	# guard rails at about 6.37m. Stairs extend to z ~= 19.05m.
	var deck_bounds: AABB = (
		(deck_meshes[0] as MeshInstance3D).global_transform *
		(deck_meshes[0] as MeshInstance3D).get_aabb()
	)
	for candidate in deck_meshes.slice(1):
		var node: MeshInstance3D = candidate as MeshInstance3D
		deck_bounds = deck_bounds.merge(node.global_transform * node.get_aabb())
	assert(deck_bounds.position.x < -25.0)
	assert(deck_bounds.end.x > -12.6)
	assert(deck_bounds.position.z < 2.8)
	assert(deck_bounds.end.z > 18.8)
	assert(deck_bounds.end.y > 6.1)
	assert(deck_bounds.end.y < 6.7)
	# Floor can be traversed UNDER the deck without snapping upstairs.
	var old_under: Vector3 = Vector3(-18.0, 1.75, 8.0)
	menu._garage_page._walk_position = old_under + Vector3(0.4, 0, 0.2)
	menu._garage_page._resolve_deck_walk(old_under)
	assert(is_equal_approx(menu._garage_page._walk_position.y, 1.75))
	# Stair height is continuous; entering from the lower landing works.
	var foot: Vector3 = Vector3(-24.0, 1.75, 19.12)
	menu._garage_page._walk_position = Vector3(-24.0, 1.75, 18.96)
	menu._garage_page._resolve_deck_walk(foot)
	assert(menu._garage_page._walk_position.y > 1.75)
	assert(menu._garage_page._walk_position.y < 2.0)
	var stair_mid: Vector3 = Vector3(-24.0, 4.1, 14.6)
	menu._garage_page._walk_position = Vector3(-24.0, 4.1, 14.4)
	menu._garage_page._resolve_deck_walk(stair_mid)
	assert(menu._garage_page._walk_position.y > 3.5)
	assert(menu._garage_page._walk_position.y < 5.5)
	# Reaching upper landing grants actual 3D viewing level.
	var upper_stair: Vector3 = Vector3(-24.0, 6.88, 10.72)
	menu._garage_page._walk_position = Vector3(-24.0, 6.88, 10.54)
	menu._garage_page._resolve_deck_walk(upper_stair)
	assert(is_equal_approx(
		menu._garage_page._walk_position.y, 1.75 + menu._garage_page.DECK_SURFACE_Y
	))
	# Do not walk through guardrails or fall from the elevated platform.
	var upper_deck: Vector3 = Vector3(-18.0, 6.95, 4.0)
	menu._garage_page._walk_position = Vector3(-11.0, 6.95, 4.0)
	menu._garage_page._resolve_deck_walk(upper_deck)
	assert(menu._garage_page._walk_position.is_equal_approx(upper_deck))
	menu._garage_page._walk_position = Vector3(0, 1.75, 11.0)
	# The enlarged empty shell must be navigable near the new perimeter,
	# without allowing a thumbstick to push the camera through its walls.
	menu._garage_page._walk_position = Vector3(99.0, 1.75, -99.0)
	menu._garage_page._toggle_walk()
	menu._garage_page._process(0.016)
	assert(menu._garage_page._walk_position.x < 25.0)
	assert(menu._garage_page._walk_position.z > -22.0)
	menu._garage_page._toggle_walk()
	menu._garage_page._walk_position = Vector3(0.0, 1.75, 11.0)
	assert(menu._garage_page._world.get_node("ChassisContactShadow") != null)
	assert(menu._garage_page._world.get_node("PlatformContactShadow") != null)
	assert(menu._garage_page._reflection_probe.update_mode == ReflectionProbe.UPDATE_ONCE)
	assert(menu._garage_page._reflection_probe.box_projection)
	assert(not menu._garage_page._hero_key.visible)
	assert(is_equal_approx(menu._garage_page._garage_viewport.scaling_3d_scale, 0.85))
	menu._garage_page._set_graphics_detail(true)
	assert(menu._garage_page._quality_detail)
	assert(is_equal_approx(menu._garage_page._garage_viewport.scaling_3d_scale, 1.0))
	assert(not menu._garage_page._hero_key.shadow_enabled)
	assert(not menu._garage_page._reflection_probe.visible)
	assert(menu._garage_page._garage_viewport.anisotropic_filtering_level == Viewport.ANISOTROPY_8X)
	menu._garage_page._set_graphics_detail(false)
	assert(not menu._garage_page._hero_key.shadow_enabled)
	assert(is_equal_approx(menu._garage_page._garage_viewport.scaling_3d_scale, 0.85))
	assert(menu.get_node("ImmersiveGarage/Garage3D/GarageViewport/FoundryLot") != null)
	var workshop: Node3D = menu.get_node("ImmersiveGarage/Garage3D/GarageViewport/FoundryLot/LiveWorkshopEquipment")
	assert(workshop != null)
	assert(workshop.get_node("Batched_steel") != null)
	assert(workshop.get_node("Batched_bench") != null)
	# Isolated unit test for the original bench-top bug: Godot is CW.
	# For the top face, the cross product must oppose the UP normal.
	var box_probe := SurfaceTool.new()
	box_probe.begin(Mesh.PRIMITIVE_TRIANGLES)
	var old_black_tool: SurfaceTool = workshop._tools["black"]
	workshop._tools["black"] = box_probe
	workshop._box("black", Vector3.ZERO, Vector3.ONE)
	var probe_arrays: Array = box_probe.commit_to_arrays()
	workshop._tools["black"] = old_black_tool
	var probe_vertices: PackedVector3Array = probe_arrays[Mesh.ARRAY_VERTEX]
	var probe_normals: PackedVector3Array = probe_arrays[Mesh.ARRAY_NORMAL]
	assert(probe_vertices.size() == 36)
	var upper: int = 12
	var cross_normal: Vector3 = (
		probe_vertices[upper + 1] - probe_vertices[upper]
	).cross(probe_vertices[upper + 2] - probe_vertices[upper])
	assert(cross_normal.dot(Vector3.UP) < -0.99)
	assert(probe_normals[upper].dot(Vector3.UP) > 0.99)
	assert(workshop.get_node("ArticulatedServiceRobot") != null)
	var diagnostic_labels: Array[Node] = workshop.find_children("*", "Label3D", true, false)
	assert(diagnostic_labels.size() >= 12)
	var steel_mesh: MeshInstance3D = workshop.get_node("Batched_steel") as MeshInstance3D
	assert(steel_mesh.mesh.get_surface_count() >= 1)
	var staged_cc0: String = "res://assets/garage/pbr/steel_color.jpg"
	if ResourceLoader.exists(staged_cc0):
		var material: StandardMaterial3D = steel_mesh.material_override as StandardMaterial3D
		assert(not material.normal_enabled)
		assert(material.normal_texture != null)
		assert(steel_mesh.mesh.surface_get_format(0) & Mesh.ARRAY_FORMAT_TANGENT != 0)
	# Ensure bench tops and painted metal no longer sample oversized rust.
	var worktop: MeshInstance3D = workshop.get_node("Batched_bench") as MeshInstance3D
	assert((worktop.material_override as StandardMaterial3D).albedo_texture == null)
	var cabinets: MeshInstance3D = workshop.get_node("Batched_wear") as MeshInstance3D
	assert((cabinets.material_override as StandardMaterial3D).albedo_texture == null)
	var imported_cc0: String = "res://assets/garage/kenney_factory/machine-window.obj"
	if ResourceLoader.exists(imported_cc0):
		assert(workshop.get_node_or_null("Kenney_machine_window") != null)
	var carriages: Array = workshop.get("_lift_carriages")
	assert(carriages.size() == 2)
	workshop.call("toggle_lifts")
	assert(float(workshop.get("_lift_target")) > 1.0)
	workshop.call("toggle_lifts")
	assert(float(workshop.get("_lift_target")) < 0.2)
	workshop.call("set_scanner_active", false)
	assert(not bool(workshop.get("_scanner_enabled")))
	workshop.call("set_scanner_active", true)
	menu._garage_page._move_view(1.57, 0.15, 12.3)
	menu._garage_page._zoom(-1.0)
	menu._garage_page._toggle_walk()
	assert(menu._garage_page._walk_mode)
	assert(not menu._garage_page._tools_panel.visible)
	assert(menu._garage_page._walk_joysticks.visible)
	var pad: Control = menu._garage_page._walk_joysticks
	assert(pad.get_node_or_null(".") != null)
	var radius: float = float(pad.call("get_radius"))
	var origin: Vector2 = pad.get_global_rect().position
	var left_center: Vector2 = origin + Vector2(pad.call("get_stick_center", false))
	var right_center: Vector2 = origin + Vector2(pad.call("get_stick_center", true))
	# Both fingers start neutral, then independently move and look.
	var left_down := InputEventScreenTouch.new()
	left_down.index = 11
	left_down.position = left_center
	left_down.pressed = true
	menu._garage_page._input(left_down)
	assert(int(pad.get("move_finger")) == 11)
	var right_down := InputEventScreenTouch.new()
	right_down.index = 12
	right_down.position = right_center
	right_down.pressed = true
	menu._garage_page._input(right_down)
	assert(int(pad.get("look_finger")) == 12)
	var left_drag := InputEventScreenDrag.new()
	left_drag.index = 11
	left_drag.position = left_center + Vector2(0.55 * radius, -0.81 * radius)
	menu._garage_page._input(left_drag)
	var right_drag := InputEventScreenDrag.new()
	right_drag.index = 12
	right_drag.position = right_center + Vector2(0.62 * radius, -0.61 * radius)
	menu._garage_page._input(right_drag)
	var movement: Vector2 = pad.get("move_axis")
	var viewing: Vector2 = pad.get("look_axis")
	assert(movement.x > 0.3 and movement.y < -0.4)
	assert(viewing.x > 0.3 and viewing.y < -0.3)
	var old_pos: Vector3 = menu._garage_page._walk_position
	var old_yaw: float = menu._garage_page._walk_yaw
	menu._garage_page._process(0.12)
	assert(menu._garage_page._walk_position.distance_to(old_pos) > 0.1)
	assert(menu._garage_page._walk_yaw < old_yaw)
	assert(menu._garage_page._walk_pitch > 0.03)
	# Releasing one finger must NOT kill the other stick's tracking.
	var left_up := InputEventScreenTouch.new()
	left_up.index = 11
	left_up.position = left_center
	left_up.pressed = false
	menu._garage_page._input(left_up)
	assert(Vector2(pad.get("move_axis")) == Vector2.ZERO)
	assert(int(pad.get("look_finger")) == 12)
	assert(Vector2(pad.get("look_axis")).length() > 0.3)
	var right_up := InputEventScreenTouch.new()
	right_up.index = 12
	right_up.position = right_center
	right_up.pressed = false
	menu._garage_page._input(right_up)
	assert(Vector2(pad.get("look_axis")) == Vector2.ZERO)
	# Back navigation resets all input states and hides both controls.
	menu._garage_page._toggle_walk()
	assert(not menu._garage_page._walk_mode)
	assert(not pad.visible)
	assert(int(pad.get("move_finger")) == -1)
	assert(int(pad.get("look_finger")) == -1)
	assert(not menu._garage_page._tools_panel.visible)
	menu._garage_page._show_tuning()
	assert(menu._garage_page._bay_state == "tuning")
	menu._garage_page._show_cosmetic()
	assert(menu._garage_page._bay_state == "customize")
	menu._garage_page._show_craft()
	assert(menu._garage_page._bay_state == "select")
	menu._garage_page.return_to_hub.emit()
	assert(menu.current_page == "menu")
	assert(menu._garage_page == null)

	menu._open_section("store")
	assert(menu.current_page == "module")
	assert(menu._flow_page.current_page == "store")
	menu._flow_page._goto("store_parts")
	assert(menu._flow_page.current_page == "store_parts")
	menu._open_section("profile")
	assert(menu.current_page == "module")
	assert(menu._flow_page.current_page == "profile")
	menu._flow_page._goto("controls")
	assert(menu._flow_page.current_page == "controls")
	menu._open_section("races")
	assert(menu.current_page == "module")
	assert(menu._flow_page.current_page == "mode")
	menu._flow_page._choose_mode("hybrid")
	assert(menu._flow_page.current_page == "tracks")
	menu._flow_page._choose_track("neon_cross")
	assert(menu._flow_page.current_page == "lobby")
	menu._flow_page.request_garage.emit()
	assert(menu.current_page == "garage")
	assert(menu._garage_page != null)
	menu._garage_page.request_race_control.emit()
	assert(menu.current_page == "module")
	assert(menu._flow_page.current_page == "mode")
	menu._flow_page._choose_mode("hybrid")
	menu._flow_page._choose_track("neon_cross")
	menu._flow_page._start_flow_demo()
	assert(menu._flow_page.current_page == "loading")
	await create_timer(1.4).timeout
	assert(menu._flow_page.current_page == "race_demo")
	menu._flow_page._goto("pause")
	assert(menu._flow_page.current_page == "pause")
	menu._flow_page.navigate_back()
	assert(menu._flow_page.current_page == "race_demo")
	menu._flow_page._demo_finished()
	assert(menu._flow_page.current_page == "results")
	menu.show_main_menu()
	assert(menu.current_page == "menu")
	menu.show_title()
	assert(menu.current_page == "title")
	menu.queue_free()
	await process_frame
	print("NEON_FOUNDRY_MENU_SMOKE_OK independent garage/retail/profile/race scenes and complete race UI flow")
	quit()
