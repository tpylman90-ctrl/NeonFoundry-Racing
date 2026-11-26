"""NF-BW01 Gate04 R4: clear guarding and purposeful industrial service detail.

Input immutable R3 Blender release. Adds REVERSIBLE R4 collection, revises
existing guard glazing on a derivative only, and creates real Cycles render
views (closed door / open inspection, matching R3 cameras). Does not claim
functional animation, finished texture bakes, or Unity suitability.
"""
import bpy, math, sys, json
from mathutils import Vector
from pathlib import Path

OUT=Path(__file__).resolve().parent/"gate04_r4_output"
if "--out" in sys.argv:OUT=Path(sys.argv[sys.argv.index("--out")+1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)

original=bpy.data.collections.get("NF-BW01 R3 | Reversible mechanical refinement")
base=bpy.data.collections.get("GATE03_LOD0")
if not original or not base:raise RuntimeError("Expected verified R3 + LOD0 source scene")
GLASS=bpy.data.materials.get("NF_BW01_R3 | clear interlocked polycarbonate")
if not GLASS:raise RuntimeError("Expected R3 guard glazing")
glazing=[o for o in original.objects if o.type=="MESH" and
         ("clear guarding" in o.name or "safety glazing" in o.name or
          "sliding transparent gate" in o.name)]
if len(glazing)!=5:raise RuntimeError("Expected five independent glazing sheets; got "+str(len(glazing)))
# Blender's previous blue, rough, heavily tinted polycarbonate made the
# mechanism invisible. Use a near-neutral, optically clear material with
# minimal diffuse tint and modest interface reflections.
GLASS.diffuse_color=(.94,.97,1.,.11)
p=GLASS.node_tree.nodes.get("Principled BSDF")
p.inputs["Base Color"].default_value=(.96,.985,1.,1.)
p.inputs["Roughness"].default_value=.015
p.inputs["Transmission Weight"].default_value=.97
p.inputs["IOR"].default_value=1.49
p.inputs["Metallic"].default_value=0.
p.inputs["Alpha"].default_value=.12
# glTF uses material alpha/blend mode, while Cycles uses transmission.
# Actual URP glass will still need its own Gate05 tuning.
if hasattr(GLASS,"surface_render_method"):
    GLASS.surface_render_method="DITHERED"
if hasattr(GLASS,"blend_method"):
    try:GLASS.blend_method="BLEND"
    except (TypeError,ValueError):pass
for o in glazing:
    for mod in list(o.modifiers):
        if mod.type=="WEIGHTED_NORMAL":o.modifiers.remove(mod)
    # Panels are razor-thin 9-10 mm in R3; retain original geometry and
    # independent inspectability, don't alter gate track or unit dimensions.

COL=bpy.data.collections.new("NF-BW01 R4 | Clear guard + industrial subassemblies")
bpy.context.scene.collection.children.link(COL)
M={x:bpy.data.materials.get("NF_BW01_PBR_"+x) for x in
   ("STEEL","BRUSH","DARK","ARMOR","HOUSING","SEAL","MARK","GLAZE")}
if any(v is None for v in M.values()):raise RuntimeError("PBR material family absent")
def link(o,mat):
    for c in list(o.users_collection):c.objects.unlink(o)
    COL.objects.link(o);o.data.materials.clear();o.data.materials.append(mat)
    return o
def bevel(o,w=.006):
    if w:
        b=o.modifiers.new("Milled edge radii","BEVEL");b.width=w;b.segments=3
    n=o.modifiers.new("Weighted normals","WEIGHTED_NORMAL");n.keep_sharp=True
    return o
def box(name,at,dim,mat="STEEL",w=.007):
    bpy.ops.mesh.primitive_cube_add(size=1,location=at)
    o=bpy.context.object;o.name="R4 | "+name;o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    link(o,M[mat]);bevel(o,w);return o
def cylinder(name,at,rad,d,mat="STEEL",axis="Z",n=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=rad,depth=d,location=at)
    o=bpy.context.object;o.name="R4 | "+name
    if axis=="X":o.rotation_euler.y=math.pi/2
    if axis=="Y":o.rotation_euler.x=math.pi/2
    link(o,M[mat])
    for face in o.data.polygons:face.use_smooth=True
    bevel(o,min(rad*.15,.004));return o
def cable(name,pts,r=.013,mat="DARK"):
    cur=bpy.data.curves.new(name,"CURVE");cur.dimensions="3D"
    cur.bevel_depth=r;cur.bevel_resolution=4
    s=cur.splines.new("BEZIER");s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts):
        p.co=co;p.handle_left_type="AUTO";p.handle_right_type="AUTO"
    o=bpy.data.objects.new("R4 | "+name,cur);COL.objects.link(o)
    cur.materials.append(M[mat]);return o
