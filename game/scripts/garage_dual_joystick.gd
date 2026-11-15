extends Control
## Two independently captured touchscreen sticks for garage walkaround.
## Draw-only overlay: touch ownership is handled by GaragePage._input(), which
## prevents SubViewport camera gestures from stealing either finger.
##
## Left:  X = strafe, -Y = forward. Right: X = yaw, -Y = look up.
## Normalized analog vectors have a circular dead zone and return to zero
## immediately on release or on leaving walk mode.

const LEFT_TINT: Color = Color("5ddfea")
const RIGHT_TINT: Color = Color("ffb16e")
const RING_BG: Color = Color(0.012, 0.046, 0.068, 0.70)
const DEAD_ZONE: float = 0.11
const HIT_MULTIPLIER: float = 1.29

var move_axis: Vector2 = Vector2.ZERO
var look_axis: Vector2 = Vector2.ZERO
var move_finger: int = -1
var look_finger: int = -1


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	queue_redraw()


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		queue_redraw()


func get_radius() -> float:
	return clampf(size.y * 0.109, 48.0, 83.0)


func get_stick_center(right: bool) -> Vector2:
	var width_fraction: float = 0.85 if right else 0.145
	return Vector2(size.x * width_fraction, size.y * 0.742)


func _analog(pointer: Vector2, center: Vector2) -> Vector2:
	var delta: Vector2 = (pointer - center) / get_radius()
	var intensity: float = minf(delta.length(), 1.0)
	if intensity <= DEAD_ZONE:
		return Vector2.ZERO
	return delta.normalized() * ((intensity - DEAD_ZONE) / (1.0 - DEAD_ZONE))


func handle_screen_event(event: InputEvent) -> bool:
	if not visible:
		return false
	if event is InputEventScreenTouch:
		var touch: InputEventScreenTouch = event
		var local_pointer: Vector2 = touch.position - get_global_rect().position
		if touch.pressed:
			if move_finger == -1 and local_pointer.distance_to(
					get_stick_center(false)) <= get_radius() * HIT_MULTIPLIER:
				move_finger = touch.index
				move_axis = _analog(local_pointer, get_stick_center(false))
				queue_redraw()
				return true
			if look_finger == -1 and local_pointer.distance_to(
					get_stick_center(true)) <= get_radius() * HIT_MULTIPLIER:
				look_finger = touch.index
				look_axis = _analog(local_pointer, get_stick_center(true))
				queue_redraw()
				return true
		elif touch.index == move_finger:
			move_finger = -1
			move_axis = Vector2.ZERO
			queue_redraw()
			return true
		elif touch.index == look_finger:
			look_finger = -1
			look_axis = Vector2.ZERO
			queue_redraw()
			return true
	elif event is InputEventScreenDrag:
		var drag: InputEventScreenDrag = event
		var pointer: Vector2 = drag.position - get_global_rect().position
		if drag.index == move_finger:
			move_axis = _analog(pointer, get_stick_center(false))
			queue_redraw()
			return true
		if drag.index == look_finger:
			look_axis = _analog(pointer, get_stick_center(true))
			queue_redraw()
			return true
	return false


func release_all() -> void:
	move_finger = -1
	look_finger = -1
	move_axis = Vector2.ZERO
	look_axis = Vector2.ZERO
	queue_redraw()


func _draw() -> void:
	var radius: float = get_radius()
	var font: Font = ThemeDB.fallback_font
	for side in range(2):
		var right: bool = side == 1
		var center: Vector2 = get_stick_center(right)
		var axis: Vector2 = look_axis if right else move_axis
		var tint: Color = RIGHT_TINT if right else LEFT_TINT
		var active: bool = look_finger >= 0 if right else move_finger >= 0
		draw_circle(center, radius * 1.16, Color(0.006, 0.022, 0.033, 0.28))
		draw_circle(center, radius, RING_BG)
		draw_arc(center, radius, 0.0, TAU, 64,
			tint.darkened(0.28) if not active else tint, 3.1, true)
		draw_arc(center, radius * 0.67, 0.0, TAU, 48,
			tint * Color(1.0, 1.0, 1.0, 0.23), 1.3, true)
		for direction in [Vector2.LEFT, Vector2.RIGHT, Vector2.UP, Vector2.DOWN]:
			draw_line(center + direction * radius * 0.82,
				center + direction * radius * 0.94,
				Color(tint.r, tint.g, tint.b, 0.75), 2.5, true)
		var thumb: Vector2 = center + axis * radius * 0.66
		draw_circle(thumb, radius * 0.38, Color(0.02, 0.12, 0.16, 0.92))
		draw_arc(thumb, radius * 0.38, 0.0, TAU, 36, tint, 2.8, true)
		draw_circle(thumb, radius * 0.17, Color(tint.r, tint.g, tint.b, 0.56))
		var title: String = "RIGHT  /  LOOK" if right else "LEFT  /  MOVE"
		draw_string(font, center + Vector2(-radius, -radius * 1.23),
			title, HORIZONTAL_ALIGNMENT_CENTER, radius * 2.0,
			16, tint)
