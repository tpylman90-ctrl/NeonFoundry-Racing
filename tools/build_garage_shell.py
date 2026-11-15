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

rng = np.random.default_rng(20261114)


def smooth_noise(w: int, seed: int, scale: int) -> np.ndarray:
    # Periodic multiscale field: no visible seams after texture wrap.
    random = np.random.default_rng(seed)
    base = random.random((scale, scale)).astype(np.float32)
    rep = max(1, w // scale)
    up = np.repeat(np.repeat(base, rep, axis=0), rep, axis=1)
    up = up[:w, :w]
    # Periodic low-pass, flat and cheap to generate in Blender's NumPy.
    for n in (3, 6, 12):
        up = (
            up + np.roll(up, n, axis=0) + np.roll(up, -n, axis=0)
            + np.roll(up, n, axis=1) + np.roll(up, -n, axis=1)
        ) / 5.0
    up -= up.mean()
    up /= max(float(up.std()), 0.0001)
    return up


def save_map(name: str, rgb: np.ndarray, colorspace: str):
    size = rgb.shape[0]
    pixels = np.ones((size, size, 4), dtype=np.float32)
    pixels[:, :, 0:3] = np.clip(rgb, 0.0, 1.0).astype(np.float32)
    image = bpy.data.images.new(name=name, width=size, height=size, alpha=True)
    image.pixels.foreach_set(pixels.reshape(-1))
    image.filepath_raw = str(SOURCE / f"{name}.png")
    image.file_format = "PNG"
    image.save()
    image.colorspace_settings.name = colorspace
    image.pack()
    return image


def make_maps(kind: str, count: int) -> tuple:
    x, y = np.meshgrid(
        np.linspace(0, math.tau, count, endpoint=False, dtype=np.float32),
        np.linspace(0, math.tau, count, endpoint=False, dtype=np.float32),
    )
    low = smooth_noise(count, 173 + len(kind), 16)
    med = smooth_noise(count, 749 + len(kind), 64)
    fine = smooth_noise(count, 951 + len(kind), 128)
    if kind == "floor":
        # Oil-tinted industrial epoxy with subtle, physically plausible patches.
        base = np.array([0.27, 0.315, 0.334], dtype=np.float32)
        rough = 0.64 + 0.065 * low + 0.03 * med
        height = 0.13 * low + 0.055 * med + 0.01 * fine
        stains = np.clip(0.13 * low + 0.035 * med, -0.16, 0.13)
        color = base + stains[..., None] * np.array([0.12, 0.16, 0.16])
        # Hairline abrasion, not black rust blotches.
        scuff = (np.sin(37.0 * x + 3.0 * np.sin(2.0 * y)) > 0.986).astype(np.float32)
        color += scuff[..., None] * 0.010
        rough += scuff * 0.035
    elif kind == "wall":
        # Brushed painted industrial sheet/ceramic-finished concrete panels.
        base = np.array([0.39, 0.435, 0.454], dtype=np.float32)
        striae = 0.045 * np.sin(53.0 * x + np.sin(3.0 * y))
        color = base + (0.012 * low + 0.009 * med + striae * 0.18)[..., None]
        rough = 0.71 + 0.026 * med + 0.012 * fine
        height = 0.035 * low + 0.028 * med + 0.008 * striae
    else:
        # Powder-coated steel acoustic ceiling cassettes.
        base = np.array([0.265, 0.30, 0.323], dtype=np.float32)
        ribs = 0.025 * np.cos(12.0 * x)
        color = base + (0.015 * low + ribs)[..., None]
        rough = 0.73 + 0.034 * low + 0.017 * fine
        height = 0.025 * low + 0.02 * med + 0.016 * np.sin(12.0 * x)

    rough = np.clip(rough, 0.43, 0.91)
    rough_rgb = np.repeat(rough[..., None], 3, axis=2)
    # Shallow OpenGL (+Y) tangent-space normals, no exaggerated raised bumps.
    d_y, d_x = np.gradient(height.astype(np.float32))
    strength = 0.18 if kind == "floor" else 0.15
    nx = -d_x * strength
    ny = -d_y * strength
    nz = np.ones_like(nx)
    normal = np.stack([nx, ny, nz], axis=-1)
    normal /= np.sqrt(np.sum(normal ** 2, axis=-1))[..., None]
    normal = normal * 0.5 + 0.5
    return (
        save_map(f"NF_SHELL_{kind}_albedo", color, "sRGB"),
        save_map(f"NF_SHELL_{kind}_roughness", rough_rgb, "Non-Color"),
        save_map(f"NF_SHELL_{kind}_normalGL", normal, "Non-Color"),
    )


def material(name: str, kind: str, metal: float, texture_meters: float):
    size = 1024 if kind == "floor" else 512
    albedo, roughness, normal = make_maps(kind, size)
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (0.55, 0.6, 0.62, 1)
    mat.use_nodes = True
    n = mat.node_tree.nodes
    n.clear()
    links = mat.node_tree.links
    out = n.new("ShaderNodeOutputMaterial")
    out.location = (650, 0)
    bsdf = n.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (320, 0)
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = 0.65
    bsdf.inputs["IOR"].default_value = 1.45
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    def tex(image, yy):
        node = n.new("ShaderNodeTexImage")
        node.image = image
        node.interpolation = "Linear"
        node.extension = "REPEAT"
        node.location = (-420, yy)
        return node
    t_color = tex(albedo, 250)
    t_rough = tex(roughness, 0)
    t_normal = tex(normal, -240)
    normal_map = n.new("ShaderNodeNormalMap")
    normal_map.space = "TANGENT"
    normal_map.inputs["Strength"].default_value = 0.40
    normal_map.location = (-70, -240)
    links.new(t_color.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(t_rough.outputs["Color"], bsdf.inputs["Roughness"])
    links.new(t_normal.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])
    mat["surface"] = kind
    mat["uv_texel_metres"] = texture_meters
    return mat


MAT_WALL = material("NF/Shell/Wall — satin ceramic", "wall", 0.17, 3.0)
MAT_FLOOR = material("NF/Shell/Floor — epoxy", "floor", 0.07, 3.5)
MAT_CEILING = material("NF/Shell/Ceiling — powder coated", "ceiling", 0.23, 3.0)
MAT_GAP = bpy.data.materials.new("NF/Shell/Panel joints — matte graphite")
MAT_GAP.diffuse_color = (0.095, 0.116, 0.133, 1)
MAT_GAP.use_nodes = True
MAT_GAP.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.095, 0.116, 0.133, 1)
MAT_GAP.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = 0.84


def uv_metric(obj, density: float) -> None:
    # Every texture repeats in metres. No box-face stretching.
    uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
    for poly in obj.data.polygons:
        normal = poly.normal
        axis = max(range(3), key=lambda k: abs(normal[k]))
        for loop_index in poly.loop_indices:
            vertex = obj.data.vertices[obj.data.loops[loop_index].vertex_index].co
            if axis == 0:
                coords = (vertex.y, vertex.z)
            elif axis == 1:
                coords = (vertex.x, vertex.z)
            else:
                coords = (vertex.x, vertex.y)
            uv.data[loop_index].uv = (coords[0] / density, coords[1] / density)


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
                            MAT_WALL, 0.017))
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
bpy.context.scene["static_bake_status"] = "UV1 only - UV2 and LightmapGI next stage"

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
    export_lights=False)
assert OUTPUT.stat().st_size > 20_000, "GLB is unexpectedly small"
assert len(items) == 6, "Expected exactly four walls, one ceiling, one floor"
print("NEON_FOUNDRY_SHELL_STAGE01_OK meshes=6 assets=original_pbr blend=editable glb=%d" %
      OUTPUT.stat().st_size)