def label(name,txt,at,size=.047,rot=(math.pi/2,0,0),mat="MARK"):
    cr=bpy.data.curves.new(name,"FONT");cr.body=txt;cr.size=size
    cr.extrude=.0002
    o=bpy.data.objects.new("R4 | "+name,cr);COL.objects.link(o)
    o.location=at;o.rotation_euler=rot;cr.materials.append(M[mat])
    return o
# Transparent doors still have structurally believable metal edges.
# Put a strip only on the 4mm edge; do not obscure important silhouettes.
for x in (-1.62,-.11,.11,1.62):
    box("door protective perimeter bumper "+str(x),(x,-1.055,1.41),
        (.022,.018,1.82),"SEAL",.002)
for x in (-.80,.80):
    box("door positive travel stop "+str(x),(x,-1.093,.48),
        (.080,.095,.080),"DARK",.010)
# Actual gripper: align visible toolhead, captive jaw wear pads, hydraulic
# feeds and end-of-travel sensor stops, all individually reviewable.
for side in (-1,1):
    x=-.25+side*.302
    box("carbide contact shoe "+str(side),(x-side*.049,-.260,1.876),
        (.020,.090,.116),"BRUSH",.002)
    cylinder("gripper pad retaining stud "+str(side),
             (x,-.285,1.91),.013,.032,"STEEL","Y",24)
    box("jaw proximity sensor bracket "+str(side),
        (x,-.092,2.102),(.088,.045,.066),"DARK",.008)
    cylinder("sensor inductive tip "+str(side),
             (x,-.125,2.11),.019,.027,"MARK","Y",32)
    cable("jaw air line "+str(side),
          [(-.25+side*.16,-.077,2.08),(-.25+side*.22,-.035,2.20),
           (x,-.083,2.24)],.009,"SEAL")
box("linear rack safety cover",(-.25,-.118,2.115),(.59,.028,.028),
    "BRUSH",.004)
for i in range(9):
    x=-.25-.23+i*.057
    box("gripper travel graduation %02d"%i,(x,-.141,2.134),
        (.009,.009,.014),"MARK",.001)
# Battery cassette top has service lock geometry and blind-mate sockets.
for tag,(x,y,z) in enumerate(((-.17,-.25,1.115),(1.07,.31,1.195))):
    for side in (-1,1):
        xx=x+side*.24
        box("battery cam latch housing %d %s"%(tag,side),
            (xx,y-.36,z+.158),(.075,.10,.075),"STEEL",.009)
        cylinder("battery camlock fastener %d %s"%(tag,side),
                 (xx,y-.36,z+.204),.020,.021,"DARK",n=32)
        box("battery port identification plate %d %s"%(tag,side),
            (x+side*.15,y+.44,z+.104),(.09,.017,.045),
            "ARMOR" if side>0 else "DARK",.004)
    box("battery gasket edge service cover %d"%tag,
        (x,y-.432,z-.092),(.33,.035,.056),"DARK",.004)
    label("battery pack identifier %d"%tag,"NF 72",
          (x-.10,y-.431,z+.02),.037)
# Readable top-mounted diagnostics and coolant connection on the power cabinet.
for i in range(6):
    zz=.92+i*.16
    box("power-cabinet cooling radiator fin %d"%i,
        (1.620,.397,zz),(.295,.028,.029),"BRUSH",.004)
for side in (-1,1):
    xx=1.62+side*.112
    cylinder("power cabinet hose flange "+str(side),
             (xx,.386,2.005),.039,.046,"DARK","Y",40)
    cylinder("power cabinet adapter "+str(side),
             (xx,.344,2.005),.025,.027,"STEEL","Y",40)
label("cabinet safe service marking","NF CELL / 02",(1.445,.405,1.823),.040)
# Visible status lights and diagnostic bars on the HMI monitor.
for i in range(4):
    box("HMI channel waveform %d"%i,
        (1.35,-1.091,1.792+i*.069),(.21-.023*i,.009,.016),
        "MARK" if i==0 else "BRUSH",.003)
