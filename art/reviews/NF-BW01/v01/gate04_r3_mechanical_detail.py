"""NF-BW01 Gate04/R3 — non-destructive mechanical finish REVISION CANDIDATE.

Input: actual, approved PBR-lookdev Blender scene. Adds a physically modeled
upgrade layer (guard panels/interlock, machined motor sleeves, cassette blind-
mate connectors, gripper tooling, HMI status), then exports actual geometry and
renders 4 review cameras. Baseline source and previous releases are untouched.
Not a simulation or proof of gripping or industrial safety.
"""
import bpy,math,json,sys
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent/"gate04_r3_output"
if "--out" in sys.argv:OUT=Path(sys.argv[sys.argv.index("--out")+1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)

G=bpy.data.collections.new("NF-BW01 R3 | Reversible mechanical refinement")
bpy.context.scene.collection.children.link(G)
M={}
for key in ("HOUSING","STEEL","BRUSH","DARK","ARMOR","SEAL","GLAZE","MARK"):
    M[key]=bpy.data.materials.get("NF_BW01_PBR_"+key)
    if not M[key]:raise RuntimeError("Material source missing: "+key)
GLASS=bpy.data.materials.new("NF_BW01_R3 | clear interlocked polycarbonate")
GLASS.diffuse_color=(.40,.68,.77,.20)
GLASS.use_nodes=True
bs=GLASS.node_tree.nodes.get("Principled BSDF")
bs.inputs["Base Color"].default_value=(.36,.57,.68,1.)
bs.inputs["Roughness"].default_value=.11
bs.inputs["Transmission Weight"].default_value=.78
bs.inputs["IOR"].default_value=1.49
bs.inputs["Metallic"].default_value=0.
# Render as real transmissive material in Cycles. Alpha attenuation in game
# is not yet tested; no URP readiness claim.
def link_obj(o,mat):
    for c in list(o.users_collection):c.objects.unlink(o)
    G.objects.link(o)
    o.data.materials.clear();o.data.materials.append(mat)
    return o
def edge(o,width=.007):
    if width:
        b=o.modifiers.new("Manufactured edge radii","BEVEL")
        b.width=width;b.segments=3
    w=o.modifiers.new("Machine-weighted surface normals","WEIGHTED_NORMAL")
    w.keep_sharp=True
    return o
def box(name,p,dim,kind="STEEL",bevel=.009):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name="R3 | "+name;o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    link_obj(o,M[kind] if kind in M else GLASS)
    return edge(o,bevel)
def cylinder(name,p,r,depth,kind="STEEL",axis="Z",n=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=depth,location=p)
    o=bpy.context.object;o.name="R3 | "+name
    if axis=="Y":o.rotation_euler.x=math.pi/2
    if axis=="X":o.rotation_euler.y=math.pi/2
    link_obj(o,M[kind])
    for polygon in o.data.polygons:polygon.use_smooth=True
    return edge(o,.005)
def torus(name,p,major,minor,kind="BRUSH",axis="Z"):
    bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=12,
        location=p,major_radius=major,minor_radius=minor)
    o=bpy.context.object;o.name="R3 | "+name
    if axis=="Y":o.rotation_euler.x=math.pi/2
    if axis=="X":o.rotation_euler.y=math.pi/2
    link_obj(o,M[kind])
    for poly in o.data.polygons:poly.use_smooth=True
    return o
def label(name,txt,p,size=.035,kind="MARK",rot=(math.pi/2,0,0)):
    data=bpy.data.curves.new(name,"FONT");data.body=txt
    data.size=size;data.extrude=.0003
    o=bpy.data.objects.new("R3 | "+name,data)
    G.objects.link(o);o.location=p;o.rotation_euler=rot
    data.materials.append(M[kind]);return o

# 1. SOFTEN large exposed cylindrical drive housings with actual 96-sided
# machinable exterior sleeves. Existing parts remain intact for comparison.
for name,p,r,d,axis in (
    ("axis1 precision yaw stator",(-1.10,.56,.89),.300,.115,"Z"),
    ("axis2 shoulder planetary cover",(-1.40,.48,1.825),.235,.085,"Y"),
    ("axis3 elbow planetary cover",(-.88,.20,2.53),.153,.066,"X"),
    ("axis4 gripper rotation gearbox",(-.25,-.21,2.302),.139,.080,"Z"),
):
    cylinder(name,p,r,d,"DARK",axis)
    # Fully circular bevelled rings add readable machining and hide low-facet
    # transition bands without changing the robot's overall dimensions.
    offsets=(.045,-.045) if axis=="Y" else ((.055,-.055) if axis=="Z" else (.034,-.034))
    for side,offset in enumerate(offsets):
        x,y,z=p
        pt=(x+offset,y,z) if axis=="X" else ((x,y+offset,z) if axis=="Y" else (x,y,z+offset))
        torus(name+" | machined retaining race "+str(side),pt,r*.94,.009,"BRUSH",axis)

