extends Control
## Temporary boot scene: renderer and APK readiness only, not gameplay.

@onready var renderer_label: Label = %RendererLabel
@onready var status_label: Label = %StatusLabel

func _ready() -> void:
	var method: String = RenderingServer.get_current_rendering_method()
	var driver: String = RenderingServer.get_current_rendering_driver_name()
	renderer_label.text = "GRAPHICS  /  %s  /  %s" % [method.to_upper(), driver.to_upper()]
	if method == "mobile" and driver == "vulkan":
		status_label.text = "FOUNDATION ONLINE  /  MOBILE + VULKAN"
	else:
		status_label.text = "CHECK GRAPHICS BACKEND  /  %s + %s" % [method, driver]
		push_warning("Expected Mobile/Vulkan; runtime selected %s/%s" % [method, driver])
