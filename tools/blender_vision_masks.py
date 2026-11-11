"""Render measurable transparent silhouettes from the REAL NF-H01 Blender scene.

Usage:
blender -b path/to/NF-H01_Gate02_Clay.blend \
    --python tools/blender_vision_masks.py -- --output-dir build/geometry_vision

This script never saves/changes the input .blend or edits production geometry.
The camera positions match tools/build_hero_01_clay.py, Gate 02 V12.
"""
import argparse
import json
from pathlib import Path

import bpy
from mathutils import Vector


VIEWS = [
    ("01_front", (0, -17, 2.2), (0, 0, 1.2), 7.9),
    ("02_rear", (0, 17, 2.0), (0, 0, 1.2), 7.9),
    ("03_port_side", (-17, 0, 2.1), (0, 0, 1.18), 9.4),
    ("04_starboard_side", (17, 0, 2.1), (0, 0, 1.18), 9.4),
    ("05_top", (0, 0, 18.0), (0, 0, 1.20), 11.8),
    ("06_underside", (0, 0, -17.0), (0, 0, 1.18), 11.8),
    ("07_front_three_quarter", (-12.7, -14.5, 9.0), (0, 0, 1.06), 10.1),
    ("08_rear_three_quarter", (-12.7, 14.5, 8.2), (0, 0, 1.04), 10.1),
]

parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", type=Path, default=Path("build/geometry_vision"))
args = parser.parse_args(
    __import__("sys").argv[__import__("sys").argv.index("--") + 1:]
    if "--" in __import__("sys").argv else []
)
dest = args.output_dir.resolve()
dest.mkdir(parents=True, exist_ok=True)

root = bpy.data.objects.get("NF_H01_ROOT")
if root is None:
    raise RuntimeError("Missing NF_H01_ROOT: load a real NF-H01 Blender craft .blend")
craft = [o for o in bpy.data.objects if o.type == "MESH" and o.parent == root]
if len(craft) < 12:
    raise RuntimeError("Inspection scene does not contain the expected separate craft meshes")
required = {
    "BLK_096_GreenhouseAftArmoredCowl",
    "BLK_082_RearSideWing_PORT", "BLK_083_RearSideWing_STBD",
    "BLK_062_InnerBoosterEnvelope_PORT", "BLK_063_InnerBoosterEnvelope_STBD",
}
missing = sorted(required - {ob.name for ob in craft})
if missing:
    raise RuntimeError("Expected independently modeled rear components are missing: " + str(missing))

depsgraph = bpy.context.evaluated_depsgraph_get()
part_metrics = {}
for ob in craft:
    eval_obj = ob.evaluated_get(depsgraph)
    points = [eval_obj.matrix_world @ Vector(p) for p in eval_obj.bound_box]
    mins = [min(v[i] for v in points) for i in range(3)]
    maxs = [max(v[i] for v in points) for i in range(3)]
    part_metrics[ob.name] = {
        "bounds_m": [[round(v, 5) for v in mins], [round(v, 5) for v in maxs]],
        "dimensions_m": [round(maxs[i] - mins[i], 5) for i in range(3)],
        "mesh_vertices_evaluated": len(eval_obj.to_mesh().vertices),
    }
    eval_obj.to_mesh_clear()

mat = bpy.data.materials.new("VISION | pure white silhouette (temporary)")
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()
em = nodes.new("ShaderNodeEmission")
em.inputs["Color"].default_value = (1, 1, 1, 1)
em.inputs["Strength"].default_value = 1
out = nodes.new("ShaderNodeOutputMaterial")
mat.node_tree.links.new(em.outputs["Emission"], out.inputs["Surface"])

for ob in bpy.data.objects:
    if ob.type == "MESH":
        if ob in craft:
            ob.hide_render = False
            ob.data.materials.clear()
            ob.data.materials.append(mat)
        else:
            ob.hide_render = True

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 1
scene.render.film_transparent = True
scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "8"
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"
# An emission mask is insensitive to lighting and existing clay surface color.
camera_object = scene.camera
if camera_object is None:
    camera_data = bpy.data.cameras.new("VISION | orthographic review camera")
    camera_object = bpy.data.objects.new("VISION | camera", camera_data)
    scene.collection.objects.link(camera_object)
    scene.camera = camera_object
camera_object.data.type = "ORTHO"
camera_object.data.clip_end = 350

for name, location, target, scale in VIEWS:
    camera_object.location = location
    camera_object.rotation_euler = (Vector(target) - camera_object.location).to_track_quat("-Z", "Y").to_euler()
    camera_object.data.ortho_scale = scale
    scene.render.filepath = str(dest / (name + ".png"))
    bpy.ops.render.render(write_still=True)
    if not (dest / (name + ".png")).is_file():
        raise RuntimeError("Mask render missing: " + name)

payload = {
    "asset_id": "NF-H01",
    "gate": 2,
    "source": bpy.data.filepath,
    "coordinate_system": "Blender meters, X width, Y nose/tail, Z up",
    "scale": "Review cameras match Gate 02 V12 source",
    "masks": [x[0] + ".png" for x in VIEWS],
    "part_metrics": part_metrics,
    "status": "measurement only; no edits to source or approval",
}
(dest / "mesh_metrics.json").write_text(json.dumps(payload, indent=2) + "\n")
print("NFR_VISION_MASKS_OK masks=8 parts=" + str(len(part_metrics)), flush=True)
