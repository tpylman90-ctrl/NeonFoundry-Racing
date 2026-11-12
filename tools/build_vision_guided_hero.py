"""NF-H01 Gate 02 V13: reference-guided, measurable clay geometry experiment.

Load the actual V12 editable Blender craft; do NOT replace the accepted baseline.
Use geometric targets observed from the owner's eight-view image sheet, explicitly
not AI-inferred absolute dimensions. This re-shapes physical mesh vertices and
re-exports editable Blender source, real GLB and eight new Blender camera renders.

This is ONLY Gate 02 silhouette massing: no production materials, fake openings,
auto approval or Godot import. DINOv2 / Depth Anything V2 have been independently
verified on V12 Blender renders; their relative features alone are not CAD.
"""
import bpy
import bmesh
import json
import math
import os
import struct
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "build/hero_01_gate02" / "NF-H01_Gate02_Clay.blend"
OUT = ROOT / "build" / "hero_01_vision_v13"
assert SRC.is_file(), "First download the authentic V12 Gate02 Blender source artifact"
OUT.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=str(SRC))
scene = bpy.context.scene
core = bpy.data.objects["NF_H01_ROOT"]
original = [o for o in bpy.data.objects if o.type == "MESH" and o.parent == core]
assert len(original) >= 26
names = {o.name for o in original}
required = {
  "BLK_096_GreenhouseAftArmoredCowl",
  "BLK_082_RearSideWing_PORT", "BLK_083_RearSideWing_STBD",
  "BLK_080_FinRear_PORT", "BLK_081_FinRear_STBD",
  "BLK_060_Nozzle_PORT", "BLK_061_Nozzle_STBD",
  "BLK_062_InnerBoosterEnvelope_PORT", "BLK_063_InnerBoosterEnvelope_STBD",
}
assert required.issubset(names), required - names


def remodel(name, coords):
    ob = bpy.data.objects[name]
    if len(ob.data.vertices) != len(coords):
        raise ValueError("Expected actual V12 topology for " + name +
                         " (got %s vs %s vertices)" % (len(ob.data.vertices), len(coords)))
    for v, pos in zip(ob.data.vertices, coords):
        v.co = pos
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


# A narrower, lower central armor bridge with a long almost-level rear
# roof, which clears the glass and terminates above the two inboard boosters.
# The broad side haunches and shoulder rails remain *independent* and unmodified.
# V12 used rear halfwidth 1.29-1.39, which swallowed much of the rear shoulder.
# V13 retains broad side blends via physical outer shoulder armor, but reduces
# the central cowl's rear width, following the sheet's narrow central roof.
cowl_stations = [
    (.41,.53,2.28,2.07,.32,2.19),
    (.68,.68,2.29,1.87,.43,2.18),
    (.96,.74,2.28,1.73,.49,2.16),
    (1.26,.82,2.27,1.62,.55,2.13),
    (1.60,.89,2.25,1.54,.60,2.11),
    (2.06,.96,2.23,1.53,.65,2.09),
    (2.58,1.02,2.21,1.53,.70,2.07),
    (3.04,1.04,2.19,1.54,.71,2.05),
    (3.43,1.04,2.17,1.55,.71,2.03),
    (3.72,.98,2.16,1.58,.68,2.02),
]
def cowl_ring(y,half,top,bottom,inner,inner_top):
    assert inner < half and bottom < inner_top < top
    vertices = [
        (-half*.68,top), (half*.68,top),
        (half*.93,top-.045), (half,top-.16),
        (half,bottom+.095), (half*.83,bottom),
        (inner,bottom), (inner,inner_top-.055),
        (inner*.70,inner_top), (-inner*.70,inner_top),
        (-inner,inner_top-.055), (-inner,bottom),
        (-half*.83,bottom), (-half,bottom+.095),
        (-half,top-.16), (-half*.93,top-.045),
    ]
    return [(x,y,z) for x,z in vertices]
