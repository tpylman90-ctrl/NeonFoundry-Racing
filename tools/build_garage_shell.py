#!/usr/bin/env python3
"""Blender 5.2 LTS: Foundry Lot STAGE 01 - six reusable architecture surfaces.

The floor, ceiling, front/back and two side walls are exported as one GLB
with authentic UV-mapped, self-authored PBR maps. No industrial props, girders,
turntable, craft or interior partitions are exported in this stage.

All generated maps are original and require no third-party asset license.
Keep the .blend and source textures under build/shell_source for later stages.
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "game/assets/garage/shell/shell_stage01.glb"
SOURCE = ROOT / "build/shell_source"
SOURCE.mkdir(parents=True, exist_ok=True)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

# Match the established Godot Foundry Lot. Units are metres (not centimetres).
LEFT, RIGHT = -19.9, 19.9
BACK, FRONT = -17.9, 14.4
FLOOR_Y, CEILING_Y = -0.08, 14.70

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0

# Stage-01 materials have their own offline high-resolution PBR bake.
# This keeps mesh layout independent of visual detailing.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from garage_shell_pbr import shell_material

MAT_FLOOR = shell_material("NF/Shell/Floor • oil-streaked epoxy", "floor", 1.0, SOURCE)
MAT_WALL_LONG = shell_material("NF/Shell/Wall • matte composite long", "wall_long", 1.0, SOURCE)
MAT_WALL_SIDE = shell_material("NF/Shell/Wall • matte composite side", "wall_side", 1.0, SOURCE)
MAT_CEILING = shell_material("NF/Shell/Ceiling • acoustic steel", "ceiling", 1.0, SOURCE)

MAT_GAP = bpy.data.materials.new("NF/Shell/Panel joints — matte graphite")
MAT_GAP.diffuse_color = (0.095, 0.116, 0.133, 1)
MAT_GAP.use_nodes = True
MAT_GAP.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.095, 0.116, 0.133, 1)
MAT_GAP.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = 0.84


def uv_metric(obj, density: float) -> None:
    # World-space atlas UVs ensure each cladding panel samples a DIFFERENT
    # part of the original packed maps (no repeated wallpaper/marble).
    # Coordinates are evaluated before our Blender->Godot export transform.
    surface = str(obj.data.materials[0].get("surface", ""))
    uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
    loc = obj.location
    for poly in obj.data.polygons:
        normal = poly.normal
        axis = max(range(3), key=lambda k: abs(normal[k]))
        for loop_index in poly.loop_indices:
            vertex = obj.data.vertices[obj.data.loops[loop_index].vertex_index].co
            wx, wy, wz = vertex.x + loc.x, vertex.y + loc.y, vertex.z + loc.z
            if surface in ("floor", "ceiling"):
                coords = ((wx - LEFT) / (RIGHT - LEFT),
                          (wz - BACK) / (FRONT - BACK))
            elif surface.startswith("wall"):
                if obj.name.startswith(("LEFT/", "RIGHT/")):
                    along = (wz - BACK) / (FRONT - BACK)
                else:
                    along = (wx - LEFT) / (RIGHT - LEFT)
                coords = (along, (wy - FLOOR_Y) / (CEILING_Y - FLOOR_Y))
            elif axis == 0:
                coords = (vertex.y / density, vertex.z / density)
            elif axis == 1:
                coords = (vertex.x / density, vertex.z / density)
            else:
                coords = (vertex.x / density, vertex.y / density)
            uv.data[loop_index].uv = coords


def box(name: str, center: tuple, size: tuple, mat, bevel: float = 0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    uv_metric(obj, float(mat.get("uv_texel_metres", 3.0)))
    if bevel:
        modifier = obj.modifiers.new("Physical edge chamfer", "BEVEL")
        modifier.width = min(bevel, min(size) * 0.18)
        modifier.segments = 2
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        smooth = obj.modifiers.new("Area-weighted edge normals", "WEIGHTED_NORMAL")
        smooth.keep_sharp = True
        smooth.weight = 40
        bpy.ops.object.modifier_apply(modifier=smooth.name)
    return obj


def merge(name: str, objects: list):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    merged = bpy.context.object
    merged.name = name
    merged["garage_phase"] = "01"
    return merged


items: list[bpy.types.Object] = []

# 1. Main floor panels; all geometry is real, not a texture over the old floor.
floor_bits = [box("Floor/base slab", (0, -0.235, -1.75),
                  (39.8, 0.27, 32.3), MAT_GAP, 0.035)]
for i in range(10):
    for j in range(8):
        x = LEFT + (i + 0.5) * ((RIGHT - LEFT) / 10)
        z = BACK + (j + 0.5) * ((FRONT - BACK) / 8)
        floor_bits.append(box(f"Floor/epoxy bay {i}_{j}", (x, -0.076, z),
            ((RIGHT - LEFT) / 10 - 0.045, 0.052,
             (FRONT - BACK) / 8 - 0.045), MAT_FLOOR, 0.018))
items.append(merge("SHELL_01_FLOOR", floor_bits))

# 2. Fully enclosed walls, partitioned into physical panels with narrow
# honest construction joints. This stage contains no pillars/girders.
HEIGHT = CEILING_Y - FLOOR_Y
for side, along_x, sign in (
    ("BACK", True, -1), ("FRONT", True, +1),
    ("LEFT", False, -1), ("RIGHT", False, +1),
):
    if along_x:
        center = (0, HEIGHT / 2, BACK if sign < 0 else FRONT)
        size = (RIGHT - LEFT, HEIGHT, 0.31)
        n_bays = 10
    else:
        center = (LEFT if sign < 0 else RIGHT, HEIGHT / 2, -1.75)
        size = (0.31, HEIGHT, FRONT - BACK)
        n_bays = 8
    bits = [box(f"{side}/backing", center, size, MAT_GAP, 0.045)]
    width = (RIGHT - LEFT) / n_bays if along_x else (FRONT - BACK) / n_bays
    for i in range(n_bays):
        for tier in range(3):
            coord = ((LEFT if along_x else BACK) + (i + 0.5) * width)
            y = FLOOR_Y + (tier + 0.5) * (HEIGHT / 3)
            if along_x:
                z = center[2] - sign * 0.17
                loc = (coord, y, z)
                dims = (width - 0.057, HEIGHT / 3 - 0.073, 0.045)
            else:
                x = center[0] - sign * 0.17
                loc = (x, y, coord)
                dims = (0.045, HEIGHT / 3 - 0.073, width - 0.057)
            bits.append(box(f"{side}/satin cladding {tier}_{i}", loc, dims,
                            (MAT_WALL_LONG if along_x else MAT_WALL_SIDE), 0.017))
    items.append(merge(f"SHELL_01_{side}_WALL", bits))

# 3. Ceiling, separately tiled in a dark non-reflective architectural finish.
roof_bits = [box("Ceiling/backing", (0, CEILING_Y + 0.15, -1.75),
                 (39.8, 0.30, 32.3), MAT_GAP, 0.030)]
for i in range(10):
    for j in range(8):
        x = LEFT + (i + 0.5) * ((RIGHT - LEFT) / 10)
        z = BACK + (j + 0.5) * ((FRONT - BACK) / 8)
        roof_bits.append(box(f"Ceiling/acoustic cassette {i}_{j}",
            (x, CEILING_Y - 0.077, z),
            ((RIGHT - LEFT) / 10 - 0.070, 0.060,
             (FRONT - BACK) / 8 - 0.070), MAT_CEILING, 0.022))
items.append(merge("SHELL_01_CEILING", roof_bits))

bpy.context.scene["nf_stage"] = 1
bpy.context.scene["shell_wall_count"] = 4
bpy.context.scene["shell_dimensions"] = "39.8m x 32.3m x 14.78m"
bpy.context.scene["static_bake_status"] = "PBR/ORM microdetails texture-baked on UV1; UV2 GI next milestone"
bpy.context.scene["pbr_packing"] = "Occlusion R, Roughness G, Metallic B"
bpy.context.scene["normal_source"] = "Procedural high-resolution relief prebake, OpenGL tangent space"

# The scene above uses Godot-style X/Y/Z coordinates intentionally.
# Blender exports from Z-up to glTF Y-up, so pre-rotate +90 degrees around
# Blender X. The combined transform preserves Godot Y as physical height.
from mathutils import Matrix
for node in items:
    node.matrix_world = Matrix.Rotation(math.pi / 2.0, 4, "X") @ node.matrix_world

# Preserve editable Blender source, including source image datablocks.
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "build/garage_shell_stage01.blend"))
bpy.ops.object.select_all(action="DESELECT")
for obj in items:
    obj.select_set(True)
bpy.context.view_layer.objects.active = items[0]
bpy.ops.export_scene.gltf(filepath=str(OUTPUT), export_format="GLB",
    use_selection=True, export_apply=True, export_cameras=False,
    export_lights=False, export_tangents=True)
assert OUTPUT.stat().st_size > 20_000, "GLB is unexpectedly small"
assert len(items) == 6, "Expected exactly four walls, one ceiling, one floor"
print("NEON_FOUNDRY_SHELL_STAGE01_OK meshes=6 assets=original_ORM_bakedNormals blend=editable glb=%d" %
      OUTPUT.stat().st_size)
