"""NF-H01 'Forge One' — GATE 02 / V7 FACETED ARMOR SILHOUETTE ONLY.

Generate a real, editable, original Blender model from the approved Gate 01
engineering stations. Outputs eight orthographic/isometric neutral clay views,
an editable .blend, and construction metadata. NOT a textured hero model.
Never advance status to Gate 03 from this generator.

Usage (Blender 4.5.3):
  blender --background --threads 4 --python tools/build_hero_01_clay.py

All geometry is built as independent objects and each object is part of
the production assembly hierarchy. No reference/trademark geometry is used.
"""
import bpy
import bmesh
import json
import math
import os
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "art/hero_01/01_PROPORTIONS.json").read_text())
PROGRESS = json.loads((ROOT / "art/hero_01/progress.json").read_text())
assert PROGRESS["last_approved_stage"] == 1 and PROGRESS["current_stage"] == 2
assert PROGRESS["gates"][1]["state"] == "in_progress"
assert DATA["approval_status"] == "approved_for_blockout", "Gate 01 dimensions must be explicitly approved before modeling"

OUT = ROOT / "build" / "hero_01_gate02"
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c

COL_ROOT = collection("NF-H01 | GATE 02 CLAY")
COL_BODY = collection("01 Primary fuselage")
COL_CAB = collection("02 Cockpit mass")
COL_AERO = collection("03 Shoulder and aero masses")
COL_REAR = collection("04 Aft engines and cradle")
COL_STUDIO = collection("STUDIO | cameras and lights")
ROOT_EMPTY = bpy.data.objects.new("NF_H01_ROOT", None)
COL_ROOT.objects.link(ROOT_EMPTY)

def clay(name, value, rough=.82):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (value, value * .988, value * .965, 1.0)
    m.use_nodes = True
    shader = m.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = m.diffuse_color
    shader.inputs["Roughness"].default_value = rough
    return m

MAT_BODY = clay("CLAY / primary neutral warm gray",.53)
MAT_NOSE = clay("CLAY / front shell light gray",.62)
MAT_CAB = clay("CLAY / canopy volume charcoal",.23)
MAT_SHOULDER = clay("CLAY / layered shoulder silver",.58)
MAT_REAR = clay("CLAY / engine exterior dark gray",.37)
MAT_FIN = clay("CLAY / aerostructure",.66)
MAT_CUT = clay("CLAY / approximate intake negative space marker",.23)
MAT_GROUND = clay("STUDIO / matte backdrop floor",.23)

def attach(obj, name, material, col):
    obj.name = name
    obj.parent = ROOT_EMPTY
    obj.data.materials.append(material)
    # Move object out of Blender's active collection into the correct assembly.
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    col.objects.link(obj)
    if obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth = False
    return obj

def mesh_obj(name, verts, faces, material, col, edge_width=0.018):
    me = bpy.data.meshes.new(name + " | topology")
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    ob.parent = ROOT_EMPTY
    me.materials.append(material)
    # Recalculate consistent outward normals, avoiding invisible road/body faces.
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = False
    if edge_width > 0.0:
        bevel = ob.modifiers.new("Blockout silhouette edge break", "BEVEL")
        bevel.width = edge_width
        bevel.segments = 1
        bevel.limit_method = 'ANGLE'
        weighted = ob.modifiers.new("Weighted clay normals", "WEIGHTED_NORMAL")
        weighted.keep_sharp = True
    return ob

def loft(name, rings, ring_fn, material, col, bevel=.02):
    verts = []
    for ring in rings:
        verts.extend(ring_fn(*ring))
    count = len(ring_fn(*rings[0]))
    faces = []
    for i in range(len(rings)-1):
        a = i*count
        b = a+count
        for j in range(count):
            n=(j+1)%count
            faces.append((a+j, a+n, b+n, b+j))
    faces.append(tuple(reversed(tuple(range(count)))))
    start = (len(rings)-1)*count
    faces.append(tuple(range(start,start+count)))
    return mesh_obj(name,verts,faces,material,col,bevel)

def smooth_stations(values, segments=4):
    """Silhouette-only hard surface: do not subdivide loft stations.
    
    Broad planar segments across the Y axis are deliberate armored facets.
    Gate 03 will introduce production topology and selective bevel control.
    """
    return list(values)

