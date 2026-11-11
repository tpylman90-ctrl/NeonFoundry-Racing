extends Control
## Boot/title -> main menu -> informational sections and persistent settings.
## Garage and races are clearly labelled as future milestones.

signal page_changed(next_page: String)

const BackdropScript = preload("res://scripts/menu_backdrop.gd")
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

func _process(_delta: float) -> void:
	if _fps_label != null and _fps_label.visible:
		_fps_label.text = "FPS  %d" % Engine.get_frames_per_second()

func _build_interface() -> void:
	_backdrop = Control.new()
	_backdrop.name = "ProceduralBackdrop"
	_backdrop.set_script(BackdropScript)
	_backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_backdrop)

	var top_brand: Label = _label("NF  /  NEON FOUNDRY", 20, CYAN, true)
	top_brand.anchor_left = 0.055
	top_brand.anchor_top = 0.047
	top_brand.anchor_right = 0.44
	top_brand.anchor_bottom = 0.10
	add_child(top_brand)

	var version: Label = _label("MOTORSPORT DIVISION    •    PRE-ALPHA", 16, MUTED, true)
	version.anchor_left = 0.55
	version.anchor_right = 0.96
	version.anchor_top = 0.052
	version.anchor_bottom = 0.11
	version.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	add_child(version)

	_fps_label = _label("FPS  --", 16, CYAN, true)
	_fps_label.anchor_left = 0.80
	_fps_label.anchor_right = 0.97
	_fps_label.anchor_top = 0.12
	_fps_label.anchor_bottom = 0.16
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

	var footer: Label = _label("BUILD 0.1  /  ANDROID • MOBILE/VULKAN  /  ORIGINAL GAME IN DEVELOPMENT", 14, Color("698391"), true)
	footer.anchor_left = 0.054
	footer.anchor_right = 0.95
	footer.anchor_top = 0.948
	footer.anchor_bottom = 0.99
	add_child(footer)

func _build_title() -> void:
	var anywhere: Button = Button.new()
	anywhere.name = "TapAnywhere"
	anywhere.flat = true
	anywhere.focus_mode = Control.FOCUS_NONE
	anywhere.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	anywhere.pressed.connect(show_main_menu)
	_title_page.add_child(anywhere)

	var column: VBoxContainer = _column(0.073, 0.20, 0.68, 0.83, 11)
	_title_page.add_child(column)
	column.add_child(_label("THE NEXT GENERATION OF HOVER MOTORSPORT", 18, AMBER, true))
	column.add_child(_label("NEON", 83, PALE, true))
	column.add_child(_label("FOUNDRY", 83, PALE, true))
	column.add_child(_label("R A C I N G", 40, CYAN, true))
	column.add_child(_label("OWN THE CRAFT. KNOW THE MACHINE.\nRACE BEYOND THE ROAD.", 20, MUTED))
	var spacer := Control.new()
	spacer.custom_minimum_size.y = 16.0
	column.add_child(spacer)
	var play: Button = _button("ENTER THE FOUNDRY  >", true)
	play.custom_minimum_size.x = 390.0
	play.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	play.pressed.connect(show_main_menu)
	column.add_child(play)
	column.add_child(_label("TAP ANYWHERE OR PRESS ENTER", 15, MUTED, true))

func _build_menu() -> void:
	var column: VBoxContainer = _column(0.073, 0.12, 0.48, 0.93, 9)
	_menu_page.add_child(column)
	column.add_child(_label("RACE CONTROL / PLAYER HOME", 17, AMBER, true))
	column.add_child(_label("MAIN MENU", 55, PALE, true))
	column.add_child(_label("YOUR MACHINE. YOUR GARAGE. YOUR RACE.", 17, MUTED))
	var gap := Control.new()
	gap.custom_minimum_size.y = 12.0
	column.add_child(gap)
	var garage: Button = _button("01    ENTER GARAGE       [PREVIEW]", true)
	garage.pressed.connect(func() -> void: _open_section("garage"))
	column.add_child(garage)
	var races: Button = _button("02    RACE CONTROL        [PREVIEW]")
	races.pressed.connect(func() -> void: _open_section("races"))
	column.add_child(races)
	var settings: Button = _button("03    SETTINGS")
	settings.pressed.connect(open_settings)
	column.add_child(settings)
	var about: Button = _button("04    ABOUT THE PROJECT")
	about.pressed.connect(func() -> void: _open_section("about"))
	column.add_child(about)
	var title: Button = _button("05    RETURN TO TITLE")
	title.pressed.connect(show_title)
	column.add_child(title)
	var quit: Button = _button("06    QUIT")
	quit.pressed.connect(func() -> void: get_tree().quit())
	column.add_child(quit)

func _build_detail() -> void:
	var col: VBoxContainer = _column(0.078, 0.24, 0.61, 0.84, 20)
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
	panel.anchor_left = 0.067
	panel.anchor_top = 0.12
	panel.anchor_right = 0.57
	panel.anchor_bottom = 0.925
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
	b.custom_minimum_size.y = 59.0
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	b.add_theme_font_size_override("font_size", 21)
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
	sb.bg_color = Color("275363") if primary else Color(0.04, 0.09, 0.14, 0.88)
	if hovered:
		sb.bg_color = Color("336a77")
	sb.set_corner_radius_all(5)
	sb.content_margin_left = 20
	sb.content_margin_right = 12
	sb.border_width_left = 4 if primary else 2
	sb.border_color = AMBER if primary else Color("3b7d8a")
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
	sb.bg_color = Color(0.027, 0.066, 0.102, 0.93)
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
