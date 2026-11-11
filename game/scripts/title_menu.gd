extends Control
## Boot/title -> main menu -> informational sections and persistent settings.
## Garage and races are clearly labelled as future milestones.

signal page_changed(next_page: String)

const BackdropScript = preload("res://scripts/menu_backdrop.gd")
const ChromeScript = preload("res://scripts/menu_chrome.gd")
const MENU_ART: String = "res://assets/menu/launch_scene.png"
const SETTINGS_FILE: String = "user://neon_foundry_settings.cfg"
const CYAN: Color = Color("4dd5db")
const AMBER: Color = Color("f69b70")
const PALE: Color = Color("eef5fb")
const MUTED: Color = Color("9aafbd")

var current_page: String = "title"
var _master_volume: float = 0.8
var _menu_motion: bool = true
var _show_fps: bool = false
var _backdrop: Control
var _chrome: Control
var _preview_title: Label
var _preview_detail: Label
var _title_page: Control
var _menu_page: Control
var _detail_page: Control
var _settings_page: Control
var _detail_title: Label
var _detail_subtitle: Label
var _fps_label: Label
var _volume_slider: HSlider
var _motion_button: CheckButton
var _fps_button: CheckButton

func _ready() -> void:
	_load_settings()
	_build_interface()
	_apply_settings()
	_show_page("title")
	if "--capture-title" in OS.get_cmdline_user_args():
		_capture_screen("NeonFoundry-Title.png", "title")
	elif "--capture-menu" in OS.get_cmdline_user_args():
		_capture_screen("NeonFoundry-MainMenu.png", "menu")
	elif "--capture-settings" in OS.get_cmdline_user_args():
		_capture_screen("NeonFoundry-Settings.png", "settings")

func _process(_delta: float) -> void:
	if _fps_label != null and _fps_label.visible:
		_fps_label.text = "FPS  %d" % Engine.get_frames_per_second()

func _build_interface() -> void:
	# The expensive scene is generated and lit in Blender at build-time.
	# Mobile/Vulkan only composites the finished background and lightweight HUD.
	_backdrop = Control.new()
	_backdrop.name = "ProceduralFallback"
	_backdrop.set_script(BackdropScript)
	_backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_backdrop)

	if ResourceLoader.exists(MENU_ART):
		var hero_image := TextureRect.new()
		hero_image.name = "BlenderCinematicBackdrop"
		hero_image.texture = load(MENU_ART)
		hero_image.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		hero_image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		hero_image.mouse_filter = Control.MOUSE_FILTER_IGNORE
		hero_image.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(hero_image)
		print("NEON_FOUNDRY_BLENDER_BACKDROP_READY")
	else:
		push_warning("Blender menu scene not generated; use tools/build_menu_hero.py to create it.")

	_chrome = Control.new()
	_chrome.name = "NeonTelemetryChrome"
	_chrome.set_script(ChromeScript)
	_chrome.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_chrome)

	var top_brand: Label = _label("N / F     MOTORSPORT DIVISION", 17, CYAN, true)
	top_brand.anchor_left = 0.067
	top_brand.anchor_top = 0.035
	top_brand.anchor_right = 0.48
	top_brand.anchor_bottom = 0.091
	add_child(top_brand)

	var version: Label = _label("01  /  PRE-ALPHA     •     VULKAN ACTIVE", 15, MUTED, true)
	version.anchor_left = 0.57
	version.anchor_right = 0.958
	version.anchor_top = 0.035
	version.anchor_bottom = 0.088
	version.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	add_child(version)

	_fps_label = _label("FPS --", 16, CYAN, true)
	_fps_label.anchor_left = 0.83
	_fps_label.anchor_right = 0.965
	_fps_label.anchor_top = 0.088
	_fps_label.anchor_bottom = 0.13
	_fps_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	add_child(_fps_label)

	_title_page = Control.new()
	_title_page.name = "TitleScreen"
	_title_page.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_title_page)
	_build_title()

	_menu_page = Control.new()
	_menu_page.name = "MainMenu"
	_menu_page.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_menu_page)
	_build_menu()

	_detail_page = Control.new()
	_detail_page.name = "SectionPreview"
	_detail_page.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_detail_page)
	_build_detail()

	_settings_page = Control.new()
	_settings_page.name = "Settings"
	_settings_page.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_settings_page)
	_build_settings()

	var footer: Label = _label("NEON FOUNDRY  //  PROTOTYPE 0.2     •     ANDROID / MOBILE / VULKAN", 14, Color("98b1bd"), true)
	footer.anchor_left = 0.068
	footer.anchor_right = 0.89
	footer.anchor_top = 0.943
	footer.anchor_bottom = 0.975
	add_child(footer)

