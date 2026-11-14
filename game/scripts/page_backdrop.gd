extends Control
## Purpose-built full-screen backgrounds for each independent page.
## All panels remain native Godot controls; artwork never captures touch input.
var current_page: String = "store"

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(queue_redraw)

func _draw() -> void:
	var w: float = size.x
	var h: float = size.y
	if w < 10 or h < 10:
		return
	var store: bool = current_page.begins_with("store")
	var profile: bool = current_page in ["profile", "controls", "achievements"]
	var results: bool = current_page == "results"
	var event: bool = not store and not profile and not results
	var base: Color = Color("10141c") if store else (Color("101e2a") if profile else Color("071324"))
	var accent: Color = Color("ffae6e") if store else (Color("74e5dd") if profile else Color("4ccefa"))
	draw_rect(Rect2(0, 0, w, h), base)
	for i in range(25):
		var x: float = float(i) * w / 24.0
		draw_line(Vector2(x, 0), Vector2(x, h), Color(accent.r, accent.g, accent.b, 0.035), 1.0)
	for i in range(13):
		var y: float = float(i) * h / 12.0
		draw_line(Vector2(0, y), Vector2(w, y), Color(accent.r, accent.g, accent.b, 0.04), 1.0)
	draw_rect(Rect2(0, 0, w, 5), accent)
	draw_rect(Rect2(0, h - 5, w, 5), accent.darkened(0.3))
	draw_line(Vector2(w * 0.71, 0), Vector2(w * 0.71, h), Color(accent.r, accent.g, accent.b, 0.13), 1.0)
	var cx: float = w * 0.805
	var cy: float = h * 0.52
	if store:
		draw_rect(Rect2(w * 0.625, h * 0.24, w * 0.32, h * 0.55), Color("202e38"))
		for i in range(3):
			var tx: float = w * (0.666 + float(i) * 0.098)
			var ty: float = h * (0.64 - 0.045 * float(i % 2))
			draw_colored_polygon(PackedVector2Array([
				Vector2(tx - 42, ty), Vector2(tx - 20, ty - 38),
				Vector2(tx + 34, ty - 34), Vector2(tx + 57, ty),
				Vector2(tx + 10, ty + 20), Vector2(tx - 28, ty + 20)
			]), Color("4c6170"))
			draw_line(Vector2(tx - 28, ty + 23), Vector2(tx + 56, ty + 23), accent, 4.0, true)
			draw_rect(Rect2(tx - 49, ty + 32, 106, 6), Color("17242b"))
		draw_string(ThemeDB.fallback_font, Vector2(w * 0.66, h * 0.22), "DEALERSHIP", HORIZONTAL_ALIGNMENT_LEFT, -1, 30, accent)
		draw_string(ThemeDB.fallback_font, Vector2(w * 0.65, h * 0.86), "SHOWROOM / PRE-ALPHA", HORIZONTAL_ALIGNMENT_LEFT, -1, 17, accent)
	elif profile:
		draw_arc(Vector2(cx, cy - 46), 112.0, 0, TAU, 88, Color(accent.r, accent.g, accent.b, 0.43), 3.5, true)
		draw_arc(Vector2(cx, cy - 46), 87.0, 0.4, TAU - 0.4, 88, Color(accent.r, accent.g, accent.b, 0.30), 1.8, true)
		draw_circle(Vector2(cx, cy - 87), 30, Color("48677c"))
		draw_colored_polygon(PackedVector2Array([
			Vector2(cx - 72, cy + 6), Vector2(cx - 51, cy - 30),
			Vector2(cx + 51, cy - 30), Vector2(cx + 72, cy + 6)
		]), Color("48677c"))
		for i in range(4):
			draw_rect(Rect2(cx - 115, cy + 115 + float(i) * 22, 230, 9), Color("203849"))
			draw_rect(Rect2(cx - 115, cy + 115 + float(i) * 22, 45.0 + float(i % 3) * 36, 9), accent.darkened(0.40))
		draw_string(ThemeDB.fallback_font, Vector2(w * 0.714, h * 0.24), "DRIVER IDENTITY", HORIZONTAL_ALIGNMENT_LEFT, -1, 26, accent)
	elif results:
		var sizes: Array[float] = [70.0, 124.0, 92.0]
		for i in range(3):
			var x: float = cx - 134 + float(i) * 112.0
			var height: float = sizes[i]
			draw_rect(Rect2(x - 42, cy + 70 - height, 85, height), Color("235267"))
			draw_rect(Rect2(x - 42, cy + 70 - height, 85, 7), accent)
			draw_string(ThemeDB.fallback_font, Vector2(x - 13, cy + 46 - height), str(i + 1), HORIZONTAL_ALIGNMENT_LEFT, -1, 29, Color("e8eff2"))
		draw_string(ThemeDB.fallback_font, Vector2(w * 0.69, h * 0.24), "RESULTS / DEMO", HORIZONTAL_ALIGNMENT_LEFT, -1, 27, accent)
	elif event:
		for layer in range(8):
			var depth: float = float(layer) / 8.0
			var yy: float = h * (0.43 + depth * 0.55)
			draw_line(Vector2(w * (0.74 - depth * 0.22), yy), Vector2(w * (0.83 + depth * 0.29), yy), Color(accent.r, accent.g, accent.b, 0.18 + depth * 0.15), 1.7, true)
		draw_colored_polygon(PackedVector2Array([
			Vector2(cx - 10, h * 0.40), Vector2(cx + 30, h * 0.40),
			Vector2(w * 1.05, h), Vector2(w * 0.52, h)
		]), Color("132c42"))
		draw_line(Vector2(cx - 10, h * 0.40), Vector2(w * 0.52, h), accent, 3.2, true)
		draw_line(Vector2(cx + 30, h * 0.40), Vector2(w * 1.05, h), accent, 3.2, true)
		for i in range(3):
			var z: float = 1.0 - float(i) * 0.23
			var x: float = cx + 22 * float(i)
			var y: float = h * (0.54 - float(i) * 0.07)
			var wide: float = 55.0 * z
			var high: float = 82.0 * z
			draw_polyline(PackedVector2Array([
				Vector2(x - wide, y + high), Vector2(x - wide, y - high),
				Vector2(x + wide, y - high), Vector2(x + wide, y + high)
			]), accent, 3.0, true)
		var tag: String = "RACE CONTROL"
		if current_page == "tracks":
			tag = "TRACK SELECT"
		elif current_page == "lobby":
			tag = "GRID / PRE-RACE"
		elif current_page == "race_demo":
			tag = "TELEMETRY SIMULATION"
		elif current_page == "pause":
			tag = "RACE PAUSED"
		elif current_page == "loading":
			tag = "LOADING"
		draw_string(ThemeDB.fallback_font, Vector2(w * 0.71, h * 0.22), tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 25, accent)
		draw_string(ThemeDB.fallback_font, Vector2(w * 0.73, h * 0.82), "NO LIVE TRACK", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, accent)
