#!/usr/bin/env python3
"""Stage 02C: build the six approved interior garage zones.

Partitions follow docs/garage/NeonFoundry_Garage_Layout_v2.json. Open portals
are retained at every vehicle route, the 7 m transverse aisle, the 9 m ingress
lane, and the front showroom approach. No equipment or props are authored.
"""
from __future__ import annotations

import math
from pathlib import Path
import bpy
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "game/assets/garage/shell/interior_partitions_stage02c.glb"
SOURCE = ROOT / "build/garage_interior_partitions_stage02c.blend"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
SOURCE.parent.mkdir(parents=True, exist_ok=True)

LEFT, RIGHT = -27.0, 27.0
BACK, FRONT = -23.75, 20.25
HEIGHT = 7.2
THICKNESS = 0.24
DOOR_HEIGHT = 5.8

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0


def paint(name: str, rgb: tuple[float, float, float], rough: float, metal: float):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*rgb, 1.0)
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1.0)
    shader.inputs["Roughness"].default_value = rough
    shader.inputs["Metallic"].default_value = metal
    return mat


CORE = paint("NF/Interior/structural graphite core", (0.075, 0.105, 0.13), .68, .48)
PANEL = paint("NF/Interior/satin blue-grey cladding", (0.22, 0.31, 0.36), .56, .42)
FRAME = paint("NF/Interior/brushed steel portal frames", (0.38, 0.51, 0.56), .34, .72)
SAFETY = paint("NF/Interior/amber lintel markers", (0.92, 0.40, 0.10), .42, .16)
MATERIALS = {CORE: [], PANEL: [], FRAME: [], SAFETY: []}


def box(name: str, center: tuple[float, float, float], size: tuple[float, float, float],
        material, bevel: float = .018):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new("Soft structural edge", "BEVEL")
        mod.width = min(bevel, min(size) * .18)
        mod.segments = 2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        normal = obj.modifiers.new("Weighted panel normals", "WEIGHTED_NORMAL")
        normal.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=normal.name)
    MATERIALS[material].append(obj)
    return obj


def wall_run(axis: str, fixed: float, a: float, b: float, name: str):
    """A panelized wall segment with cladding on both sides."""
    if b - a < .15:
        return
    panel_length = 3.25
    count = max(1, math.ceil((b - a) / panel_length))
    step = (b - a) / count
    for i in range(count):
        lo, hi = a + i * step, a + (i + 1) * step
        length = hi - lo - .045
        mid = (lo + hi) * .5
        if axis == "z":
            box(f"{name}/core_{i}", (fixed, HEIGHT * .5, mid),
                (THICKNESS, HEIGHT, length), CORE, .025)
            for sign in (-1, 1):
                box(f"{name}/skin_{i}_{sign}",
                    (fixed + sign * (THICKNESS * .5 + .024), HEIGHT * .5, mid),
                    (.045, HEIGHT - .10, length), PANEL, .022)
            for sign in (-1, 1):
                box(f"{name}/top_cap_{i}_{sign}",
                    (fixed + sign * (THICKNESS * .5 + .038), HEIGHT - .055, mid),
                    (.08, .11, length + .04), FRAME, .012)
        else:
            box(f"{name}/core_{i}", (mid, HEIGHT * .5, fixed),
                (length, HEIGHT, THICKNESS), CORE, .025)
            for sign in (-1, 1):
                box(f"{name}/skin_{i}_{sign}",
                    (mid, HEIGHT * .5, fixed + sign * (THICKNESS * .5 + .024)),
                    (length, HEIGHT - .10, .045), PANEL, .022)
            for sign in (-1, 1):
                box(f"{name}/top_cap_{i}_{sign}",
                    (mid, HEIGHT - .055, fixed + sign * (THICKNESS * .5 + .038)),
                    (length + .04, .11, .08), FRAME, .012)


def lintel(axis: str, fixed: float, lo: float, hi: float, clear_height: float, name: str):
    """Wall/header above an open portal, plus visible frame and safety band."""
    if clear_height >= HEIGHT:
        return
    height = HEIGHT - clear_height
    if axis == "z":
        box(f"{name}/header_core", (fixed, clear_height + height * .5, (lo + hi) * .5),
            (THICKNESS, height, hi - lo), CORE, .02)
        for sign in (-1, 1):
            face = fixed + sign * (THICKNESS * .5 + .024)
            box(f"{name}/header_skin_{sign}", (face, clear_height + height * .5, (lo + hi) * .5),
                (.045, max(.1, height - .04), hi - lo), PANEL, .018)
            box(f"{name}/portal_lintel_{sign}", (face + sign * .026, clear_height + .04, (lo + hi) * .5),
                (.06, .09, hi - lo + .04), FRAME, .012)
            box(f"{name}/amber_lintel_{sign}", (face + sign * .064, clear_height + .16, (lo + hi) * .5),
                (.025, .045, hi - lo - .10), SAFETY, .008)
    else:
        box(f"{name}/header_core", ((lo + hi) * .5, clear_height + height * .5, fixed),
            (hi - lo, height, THICKNESS), CORE, .02)
        for sign in (-1, 1):
            face = fixed + sign * (THICKNESS * .5 + .024)
            box(f"{name}/header_skin_{sign}", ((lo + hi) * .5, clear_height + height * .5, face),
                (hi - lo, max(.1, height - .04), .045), PANEL, .018)
            box(f"{name}/portal_lintel_{sign}", ((lo + hi) * .5, clear_height + .04, face + sign * .026),
                (hi - lo + .04, .09, .06), FRAME, .012)
            box(f"{name}/amber_lintel_{sign}", ((lo + hi) * .5, clear_height + .16, face + sign * .064),
                (hi - lo - .10, .045, .025), SAFETY, .008)