func _build_title() -> void:
	var anywhere := Button.new()
	anywhere.name = "TapAnywhere"
	anywhere.flat = true
	anywhere.focus_mode = Control.FOCUS_NONE
	anywhere.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	anywhere.pressed.connect(show_main_menu)
	_title_page.add_child(anywhere)

	var col := _column(0.075, 0.17, 0.59, 0.84, 5)
	_title_page.add_child(col)
	col.add_child(_label("◢   SEASON ZERO   /   INITIALIZATION", 18, AMBER, true))
	var gap := Control.new()
	gap.custom_minimum_size.y = 22.0
	col.add_child(gap)
	col.add_child(_label("NEON", 94, PALE, true))
	col.add_child(_label("FOUNDRY", 94, PALE, true))
	col.add_child(_label("R A C I N G", 44, CYAN, true))
	var spacer := Control.new()
	spacer.custom_minimum_size.y = 19.0
	col.add_child(spacer)
	col.add_child(_label("CRAFT YOUR LEGACY.  OWN THE SKY.", 20, PALE, true))
	col.add_child(_label("THE FUTURE OF HOVER MOTORSPORT STARTS HERE", 15, MUTED))
	var spacer2 := Control.new()
	spacer2.custom_minimum_size.y = 14
	col.add_child(spacer2)
	var enter: Button = _button("››    ENTER THE FOUNDRY", true)
	enter.custom_minimum_size.x = 390
	enter.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	enter.pressed.connect(show_main_menu)
	col.add_child(enter)
	col.add_child(_label("TAP TO INITIALIZE     /     PRESS ENTER", 14, CYAN, true))

func _build_menu() -> void:
	var col := _column(0.075, 0.158, 0.434, 0.916, 4)
	_menu_page.add_child(col)
	col.add_child(_label("SEASON ZERO  /  PLAYER TERMINAL", 16, AMBER, true))
	col.add_child(_label("NEON FOUNDRY", 46, PALE, true))
	col.add_child(_label("R A C I N G", 32, CYAN, true))
	col.add_child(_label("SELECT YOUR DESTINATION", 14, MUTED, true))
	var spacer := Control.new()
	spacer.custom_minimum_size.y = 12
	col.add_child(spacer)

	var enter: Button = _button("01   ENTER THE FOUNDRY", true)
	enter.custom_minimum_size.y = 54
	enter.pressed.connect(func() -> void: _open_section("garage"))
	enter.mouse_entered.connect(func() -> void: _set_menu_preview("garage"))
	enter.focus_entered.connect(func() -> void: _set_menu_preview("garage"))
	col.add_child(enter)

	var races: Button = _button("02   RACE CONTROL")
	races.custom_minimum_size.y = 54
	races.pressed.connect(func() -> void: _open_section("races"))
	races.mouse_entered.connect(func() -> void: _set_menu_preview("races"))
	races.focus_entered.connect(func() -> void: _set_menu_preview("races"))
	col.add_child(races)

	var fleet: Button = _button("03   THE FLEET")
	fleet.custom_minimum_size.y = 54
	fleet.pressed.connect(func() -> void: _open_section("fleet"))
	fleet.mouse_entered.connect(func() -> void: _set_menu_preview("fleet"))
	fleet.focus_entered.connect(func() -> void: _set_menu_preview("fleet"))
	col.add_child(fleet)

	var options: Button = _button("04   OPTIONS")
	options.custom_minimum_size.y = 54
	options.pressed.connect(open_settings)
	options.mouse_entered.connect(func() -> void: _set_menu_preview("settings"))
	options.focus_entered.connect(func() -> void: _set_menu_preview("settings"))
	col.add_child(options)

	var about: Button = _button("05   ABOUT")
	about.custom_minimum_size.y = 54
	about.pressed.connect(func() -> void: _open_section("about"))
	about.mouse_entered.connect(func() -> void: _set_menu_preview("about"))
	about.focus_entered.connect(func() -> void: _set_menu_preview("about"))
	col.add_child(about)

	var quit: Button = _button("06   QUIT")
	quit.custom_minimum_size.y = 54
	quit.pressed.connect(func() -> void: get_tree().quit())
	quit.mouse_entered.connect(func() -> void: _set_menu_preview("quit"))
	quit.focus_entered.connect(func() -> void: _set_menu_preview("quit"))
	col.add_child(quit)

	var title: Button = _button("‹    RETURN TO TITLE")
	title.custom_minimum_size.y = 36
	title.add_theme_font_size_override("font_size", 15)
	title.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	title.pressed.connect(show_title)
	col.add_child(title)

	# Contextual diagnostics along the top edge. The hero craft stays visible.
	var card := PanelContainer.new()
	card.name = "SelectionTelemetry"
	card.anchor_left = 0.691
	card.anchor_right = 0.957
	card.anchor_top = 0.151
	card.anchor_bottom = 0.272
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.02, 0.055, 0.085, 0.61)
	style.border_width_top = 1
	style.border_color = CYAN.darkened(0.23)
	style.content_margin_left = 14
	style.content_margin_top = 9
	style.content_margin_bottom = 8
	card.add_theme_stylebox_override("panel", style)
	_menu_page.add_child(card)
	var info := VBoxContainer.new()
	info.add_theme_constant_override("separation", 2)
	card.add_child(info)
	_preview_title = _label("01   ENTER THE FOUNDRY", 18, CYAN, true)
	info.add_child(_preview_title)
	_preview_detail = _label("GARAGE ACCESS / IN DEVELOPMENT", 14, MUTED, true)
	info.add_child(_preview_detail)
	_set_menu_preview("garage")

