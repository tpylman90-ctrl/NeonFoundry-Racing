extends Control
## Lightweight, original procedural title artwork. No textures, external art,
## models, GPU-heavy effects, or gameplay assets are required at boot.

var motion_enabled: bool = true
var _clock: float = 0.0
var _draw_budget: float = 0.0

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(queue_redraw)

func _process(delta: float) -> void:
	if not motion_enabled:
		return
	_clock += delta
	_draw_budget += delta
	if _draw_budget >= 1.0 / 24.0:
		_draw_budget = 0.0
		queue_redraw()

func _draw() -> void:
	var w: float = size.x
	var h: float = size.y
	if w < 10.0 or h < 10.0:
		return
	var horizon: float = h * 0.565
	var pulse: float = 0.5 + 0.5 * sin(_clock * 0.95)

	# Navy gradient and atmosphere, built entirely from CanvasItem geometry.
	for i in range(48):
		var t: float = float(i) / 47.0
		var color: Color = Color("050d1a").lerp(Color("1a3140"), pow(t, 1.6))
		draw_rect(Rect2(0.0, float(i) * h / 48.0, w, h / 48.0 + 1.0), color)
	for i in range(12):
		var y: float = horizon - 96.0 + float(i) * 15.0
		draw_rect(Rect2(0.0, y, w, 15.0), Color(0.11, 0.29, 0.34, (1.0 - float(i) / 12.0) * 0.045))

	# Uneven skyline, reading as a high-speed city rather than a flat panorama.
	for i in range(31):
		var x: float = 260.0 + float(i) * (w - 170.0) / 30.0
		var width: float = 21.0 + float((i * 13) % 19)
		var height: float = 52.0 + float((i * 47 + 17) % 158)
		var top: float = horizon - height
		var tint: Color = Color("101d2c") if i % 3 == 0 else Color("132736")
		draw_rect(Rect2(x, top, width, height + 6.0), tint)
		draw_rect(Rect2(x, top, width, 1.6), Color(0.26, 0.74, 0.79, 0.27))
		for row in range(2, int(height / 17.0)):
			for column in range(2):
				if (i * 7 + row * 5 + column * 3) % 5 < 2:
					draw_rect(Rect2(x + 7.0 + column * 11.0, top + 8.0 + row * 15.0, 3.0, 4.0), Color(0.27, 0.72, 0.80, 0.33))

	# The road tapers into the horizon; it is just menu artwork, not an in-game route.
	var vanishing: Vector2 = Vector2(w * 0.745, horizon + 5.0)
	var near_left: Vector2 = Vector2(w * 0.275, h + 30.0)
	var near_right: Vector2 = Vector2(w * 1.15, h + 30.0)
	draw_colored_polygon(PackedVector2Array([vanishing + Vector2(-13, 0), vanishing + Vector2(23, 0), near_right, near_left]), Color("172630"))
	draw_line(vanishing + Vector2(-12, 0), near_left, Color("d96352"), 5.0, true)
	draw_line(vanishing + Vector2(23, 0), near_right, Color("43b3bd"), 4.0, true)
	for i in range(1, 10):
		var depth: float = fposmod(float(i) / 10.0 + (_clock * 0.17 if motion_enabled else 0.0), 1.0)
		depth = pow(depth, 2.05)
		var left: Vector2 = vanishing.lerp(near_left, depth)
		var right: Vector2 = vanishing.lerp(near_right, depth)
		draw_line(left, right, Color(0.27, 0.69, 0.74, 0.035 + depth * 0.12), 1.5, true)

	# An original stylized hovercraft-shaped graphic. The production vehicle
	# will later be its own inspectable Blender asset, NOT this illustration.
	var anchor: Vector2 = Vector2(w * 0.765, h * 0.745)
	var bob: float = sin(_clock * 1.5) * 3.5 if motion_enabled else 0.0
	anchor.y += bob
	draw_circle(anchor + Vector2(-12, 36), 92.0, Color(0.11, 0.80, 0.83, 0.045 + pulse * 0.018))
	draw_colored_polygon(PackedVector2Array([
		anchor + Vector2(-138, 13), anchor + Vector2(-92, -18),
		anchor + Vector2(52, -30), anchor + Vector2(148, 10),
		anchor + Vector2(110, 33), anchor + Vector2(-95, 42)
	]), Color("263b49"))
	draw_colored_polygon(PackedVector2Array([
		anchor + Vector2(-93, -21), anchor + Vector2(-39, -64),
		anchor + Vector2(55, -58), anchor + Vector2(95, -18),
		anchor + Vector2(41, -8), anchor + Vector2(-76, 0)
	]), Color("43586a"))
	draw_colored_polygon(PackedVector2Array([
		anchor + Vector2(-30, -60), anchor + Vector2(38, -60),
		anchor + Vector2(65, -31), anchor + Vector2(-53, -27)
	]), Color("102a38"))
	for side in [-1.0, 1.0]:
		var loc: Vector2 = anchor + Vector2(side * 106.0, 33.0)
		draw_circle(loc, 25.0, Color("13202b"))
		draw_arc(loc, 23.0, 0.2, TAU - 0.2, 38, Color(0.24, 0.84, 0.85, 0.85), 3.5, true)
		draw_circle(loc, 11.0, Color("307983"))
	draw_line(anchor + Vector2(-111, 17), anchor + Vector2(119, 12), Color("c85d4e"), 3.0, true)
	draw_line(anchor + Vector2(-62, 41), anchor + Vector2(87, 38), Color(0.28, 0.91, 0.92, 0.82), 2.0, true)

	# Left vignette keeps the typography legible over the backdrop.
	for stripe in range(24):
		var x: float = float(stripe) * w * 0.67 / 24.0
		var opacity: float = pow(1.0 - float(stripe) / 24.0, 1.15) * 0.71
		draw_rect(Rect2(x, 0, w * 0.67 / 24.0 + 1.0, h), Color(0.015, 0.027, 0.051, opacity))

	draw_rect(Rect2(0, 0, w, 4.0), Color("e36b57"))
	draw_line(Vector2(w * 0.59, 0), Vector2(w, 0), Color("50c9cf"), 2.0, true)
