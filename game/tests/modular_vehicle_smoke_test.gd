extends SceneTree
## Test real GLB loading/swapping in a headless Godot renderer, no gameplay assumptions.
func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var script: Script = load("res://scripts/vehicle_modular_rig.gd")
	assert(script != null)
	var rig: Node3D = script.new() as Node3D
	assert(rig != null)
	root.add_child(rig)
	await process_frame
	assert(rig.initialize())
	assert(rig.get_current_loadout().size() == 9)
	assert(rig.get_available_parts("rear_engine").size() == 4)
	assert(rig.get_available_parts("rear_fins").size() == 3)
	assert(rig.get_available_parts("side_intakes").size() == 3)
	assert(rig.get_active_part_node("rear_engine") != null)
	assert(rig.get_node("SOCKET_rear_engine").position.is_equal_approx(Vector3(0.0, 0.57, -1.83)))
	var original_engine: Node3D = rig.get_active_part_node("rear_engine")
	assert(rig.install("rear_engine", "engine_nova"))
	assert(rig.get_active_part_node("rear_engine") != original_engine)
	assert(rig.get_engine_stats().get("tier") == 3)
	assert(rig.install("rear_fins", "fins_2"))
	assert(rig.install("side_intakes", "intakes_2"))
	var before_invalid: Dictionary = rig.get_current_loadout()
	assert(not rig.install("rear_engine", "nonexistent_engine"))
	assert(rig.get_current_loadout() == before_invalid)
	assert(rig.set_style_preset("aero"))
	assert(rig.get_current_loadout()["rear_engine"] == "engine_vortex")
	assert(rig.get_current_loadout()["rear_fins"] == "fins_1")
	assert(rig.set_style_preset("industrial"))
	assert(rig.get_current_loadout()["rear_engine"] == "engine_nova")
	for slot_id in rig.get_current_loadout():
		assert(rig.get_active_part_node(str(slot_id)) != null)
		assert(rig.get_node("SOCKET_" + str(slot_id)).get_child_count() == 1)
	print("NFR_MODULAR_KHRONOS_GLB_SWAP_TEST_OK slots=9 engine_tiers=4 kits=3")
	quit(0)
