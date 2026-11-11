extends Control
## 2D reactive HUD on top of a Blender-rendered background.
## Deliberately lightweight: static image is costly to author, cheap to draw.
var motion_enabled: bool = true
var _time: float = 0.0
var _draw_accumulator: float = 0.0

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(queue_redraw)

func _process(delta: float) -> void:
	if not motion_enabled:
		return
	_time += delta
	_draw_accumulator += delta
	if _draw_accumulator > 0.065:
		_draw_accumulator = 0.0
		queue_redraw()

func _draw() -> void:
	var w: float = size.x
	var h: float = size.y
	if w < 10.0 or h < 10.0:
		return
	# Technical glass, increasing visibility over a detailed 3D city.
	for stripe in range(60):
		var t: float = float(stripe) / 60.0
		var x: float = t * w * 0.63
		var alpha: float = 0.93 * pow(1.0-t, 1.55)
		draw_rect(Rect2(x, 0, w * 0.63 / 60.0+1.5, h), Color(.012,.020,.040,alpha))
	draw_rect(Rect2(0,0,w,3.0),Color(.14,.70,.81,.62))
	draw_rect(Rect2(0,h-3.0,w,3.0),Color(.08,.33,.48,.57))
	# Fine engineering grid, deliberately quiet behind the navigation.
	var grid_step: float = maxf(45.0,w/27.0)
	for k in range(int(w*.50/grid_step)+1):
		var x: float=27.0+float(k)*grid_step
		draw_line(Vector2(x,0),Vector2(x,h),Color(.26,.56,.68,.055),1.0)
	for k in range(int(h/47.0)+1):
		var y: float = float(k)*47.0
		draw_line(Vector2(0,y),Vector2(w*.51,y),Color(.22,.45,.59,.045),1.0)
	# A transparent angular panel, not a large opaque box.
	draw_polyline(PackedVector2Array([
		Vector2(w*.048,h*.14),Vector2(w*.439,h*.14),
		Vector2(w*.452,h*.17),Vector2(w*.452,h*.915),
		Vector2(w*.068,h*.915)
	]),Color(.14,.64,.75,.28),1.35,true)
	draw_line(Vector2(w*.068,h*.155),Vector2(w*.197,h*.155),Color(.91,.31,.21,.9),2.0)
	draw_line(Vector2(w*.09,h*.904),Vector2(w*.224,h*.904),Color(.12,.81,.94,.58),1.5)
	# Right corner race telemetry framing (not over the vehicle itself).
	var top_y: float = h*.05
	draw_polyline(PackedVector2Array([
		Vector2(w*.80,top_y),Vector2(w*.955,top_y),
		Vector2(w*.973,h*.077),Vector2(w*.973,h*.14)
	]),Color(.30,.86,1.0,.45),1.4,true)
	draw_polyline(PackedVector2Array([
		Vector2(w*.945,h*.91),Vector2(w*.979,h*.91),
		Vector2(w*.979,h*.975),Vector2(w*.82,h*.975)
	]),Color(.30,.80,.95,.38),1.0,true)
	for i in range(3):
		var x: float = w*(.48+.019*float(i))
		draw_line(Vector2(x,h*.048),Vector2(x+13.0,h*.048),Color(1,.41,.23,.34+float(i)*.14),2.0)
	# Slow telemetry animation. No expensive full-screen shader or blur.
	for i in range(6):
		var p: float=fposmod(float(i)*.17+_time*.045,1.0)
		var xx: float=w*(.58+.35*p)
		draw_line(Vector2(xx,h*.142),Vector2(xx+6.0,h*.142),Color(.26,.89,.96,.15+.30*(1.0-p)),1.25)
	var pulse: float=.55+.45*sin(_time*2.0)
	draw_circle(Vector2(w*.963,h*.925),2.0,Color(1,.37,.24,.40+.48*pulse))
	draw_arc(Vector2(w*.963,h*.925),9.0,0,TAU,32,Color(.27,.80,.90,.22+.18*pulse),1.0)
