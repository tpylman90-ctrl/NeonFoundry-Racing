extends Control
const PageBackdrop = preload("res://scripts/page_backdrop.gd")
## Lightweight, touch-first navigation skeleton. No craft, race, checkout, or rewards are simulated as production gameplay.
signal request_main_menu
signal request_device_settings
signal request_garage
signal flow_page_changed(page: String)

const CYAN: Color = Color("4dd5db")
const AMBER: Color = Color("f69b70")
const PALE: Color = Color("eef5fb")
const MUTED: Color = Color("a4b5c4")

const TRACKS: Array[Dictionary] = [
	{"id": "neon_cross", "name": "NEON CROSS", "modes": ["hybrid", "aerial"], "detail": "Skyline gaps, a steep climb, and an open-air descent."},
	{"id": "crimson_serpent", "name": "CRIMSON SERPENT", "modes": ["surface", "hybrid"], "detail": "Canyon walls, sweeping turns, and mixed terrain."},
	{"id": "skyfall_run", "name": "SKYFALL RUN", "modes": ["hybrid", "aerial"], "detail": "High-altitude sections and long airborne transitions."}
]

var current_page: String = ""
var selected_mode: String = "hybrid"
var selected_track: String = ""
var selected_craft: String = "NF-H01 / UI TEST MULE"
var _history: Array[String] = []
var _eyebrow: Label
var _stage: Control
var _title: Label
var _summary: Label
var _content: VBoxContainer
var _back: Button
var _status: Label

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_build_shell()

func _build_shell() -> void:
	_stage = Control.new()
	_stage.name = "PageAtmosphere"
	_stage.set_script(PageBackdrop)
	_stage.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_stage)
	var panel := PanelContainer.new()
	panel.name = "FlowPanel"
	panel.anchor_left = 0.04
	panel.anchor_top = 0.10
	panel.anchor_right = 0.615
	panel.anchor_bottom = 0.923
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.013, 0.035, 0.057, 0.93)
	style.border_color = Color(0.22, 0.64, 0.74, 0.7)
	style.border_width_left = 3
	style.border_width_top = 1
	style.set_corner_radius_all(7)
	style.content_margin_left = 23
	style.content_margin_right = 23
	style.content_margin_top = 14
	style.content_margin_bottom = 13
	panel.add_theme_stylebox_override("panel", style)
	add_child(panel)

	var shell := VBoxContainer.new()
	shell.add_theme_constant_override("separation", 7)
	panel.add_child(shell)
	_eyebrow = _label("", 15, AMBER)
	shell.add_child(_eyebrow)
	_title = _label("", 38, PALE)
	shell.add_child(_title)
	_summary = _label("", 16, MUTED)
	_summary.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	shell.add_child(_summary)
	shell.add_child(HSeparator.new())

	var scrolling := ScrollContainer.new()
	scrolling.name = "FlowScroll"
	scrolling.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scrolling.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	shell.add_child(scrolling)
	_content = VBoxContainer.new()
	_content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_content.add_theme_constant_override("separation", 9)
	scrolling.add_child(_content)

	shell.add_child(HSeparator.new())
	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation", 10)
	shell.add_child(actions)
	_back = _button("‹  BACK")
	_back.custom_minimum_size.x = 148
	_back.pressed.connect(navigate_back)
	actions.add_child(_back)
	var home := _button("⌂  MAIN HUB")
	home.custom_minimum_size.x = 170
	home.pressed.connect(func() -> void: request_main_menu.emit())
	actions.add_child(home)
	_status = _label("PRE-ALPHA  /  INTERFACE FRAMEWORK", 12, CYAN)
	_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_status.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	actions.add_child(_status)

func _label(value: String, font_size: int, tint: Color) -> Label:
	var label := Label.new()
	label.text = value
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", tint)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label