remodel("BLK_096_GreenhouseAftArmoredCowl",
        [v for station in cowl_stations for v in cowl_ring(*station)])

# The sheet's side elevations place rear fin tips much closer to canopy
# roof height than the V12 extra-high fins. Preserve both physical fins,
# lean-back, closed solid geometry and front-to-aft sweep.
for sign, side, index in [(-1.0,"PORT",80),(1.0,"STBD",81)]:
    root_x = sign * 1.11
    fin_profile = [
        (1.94,1.55), (2.22,1.76), (2.87,2.20),
        (3.26,2.43), (3.55,2.40), (3.37,1.56),
    ]
    coords = [
        (root_x+sign*(z-1.50)*.40+offset,y,z)
        for offset in (-.078,.078) for y,z in fin_profile
    ]
    remodel("BLK_%03d_FinRear_%s" % (index,side),coords)

# Reduce excessive rear wing span without deleting either broad external
# wing flare; tips remain far outside the shoulder body and clearly visible.
for sign, side, index in [(-1.0,"PORT",82),(1.0,"STBD",83)]:
    wing_outline = [
        (sign*1.50,1.98,1.47),
        (sign*2.19,2.06,1.44),
        (sign*2.69,2.60,1.35),
        (sign*2.70,2.83,1.33),
        (sign*2.47,2.95,1.35),
        (sign*1.53,3.22,1.46),
    ]
    coords = [(x,y,z+layer) for layer in (-.075,.075)
              for x,y,z in wing_outline]
    remodel("BLK_%03d_RearSideWing_%s" % (index,side),coords)

# Physical 16-sided main nozzle mass, real geometry in the existing named
# mesh object. Slightly increase exit diameter without painting fake bores.
for sign, side, index in [(-1.0,"PORT",60),(1.0,"STBD",61)]:
    engine_stations = [
        (2.32,1.15,1.03,.54),
        (2.55,1.15,1.03,.63),
        (3.45,1.15,1.03,.63),
        (3.94,1.15,1.03,.71),
        (4.10,1.15,1.03,.73),
    ]
    coords = [(sign*cx+radius*math.cos(i*2*math.pi/16),y,
               z+radius*math.sin(i*2*math.pi/16))
              for y,cx,z,radius in engine_stations
              for i in range(16)]
    remodel("BLK_%03d_Nozzle_%s" % (index,side),coords)

# Two distinct smaller upper booster volumes remain BETWEEN the mains,
# raised behind the nearly level roof as in the rear orthographic reference.
for sign,side,index in [(-1.0,"PORT",62),(1.0,"STBD",63)]:
    inner_stations = [
        (3.02,.43,1.81,.18),
        (3.20,.43,1.81,.235),
        (3.80,.43,1.84,.245),
        (4.12,.43,1.84,.28),
        (4.24,.43,1.84,.28),
    ]
    coords = [(sign*cx+radius*math.cos(i*2*math.pi/12),y,
               z+radius*math.sin(i*2*math.pi/12))
              for y,cx,z,radius in inner_stations
              for i in range(12)]
    remodel("BLK_%03d_InnerBoosterEnvelope_%s" % (index,side),coords)

# DO NOT edit the source .blend. Save a separate experiment with coherent
# independent parts, proof in 8 real camera views, and an inspection-only GLB.
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = int(os.environ.get("NFR_CLAY_SAMPLES", "10"))
scene.cycles.use_denoising = True
scene.render.resolution_x=1200
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
scene.render.image_settings.color_depth="8"
try:
    scene.view_settings.view_transform="AgX"
except Exception:
    pass

bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "NF-H01_Gate02_V13_VisionTest.blend"))
bpy.ops.object.select_all(action="DESELECT")
core.select_set(True)
craft = [ob for ob in bpy.data.objects if ob.type == "MESH" and ob.parent == core]
for ob in craft:
    ob.select_set(True)
bpy.context.view_layer.objects.active = core
bpy.ops.export_scene.gltf(
    filepath=str(OUT / "NF-H01_Gate02_V13_Inspection.glb"),
    export_format="GLB", use_selection=True, export_yup=True)