func _set_menu_preview(section: String) -> void:
	if _preview_title == null or _preview_detail == null:
		return
	match section:
		"garage":
			_preview_title.text = "01   ENTER THE FOUNDRY"
			_preview_detail.text = "INSPECT  /  UPGRADE  /  PREPARE"
		"races":
			_preview_title.text = "02   RACE CONTROL"
			_preview_detail.text = "SURFACE  /  HYBRID  /  FLIGHT"
		"fleet":
			_preview_title.text = "03   THE FLEET"
			_preview_detail.text = "COLLECT  /  CUSTOMIZE  /  SELECT"
		"settings":
			_preview_title.text = "04   OPTIONS"
			_preview_detail.text = "AUDIO  /  MOTION  /  DISPLAY"
		"about":
			_preview_title.text = "05   ABOUT"
			_preview_detail.text = "ORIGINAL HOVER MOTORSPORT"
		"quit":
			_preview_title.text = "06   QUIT"
			_preview_detail.text = "RETURN TO DEVICE"

func _build_detail() -> void:
	var col: VBoxContainer = _column(0.078, 0.27, 0.56, 0.83, 19)
	_detail_page.add_child(col)
	col.add_child(_label("NEON FOUNDRY / SYSTEM MODULE", 18, AMBER, true))
	_detail_title = _label("COMING SOON", 55, PALE, true)
	col.add_child(_detail_title)
	_detail_subtitle = _label("", 23, MUTED)
	_detail_subtitle.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	col.add_child(_detail_subtitle)
	var back: Button = _button("<    BACK TO MAIN MENU", true)
	back.custom_minimum_size.x = 350
	back.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	back.pressed.connect(show_main_menu)
	col.add_child(back)

