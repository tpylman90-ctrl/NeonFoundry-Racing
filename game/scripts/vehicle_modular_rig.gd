extends Node3D
## NFR interchangeable hardpoint rig for native Godot (Vulkan Mobile).
## The base car never changes when a module is swapped. All geometry is GLB.
## This is a stand-alone experimental rig, not yet linked to production garage.
signal part_installed(slot_id: String, part_id: String)

const DEFAULT_MANIFEST := "res://assets/vehicle_modular/module_manifest.json"

var _manifest: Dictionary = {}
var _mounts: Dictionary = {}
var _current: Dictionary = {}
var _base_mesh: Node3D

func initialize(manifest_path: String = DEFAULT_MANIFEST) -> bool:
	if not FileAccess.file_exists(manifest_path):
		push_warning("NFR_MODULAR_MANIFEST_NOT_STAGED: " + manifest_path)
		return false
	var file := FileAccess.open(manifest_path, FileAccess.READ)
	if file == null:
		return false
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	if not parsed is Dictionary:
		push_error("NFR_MODULAR_INVALID_CATALOG")
		return false
	var info: Dictionary = parsed
	if int(info.get("schema_version", -1)) != 1:
		return false
	if not info.has("slots") or not info.has("sockets"):
		return false
	if _base_mesh != null:
		push_warning("NFR_MODULAR_ALREADY_INITIALIZED")
		return false
	var packed: Resource = load(str(info.get("base_scene", "")))
	if not packed is PackedScene:
		push_error("NFR_MODULAR_BASE_GLB_UNAVAILABLE")
		return false
	var body: Node = (packed as PackedScene).instantiate()
	if not body is Node3D:
		body.queue_free()
		return false
	_manifest = info
	_base_mesh = body as Node3D
	_base_mesh.name = "PermanentDonorBody"
	add_child(_base_mesh)
	var sockets: Dictionary = info["sockets"]
	for slot_id in sockets:
		var socket_info: Dictionary = sockets[slot_id]
		var p: Array = socket_info.get("position_m", [])
		if p.size() != 3:
			push_error("NFR_MODULAR_BAD_SOCKET: " + str(slot_id))
			return false
		var mount := Node3D.new()
		mount.name = "SOCKET_" + str(slot_id)
		mount.position = Vector3(float(p[0]), float(p[1]), float(p[2]))
		add_child(mount)
		_mounts[slot_id] = mount
	return restore_loadout(info.get("default_loadout", {}))

func _entry_for(slot_id: String, part_id: String) -> Dictionary:
	if not _manifest.has("slots"):
		return {}
	var catalog: Dictionary = _manifest["slots"]
	if not catalog.has(slot_id):
		return {}
	var items: Array = catalog[slot_id]
	for candidate in items:
		if candidate is Dictionary and str(candidate.get("id", "")) == part_id:
			return candidate
	return {}

func install(slot_id: String, part_id: String) -> bool:
	if not _mounts.has(slot_id):
		return false
	var entry: Dictionary = _entry_for(slot_id, part_id)
	if entry.is_empty():
		return false
	if _current.get(slot_id, "") == part_id:
		return true
	var resource_path: String = str(entry.get("scene", ""))
	var resource: Resource = load(resource_path)
	if not resource is PackedScene:
		push_warning("NFR_MODULAR_PART_MISSING: " + resource_path)
		return false
	var new_model: Node = (resource as PackedScene).instantiate()
	if not new_model is Node3D:
		new_model.queue_free()
		return false
	var mount: Node3D = _mounts[slot_id]
	new_model.name = "INSTALLED_" + part_id
	mount.add_child(new_model)
	# Swap after successful instantiation, so missing assets never delete a part.
	for old_node in mount.get_children():
		if old_node != new_model:
			mount.remove_child(old_node)
			old_node.queue_free()
	_current[slot_id] = part_id
	part_installed.emit(slot_id, part_id)
	return true

func restore_loadout(loadout: Dictionary) -> bool:
	if loadout.size() != _mounts.size():
		return false
	for slot_id in _mounts:
		if not loadout.has(slot_id):
			return false
		if _entry_for(str(slot_id), str(loadout[slot_id])).is_empty():
			return false
	# Validate resources ahead of mutation to avoid partial build on a bad preset.
	for slot_id in _mounts:
		var entry: Dictionary = _entry_for(str(slot_id), str(loadout[slot_id]))
		if not ResourceLoader.exists(str(entry["scene"])):
			return false
	for slot_id in _mounts:
		if not install(str(slot_id), str(loadout[slot_id])):
			return false
	return true

func set_style_preset(preset: String) -> bool:
	if not _manifest.has("preview_loadouts"):
		return false
	var presets: Dictionary = _manifest["preview_loadouts"]
	if not presets.has(preset):
		return false
	return restore_loadout(presets[preset])

func get_current_loadout() -> Dictionary:
	return _current.duplicate(true)

func get_available_parts(slot_id: String) -> Array:
	if not _manifest.has("slots"):
		return []
	var entries: Dictionary = _manifest["slots"]
	return entries.get(slot_id, []).duplicate(true)

func get_engine_stats() -> Dictionary:
	var id: String = str(_current.get("rear_engine", ""))
	var entry: Dictionary = _entry_for("rear_engine", id)
	return entry.get("stats", {}).duplicate(true)

func get_active_part_node(slot_id: String) -> Node3D:
	if not _mounts.has(slot_id):
		return null
	var mount: Node3D = _mounts[slot_id]
	if mount.get_child_count() != 1:
		return null
	return mount.get_child(0) as Node3D