def portal_jambs(axis: str, fixed: float, lo: float, hi: float, clear_height: float, name: str):
    for point, side in ((lo, "a"), (hi, "b")):
        if axis == "z":
            box(f"{name}/jamb_{side}", (fixed, clear_height * .5, point),
                (THICKNESS + .10, clear_height, .18), FRAME, .018)
            box(f"{name}/jamb_safety_{side}",
                (fixed + THICKNESS * .5 + .06, clear_height * .5, point),
                (.03, clear_height - .10, .045), SAFETY, .009)
        else:
            box(f"{name}/jamb_{side}", (point, clear_height * .5, fixed),
                (.18, clear_height, THICKNESS + .10), FRAME, .018)
            box(f"{name}/jamb_safety_{side}",
                (point, clear_height * .5, fixed + THICKNESS * .5 + .06),
                (.045, clear_height - .10, .03), SAFETY, .009)


def partition(axis: str, fixed: float, start: float, end: float,
              openings: list[tuple[float, float, float]], name: str):
    """Build a wall run while preserving declared centered door portals.

    Each opening tuple is (center, width, clear_height).
    """
    cuts = sorted((center - width * .5, center + width * .5, clear)
                  for center, width, clear in openings)
    cursor = start
    for lo, hi, clear in cuts:
        lo, hi = max(start, lo), min(end, hi)
        if lo > cursor:
            wall_run(axis, fixed, cursor, lo, name)
        lintel(axis, fixed, lo, hi, clear, name)
        portal_jambs(axis, fixed, lo, hi, clear, name)
        cursor = max(cursor, hi)
    if cursor < end:
        wall_run(axis, fixed, cursor, end, name)


# Rear edge of the 7m cross-aisle: three aligned lift portals, plus assembly
# and HQ portals. All remain unobstructed through the full 5.8m vehicle height.
partition("x", -5.75, LEFT, RIGHT,
          [(-23, 5.8, DOOR_HEIGHT), (-15, 5.8, DOOR_HEIGHT),
           (-7, 5.8, DOOR_HEIGHT), (6, 8.0, 6.2), (21, 6.0, DOOR_HEIGHT)],
          "AISLE/rear_service_portals")

# Front edge of the aisle: diagnostics, 9m ingress lane, and visitor showroom.
partition("x", 1.25, LEFT, RIGHT,
          [(-19, 6.0, DOOR_HEIGHT), (-2.5, 9.0, 6.2),
           (15.5, 7.0, DOOR_HEIGHT)],
          "AISLE/front_zone_portals")

# Rear shops are separated with walk-through service portals.
partition("z", -3.0, BACK, -5.75, [(-10.0, 4.6, 3.2)],
          "REAR/lift_to_assembly")
partition("z", 15.0, BACK, -5.75, [(-10.0, 3.2, 3.0)],
          "REAR/assembly_to_hq")

# Front room dividers have pedestrian portals; vehicle flow stays in the
# marked central 9m lane and enters each bay through the cross-aisle portals.
partition("z", -11.0, 1.25, FRONT, [(12.0, 2.2, 2.65)],
          "FRONT/diagnostics_to_depot")
partition("z", 6.0, 1.25, FRONT, [(12.0, 2.2, 2.65)],
          "FRONT/depot_to_showroom")


def join_material(label: str, objects: list):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    merged = bpy.context.object
    merged.name = "INT_WALL_" + label
    merged["garage_stage"] = "02C"
    return merged


joined = []
for mat, objects in MATERIALS.items():
    if objects:
        label = "Structure" if mat == CORE else (
            "Cladding" if mat == PANEL else ("Portals" if mat == FRAME else "Safety"))
        joined.append(join_material(label, objects))

for obj in joined:
    obj.matrix_world = Matrix.Rotation(math.pi / 2, 4, "X") @ obj.matrix_world

bpy.context.scene["garage_stage"] = "02C / zone partitions with vehicle portals"
bpy.context.scene["zones"] = "01 lifts; 02 assembly; 03 AI/HQ; 04 diagnostics; 05 depot; 06 showroom"
bpy.context.scene["vehicle_access"] = "three lift portals; assembly and HQ portals; 9m front ingress; showroom portal"
bpy.context.scene["partition_height"] = HEIGHT
bpy.context.scene["props"] = "none"
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
bpy.ops.object.select_all(action="DESELECT")
for obj in joined:
    obj.select_set(True)
bpy.context.view_layer.objects.active = joined[0]
bpy.ops.export_scene.gltf(filepath=str(OUTPUT), export_format="GLB",
    use_selection=True, export_apply=True, export_cameras=False,
    export_lights=False, export_tangents=True)
assert OUTPUT.stat().st_size > 20_000, OUTPUT
assert len(joined) == 4, len(joined)
print("NEON_FOUNDRY_PARTITIONS_STAGE02C_OK meshes=4 height=%.1f openings=12 glb=%d" %
      (HEIGHT, OUTPUT.stat().st_size))