func _build_settings() -> void:
	var panel := PanelContainer.new()
	panel.name = "SettingsPanel"
	panel.anchor_left = 0.075
	panel.anchor_top = 0.17
	panel.anchor_right = 0.53
	panel.anchor_bottom = 0.89
	panel.add_theme_stylebox_override("panel", _panel_style())
	_settings_page.add_child(panel)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 11)
	panel.add_child(col)
	col.add_child(_label("PREFERENCES / LOCAL DEVICE", 17, AMBER, true))
	col.add_child(_label("SETTINGS", 48, PALE, true))
	col.add_child(_label("MASTER AUDIO", 18, CYAN, true))
	_volume_slider = HSlider.new()
	_volume_slider.name = "MasterVolume"
	_volume_slider.min_value = 0.0
	_volume_slider.max_value = 1.0
	_volume_slider.step = 0.05
	_volume_slider.value = _master_volume
	_volume_slider.custom_minimum_size.y = 44
	_volume_slider.value_changed.connect(_on_volume_changed)
	col.add_child(_volume_slider)
	_motion_button = CheckButton.new()
	_motion_button.name = "MenuMotion"
	_motion_button.text = "ANIMATED MENU BACKDROP"
	_motion_button.button_pressed = _menu_motion
	_motion_button.add_theme_font_size_override("font_size", 20)
	_motion_button.toggled.connect(_on_motion_changed)
	col.add_child(_motion_button)
	_fps_button = CheckButton.new()
	_fps_button.name = "ShowFPS"
	_fps_button.text = "SHOW FPS COUNTER"
	_fps_button.button_pressed = _show_fps
	_fps_button.add_theme_font_size_override("font_size", 20)
	_fps_button.toggled.connect(_on_fps_changed)
	col.add_child(_fps_button)
	col.add_child(_label("SETTINGS ARE SAVED LOCALLY ON THIS DEVICE.", 14, MUTED))
	var reset: Button = _button("RESTORE DEFAULTS")
	reset.pressed.connect(_restore_defaults)
	col.add_child(reset)
	var back: Button = _button("<    BACK TO MAIN MENU", true)
	back.pressed.connect(show_main_menu)
	col.add_child(back)

func _label(value: String, font_size: int, tint: Color, strong: bool = false) -> Label:
	var result := Label.new()
	result.text = value
	result.mouse_filter = Control.MOUSE_FILTER_IGNORE
	result.add_theme_color_override("font_color", tint)
	result.add_theme_font_size_override("font_size", font_size)
	if strong:
		result.add_theme_color_override("font_shadow_color", Color(0.0, 0.0, 0.0, 0.35))
		result.add_theme_constant_override("shadow_offset_x", 1)
		result.add_theme_constant_override("shadow_offset_y", 2)
	return result

func _column(left: float, top: float, right: float, bottom: float, separation: int) -> VBoxContainer:
	var col := VBoxContainer.new()
	col.anchor_left = left
	col.anchor_top = top
	col.anchor_right = right
	col.anchor_bottom = bottom
	col.add_theme_constant_override("separation", separation)
	return col

func _button(value: String, primary: bool = false) -> Button:
	var b := Button.new()
	b.text = value
	b.custom_minimum_size.y = 55.0
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	b.add_theme_font_size_override("font_size", 20)
	b.add_theme_color_override("font_color", PALE)
	b.add_theme_color_override("font_hover_color", Color.WHITE)
	b.add_theme_color_override("font_pressed_color", Color.WHITE)
	b.add_theme_stylebox_override("normal", _button_style(primary, false))
	b.add_theme_stylebox_override("hover", _button_style(primary, true))
	b.add_theme_stylebox_override("pressed", _button_style(true, true))
	b.add_theme_stylebox_override("focus", _focus_style())
	return b

func _button_style(primary: bool, hovered: bool) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.045, 0.27, 0.36, 0.88) if primary else Color(0.018, 0.052, 0.082, 0.60)
	if hovered:
		sb.bg_color = Color(0.10, 0.36, 0.48, 0.94)
	sb.set_corner_radius_all(5)
	sb.content_margin_left = 20
	sb.content_margin_right = 12
	sb.border_width_left = 5 if primary else 2
	sb.border_width_top = 1
	sb.border_width_bottom = 1
	sb.border_color = AMBER if primary else Color("35899b")
	return sb

func _focus_style() -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color.TRANSPARENT
	sb.set_border_width_all(2)
	sb.border_color = CYAN
	sb.set_corner_radius_all(5)
	return sb

func _panel_style() -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.013, 0.038, 0.064, 0.87)
	sb.border_width_left = 3
	sb.border_color = CYAN
	sb.set_corner_radius_all(6)
	sb.content_margin_left = 26
	sb.content_margin_right = 26
	sb.content_margin_top = 20
	sb.content_margin_bottom = 18
	return sb