func _button(value: String, prominent: bool = false) -> Button:
	var button := Button.new()
	button.text = value
	button.custom_minimum_size.y = 48
	button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	button.alignment = HORIZONTAL_ALIGNMENT_CENTER
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	button.add_theme_font_size_override("font_size", 17)
	button.add_theme_color_override("font_color", PALE)
	button.add_theme_color_override("font_hover_color", Color.WHITE)
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(0.052, 0.28, 0.36, 0.95) if prominent else Color(0.035, 0.093, 0.133, 0.91)
	normal.border_color = AMBER if prominent else Color(0.20, 0.53, 0.61)
	normal.border_width_left = 4 if prominent else 2
	normal.border_width_bottom = 1
	normal.set_corner_radius_all(5)
	normal.content_margin_left = 12
	normal.content_margin_right = 12
	button.add_theme_stylebox_override("normal", normal)
	var hover: StyleBoxFlat = normal.duplicate()
	hover.bg_color = Color(0.08, 0.36, 0.45, 1)
	button.add_theme_stylebox_override("hover", hover)
	button.add_theme_stylebox_override("pressed", hover)
	return button

func _action(label_text: String, callback: Callable, prominent: bool = false, enabled: bool = true) -> Button:
	var button: Button = _button(label_text, prominent)
	button.disabled = not enabled
	button.pressed.connect(callback)
	_content.add_child(button)
	return button

func _pair(first: String, first_call: Callable, second: String, second_call: Callable) -> void:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	var a := _button(first)
	a.pressed.connect(first_call)
	row.add_child(a)
	var b := _button(second)
	b.pressed.connect(second_call)
	row.add_child(b)
	_content.add_child(row)

func _note(text_value: String) -> void:
	var note := _label(text_value, 16, MUTED)
	note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_content.add_child(note)

func _card(head: String, body: String) -> void:
	var panel := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.038, 0.075, 0.111, 0.9)
	style.border_width_left = 2
	style.border_color = Color(0.24, 0.65, 0.71)
	style.content_margin_left = 14
	style.content_margin_right = 14
	style.content_margin_top = 10
	style.content_margin_bottom = 10
	style.set_corner_radius_all(4)
	panel.add_theme_stylebox_override("panel", style)
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 4)
	panel.add_child(column)
	column.add_child(_label(head, 19, CYAN))
	var description := _label(body, 15, MUTED)
	description.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	column.add_child(description)
	_content.add_child(panel)

func _header(overline: String, heading: String, description: String) -> void:
	_eyebrow.text = overline
	_title.text = heading
	_summary.text = description

func open_page(page: String) -> void:
	_history.clear()
	_set_page(page)

func _goto(page: String) -> void:
	if current_page != "":
		_history.append(current_page)
	_set_page(page)

func _set_page(page: String) -> void:
	current_page = page
	_render()
	flow_page_changed.emit(current_page)

func navigate_back() -> void:
	if _history.is_empty():
		request_main_menu.emit()
	else:
		_set_page(_history.pop_back())

func _choose_mode(mode: String) -> void:
	selected_mode = mode
	selected_track = ""
	_goto("tracks")

func _choose_track(track_id: String) -> void:
	selected_track = track_id
	_goto("lobby")

func _selected_track() -> Dictionary:
	for track in TRACKS:
		if track["id"] == selected_track:
			return track
	return {}

func _start_flow_demo() -> void:
	_goto("loading")

func _demo_finished() -> void:
	_goto("results")