# 2. The gripper remains a distinct tool. Replaceable wear pads, visible
# adjustment screws, two guided actuator rods and pneumatic inlet blocks.
for side in (-1,1):
    x=-.25+side*.302
    box("gripper contact wear pad "+str(side),(x-side*.035,-.26,1.86),
        (.032,.095,.130),"SEAL",.004)
    cylinder("gripper replaceable pin "+str(side),(x,-.21,1.892),.018,.128,"STEEL","Y",48)
    cylinder("gripper jaw adjustment screw "+str(side),(x,-.21,2.172),.022,.045,"BRUSH","Z",48)
    cylinder("parallel jaw actuator piston "+str(side),
             (-.25+side*.205,-.137,2.064),.028,.17,"STEEL","X",48)
    box("jaw pneumatic service block "+str(side),
        (-.25+side*.157,-.085,2.055),(.091,.090,.098),"HOUSING",.016)
# Laser etched maximum load designation, purely decorative; no physical rating
# or real industrial certification is implied.
label("gripper jaw size guide","NF-72 / TOOL 01",(-.48,-.325,2.173),.030)

# 3. Cassettes — separate keyed positive/negative high-voltage couplers,
# blue/black coolant plugs and mechanical latch receivers. Both loaded and
# stored modules receive their own connectors in the actual world coordinates.
for tag,(cx,cy,cz) in enumerate(((-.17,-.25,1.115),(1.07,.31,1.195))):
    back=cy+.44
    for sign,kind in ((-1,"DARK"),(1,"ARMOR")):
        xx=cx+sign*.14
        cylinder("cassette %d HV insulating feedthrough %s"%(tag,sign),
                 (xx,back,cz-.058),.057,.075,"DARK","Y",64)
        cylinder("cassette %d HV copper contact %s"%(tag,sign),
                 (xx,back+.055,cz-.058),.034,.026,"BRUSH","Y",64)
        torus("cassette %d face gasket %s"%(tag,sign),
              (xx,back+.049,cz-.058),.048,.007,kind,"Y")
    for sign in (-1,1):
        xx=cx+sign*.23
        cylinder("cassette %d coolant quick connector %s"%(tag,sign),
                 (xx,cy-.445,cz-.08),.038,.060,"STEEL","Y",48)
        torus("cassette %d coolant sealing flange %s"%(tag,sign),
              (xx,cy-.476,cz-.08),.040,.007,"SEAL","Y")
        box("cassette %d tool socket lip %s"%(tag,sign),
            (cx+sign*.305,cy-.34,cz+.08),(.044,.12,.106),"BRUSH",.007)
# 4. Interlocked transparent safety enclosure, fitted to approved steel posts.
# DO NOT make a flat opaque wall across the model; the camera must still see
# the machinery and the front gate will be independently inspectable.
# Rear fixed shield, two flanks, front upper + two sliding door leafs.
box("rear clear guarding",(0,1.028,1.37),(3.38,.009,2.00),"GLASS",.002)
for sign in (-1,1):
    box("side safety glazing "+str(sign),(sign*1.754,0,1.35),
        (.009,1.92,2.00),"GLASS",.002)
    for z in (.52,2.25):
        box("side glass captive rubber molding "+str(sign),
            (sign*1.749,0,z),(.020,1.99,.021),"SEAL",.003)
# Narrow door pair separated by a physical center rail. Doors are rendered
# shut for this parked-state inspection; no real interlock is implemented.
for sign in (-1,1):
    x=sign*.86
    box("front sliding transparent gate "+str(sign),
        (x,-1.026,1.42),(1.55,.010,1.94),"GLASS",.002)
    box("sliding door lower track "+str(sign),
        (x,-1.047,.43),(1.61,.060,.041),"STEEL",.007)
    box("sliding door pull "+str(sign),
        (sign*.15,-1.08,1.41),(.080,.058,.20),"DARK",.014)
    box("door frame center stile "+str(sign),
        (sign*.065,-1.052,1.42),(.032,.054,2.02),"BRUSH",.004)
# A central interlock plus status cluster, visible above the approach.
box("safety gate interlock",(0,-1.035,2.315),(.19,.065,.14),"DARK",.009)
for x,key in ((-.057,"ARMOR"),(.057,"MARK")):
    cylinder("guard status lens "+key,(x,-1.074,2.324),.022,.018,key,"Y",32)