def fuselage_ring(y, half, top, bottom):
    # Ten-point hard-surface cross-section: flat armor deck, sharp 45-degree
    # upper chines, near-vertical flanks, and planar angled lower armor.
    # This is silhouette massing, not inset panels or actual hollow ducts.
    dz = top-bottom
    profile=[
      (-half*.67,top), (half*.67,top),
      (half,top-dz*.27), (half,bottom+dz*.26),
      (half*.70,bottom), (half*.28,bottom+.08),
      (-half*.28,bottom+.08), (-half*.70,bottom),
      (-half,bottom+dz*.26), (-half,top-dz*.27),
    ]
    return [(x,y,z) for x,z in profile]

source = DATA["primary_shell_stations"]
# Gate 02 V7: Gate 01 figures are initial targets, not user-approved
# production limits. The present clay review intentionally opens the width.
stations=[]
for p in source:
    y=p["y"]
    half=p["half_width"]*1.15
    top=p["top_z"]
    bottom=p["bottom_z"]
    if y <= -3.59:
        # Squared nose face, deliberately broad and perpendicular to Y.
        half=.57; top=1.06; bottom=.57
    elif y <= -3.14:
        half=.75; top=1.15; bottom=.52
    stations.append((y,half,top,bottom))

def station_at(y):
    for a,b in zip(stations,stations[1:]):
        if a[0] <= y <= b[0]:
            t=(y-a[0])/(b[0]-a[0])
            return (y,*[a[k]+(b[k]-a[k])*t for k in range(1,4)])
    return stations[0] if y<stations[0][0] else stations[-1]

# The nose and center are separate construction volumes joined under armor.
nose = [p for p in stations if p[0]<-1.70] + [station_at(-1.56)]
center = [station_at(-1.61)] + [p for p in stations if p[0]>=-1.70]
loft("BLK_010_NosePrimary",nose,fuselage_ring,MAT_NOSE,COL_BODY,.045)
loft("BLK_020_CenterFuselage",center,fuselage_ring,MAT_BODY,COL_BODY,.040)

# V7: low elongated fighter-jet cockpit ENVIRONMENT / envelope only.
# Canopy frames, hinges, seals and actual transparent glazing are Gate 06.
canopy = [
    (-1.58,.16,1.35,1.28),
    (-1.20,.34,1.51,1.29),
    (-.67,.53,1.91,1.30),
    (.02,.66,2.16,1.32),
    (.55,.71,2.20,1.33),
    (1.05,.64,2.01,1.35),
    (1.52,.35,1.57,1.37),
    (1.78,.14,1.47,1.40),
]
def canopy_ring(y,half,top,bottom):
    h=top-bottom
    # Flat top and wide cut-glass shoulders, no spherical dome.
    shape=[
      (-half*.45,top), (half*.45,top),
      (half*.91,top-h*.32), (half,bottom+h*.08),
      (half*.74,bottom-.012), (-half*.74,bottom-.012),
      (-half,bottom+h*.08), (-half*.91,top-h*.32),
    ]
    return [(x,y,z) for x,z in shape]
loft("BLK_030_CanopyEnvelope",canopy,canopy_ring,MAT_CAB,COL_CAB,.012)

def side_ring(y,center_x,half,top,bottom):
    # Planar eight-sided armored pontoon / shoulder section with four 
    # chamfered corners and flat top/side/belly surfaces.
    h=top-bottom
    section=[
      (-.72,0),(.72,0),(1,.24),(1,.77),
      (.72,1),(-.72,1),(-1,.77),(-1,.24)
    ]
    return [(center_x+half*x,y,top-h*t) for x,t in section]