for i in range(3):
    cylinder("HMI diagnostic status LED "+str(i),
             (1.61+i*.037,-1.09,1.77),.012,.014,
             "ARMOR" if i==0 else "MARK","Y",24)

bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
pnts=[]
for ob in COL.objects:
    if ob.type not in {"MESH","CURVE","FONT"}:continue
    ev=ob.evaluated_get(dg);m=ev.to_mesh()
    if m:
        pnts.extend([ev.matrix_world@v.co for v in m.vertices])
        ev.to_mesh_clear()
if not pnts:raise RuntimeError("No R4 geometry evaluated")
bounds=[[min(p[i] for p in pnts),max(p[i] for p in pnts)] for i in range(3)]
if bounds[0][0]<-1.98 or bounds[0][1]>1.98 or bounds[1][0]<-1.29 or bounds[1][1]>1.29 or bounds[2][0]<-.03 or bounds[2][1]>3.43:
    raise RuntimeError("R4 outside approved equipment envelope "+str(bounds))
print("NF_BW01_R4_BOUNDS_OK",len(COL.objects),bounds)

# Save derivative before modifying camera/hide statuses, keeping R3 unchanged.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"NF_BW01_GATE04_R4_CLEAR_GUARD.blend"),compress=True)
export=[o for o in base.objects if o.type=="MESH"]+[o for o in original.objects if o.type in
        {"MESH","CURVE","FONT"}]+[o for o in COL.objects if o.type in {"MESH","CURVE","FONT"}]
bpy.ops.object.select_all(action="DESELECT")
for o in export:o.select_set(True)
bpy.context.view_layer.objects.active=export[0]
bpy.ops.export_scene.gltf(filepath=str(OUT/"NF_BW01_GATE04_R4_INSPECTION_ONLY.glb"),
     export_format="GLB",use_selection=True,export_materials="EXPORT",
     export_normals=True,export_texcoords=True)
print("NF_BW01_R4_GLB_OK",len(export))

scene=bpy.context.scene;scene.render.engine="CYCLES"
scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1040;scene.render.resolution_y=780
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
camera=bpy.data.objects.get("Inspection orthographic")
if not camera:raise RuntimeError("Studio camera missing")
scene.camera=camera
views={
"R4_CLEAR_FRONT_THREE_QUARTER":((7,-10,7),(0,0,1.50),5.15),
"R4_CLEAR_REAR_THREE_QUARTER":((-7,9,6),(0,0,1.50),5.15),
"R4_OPEN_GRIPPER_DETAIL":((1,-4,3.15),(-.25,-.21,2.12),1.58),
"R4_OPEN_CASSETTE_DETAIL":((3.6,-4.8,3.6),(-.12,-.15,1.12),2.38),
"R4_OPEN_MECHANICAL_THREE_QUARTER":((7,-10,7),(0,0,1.50),5.15),
}
for name,(eye,target,scale) in views.items():
    # Actual geometry cutaway: hide only glazing for component closeups,
    # leaving the metal door rails/guards unchanged, not a new image.
    cutaway=("OPEN" in name)
    for o in glazing:o.hide_render=cutaway
    camera.location=eye
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.type="ORTHO";camera.data.ortho_scale=scale
    scene.render.filepath=str(OUT/(name+".png"))
    bpy.ops.render.render(write_still=True)
    print("NF_BW01_R4_RENDER_OK",name)
for o in glazing:o.hide_render=False
manifest={
    "asset":"NF-BW01","revision":"R4","stage":"Gate04",
    "status":"VISUAL_REVIEW_PENDING",
    "new_r4_parts":len(COL.objects),
    "r3_glazing_panels":len(glazing),
    "glass":{"transmission":.97,"roughness":.015,"alpha":.12,
             "alpha_blend_URP":"NOT VALIDATED",
             "studio_note":"Neutral untinted optical panel, Blender Cycles"},
    "geometry_bounds_m":bounds,
    "views":list(views.keys()),
    "preserved":"Original R3 release .blend unchanged; R4 separate collection",
    "validation_pending":["glass result in URP","gripper clearances",
        "cassette connector fitting","new geometry UVs and AO/normal bake",
        "mobile triangles/FPS","final visual owner acceptance"]
}
(OUT/"R4_REVIEW.json").write_text(json.dumps(manifest,indent=2))
print("NF_BW01_R4_PACKAGE_OK",len(COL.objects),len(views))
