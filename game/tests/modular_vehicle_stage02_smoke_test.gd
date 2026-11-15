extends SceneTree
## Runs against real stage02 GLBs via the unmodified common native rig controller.
func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var source: Script = load("res://scripts/vehicle_modular_rig.gd")
	assert(source != null)
	var rig: Node3D = source.new() as Node3D
	assert(rig != null)
	root.add_child(rig)
	await process_frame
	assert(rig.initialize("res://assets/vehicle_modular/module_manifest_stage02.json"))
	assert(rig.get_current_loadout().size() == 10)
	assert(rig.get_available_parts("front_quarter_fins").size() == 3)
	assert(rig.get_available_parts("rear_fins").size() == 3)
	assert(rig.get_available_parts("rear_engine").size() == 4)
	assert(rig.get_node("SOCKET_front_quarter_fins").position.is_equal_approx(Vector3(0.0, 0.86, 1.30)))
	assert(rig.get_active_part_node("front_quarter_fins") != null)
	var old_fins: Node3D = rig.get_active_part_node("front_quarter_fins")
	assert(rig.install("front_quarter_fins", "quarter_fins_2"))
	assert(rig.get_active_part_node("front_quarter_fins") != old_fins)
	assert(rig.install("rear_engine", "engine_titan"))
	assert(int(rig.get_engine_stats().get("tier", -1)) == 2)
	assert(rig.install("rear_fins", "fins_1"))
	var before_invalid: Dictionary = rig.get_current_loadout()
	assert(not rig.install("front_quarter_fins", "invalid_canard"))
	assert(rig.get_current_loadout() == before_invalid)
	for preset in ["street", "aero", "industrial"]:
		assert(rig.set_style_preset(preset))
		var current: Dictionary = rig.get_current_loadout()
		assert(current.size() == 10)
		for slot in current:
			assert(rig.get_active_part_node(str(slot)) != null)
			assert(rig.get_node("SOCKET_" + str(slot)).get_child_count() == 1)
	assert(rig.get_current_loadout()["front_quarter_fins"] == "quarter_fins_2")
	assert(rig.get_current_loadout()["rear_engine"] == "engine_nova")
	print("NFR_STAGE02_GODOT_MODULAR_SWAP_OK slots=10 styles=3 engines=4")
	quit(0)
