#!/usr/bin/env python3
"""Stage 02A: industrial viewing mezzanine directly above power-cell swap.

User's Nov 2026 master blueprint: the power-cell swap is in the front-left
diagnostics bay. Center the viewing mezzanine on that swap footprint, with its
open viewing edge facing the craft and robotic lift bays across the aisle.

Author original Blender meshes, export separate GLB; keep shell six meshes
unchanged. No machinery, interior partitions or lighting are introduced.
This module is invoked by build_garage_shell.py after its Stage 01 export.
"""
from __future__ import annotations
import math
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "game/assets/garage/shell/observation_deck_stage02.glb"
SOURCE = ROOT / "build/garage_observation_deck_stage02.blend"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
SOURCE.parent.mkdir(parents=True, exist_ok=True)

# These extents are also encoded in GaragePage for walkable stair traversal.
X0, X1 = -25.65, -12.05
Z0, Z1 = 3.25, 11.55
DECK_Y = 5.20  # walkway finished top; bottom-level diagnostics stay usable
STAIR_X0, STAIR_X1 = -25.3, -22.6
STAIR_Z0, STAIR_Z1 = 11.55, 19.05  # upper landing -> ground landing
STEPS = 24

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0


def paint(name: str, rgb: tuple, rough: float, metal: float) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*rgb, 1)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat


STEEL = paint("NF Deck | coated structural graphite", (0.16, .235, .28), .48, .72)
FLOOR = paint("NF Deck | anti-slip dark graphite", (.205, .265, .28), .67, .43)
TRIM = paint("NF Deck | nickel edge accents", (.42, .50, .51), .36, .77)
YELLOW = paint("NF Deck | hazard amber paint", (.84, .435, .11), .45, .08)
materials = {STEEL: [], FLOOR: [], TRIM: [], YELLOW: []}


def box(name: str, loc: tuple, dimensions: tuple, mat, bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel > 0:
        beveler = obj.modifiers.new("Light-catching metal bevel", "BEVEL")
        beveler.width = min(bevel, min(dimensions) * .19)
        beveler.segments = 2
        bpy.ops.object.modifier_apply(modifier=beveler.name)
        weighted = obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
        weighted.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=weighted.name)
    materials[mat].append(obj)
    return obj


def beam_between(name: str, start: tuple, end: tuple,
                 thickness: float, mat, height: float | None = None):
    a = Vector(start)
    b = Vector(end)
    v = b - a
    obj = box(name, tuple((a + b) * .5),
              (thickness, v.length, height or thickness), mat, bevel=.013)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 1, 0)).rotation_difference(v)
    return obj


# Platform: 13.6m across the diagnostics bay, extending 8.3m back from the
# aisle. Its finished surface is 5.20m, leaving about 5m clear below.
cx = (X0+X1)/2
cz = (Z0+Z1)/2
box("Deck/anti-slip walking plate", (cx, DECK_Y-.10, cz),
    (X1-X0, .20, Z1-Z0), FLOOR, .034)
for edge, axis in [(Z0, "z"), (Z1, "z")]:
    box("Deck/outer edge I-beam flange", (cx, DECK_Y-.36, edge),
        (X1-X0+.26, .12, .34), STEEL)
    box("Deck/outer edge I-beam web", (cx, DECK_Y-.52, edge),
        (X1-X0+.26, .32, .105), STEEL)
    box("Deck/inner flange", (cx, DECK_Y-.71, edge),
        (X1-X0+.26, .12, .34), STEEL)
for x in (X0, X1):
    box("Deck/perimeter cross member", (x, DECK_Y-.36, cz),
        (.27, .35, Z1-Z0), STEEL)
# Lower-cost secondary metal cross beams underneath.
for z in (4.5, 6.55, 8.65):
    box("Deck/underside transverse", (cx, DECK_Y-.34, z),
        (X1-X0-.5, .19, .20), STEEL)

# Four columns at the perimeter preserve the power-cell swap footprint.
for x in (X0+.30, X1-.30):
    for z in (Z0+.25, Z1-.25):
        box("Deck/support-column", (x, (DECK_Y-.75)/2, z),
            (.32, DECK_Y-.75, .32), STEEL, .035)
        box("Deck/anchor-shoe", (x, .12, z), (.66, .24, .66), TRIM)
        box("Deck/upper-bracket", (x, DECK_Y-.65, z), (.65, .28, .65), STEEL)