func _render() -> void:
	if _stage != null:
		_stage.set("current_page", current_page)
		_stage.queue_redraw()
	if _content == null:
		return
	for item in _content.get_children():
		_content.remove_child(item)
		item.queue_free()
	_back.text = "‹  BACK" if not _history.is_empty() else "‹  HUB"
	_status.text = "UI PROTOTYPE  /  NO LIVE RACE"
	match current_page:
		"garage":
			_header("03 / VEHICLE BAY", "THE GARAGE", "Select, inspect, tune, and customize your craft.")
			_card("NF-H01  /  TEST SLOT", "Temporary UI-only craft slot. The finished hero model and ownership data have not been connected.")
			_action("SELECT CRAFT", func() -> void: _goto("craft"), true)
			_pair("PERFORMANCE / TUNING", func() -> void: _goto("tuning"), "VISUAL CUSTOMIZATION", func() -> void: _goto("customize"))
			_action("QUICK JUMP / RACE CONTROL", func() -> void: _goto("mode"))
		"craft":
			_header("GARAGE / CAR SELECT", "CRAFT SELECTION", "Vehicle slots are ready for the approved GLB fleet.")
			_card(selected_craft, "Class: PROTOTYPE. No imported model, inspection camera, or valid race performance data yet.")
			_action("USE UI TEST SLOT", func() -> void: _goto("garage"), true)
		"tuning":
			_header("GARAGE / PERFORMANCE", "TUNING BAY", "Prepared for speed, acceleration, lift, handling, and braking parameters.")
			_card("BASELINE / NOT CONNECTED", "Values and upgrade costs will be read from versioned craft data. Tuning controls are intentionally inactive until physics exists.")
			_action("APPLY TUNE  /  NOT AVAILABLE", func() -> void: pass, false, false)
		"customize":
			_header("GARAGE / APPEARANCE", "CUSTOMIZATION", "Paint, clearcoat, materials, liveries, and engine effects.")
			_card("COSMETIC WORKSHOP / PLACEHOLDER", "Part highlighting, material swaps, and live 3D inspection will be installed after the craft is approved.")
			_action("SAVE DESIGN  /  NOT AVAILABLE", func() -> void: pass, false, false)
		"store":
			_header("04 / DEALERSHIP", "THE SHOWROOM", "Browse vehicles and upgrades. Purchases are not enabled.")
			_pair("NEW VEHICLES", func() -> void: _goto("store_vehicles"), "PARTS & UPGRADES", func() -> void: _goto("store_parts"))
			_pair("CURRENCY BUNDLES", func() -> void: _goto("store_bundles"), "FEATURED DEALS", func() -> void: _goto("store_featured"))
			_note("Offline pre-alpha: no purchases, billing, ads, or live storefront.")
		"store_vehicles", "store_parts", "store_bundles", "store_featured":
			var titles: Dictionary = {
				"store_vehicles": "VEHICLE CATALOG",
				"store_parts": "PARTS & UPGRADES",
				"store_bundles": "CURRENCY BUNDLES",
				"store_featured": "FEATURED / DAILY"
			}
			_header("DEALERSHIP / PREVIEW", str(titles[current_page]), "Catalog layout only; not a working shop.")
			_card("NO INVENTORY AVAILABLE", "Pricing, ownership checks, availability, and transactions will be added only when the economy is designed.")
			_action("CHECKOUT  /  DISABLED", func() -> void: pass, false, false)
		"profile":
			_header("05 / DRIVER TERMINAL", "PROFILE & SETTINGS", "Manage driving assists, device preferences, and driver progression.")
			_pair("CONTROLS / ASSISTS", func() -> void: _goto("controls"), "AUDIO / GRAPHICS", func() -> void: request_device_settings.emit())
			_action("STATS / ACHIEVEMENTS", func() -> void: _goto("achievements"))
			_note("Audio volume, menu motion, and the FPS overlay already save to this device.")
		"controls":
			_header("PROFILE / INPUT", "CONTROLS & ASSISTS", "Touch control layout, steering sensitivity, brake/reverse, hover stabilization.")
			_card("DRIVING CONTROLS / NOT CONNECTED", "Actual control binding and assist calibration require a working vehicle controller.")
			_action("APPLY CONTROLS  /  DISABLED", func() -> void: pass, false, false)
		"achievements":
			_header("PROFILE / PROGRESSION", "DRIVER STATS", "Race history, XP, credits, records, achievements, and unlocks.")
			_card("NO RECORDED RACES", "Driver progression will be backed by a versioned local save once actual events and scoring exist.")
		"mode":
			_header("06 / RACE CONTROL", "SELECT A MODE", "The three intended disciplines use the same craft with different race demands.")
			_action("SURFACE  /  GROUNDED RACING", func() -> void: _choose_mode("surface"), true)
			_action("HYBRID  /  ROAD + OPEN AIR", func() -> void: _choose_mode("hybrid"))
			_action("AERIAL  /  3D FLIGHT GATES", func() -> void: _choose_mode("aerial"))
		"tracks":
			_header("07 / COURSE TERMINAL", "TRACK SELECTION", "Mode: %s  /  Proposed venues; no track scenes loaded yet." % selected_mode.to_upper())
			var compatible_count: int = 0
			for track in TRACKS:
				var allowed: bool = selected_mode in track["modes"]
				if allowed:
					compatible_count += 1
				_card(str(track["name"]) + ("  /  COMPATIBLE" if allowed else "  /  OTHER DISCIPLINE"), str(track["detail"]))
				if allowed:
					_action("SELECT  /  " + str(track["name"]), _choose_track.bind(str(track["id"])))
			if compatible_count == 0:
				_note("No tracks support this discipline yet.")
		"lobby":
			_header("08 / EVENT CHECK", "PRE-RACE LOBBY", "Confirm your selected mode, venue, and craft before loading.")
			var track: Dictionary = _selected_track()
			_card("EVENT / " + str(track.get("name", "NO TRACK")), "Discipline: %s. Venue is currently a selection record, not a playable Godot scene." % selected_mode.to_upper())
			_card("CRAFT / " + selected_craft, "Eligibility: UI DEMO ONLY. Vehicle class, upgrades, and rule validation cannot be evaluated yet.")
			_pair("CHANGE CRAFT / GARAGE", func() -> void: request_garage.emit(), "CHANGE TRACK", func() -> void: _goto("tracks"))
			_action("LAUNCH UI FLOW DEMO", _start_flow_demo, true)
		"loading":
			_header("09 / RACE INITIALIZATION", "LOADING", "Preparing interface demonstration...")
			_card("TRACK CARD / " + str(_selected_track().get("name", "UNKNOWN")), "Future: async course loading, asset warm-up, minimap, gameplay tips, and performance checks.")
			_note("No track assets or real race scene are loaded in this prototype.")
			get_tree().create_timer(1.2).timeout.connect(func() -> void:
				if is_inside_tree() and current_page == "loading":
					_goto("race_demo")
			)
		"race_demo":
			_header("10 / RACE TELEMETRY", "IN-RACE HUD", "SCREEN DEMO ONLY / no vehicle simulation or collision physics.")
			_card("SPEED  000 KM/H    |    LAP --/--", "Position --  /  Time 00:00.000  /  Boost --  /  Energy --")
			_card("COURSE / " + str(_selected_track().get("name", "UNKNOWN")), "HUD elements are placeholders for live telemetry and a 3D chase/cockpit camera.")
			_pair("PAUSE", func() -> void: _goto("pause"), "FINISH FLOW DEMO", _demo_finished)
		"pause":
			_header("RACE / PAUSED", "PAUSE MENU", "UI demo paused. This is not an active physics simulation.")
			_action("RESUME DEMO", func() -> void: navigate_back(), true)
			_action("RESTART DEMO", _start_flow_demo)
			_action("QUIT TO MAIN HUB", func() -> void: request_main_menu.emit())
		"results":
			_header("11 / EVENT SUMMARY", "POST-RACE RESULTS", "UI-flow test completed; no race has been recorded.")
			_card("DEMO COMPLETE  /  NO PODIUM RESULT", "XP +0  /  Credits +0  /  Time N/A. No actual rewards or profile updates are issued.")
			_pair("RESTART DEMO", _start_flow_demo, "NEXT EVENT", func() -> void: _goto("tracks"))
			_action("EXIT TO MAIN HUB", func() -> void: request_main_menu.emit(), true)
		_:
			_header("NEON FOUNDRY", "MODULE UNAVAILABLE", "Return to the hub and choose a supported destination.")