for direction, tag in [(-1.0,"PORT"),(1.0,"STBD")]:
    # Heavy shoulder rail: parallel planar wall, not flowing teardrop.
    shoulder=[
        (-2.80,1.13,.24,1.18,.60),
        (-2.31,1.29,.34,1.33,.54),
        (-1.76,1.37,.43,1.43,.49),
        (-.75,1.41,.46,1.48,.47),
        (.42,1.42,.47,1.53,.47),
        (1.38,1.41,.47,1.58,.48),
        (2.24,1.39,.46,1.56,.51),
        (3.01,1.36,.41,1.46,.56)
    ]
    def ring_mirror(y, center, half, top, bottom):
        return side_ring(y,direction*center,half,top,bottom)
    loft("BLK_040_Shoulder_"+tag if direction<0 else "BLK_041_Shoulder_"+tag,
         shoulder,ring_mirror,MAT_SHOULDER,COL_AERO,.042)

    # Envelopes ONLY. Actual rectangular bores, scoops, separators and
    # mechanical liners are deferred to Gate 04.
    intake=[
        (-3.32,1.31,.42,1.33,.50), 
        (-3.15,1.32,.46,1.41,.45),
        (-2.76,1.37,.49,1.48,.42),
        (-2.15,1.42,.51,1.53,.40),
        (-1.64,1.43,.51,1.54,.40),
        (-1.11,1.44,.48,1.50,.45),
        (-.68,1.43,.41,1.47,.50),
    ]
    def intake_ring(y,center,half,top,bottom):
        return side_ring(y,direction*center,half,top,bottom)
    loft("BLK_IntakeEnvelope_"+tag,intake,intake_ring,
         MAT_CUT,COL_AERO,.036)

# Squared heavy rear bulkhead volume, independently modeled from the hull.
aft = [
    (1.18,1.27,1.48,.55),
    (1.82,1.43,1.59,.50),
    (2.56,1.49,1.60,.51),
    (3.20,1.50,1.57,.52),
    (3.52,1.46,1.53,.54)
]
loft("BLK_050_AftMachinery",aft,fuselage_ring,MAT_REAR,COL_REAR,.048)

def cylinder(name,center,radius,depth,mat,segments=16):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=segments,radius=radius,depth=depth,location=center)
    ob=bpy.context.object
    ob.rotation_euler.x=math.pi/2
    return attach(ob,name,mat,COL_REAR)

# Larger OUTER nozzle envelopes only; bells, lips, rings and ribs: Gate 05.
for tag,sign,index in [("PORT",-1.0,60),("STBD",1.0,61)]:
    cylinder("BLK_%03d_Nozzle_%s"%(index,tag),
             (sign*1.18,3.16,1.02),.60,1.70,MAT_REAR,16)

# Gate 02 winglet masses: thin swept trapezoid, downward from pontoon root.
# Dedicated structural mounting / actual aero section waits for Gate 04.
def fin_solid(name,outline,thickness,mat,col):
    verts=[]
    for z in [-thickness/2,thickness/2]:
        verts.extend([(x,y,h+z) for x,y,h in outline])
    n=len(outline)
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,n+j,n+i))
    return mesh_obj(name,verts,faces,mat,col,.014)

for sign,tag,first,rear in [(-1,"PORT",70,80),(1,"STBD",71,81)]:
    wing=[
        (sign*1.73,-1.18,.66),
        (sign*2.26,-1.00,.59),
        (sign*2.32,-.34,.56),
        (sign*1.75,-.62,.65)
    ]
    fin_solid("BLK_%03d_FinFront_%s"%(first,tag),
              wing,.085,MAT_FIN,COL_AERO)

    # Taller swept-outward rear fin, rooted INBOARD on upper engine deck.
    # An extruded planar fin mass (not a detailed production aerofoil).
    root_x=sign*1.10
    base=[(2.08,1.52),(2.28,2.06),(2.82,2.68),
          (3.28,2.58),(3.36,1.52)]
    verts=[]
    for offset in [-.075,.075]:
        for yy,zz in base:
            verts.append((root_x+sign*(zz-1.50)*.16+offset,yy,zz))
    n=len(base)
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    for k in range(n):
        j=(k+1)%n
        faces.append((k,j,n+j,n+k))
    mesh_obj("BLK_%03d_FinRear_%s"%(rear,tag),
             verts,faces,MAT_FIN,COL_AERO,.02)

# Studio is NOT part of the production craft geometry.
def area(name,loc,power,scale,target):
    light=bpy.data.lights.new(name,'AREA')
    light.energy=power
    light.shape='DISK'
    light.size=scale
    obj=bpy.data.objects.new(name,light)
    COL_STUDIO.objects.link(obj)
    obj.location=loc
    vec=Vector(target)-obj.location
    obj.rotation_euler=vec.to_track_quat('-Z','Y').to_euler()

area("Studio softbox / forward",(-4,-8,9),950,7,(0,0,1))
area("Studio softbox / aft",(5,6,9),780,8,(0,0,1))
area("Studio strip / top",(0,1,13),880,9,(0,0,1))
area("Studio fill",(0,-1,4),250,5,(0,0,1))

bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-.035))
floor=bpy.context.object
floor.name="STUDIO | matte ground"
floor.data.materials.append(MAT_GROUND)
for c in list(floor.users_collection):
    c.objects.unlink(floor)
COL_STUDIO.objects.link(floor)

world=bpy.data.worlds.new("Matte graphite ambient studio")
scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.16,.18,.21,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.48

scene.render.engine='CYCLES'
scene.cycles.device='CPU'
scene.cycles.samples=int(os.environ.get("NFR_CLAY_SAMPLES","12"))
scene.cycles.use_denoising=True
scene.render.resolution_x=1200
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.render.image_settings.color_depth='8'
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.view_settings.exposure = -0.25
try:
    scene.view_settings.look="AgX - Medium High Contrast"
except Exception:
    pass

# Eight actual camera renders. Orthographic images are used for proportion
# checking; isometric views show overlapping volumes and attachment depth.
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
camera=bpy.data.cameras.new("ORTHO / silhouette review")
cam_obj=bpy.data.objects.new("GATE 02 REVIEW CAMERA",camera)
COL_STUDIO.objects.link(cam_obj)
scene.camera=cam_obj
camera.type='ORTHO'
camera.clip_end=350
camera.lens=44

# Save the actual editable production blockout before rendering.
cam_obj.location=(0,-17,2.2)
cam_obj.rotation_euler=(Vector((0,0,1.2))-cam_obj.location).to_track_quat('-Z','Y').to_euler()
camera.ortho_scale=9.0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"NF-H01_Gate02_Clay.blend"))

# Viewer-only GLB: export the *same* independent craft meshes with the
# parent root, but exclude floor, studio lamps and review camera. This
# is NOT a production export (Gate 10 stays locked).
bpy.ops.object.select_all(action='DESELECT')
ROOT_EMPTY.select_set(True)
craft_meshes = [obj for obj in bpy.data.objects
                if obj.parent == ROOT_EMPTY and obj.type == 'MESH']
for obj in craft_meshes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = ROOT_EMPTY
bpy.ops.export_scene.gltf(
    filepath=str(OUT/"NF-H01_Gate02_Inspection.glb"),
    export_format='GLB',
    use_selection=True,
    export_yup=True,
)
assert (OUT/"NF-H01_Gate02_Inspection.glb").stat().st_size > 30000
print("NF_H01_GATE02_INSPECTION_GLB_OK meshes=%d" % len(craft_meshes), flush=True)
bpy.ops.object.select_all(action='DESELECT')

for label, loc, target, scale in VIEWS:
    floor.hide_render=(label in ("05_top","06_underside"))
    cam_obj.location=loc
    look=Vector(target)-cam_obj.location
    cam_obj.rotation_euler=look.to_track_quat('-Z','Y').to_euler()
    camera.ortho_scale=scale
    scene.render.filepath=str(OUT/(label+".png"))
    bpy.ops.render.render(write_still=True)
    f=OUT/(label+".png")
    assert f.exists() and f.stat().st_size>10000, "Invalid clay review render: "+str(f)
    print("NF_H01_CLAY_VIEW_OK",label,f.stat().st_size,flush=True)

expected=DATA["object_blockout"]
existing={o.name for o in bpy.data.objects}
missing=[n for n in expected if n not in existing]
assert not missing,"Missing approval-gate blockout objects: "+str(missing)
# A single complete Blender file, not independent concept/raster shapes.
assert (OUT/"NF-H01_Gate02_Clay.blend").stat().st_size>30000
manifest={
 "asset_id":"NF-H01","gate":2,"revision":"V7-faceted-armor","approval":"pending user visual inspection",
 "references":"Based on user-supplied images, original geometry only",
 "source":"NF-H01_Gate02_Clay.blend",
 "inspection_glb":"NF-H01_Gate02_Inspection.glb",
 "renders":[x[0]+".png" for x in VIEWS],
 "separate_blockout_meshes":expected,
 "dimensions_proposed":DATA["proposed_envelope"],
 "note":"V7 intentionally deviates from provisional width/length; Gate 02 silhouette pending approval.",
 "future_stages_not_started":[3,4,5,6,7,8,9,10,11,12],
}
(OUT/"MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("NF_H01_GATE02_CLAY_COMPLETE views=8 objects=%d" % len(expected),flush=True)