label("equipment warning label","LOCKOUT / SERVICE",
      (-.71,-1.082,.610),.046)

# 5. Operator HMI legibility and local status: bezel plate and small controls.
box("HMI industrial interface trim",(1.45,-1.042,1.864),
    (.56,.025,.424),"DARK",.009)
for i in range(3):
    box("HMI diagnostic bar "+str(i),(1.35,-1.061,1.77+i*.069),
        (.16,.006,.012),"MARK",.003)
cylinder("HMI emergency guarded pushbutton",
         (1.70,-1.000,1.55),.055,.036,"ARMOR","Y",48)

# Explicit bounds and grouped geometry validation, with no claim this
# approximation has functional robotic swept-volume or door collision checks.
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
coords=[]
for obj in G.objects:
    if obj.type not in {"MESH","CURVE","FONT"}:continue
    ev=obj.evaluated_get(dg);me=ev.to_mesh()
    if me:
        coords.extend([ev.matrix_world@v.co for v in me.vertices])
        ev.to_mesh_clear()
xmin,xmax=min(x.x for x in coords),max(x.x for x in coords)
ymin,ymax=min(x.y for x in coords),max(x.y for x in coords)
zmin,zmax=min(x.z for x in coords),max(x.z for x in coords)
if xmin < -1.98 or xmax > 1.98 or ymin < -1.29 or ymax > 1.29 or zmin < -.03 or zmax > 3.43:
    raise RuntimeError("R3 extends beyond workstation envelope: "+str((xmin,xmax,ymin,ymax,zmin,zmax)))
print("NF_BW01_R3_GEOMETRY_AUDIT_OK",len(G.objects),(xmin,xmax,ymin,ymax,zmin,zmax))

# Save native Blender derivative before modifying render setup.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"NF_BW01_GATE04_R3_REFINEMENT.blend"),compress=True)
# GLB only the updated R3 objects plus approved LOD0 base.
base=bpy.data.collections.get("GATE03_LOD0")
if not base:raise RuntimeError("Approved LOD0 base unavailable")
export_objs=[o for o in G.objects if o.type in {"MESH","CURVE","FONT"}] + [
    o for o in base.objects if o.type=="MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in export_objs:o.select_set(True)
bpy.context.view_layer.objects.active=export_objs[0]
bpy.ops.export_scene.gltf(filepath=str(OUT/"NF_BW01_GATE04_R3_INSPECTION_ONLY.glb"),
    export_format="GLB",use_selection=True,export_materials="EXPORT",
    export_normals=True,export_texcoords=True)
print("NF_BW01_R3_GLB_OK",len(export_objs))

# Render identical 3/4 baseline view plus extra detail views of the UPDATED
# actual mesh (no AI-generated image used as evidence).
scene=bpy.context.scene;scene.render.engine="CYCLES"
scene.cycles.samples=28;scene.cycles.use_denoising=True
scene.render.resolution_x=1040;scene.render.resolution_y=780
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
camera=bpy.data.objects.get("Inspection orthographic")
scene.camera=camera
views={
"R3_FRONT_THREE_QUARTER":((7,-10,7),(0,0,1.50),5.15),
"R3_ROBOT_GRIPPER_DETAIL":((1,-4,3.15),(-.25,-.21,2.12),1.58),
"R3_CASSETTE_DOCK_DETAIL":((3.6,-4.8,3.6),(-.12,-.15,1.12),2.38),
"R3_REAR_THREE_QUARTER":((-7,9,6),(0,0,1.50),5.15),
}
for name,(eye,target,scale) in views.items():
    camera.location=eye
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.type="ORTHO";camera.data.ortho_scale=scale
    scene.render.filepath=str(OUT/(name+".png"))
    bpy.ops.render.render(write_still=True)
    print("NF_BW01_R3_ACTUAL_RENDER_OK",name)
(OUT/"R3_REVIEW.json").write_text(json.dumps({
    "asset":"NF-BW01","stage":"Gate04, reversible mechanical revision",
    "status":"GEOMETRY_REVIEW_PENDING",
    "new_parts":len(G.objects),
    "review_images":list(views),
    "limits":["Not a functioning gripper","Guard not an actual safety interlock",
              "No collision sweep","Not optimized or Android benchmarked",
              "Added mesh uses same materials, UV/bake review needed before promotion"],
},indent=2))
print("NF_BW01_R3_REVIEW_PACKAGE_OK",len(G.objects))