bpy.ops.object.select_all(action="DESELECT")
glbpath = OUT / "NF-H01_Gate02_V13_Inspection.glb"
assert glbpath.stat().st_size > 30000
assert struct.unpack_from("<4sII",glbpath.read_bytes(),0)[0] == b"glTF"

VIEWS = [
  ("01_front",(0,-17,2.2),(0,0,1.2),7.9),
  ("02_rear",(0,17,2.0),(0,0,1.2),7.9),
  ("03_port_side",(-17,0,2.1),(0,0,1.18),9.4),
  ("04_starboard_side",(17,0,2.1),(0,0,1.18),9.4),
  ("05_top",(0,0,18.0),(0,0,1.20),11.8),
  ("06_underside",(0,0,-17.0),(0,0,1.18),11.8),
  ("07_front_three_quarter",(-12.7,-14.5,9.0),(0,0,1.06),10.1),
  ("08_rear_three_quarter",(-12.7,14.5,8.2),(0,0,1.04),10.1),
]
cam = scene.camera
assert cam is not None
cam.data.type = "ORTHO"
cam.data.clip_end = 350
floor = bpy.data.objects.get("STUDIO | matte ground")
for label,loc,target,scale in VIEWS:
    if floor:
        floor.hide_render = label in ("05_top","06_underside")
    cam.location = loc
    cam.rotation_euler = (Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.ortho_scale = scale
    scene.render.filepath = str(OUT / (label + ".png"))
    bpy.ops.render.render(write_still=True)
    assert (OUT / (label + ".png")).stat().st_size > 10000
    print("NFR_V13_REAL_BLENDER_VIEW_OK",label,flush=True)

# Actual world-space bounds of physical components provide a metrological
# checksum independent of pretty renders.
depsgraph=bpy.context.evaluated_depsgraph_get()
measured={}
for ob in craft:
    ev=ob.evaluated_get(depsgraph)
    verts=[ev.matrix_world @ Vector(v) for v in ev.bound_box]
    mins=[min(v[i] for v in verts) for i in range(3)]
    maxs=[max(v[i] for v in verts) for i in range(3)]
    measured[ob.name]={
        "bounds_m":[[round(x,4) for x in mins],[round(x,4) for x in maxs]],
        "dimensions_m":[round(maxs[i]-mins[i],4) for i in range(3)],
    }

assert len(measured)>=26 and required.issubset(measured)
for side in ("PORT","STBD"):
    assert measured["BLK_082_RearSideWing_PORT" if side=="PORT" else "BLK_083_RearSideWing_STBD"]["dimensions_m"][0] > 1
report={
  "asset":"NF-H01",
  "gate":2,
  "revision":"V13 reference-guided silhouette experiment",
  "baseline":"Gate 02 V12 preserved unmodified",
  "source":"NF-H01_Gate02_V13_VisionTest.blend",
  "inspection_glb":"NF-H01_Gate02_V13_Inspection.glb",
  "render_views":[x[0]+".png" for x in VIEWS],
  "mesh_count":len(craft),
  "part_dimensions":measured,
  "changes":[
    "Narrower continuous rear roof bridge with lower crown",
    "Shorter aft vertical fins without deleting their independent geometry",
    "Trimmed but preserved broad rear wing flare on both sides",
    "Larger paired rear propulsion envelopes and raised small inboard booster pair",
  ],
  "neural_inference_proven_on": "Real V12 Blender views, not yet user's chat-uploaded image",
  "geometry_drivers":"owner's 8-view reference visual constraints, manually interpreted pending exact camera calibration",
  "materials_not_started":True,
  "gate_approval":"pending owner visual inspection",
}
(OUT/"MANIFEST.json").write_text(json.dumps(report,indent=2)+"\n")
print("NFR_V13_REAL_GEOMETRY_COMPLETE meshes=%d" % len(craft),flush=True)