# Edge railings: the NORTH viewing rail is open visually, facing lift craft.
# Stairs enter via a 2.7m opening in the SOUTH rail at the west side.
RAIL_TOP = DECK_Y + 1.17
RAIL_MID = DECK_Y + .62
def rail_run(axis: str, fixed: float, a: float, b: float):
    for y in (RAIL_TOP, RAIL_MID):
        if axis == "x":
            box("Deck/continuous-guard-rail", ((a+b)/2, y, fixed),
                (b-a, .065, .075), TRIM, .012)
        else:
            box("Deck/continuous-guard-rail", (fixed, y, (a+b)/2),
                (.075, .065, b-a), TRIM, .012)
    for i in range(int(math.floor((b-a)/1.55))+2):
        v = a + (b-a) * i/(int(math.floor((b-a)/1.55))+1)
        if axis == "x":
            pos = (v, DECK_Y+.61, fixed)
        else:
            pos = (fixed, DECK_Y+.61, v)
        box("Deck/guard-post", pos, (.075, 1.21, .075), STEEL, .009)

rail_run("x", Z0+.15, X0, X1)
rail_run("x", Z1-.15, STAIR_X1+.16, X1)
rail_run("z", X0+.12, Z0, Z1-.18)
rail_run("z", X1-.12, Z0, Z1)
box("Deck/amber edge indicating inspection outlook",
    (cx, DECK_Y+.008, Z0+.10), (X1-X0-.65, .016, .08), YELLOW, .008)

# One clear 2.7m-wide stair rises from front-left diagnostics.
STAIR_CX=(STAIR_X0+STAIR_X1)/2
run=STAIR_Z1-STAIR_Z0
for i in range(STEPS):
    y=(i+1)/STEPS*DECK_Y
    z=STAIR_Z1-(i+.5)/STEPS*run
    box("Deck/stair-tread", (STAIR_CX, y-.060, z),
        (STAIR_X1-STAIR_X0, .12, run/STEPS-.022), FLOOR, .012)
    if i % 3 == 0:
        box("Deck/stair-nosings", (STAIR_CX, y+.009, z-run/STEPS*.38),
            (STAIR_X1-STAIR_X0-.16, .018, .055), TRIM, .009)
# Sloping side stringers and guard rails, with vertical balusters.
for x in (STAIR_X0+.16, STAIR_X1-.16):
    beam_between("Deck/stair-stringer",
        (x, .10, STAIR_Z1), (x, DECK_Y-.10, STAIR_Z0), .18, STEEL, .23)
    beam_between("Deck/stair-grab-rail",
        (x, 1.10, STAIR_Z1), (x, DECK_Y+1.10, STAIR_Z0), .065, TRIM, .065)
    for i in range(0, STEPS+1, 3):
        fraction=i/STEPS
        yy=fraction*DECK_Y
        zz=STAIR_Z1-fraction*run
        box("Deck/stair-guard-post", (x, yy+.56, zz),
            (.07, 1.12, .07), STEEL, .01)
# Floor marker for stairs access, not a partition.
box("Deck/stair-entry-safety-marking", (STAIR_CX, .015, STAIR_Z1+.15),
    (STAIR_X1-STAIR_X0+.25, .018, .085), YELLOW, .008)


def batch(name, objs):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    joined = bpy.context.object
    joined.name = name
    joined["garage_stage"] = "02A"
    return joined


joined = []
for mat, objects in materials.items():
    if objects:
        label = "Structure" if mat == STEEL else ("WalkSurface" if mat == FLOOR
                else ("TrimRails" if mat == TRIM else "SafetyPaint"))
        joined.append(batch("OBS_DECK_" + label, objects))

# Godot coordinates were intentionally used in Blender authoring. Cancel
# Blender Z-up -> glTF Y-up by pre-rotating the export nodes +90 X.
for obj in joined:
    obj.matrix_world = Matrix.Rotation(math.pi/2, 4, "X") @ obj.matrix_world

bpy.context.scene["garage_stage"] = "02A / observation deck over power-cell swap"
bpy.context.scene["deck_finished_y"] = DECK_Y
bpy.context.scene["deck_footprint"] = f"x[{X0},{X1}], z[{Z0},{Z1}]"
bpy.context.scene["deck_usable_access"] = "24-step stair, lower to upper; faces craft/lift bays"
bpy.context.scene["licensing"] = "original generated project meshes and PBR colors"
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
bpy.ops.object.select_all(action="DESELECT")
for obj in joined:
    obj.select_set(True)
bpy.context.view_layer.objects.active = joined[0]
bpy.ops.export_scene.gltf(filepath=str(OUTPUT), export_format="GLB",
    use_selection=True, export_apply=True, export_cameras=False,
    export_lights=False, export_tangents=True)
assert OUTPUT.stat().st_size > 8_000, OUTPUT
assert len(joined) == 4, len(joined)
print("NEON_FOUNDRY_DECK_STAGE02_OK location=power_cell_swap meshes=4 stair_treads=%d floor_y=%.2f glb=%d" %
      (STEPS, DECK_Y, OUTPUT.stat().st_size))