func _show_page(next_page: String) -> void:
	current_page = next_page
	_title_page.visible = next_page == "title"
	_menu_page.visible = next_page == "menu"
	_detail_page.visible = next_page == "detail"
	_settings_page.visible = next_page == "settings"
	page_changed.emit(current_page)

func show_title() -> void:
	_show_page("title")

func show_main_menu() -> void:
	_show_page("menu")

func open_settings() -> void:
	_show_page("settings")

func _open_section(section: String) -> void:
	match section:
		"garage":
			_detail_title.text = "THE FOUNDRY GARAGE"
			_detail_subtitle.text = "The garage will let you walk between your owned craft, inspect bodywork and cockpits, and configure upgrades. This module has not been built yet."
		"fleet":
			_detail_title.text = "THE FLEET"
			_detail_subtitle.text = "Owned, earned and purchased craft will be displayed here when the fleet and progression systems are built. This is a preview, not a finished vehicle catalog."
		"races":
			_detail_title.text = "RACE CONTROL"
			_detail_subtitle.text = "Surface circuits, hybrid events and real three-dimensional aerial races are planned. No playable events are available in this menu milestone."
		"about":
			_detail_title.text = "NEON FOUNDRY RACING"
			_detail_subtitle.text = "An original Android hovercraft racing project created in Godot 4.5.1, Blender, and Mobile/Vulkan. The title and main menu are our first interactive milestone."
		_:
			return
	_show_page("detail")

func _on_volume_changed(value: float) -> void:
	_master_volume = value
	_apply_settings()
	_save_settings()

func _on_motion_changed(enabled: bool) -> void:
	_menu_motion = enabled
	_apply_settings()
	_save_settings()

func _on_fps_changed(enabled: bool) -> void:
	_show_fps = enabled
	_apply_settings()
	_save_settings()

func _restore_defaults() -> void:
	_master_volume = 0.8
	_menu_motion = true
	_show_fps = false
	_volume_slider.set_value_no_signal(_master_volume)
	_motion_button.set_pressed_no_signal(_menu_motion)
	_fps_button.set_pressed_no_signal(_show_fps)
	_apply_settings()
	_save_settings()

func _apply_settings() -> void:
	if AudioServer.get_bus_count() > 0:
		AudioServer.set_bus_mute(0, _master_volume < 0.001)
		AudioServer.set_bus_volume_db(0, linear_to_db(maxf(_master_volume, 0.001)))
	if _backdrop != null:
		_backdrop.set("motion_enabled", _menu_motion)
	if _chrome != null:
		_chrome.set("motion_enabled", _menu_motion)
	if _fps_label != null:
		_fps_label.visible = _show_fps

func _save_settings() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("audio", "master", _master_volume)
	cfg.set_value("menu", "animation", _menu_motion)
	cfg.set_value("menu", "show_fps", _show_fps)
	var err: Error = cfg.save(SETTINGS_FILE)
	if err != OK:
		push_warning("Unable to save local menu settings: %d" % err)

func _load_settings() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(SETTINGS_FILE) != OK:
		return
	_master_volume = clampf(float(cfg.get_value("audio", "master", 0.8)), 0.0, 1.0)
	_menu_motion = bool(cfg.get_value("menu", "animation", true))
	_show_fps = bool(cfg.get_value("menu", "show_fps", false))

func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	if event.keycode == KEY_ESCAPE or event.keycode == KEY_BACK:
		if current_page == "title":
			get_tree().quit()
		elif current_page == "menu":
			show_title()
		else:
			show_main_menu()
		get_viewport().set_input_as_handled()
	elif current_page == "title" and (event.keycode == KEY_ENTER or event.keycode == KEY_SPACE):
		show_main_menu()
		get_viewport().set_input_as_handled()

func _capture_screen(filename: String, capture_page: String) -> void:
	_show_page(capture_page)
	for frame in range(8):
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var destination: String = ProjectSettings.globalize_path("res://../build/" + filename)
	var error: Error = get_viewport().get_texture().get_image().save_png(destination)
	if error != OK:
		push_error("Menu capture failed: %d" % error)
	else:
		print("NEON_FOUNDRY_MENU_CAPTURE_OK " + filename)
	get_tree().quit()
