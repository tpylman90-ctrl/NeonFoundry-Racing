"""NF-BW01 R5 detail + texture inspection, authored over verified R4 .blend.

Original R4 geometry retained as source; additions live in an R5 collection.
Textures are real image-based service labels and patterned protection plates,
NOT a high->low normal/AO bake. The latter remains a separate Gate04 requirement.

Units meters; Blender 4.3, R4 named parts and original PBR material palette.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
from collections import Counter

OUT=Path(__file__).resolve().parent/"gate04_r5_output"
if "--out" in sys.argv:OUT=Path(sys.argv[sys.argv.index("--out")+1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
TEX=OUT/"textures";TEX.mkdir(exist_ok=True)

for group in ("NF-BW01 R4 | Clear guard + industrial subassemblies",
              "NF-BW01 R3 | Reversible mechanical refinement",
              "GATE03_LOD0"):
    if bpy.data.collections.get(group) is None:
        raise RuntimeError("Required actual source geometry missing: "+group)
COL=bpy.data.collections.new("NF-BW01 R5 | Diagnostics and manufacturing finish")
bpy.context.scene.collection.children.link(COL)
M={k:bpy.data.materials.get("NF_BW01_PBR_"+k) for k in
   ("HOUSING","STEEL","BRUSH","DARK","ARMOR","SEAL","MARK","GLAZE")}
if any(v is None for v in M.values()):raise RuntimeError("Original PBR palette missing")
# Small display-only emissive source. Unity import must later rebuild in URP,
# no runtime emissive visibility claim.
def emissive(name,color,strength):
    m=bpy.data.materials.new("NF_BW01_R5 | "+name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    n=m.node_tree.nodes.get("Principled BSDF")
    n.inputs["Base Color"].default_value=(*color,1.)
    n.inputs["Emission Color"].default_value=(*color,1.)
    n.inputs["Emission Strength"].default_value=strength
    n.inputs["Roughness"].default_value=.25
    return m
M["CYAN"]=emissive("Diagnostic cyan",(.06,.73,.88),2.6)
M["AMBER"]=emissive("Warning amber",(1.,.41,.07),1.5)

def adopt(obj,mat):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    COL.objects.link(obj);obj.data.materials.clear()
    obj.data.materials.append(M[mat] if isinstance(mat,str) else mat)
    return obj
def edge(obj,r=.004):
    if r:
        b=obj.modifiers.new("Manufacturing edge radius","BEVEL")
        b.width=r;b.segments=3
    n=obj.modifiers.new("Corner normals","WEIGHTED_NORMAL")
    n.keep_sharp=True
def block(name,pos,dim,mat="STEEL",b=.004):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o=bpy.context.object;o.name="R5 | "+name
    o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    adopt(o,mat);edge(o,b);return o
def drum(name,pos,rad,length,mat="STEEL",axis="Z",sides=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides,radius=rad,depth=length,location=pos)
    o=bpy.context.object;o.name="R5 | "+name
    if axis=="Y":o.rotation_euler.x=math.pi/2
    if axis=="X":o.rotation_euler.y=math.pi/2
    adopt(o,mat)
    for p in o.data.polygons:p.use_smooth=True
    edge(o,min(rad*.11,.003));return o
def loop(name,pos,rad,tube,mat="BRUSH",axis="Z"):
    bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=10,
                                    location=pos,major_radius=rad,minor_radius=tube)
    o=bpy.context.object;o.name="R5 | "+name
    if axis=="Y":o.rotation_euler.x=math.pi/2
    if axis=="X":o.rotation_euler.y=math.pi/2
    adopt(o,mat)
    for f in o.data.polygons:f.use_smooth=True
    return o
def cable(name,pts,r=.009,mat="SEAL"):
    curve=bpy.data.curves.new(name,"CURVE")
    curve.dimensions="3D";curve.bevel_depth=r;curve.bevel_resolution=3
    sp=curve.splines.new("BEZIER");sp.bezier_points.add(len(pts)-1)
    for p,xyz in zip(sp.bezier_points,pts):
        p.co=xyz;p.handle_left_type="AUTO";p.handle_right_type="AUTO"
    o=bpy.data.objects.new("R5 | "+name,curve);COL.objects.link(o)
    curve.materials.append(M[mat]);return o

# Robot: recessed gearbox fastener ring and organized encoder coupler
# All additions are purposeful interfaces, not arbitrarily repeated rivets.
for i in range(8):
    a=math.tau*i/8
    drum("robot elbow face screw %02d"%i,
         (-1.40+math.cos(a)*.181,.69,1.825+math.sin(a)*.181),
         .010,.019,"DARK","Y",24)
for i in range(6):
    a=math.tau*i/6
    drum("robot yaw gear lock %02d"%i,
         (-1.10+math.cos(a)*.190,.56+math.sin(a)*.190,1.038),
         .012,.021,"STEEL",sides=24)
# Multi-segment strain-relief gland through which wrist signal enters.
drum("toolhead cable gland",(-.33,.01,2.31),.041,.072,"DARK","Y")
loop("toolhead cable sealing ring",(-.33,-.031,2.31),.038,.006,"BRUSH","Y")
cable("gripper strain-relieved sensor lead",
      [(-.33,-.035,2.33),(-.39,-.04,2.39),(-.48,-.11,2.34),
       (-.48,-.15,2.17)],.011,"SEAL")

# Gripper: actual opposite jaw surface pads, keyed sensor rails, jaw end stop.
for side in (-1,1):
    x=-.25+side*.302
    block("gripper textured contact jaw %s"%side,
          (x-side*.046,-.264,1.86),(.024,.087,.123),"DARK",.003)
    for j in range(3):
        block("gripper shoe friction rib %s %s"%(side,j),
              (x-side*.064,-.265,1.817+j*.041),(.008,.065,.009),
              "SEAL",.001)
    drum("jaw sleeve shoulder bolt %s"%side,(x,-.212,2.188),
         .016,.025,"STEEL","Z",24)
    block("jaw force sensor bracket %s"%side,
          (x,-.104,2.061),(.083,.031,.042),"STEEL",.004)
    block("jaw hall sensor window %s"%side,
          (x,-.127,2.061),(.047,.006,.021),"CYAN",.001)

# Battery cassette: actual blind-mate contact guards and bay alignment.
for pack,(cx,cy,cz) in enumerate(((-.17,-.25,1.115),(1.07,.31,1.195))):
    for side in (-1,1):
        x=cx+side*.141
        drum("pack%d insulated HV bushing %s"%(pack,side),
             (x,cy+.50,cz-.057),.040,.035,"DARK","Y")
        drum("pack%d HV contact center %s"%(pack,side),
             (x,cy+.521,cz-.057),.019,.024,"BRUSH","Y",32)
        loop("pack%d flange seal %s"%(pack,side),
             (x,cy+.521,cz-.057),.031,.006,"SEAL","Y")
        xx=cx+side*.29
        block("pack%d visual keeper latch %s"%(pack,side),
              (xx,cy-.35,cz+.158),(.047,.082,.046),"ARMOR",.005)
    for xshift in (-.17,.17):
        block("pack%d polymer cooling port shield %s"%(pack,xshift),
              (cx+xshift,cy-.475,cz-.075),(.068,.023,.075),"DARK",.008)
    # Important: labels are placed on the real top panel using a shared
    # 512px digitally printed decal texture, not high-poly geometry bakes.
    block("pack%d embossed identification recess"%pack,
          (cx,cy-.050,cz+.206),(.29,.145,.006),"DARK",.002)

# Diagnostic power distribution cabinet and repairable upper access plates.
for i in range(6):
    z=.94+i*.152
    block("power service louver %d"%i,(1.62,.385,z),
          (.248,.016,.026),"DARK",.003)
    block("louver inner blade %d"%i,(1.62,.372,z),
          (.225,.013,.008),"BRUSH",.001)
for s in (-1,1):
    x=1.62+s*.115
    drum("radiator coolant coupling %s"%s,
         (x,.348,2.01),.032,.029,"BRUSH","Y",40)
    loop("coolant safety seal %s"%s,
         (x,.323,2.01),.030,.006,"SEAL","Y")
# HMI channel readouts and status lights, grounded in actual HMI placement.
for i in range(4):
    block("HMI diagnostic status row %d"%i,
          (1.35,-1.092,1.785+i*.068),
          (.17-.019*i,.010,.012),"CYAN" if i<3 else "AMBER",.001)
for i in range(3):
    drum("HMI machine-state indicator %d"%i,
         (1.615+i*.034,-1.093,1.766),.011,.011,
         "CYAN" if i==0 else "MARK","Y",24)

# Guard enclosure: discreet gasket clamps, hinge rails and clear service-view
# zone; retain approved R4 glass. We are NOT manufacturing a safety-rated cage.
for s in (-1,1):
    x=s*.055
    for z in (.62,1.22,2.03):
        block("front door gasket clamp %s %s"%(s,z),
              (x,-1.087,z),(.045,.045,.065),"STEEL",.005)
        drum("front door clamp hinge pin %s %s"%(s,z),
             (x,-1.116,z),.012,.021,"DARK","Y",24)
for s in (-1,1):
    for y in (-.83,.83):
        block("side panel captive shoe %s %s"%(s,y),
              (s*1.763,y,.38),(.073,.086,.052),"DARK",.008)

# Image-backed decals: repeatable surface labels on cassette and cabinet.
# Pure procedural authoring of a real 512x512 surface texture. No external
# assets. Dark image is NOT an AO or normal-map bake.
try:
    import numpy as np
except ImportError as exc:
    raise RuntimeError("Blender Python numpy required for actual texture production") from exc
N=512
pic=np.zeros((N,N,4),dtype=np.float32)
pic[:,:,:3]=(.036,.051,.059);pic[:,:,3]=1
# Band-stripe and diagnostic grid, with alpha unaffected (opaque)
for yy in range(70,122):
    for xx in range(58,456):
        if ((xx-58)//31)%2==0:
            pic[yy,xx,:3]=(.87,.34,.085)
for yy in [159,203,250,298,355,403]:
    pic[yy:yy+6,58:448,:3]=(.29,.45,.49)
for xx in [59,116,173,230,287,344,401,447]:
    pic[149:438,xx:xx+3,:3]=(.12,.23,.27)
for yy in range(390,429):
    for xx in range(305,442):
        if (xx//15)%2:pic[yy,xx,:3]=(.06,.55,.66)
texture=bpy.data.images.new("NF_BW01_R5_DECAL_PRINT",N,N,alpha=True)
texture.pixels.foreach_set(np.ascontiguousarray(pic).reshape(-1))
texture.filepath_raw=str(TEX/"NF_BW01_R5_MAINTENANCE_DECAL.png")
texture.file_format="PNG";texture.save()
texture.pack()
mat=bpy.data.materials.new("NF_BW01_R5 | UV-authored maintenance decal")
mat.use_nodes=True
nodes=mat.node_tree.nodes
base_shader=nodes.get("Principled BSDF")
base_shader.inputs["Metallic"].default_value=.0
base_shader.inputs["Roughness"].default_value=.60
image_node=nodes.new("ShaderNodeTexImage")
image_node.image=texture
mat.node_tree.links.new(image_node.outputs["Color"],base_shader.inputs["Base Color"])
# One small plaque on each battery and one on the cabinet.
# All planes use explicit 0..1 UV coordinates and normal pointing toward
# camera for this service/inspection sticker, so detail is real textured mesh.
def decal_plane(name,center,w,h):
    bpy.ops.mesh.primitive_plane_add(size=1,location=center)
    o=bpy.context.object;o.name="R5 | "+name
    o.dimensions=(w,h,0)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    # Plane normal +Z, horizontal above cassette
    adopt(o,mat)
    uv=o.data.uv_layers.active or o.data.uv_layers.new(name="UVMap")
    coords=[(0,0),(1,0),(1,1),(0,1)]
    for poly in o.data.polygons:
        for j,li in enumerate(poly.loop_indices):
            uv.data[li].uv=coords[j]
    return o
for tag,(cx,cy,cz) in enumerate(((-.17,-.25,1.115),(1.07,.31,1.195))):
    decal_plane("cassette service data plate %d"%tag,
                (cx,cy-.050,cz+.213),.258,.120)
decal_plane("cabinet service access diagram",
            (1.62,.68,2.255),.245,.145)

# Measured world bounds of added parts.
bpy.context.view_layer.update()
coords=[]
for o in COL.objects:
    if o.type not in {"MESH","CURVE","FONT"}:continue
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=ev.to_mesh()
    if mesh:
        coords.extend(ev.matrix_world@v.co for v in mesh.vertices)
        ev.to_mesh_clear()
bounds=[[min(c[i] for c in coords),max(c[i] for c in coords)] for i in range(3)]
if bounds[0][0]<-1.98 or bounds[0][1]>1.98 or bounds[1][0]<-1.29 or bounds[1][1]>1.29 or bounds[2][0]<-.03 or bounds[2][1]>3.43:
    raise RuntimeError("Out of bounds R5 detail "+str(bounds))
print("NF_BW01_R5_GEOMETRY_OK",len(COL.objects),bounds)

# This file is a reversible edit to a real R4 scene. The source .blend has not
# been changed in place; use the derivative output to continue work.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"NF_BW01_GATE04_R5_DETAILS.blend"),compress=True)
from_groups=("GATE03_LOD0","NF-BW01 R3 | Reversible mechanical refinement",
             "NF-BW01 R4 | Clear guard + industrial subassemblies")
export=[o for key in from_groups for o in bpy.data.collections[key].objects
        if o.type in {"MESH","CURVE","FONT"}]
export += [o for o in COL.objects if o.type in {"MESH","CURVE","FONT"}]
bpy.ops.object.select_all(action="DESELECT")
for o in export:o.select_set(True)
bpy.context.view_layer.objects.active=export[0]
bpy.ops.export_scene.gltf(filepath=str(OUT/"NF_BW01_GATE04_R5_REVIEW.glb"),
    export_format="GLB",use_selection=True,export_normals=True,
    export_texcoords=True,export_materials="EXPORT")
print("NF_BW01_R5_GLB_OK",len(export))
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1040;scene.render.resolution_y=780
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
camera=bpy.data.objects.get("Inspection orthographic")
if not camera:raise RuntimeError("Missing original inspection camera")
scene.camera=camera
R4=bpy.data.collections["NF-BW01 R3 | Reversible mechanical refinement"]
glazing=[o for o in R4.objects if o.type=="MESH" and
         any(t in o.name for t in ("clear guarding","safety glazing","sliding transparent gate"))]
if len(glazing)!=5:raise RuntimeError("Expected five original guard sheets")
views={
    "R5_FRONT_WITH_GLASS":((7,-10,7),(0,0,1.5),5.15,False),
    "R5_FRONT_OPEN_MECHANICAL":((7,-10,7),(0,0,1.5),5.15,True),
    "R5_GRIPPER_DETAIL":((1,-4,3.15),(-.25,-.21,2.12),1.58,True),
    "R5_BATTERY_CASSETTE":((3.6,-4.8,3.6),(-.12,-.15,1.12),2.38,True),
    "R5_CONTROL_CABINET":((4,-4,4),(1.48,.10,1.65),2.38,True),
}
for name,(eye,target,scale,open_cutaway) in views.items():
    for o in glazing:o.hide_render=open_cutaway
    camera.location=eye
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.type="ORTHO";camera.data.ortho_scale=scale
    scene.render.filepath=str(OUT/(name+".png"))
    bpy.ops.render.render(write_still=True)
    print("NF_BW01_R5_IMAGE_OK",name)
for o in glazing:o.hide_render=False
report={
    "asset":"NF-BW01","revision":"R5","gate":"04",
    "status":"MECHANICAL_TEXTURE_REVIEW_PENDING",
    "source":"published verified NF-BW01 R4 Blender master",
    "new_independent_objects":len(COL.objects),
    "new_texture":texture.name,
    "texture_kind":"true original surface-color print, NOT baked AO/normal geometry",
    "texture_resolution":[N,N],
    "bounds":bounds,
    "camera_views":list(views),
    "approval_pending":[
        "quality of close-up details and decal readability",
        "UV/bake coverage for all extra mesh in later optimization",
        "robot gripper actual mechanical clearance",
        "Unity URP transparency and material/texture importer review",
        "Android triangle/performance budget"],
    "full_detail_bake_complete":False,
    "unity_integrated":False
}
(OUT/"R5_REVIEW.json").write_text(json.dumps(report,indent=2))
print("NF_BW01_R5_BUILD_COMPLETE",len(COL.objects),len(views))
