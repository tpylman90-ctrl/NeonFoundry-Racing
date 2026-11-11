extends SceneTree
## Validates navigation paths and that settings save to ConfigFile.

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
	assert(menu.get_node("MainMenu").visible)
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
	assert(menu.current_page == "detail")
	assert("GARAGE" in menu._detail_title.text)
	menu._open_section("races")
	assert("RACE CONTROL" in menu._detail_title.text)
	menu.show_title()
	assert(menu.current_page == "title")
	menu.queue_free()
	await process_frame
	print("NEON_FOUNDRY_MENU_SMOKE_OK title -> menu -> settings -> garage/races -> title")
	quit()
