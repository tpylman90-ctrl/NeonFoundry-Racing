"""NF-BW01 Aegis Battery Exchange Workstation -- GATE 02 high-poly review.

Blender 4.x headless, original geometry, no external models or paid assets.
Outputs editable master .blend + high-poly inspection-only GLB + actual geometry
clay/wire PNGs. Does NOT modify Unity or generate production textures.
Local axes: X=right, Y=rear, Z=up; front toward negative Y.
"""
import bpy
import math
import json
import sys
from mathutils import Vector
from pathlib import Path
from collections import Counter

OUT=Path(__file__).resolve().parent / "output"
if "--out" in sys.argv:
    OUT=Path(sys.argv[sys.argv.index("--out")+1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for coll in list(bpy.data.collections):
    if coll.name != bpy.context.scene.collection.name and coll.users == 0:
        bpy.data.collections.remove(coll)

def collection(name):
    c=bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c
STRUCT=collection("BW01_00 | Anchored foundations")
SHUTTLE=collection("BW01_10 | Linear cassette shuttle")
CASSETTE=collection("BW01_20 | Removable battery cassette")
ROBOT=collection("BW01_30 | Robot pedestal axes")
UPPER=collection("BW01_31 | Upper arm axis")
FORE=collection("BW01_32 | Forearm axis")
WRIST=collection("BW01_33 | Wrist and gripper axes")
RACK=collection("BW01_40 | Charged and spent cassette dock")
POWER=collection("BW01_50 | Power and coolant")
HMI=collection("BW01_60 | Operator diagnostic terminal")
GUARD=collection("BW01_70 | Protective motion envelope")
FACILITY=collection("BW01_80 | Facility conduit")
STUDIO=collection("_STUDIO | Rendering only")
TARGET=STRUCT

def set_group(g):
    global TARGET
    TARGET=g

def move_group(o):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    TARGET.objects.link(o)
    return o

def clay(name, rgba, metallic=0.0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgba,1.0)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*rgba,1)
    p.inputs["Metallic"].default_value=metallic
    p.inputs["Roughness"].default_value=.62
    return m

M={
"HOUSING":clay("CLAY | cast body",(.48,.51,.53)),
"STEEL":clay("CLAY | machined alloy",(.69,.72,.73)),
"BRUSH":clay("CLAY | brushed aluminum",(.79,.80,.79)),
"DARK":clay("CLAY | dark recess",(.15,.18,.21)),
"ARMOR":clay("CLAY | formed robot shell",(.60,.64,.66)),
"SEAL":clay("CLAY | gasket rubber",(.22,.25,.27)),
"MARK":clay("CLAY | indicator and caution marker",(.87,.86,.79)),
"GLAZE":clay("CLAY | recessed screen and safety cover",(.34,.43,.46)),
}

def assign(o,mat):
    o.data.materials.clear()
    o.data.materials.append(M[mat])
    return o

def normal(o,bevel=0.0,seg=3):
    if bevel>0:
        mod=o.modifiers.new("Radiused manufactured edges","BEVEL")
        mod.width=bevel
        mod.segments=seg
        if hasattr(mod,"affect"):
            mod.affect="EDGES"
        mod.loop_slide=True
        mod.profile=.65
    if o.type=="MESH" and hasattr(o.data,"use_auto_smooth"):
        o.data.use_auto_smooth=True
    mod=o.modifiers.new("Corner normals","WEIGHTED_NORMAL")
    mod.keep_sharp=True
    mod.weight=45
    return o

def box(name, center, dims, mat="STEEL", edge=.018, seg=3, rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    o=move_group(bpy.context.object)
    o.name=name
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rot is not None:
        o.rotation_euler=rot
    assign(o,mat)
    normal(o,edge,seg)
    return o

def cyl(name, center, radius, length, mat="STEEL", axis="Z", vertices=40, edge=.006):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=length,location=center)
    o=move_group(bpy.context.object)
    o.name=name
    if axis=="X":o.rotation_euler[1]=math.pi/2
    if axis=="Y":o.rotation_euler[0]=math.pi/2
    assign(o,mat)
    normal(o,edge,3)
    return o

def torus(name,center,radius,tube,mat="STEEL",axis="Z",segments=56):
    bpy.ops.mesh.primitive_torus_add(major_segments=segments,minor_segments=14,
        location=center,major_radius=radius,minor_radius=tube)
    o=move_group(bpy.context.object)
    o.name=name
    if axis=="X":o.rotation_euler[1]=math.pi/2
    if axis=="Y":o.rotation_euler[0]=math.pi/2
    assign(o,mat)
    for p in o.data.polygons:p.use_smooth=True
    return o

def beam(name,a,b,width,depth,mat="STEEL",edge=.013):
    """Real manufacturable connecting member with orientation derived from endpoints."""
    av,bv=Vector(a),Vector(b)
    d=bv-av
    L=d.length
    if L<.005:raise ValueError("Zero length beam: "+name)
    center=(av+bv)*.5
    o=box(name,center,(width,depth,L),mat,edge)
    o.rotation_euler=d.to_track_quat("Z","Y").to_euler()
    return o

def tapered_arm(name,a,b,widths,deps,mat="ARMOR",bevel=.022):
    """Eight-point cross sections with defined tapered ends, no blob-like primitives."""
    av,bv=Vector(a),Vector(b)
    d=bv-av
    L=d.length
    rot=d.to_track_quat("Z","Y")
    verts=[];faces=[]
    stations=[(0.0,widths[0],deps[0]),(.10,widths[1],deps[1]),
              (.83,widths[1]*.89,deps[1]*.93),(1.0,widths[2],deps[2])]
    for t,w,h in stations:
        # 8 point machined chamfered rectangle.
        corners=[(-w*.39,-h*.5),(w*.39,-h*.5),(w*.5,-h*.36),
                 (w*.5,h*.36),(w*.39,h*.5),(-w*.39,h*.5),
                 (-w*.5,h*.36),(-w*.5,-h*.36)]
        verts.extend([tuple(av+rot@Vector((x,y,t*L))) for x,y in corners])
    faces.append(tuple(reversed(range(8))))
    for row in range(3):
        for i in range(8):
            j=(i+1)%8
            faces.append((row*8+i,row*8+j,(row+1)*8+j,(row+1)*8+i))
    faces.append(tuple(24+i for i in range(8)))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh)
    TARGET.objects.link(o)
    assign(o,mat)
    normal(o,bevel,4)
    return o

def cable(name,points,diam=.025,mat="SEAL"):
    c=bpy.data.curves.new(name,"CURVE")
    c.dimensions="3D"
    c.resolution_u=18
    c.bevel_depth=diam*.5
    c.bevel_resolution=4
    spl=c.splines.new("BEZIER")
    spl.bezier_points.add(len(points)-1)
    for bp,xyz in zip(spl.bezier_points,points):
        bp.co=xyz
        bp.handle_left_type="AUTO"
        bp.handle_right_type="AUTO"
    o=bpy.data.objects.new(name,c)
    TARGET.objects.link(o)
    o.data.materials.append(M[mat])
    return o

def bolt(name,point,axis="Z",radius=.018):
    # Separate washer and hex head; instancing optimized later in Gate 03.
    a=cyl(name+" | gasket washer",point,radius*1.38,.012,"DARK",axis,24,.002)
    shift=Vector((0,0,.012)) if axis=="Z" else (Vector((.012,0,0)) if axis=="X" else Vector((0,.012,0)))
    cyl(name+" | hex fastener",Vector(point)+shift,radius,.020,"STEEL",axis,6,.001)

def lettering(name,text,location,size=.075,rot=None):
    cur=bpy.data.curves.new(name,"FONT")
    cur.body=text
    cur.size=size
    cur.extrude=.0008
    cur.bevel_depth=.0003
    o=bpy.data.objects.new(name,cur)
    TARGET.objects.link(o)
    o.location=location
    if rot is not None:o.rotation_euler=rot
    o.data.materials.append(M["DARK"])
    return o

def joint(name,p,radius=.18,axis="Y"):
    cyl(name+" | through bearing",p,radius,.34,"DARK",axis,48,.008)
    cyl(name+" | machined face",p,radius*.84,.365,"STEEL",axis,48,.008)
    # rings sit slightly above the bearing face on either side
    for sign in (-1,1):
        delta=.194*sign
        x,y,z=p
        xyz=(x+delta,y,z) if axis=="X" else ((x,y+delta,z) if axis=="Y" else (x,y,z+delta))
        torus(name+" | rotational race",xyz,radius*.69,.016,"BRUSH",axis)
        for i in range(8):
            a=math.tau*i/8
            if axis=="Y":v=(x+math.cos(a)*radius*.64,y+delta,z+math.sin(a)*radius*.64)
            elif axis=="X":v=(x+delta,y+math.cos(a)*radius*.64,z+math.sin(a)*radius*.64)
            else:v=(x+math.cos(a)*radius*.64,y+math.sin(a)*radius*.64,z+delta)
            bolt(name+" | bearing cover",v,axis,.011)

def pivot(name,at):
    o=bpy.data.objects.new(name,None)
    TARGET.objects.link(o)
    o.location=at
    o.empty_display_type="ARROWS"
    o.empty_display_size=.20
    return o

def put_under(child,parent):
    """Preserve world transforms on Blender 4.0 and 4.3+ during pivot parenting.

    The evaluation graph must update before measuring and after assigning
    the parent inverse. Reassigning only matrix_world is not deterministic
    across Blender versions.
    """
    bpy.context.view_layer.update()
    original=child.matrix_world.copy()
    child.parent=parent
    child.matrix_parent_inverse=parent.matrix_world.inverted_safe()
    bpy.context.view_layer.update()
    delta=(child.matrix_world.translation-original.translation).length
    if delta>.001:
        raise RuntimeError("Parenting changed world position of "+child.name+": "+str(delta))

# foundation: directional cast plinth, narrow vertical fins, accessible anchor points
set_group(STRUCT)
box("BW01_00 | welded foundation 3.64x2.24",(0,0,.085),(3.64,2.24,.17),"HOUSING",.062,5)
box("BW01_00 | floating top plate",(0,-.035,.192),(3.47,2.08,.078),"BRUSH",.023)
for x in (-1.70,1.70):
    for y in (-.99,.99):
        box("BW01_00 | machined sole plate",(x,y,.045),(.37,.34,.080),"DARK",.012)
        for dx in (-.110,.110):
            bolt("BW01_00 | anchored fixing", (x+dx,y,.095),"Z",.020)
for x in (-1.79,1.79):
    box("BW01_00 | outer rail bumper",(x,0,.270),(.074,2.11,.12),"SEAL",.013)
for y in (-1.075,1.075):
    box("BW01_00 | underside aluminum skirt",(0,y,.19),(3.30,.05,.10),"STEEL",.010)
for x in (-1.22,-.89,-.56):
    box("BW01_00 | milled maintenance access", (x,-.97,.231),(.19,.11,.020),"DARK",.006)
for y in (-.62,-.31,.0,.31,.62):
    box("BW01_00 | upper anti-slip rib",(1.48,y,.246),(.25,.065,.015),"DARK",.004)

# precision shuttle/cradle: intentionally open, not a solid centered box
set_group(SHUTTLE)
for x in (-.69,.35):
    box("BW01_10 | twin guide rail extrusion",(x,-.28,.595),(.110,1.62,.16),"STEEL",.014)
    box("BW01_10 | floating bearing rail",(x,-.28,.690),(.068,1.52,.040),"BRUSH",.009)
    for y in (-.90,-.55,-.20,.15,.49):
        bolt("BW01_10 | rail mount bolt",(x,y,.718),"Z",.012)
for y in (-1.02,.44):
    box("BW01_10 | front/rear end stop",(-.17,y,.70),(1.27,.14,.29),"HOUSING",.022)
    for x in (-.60,.27):
        cyl("BW01_10 | elastomer bump stop",(x,y,.765),.085,.10,"SEAL","Y",32,.013)
box("BW01_10 | guided open shuttle tray",(-.17,-.26,.802),(1.12,1.34,.102),"ARMOR",.032)
box("BW01_10 | central gasket inset",(-.17,-.26,.871),(.90,1.13,.048),"DARK",.025)
for x in (-.66,.32):
    box("BW01_10 | paired side retention shoe",(x,-.25,.94),(.093,.82,.116),"STEEL",.016)
    for y in (-.58,.08):
        box("BW01_10 | captive latch dog",(x,y,1.013),(.13,.20,.075),"DARK",.012)
        cyl("BW01_10 | release pivot pin",(x,y,1.067),.035,.04,"STEEL",vertices=24)
# lead screw and bearing under sliding table
cyl("BW01_10 | enclosed drive screw",(-.17,-.24,.516),.055,1.48,"STEEL","Y",32,.003)
for y in (-.83,.30):
    cyl("BW01_10 | drive screw pillow bearing",(-.17,y,.516),.120,.160,"HOUSING","Y",32,.008)
box("BW01_10 | drive motor guard",(-.17,.61,.50),(.38,.40,.29),"DARK",.026)
for x in (-.69,.35):
    for y in (-.77,.22):
        box("BW01_10 | floating return spring",(x,y,.61),(.16,.21,.14),"HOUSING",.013)

# battery cassette: standalone high-poly prop and real socket faces
def build_cassette(center,tag):
    x,y,z=center
    base=box(tag+" | insulated outer shell",(x,y,z),(.68,.86,.34),"HOUSING",.044,5)
    box(tag+" | sealed service top",(x,y,z+.174),(.58,.75,.030),"BRUSH",.009)
    for dx in (-.305,.305):
        box(tag+" | protective rib",(x+dx,y,z),(.050,.78,.35),"STEEL",.014)
        # separate tool sockets aligned to jaws
        box(tag+" | keyed gripper cup",(x+dx,y-.34,z+.09),(.055,.095,.095),"DARK",.009)
    for dy in (-.36,.36):
        box(tag+" | molded terminal lip",(x,y+dy,z+.08),(.54,.045,.16),"DARK",.008)
    for iy in (-.20,-.05,.10,.25):
        box(tag+" | cooling spine groove",(x,y+iy,z+.198),(.43,.025,.008),"DARK",.003)
    box(tag+" | insulated docking nose",(x,y+.45,z-.042),(.36,.12,.16),"DARK",.014)
    for dx in (-.13,.13):
        cyl(tag+" | keyed bus terminal",(x+dx,y+.522,z-.055),.042,.075,"STEEL","Y",20,.005)
    for dx in (-.20,.20):
        for dy in (-.28,.28):
            bolt(tag+" | captive shell bolt",(x+dx,y+dy,z+.193),"Z",.012)
    lettering(tag+" | stamped ID","NF / C-72",(x-.23,y-.28,z+.196),.070)
    return base
set_group(CASSETTE)
build_cassette((-.17,-.25,1.115),"BW01_20")

# six-axis-inspired robotic manipulator, pivot markers stay independently editable
set_group(ROBOT)
p0=(-1.10,.57,1.090)
p1=(-1.40,.48,1.825)
p2=(-.88,.20,2.530)
p3=(-.25,-.21,2.350)
box("BW01_30 | foundation pedestal",(-1.11,.56,.475),(.71,.67,.61),"HOUSING",.092,5)
box("BW01_30 | pedestal right drive cover",(-.74,.56,.49),(.13,.54,.42),"ARMOR",.043)
for px in (-1.40,-.81):
    for py in (.28,.84):
        bolt("BW01_30 | pedestal structural anchor",(px,py,.80),"Z",.020)
cyl("BW01_30 | turntable gear mantle",(-1.11,.56,.85),.302,.144,"DARK",vertices=56,edge=.015)
torus("BW01_30 | ring bearing",(-1.11,.56,.95),.260,.033,"BRUSH")
cyl("BW01_30 | turret neck",(-1.10,.56,1.035),.225,.145,"ARMOR",vertices=48,edge=.022)
base_pivot=pivot("PIVOT | Axis 1 yaw Z",(-1.11,.56,.87))
# shoulder
set_group(UPPER)
joint("BW01_31 | shoulder Y-axis",p0,.247,"Y")
upper=tapered_arm("BW01_31 | tapered cast upper arm",p0,p1,
                  (.33,.33,.29),(.32,.36,.31),"ARMOR",.034)
beam("BW01_31 | rear kinematic linkage",(-1.28,.70,1.20),(-1.58,.68,1.76),.068,.080,"STEEL",.012)
box("BW01_31 | shoulder gear cover",(-1.09,.70,1.10),(.26,.072,.23),"HOUSING",.031)
for i in range(5):
    t=.20+i*.14
    v=Vector(p0).lerp(Vector(p1),t)
    beam("BW01_31 | formed stiffness rib",
         (v.x+.118,v.y-.11,v.z),(v.x+.118,v.y+.12,v.z),.016,.026,"STEEL",.003)
sh_pivot=pivot("PIVOT | Axis 2 shoulder Y",p0)
# elbow and forearm
set_group(FORE)
joint("BW01_32 | elbow hinge Y-axis",p1,.215,"Y")
tapered_arm("BW01_32 | extruded forearm structure",p1,p2,
            (.29,.27,.22),(.29,.30,.26),"ARMOR",.029)
beam("BW01_32 | actuation tie rod",(-1.26,.71,1.93),(-.84,.40,2.43),.060,.064,"STEEL",.012)
for i in range(4):
    q=Vector(p1).lerp(Vector(p2),.25+i*.16)
    torus("BW01_32 | hose cinch collar",(q.x,q.y,q.z),.108,.012,"DARK","Y",32)
el_pivot=pivot("PIVOT | Axis 3 elbow Y",p1)
# wrist and gripper complete kinematic path
set_group(WRIST)
joint("BW01_33 | roll drive at wrist",p2,.135,"X")
tapered_arm("BW01_33 | sealed distal wrist",p2,p3,
            (.22,.19,.18),(.25,.21,.20),"STEEL",.020)
cyl("BW01_33 | tool rotating coupling",p3,.125,.27,"DARK","Z",40,.01)
torus("BW01_33 | tool bearing race",(p3[0],p3[1],p3[2]-.132),.117,.018,"BRUSH","Z")
box("BW01_33 | toolhead crossbeam",(-.25,-.21,2.186),(.68,.20,.17),"HOUSING",.035)
for side in (-1,1):
    gx=-.25+side*.30
    box("BW01_33 | opposing linear jaw housing",(gx,-.21,2.135),(.14,.26,.25),"STEEL",.022)
    box("BW01_33 | inserted gripping finger",(gx,-.18,1.975),(.075,.095,.30),"BRUSH",.012)
    box("BW01_33 | soft toolpad",(gx,-.18,1.83),(.088,.11,.045),"SEAL",.008)
    for yi in (-.28,-.14):
        bolt("BW01_33 | jaw bolt",(gx,yi,2.269),"Z",.013)
wrist_pivot=pivot("PIVOT | Axis 4/5 wrist X/Z",p2)
tool_pivot=pivot("PIVOT | Axis 6 gripper Z",p3)
# flexible wire loom sweeps through bearings and is attached through actual collars
set_group(ROBOT)
cable("BW01_30 | cable loom from pedestal",
      [(-1.13,.82,.66),(-1.28,.90,1.16),(-1.66,.70,1.67),
       (-1.55,.69,2.08),(-1.05,.46,2.62),(-.74,.29,2.56)],.061,"SEAL")
cable("BW01_30 | parallel signal sheath",
      [(-1.03,.83,.68),(-1.15,.93,1.20),(-1.49,.77,1.62),
       (-1.49,.77,2.10),(-1.05,.53,2.64),(-.73,.36,2.55)],.026,"DARK")
for p in [(-1.28,.87,1.18),(-1.52,.73,1.70),(-1.48,.72,2.09),(-.96,.48,2.60)]:
    box("BW01_30 | fixed loom clamp",p,(.20,.08,.10),"STEEL",.014)

# receiving/replacement cassette dock, spaced two positions vertically
set_group(RACK)
rx=1.07;ry=.31
for sx in (-.47,.47):
    box("BW01_40 | dock upright",(rx+sx,ry,.94),(.075,.92,1.48),"STEEL",.018)
for y in (ry-.43,ry+.43):
    box("BW01_40 | upright lateral brace",(rx,y,.97),(1.05,.060,1.51),"DARK",.008)
for level in (.53,1.18):
    box("BW01_40 | receiver shelf",(rx,ry,level-.18),(.94,1.01,.08),"HOUSING",.016)
    for sx in (-.32,.32):
        box("BW01_40 | spring guide channel",(rx+sx,ry,level-.08),(.070,.96,.090),"BRUSH",.008)
        for y in (ry-.35,ry+.35):
            bolt("BW01_40 | cassette stop latch",(rx+sx,y,level-.025),"Z",.014)
    box("BW01_40 | status lamp socket",(rx,ry-.54,level+.07),(.40,.062,.07),"DARK",.011)
    for j in range(4):
        box("BW01_40 | status diode",(rx-.13+j*.09,ry-.574,level+.07),(.035,.010,.025),"MARK",.004)
# one stored charged pack, independent from active cassette
set_group(CASSETTE)
build_cassette((rx,ry,1.195),"BW01_20 | stored charged cassette")

# DC power and coolant cabinet: proper panel recess / cooling fins / service doors
set_group(POWER)
cx=1.62;cy=.70
box("BW01_50 | standing DC-link shell",(cx,cy,1.14),(.47,.52,2.22),"HOUSING",.053,5)
box("BW01_50 | hinged front access panel",(cx,cy-.278,1.18),(.40,.035,1.81),"ARMOR",.018)
box("BW01_50 | panel perimeter gasket",(cx,cy-.302,1.18),(.37,.016,1.76),"DARK",.011)
box("BW01_50 | access inset steel cover",(cx,cy-.312,1.18),(.33,.017,1.71),"STEEL",.009)
for iz in range(7):
    z=.70+iz*.177
    box("BW01_50 | front radiator port",(cx,cy-.332,z),(.24,.010,.067),"DARK",.005)
    box("BW01_50 | rib within cutout",(cx,cy-.344,z),(.188,.008,.023),"BRUSH",.004)
box("BW01_50 | cooling hose terminal",(cx,cy-.30,2.04),(.31,.07,.11),"DARK",.018)
for x in (cx-.16,cx+.16):
    for z in (.38,1.79):
        bolt("BW01_50 | cabinet service fastener",(x,cy-.363,z),"Y",.016)
box("BW01_50 | side heatsink spine",(cx-.269,cy,1.46),(.070,.47,1.05),"BRUSH",.016)
for z in (.97,1.12,1.27,1.42,1.57,1.72,1.87):
    box("BW01_50 | heat exchange blade",(cx-.312,cy,z),(.115,.43,.030),"STEEL",.008)
for i in range(2):
    y=.51+i*.18
    cyl("BW01_50 | coolant flanged port",(cx-.245,y,2.00),.06,.12,"DARK","X",24,.008)

# front visible human diagnostics screen
set_group(HMI)
box("BW01_60 | equipment mast",(1.46,-.82,.93),(.15,.18,1.60),"STEEL",.031)
box("BW01_60 | display gearbox",(1.46,-.82,1.77),(.37,.22,.26),"HOUSING",.031)
box("BW01_60 | bezelled tilted HMI",(1.45,-.96,1.87),(.61,.12,.50),"DARK",.034,4,rot=(math.radians(17),0,0))
box("BW01_60 | inset HMI monitor",(1.45,-1.026,1.87),(.52,.020,.39),"GLAZE",.020,3,rot=(math.radians(17),0,0))
for row in range(3):
    box("BW01_60 | screen menu strip",(1.30,-1.045,1.76+row*.092),(.20,.008,.018),"STEEL",.003)
for i in range(3):
    cyl("BW01_60 | tactile selection button",(1.40+i*.085,-1.055,1.65),.022,.020,"MARK","Y",20,.004)
cyl("BW01_60 | emergency stop pushbutton",(1.70,-.94,1.55),.067,.082,"DARK","Y",28,.008)
torus("BW01_60 | E-stop bezel",(1.70,-.99,1.55),.077,.010,"STEEL","Y",40)
lettering("BW01_60 | local face engraving","AEGIS / 01",(1.21,-1.049,1.995),.055,
          (math.pi/2,0,0))

# guard frame; sparse open center for clay review, removable safety planes later
set_group(GUARD)
for gx in (-1.78,1.78):
    for gy in (-1.05,1.05):
        box("BW01_70 | grounded steel shield post",(gx,gy,1.25),(.065,.065,2.45),"STEEL",.012)
        box("BW01_70 | post footplate",(gx,gy,.234),(.155,.155,.065),"DARK",.014)
        bolt("BW01_70 | post anchor",(gx,gy,.276),"Z",.012)
for gx in (-1.78,1.78):
    beam("BW01_70 | upper perimeter top rail",(gx,-1.05,2.49),(gx,1.05,2.49),.068,.066,"BRUSH",.013)
# rear rail, front intentionally open only for concept and visibility; requires interlocked gate later
beam("BW01_70 | overhead boundary crossbar",(-1.78,1.05,2.49),(1.78,1.05,2.49),.068,.068,"BRUSH",.011)
for gx in (-1.78,1.78):
    for gz in (.50,1.50,2.30):
        box("BW01_70 | guarded motion cue strip",(gx,-1.05,gz),(.075,.035,.065),"MARK",.005)
# Facilities conduits: physically routed and bracketed, not dangling hoses
set_group(FACILITY)
box("BW01_80 | rear cable bridge",(0,1.01,.34),(3.20,.20,.23),"DARK",.032)
for x in (-1.35,-.67,.32,1.45):
    box("BW01_80 | individually clamped DC bus",(x,1.042,.48),(.080,.20,.12),"STEEL",.012)
for x in (1.35,1.49):
    cable("BW01_80 | high-voltage conduit",
        [(x,.91,2.21),(x,.97,2.39),(x,1.13,2.44),(x,1.17,2.21)],.045,"SEAL")
for side in (-1,1):
    sx=side*1.72
    for y in (-.78,.78):
        box("BW01_80 | shield retainer",(sx,y,2.47),(.15,.14,.10),"DARK",.010)

# Hierarchy in Outliner, with real individual edit-friendly pivots
# Only physically related arm components are parented; avoid scene-wide collapsing.
for group,root in ((UPPER,sh_pivot),(FORE,el_pivot),(WRIST,wrist_pivot)):
    for obj in list(group.objects):
        if obj != root and obj.type in {"MESH","CURVE","FONT"}:
            put_under(obj,root)

# bounds stats & invariant checks
machine_collections=[STRUCT,SHUTTLE,CASSETTE,ROBOT,UPPER,FORE,WRIST,RACK,POWER,HMI,GUARD,FACILITY]
meshes=[]
for coll in machine_collections:
    for o in coll.objects:
        if o.type in {"MESH","CURVE","FONT"}:
            meshes.append(o)
if len(meshes)<70:
    raise RuntimeError("Missing detailed assemblies: only %d objects"%len(meshes))

def visible_bounds(objects):
    """Audit the actual renderable geometry, not curve control-handle bounds.

    Blender 4.3 reports the Bezier handle control polygon as the object bound;
    that includes unused handle locations far beyond the swept cable. Convert
    each evaluated object to a mesh and inspect its real vertices instead.
    """
    bpy.context.view_layer.update()
    coords=[]
    dg=bpy.context.evaluated_depsgraph_get()
    for o in objects:
        ev=o.evaluated_get(dg)
        if ev.type not in {"MESH","CURVE","FONT"}:
            continue
        shape=ev.to_mesh()
        if shape is None:
            raise RuntimeError("Could not evaluate actual mesh for bounds: "+o.name)
        for v in shape.vertices:
            coords.append(ev.matrix_world @ v.co)
        ev.to_mesh_clear()
    if not coords:
        raise RuntimeError("No evaluated real geometry for dimensional audit")
    a=[min(v[i] for v in coords) for i in range(3)]
    b=[max(v[i] for v in coords) for i in range(3)]
    return a,b,[b[i]-a[i] for i in range(3)]

bmin,bmax,dims=visible_bounds(meshes)
print("NF_BW01_MODEL_BOUNDS",bmin,bmax,dims)
if bmin[0]<-1.97 or bmax[0]>1.97 or bmin[1]<-1.29 or bmax[1]>1.29 or bmin[2]<-.04 or bmax[2]>3.43:
    for obj in meshes:
        lo,hi,_=visible_bounds([obj])
        if lo[0]<-1.97 or hi[0]>1.97 or lo[1]<-1.29 or hi[1]>1.29 or lo[2]<-.04 or hi[2]>3.43:
            print("NF_BW01_BOUND_OFFENDER",obj.name,obj.type,
                  "parent",obj.parent.name if obj.parent else "NONE",
                  "min",lo,"max",hi)
    raise RuntimeError("Gate02 model violates approved 3.8 x 2.4 x 3.4m envelope; review oversized component")

# Save an editable real Blender scene with separate assemblies, no destructive joins.
scene=bpy.context.scene
scene.unit_settings.system="METRIC"
scene.unit_settings.scale_length=1.0
scene.render.engine="BLENDER_WORKBENCH"
world=bpy.data.worlds.new("Studio neutral environment")
scene.world=world
set_group(STUDIO)
# Studio contact-shadow floor isn't part of the asset export.
box("_STUDIO | matte backdrop", (0,0,-.089), (5.9,5.5,.12),"HOUSING",.0)
cam_data=bpy.data.cameras.new("Inspection orthographic")
cam_obj=bpy.data.objects.new("Inspection orthographic",cam_data)
STUDIO.objects.link(cam_obj)
scene.camera=cam_obj
cam_data.type="ORTHO"
cam_data.lens=55
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type="BOTH"
scene.display.shading.curvature_ridge_factor=1.35
scene.display.shading.curvature_valley_factor=1.15
scene.display.shading.show_object_outline=True
scene.render.resolution_x=1400
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False

# Materials are clay-only despite being distinguishable in grayscale.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"NF_BW01_GATE02_HIGH_POLY_MASTER.blend"),
                           compress=True)
print("NF_BW01_MASTER_SAVED",OUT/"NF_BW01_GATE02_HIGH_POLY_MASTER.blend")

# Inspection-only GLB from same real geometry, not an optimized production mesh.
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
bpy.ops.export_scene.gltf(
    filepath=str(OUT/"NF_BW01_GATE02_INSPECTION_ONLY.glb"),
    export_format="GLB",use_selection=True,
    export_apply=False,export_normals=True,
    export_materials="EXPORT")
print("NF_BW01_INSPECTION_GLB_OK")

# Model-only artifact is intentionally independent of headless viewport rendering.
# It preserves the actual editable .blend and inspection GLB even if OpenGL is
# unavailable on a CI runner. Clay/wire images are still required for Gate 02
# *visual* approval.
if "--master-only" in sys.argv:
    master_manifest={
        "asset_id":"NF-BW01",
        "gate":"02",
        "status":"MASTER_AND_INSPECTION_GLB_BUILT_VISUAL_RENDERS_PENDING",
        "owner_approval_gate_01":"2026-11-23: Looks good proceed",
        "unit":"m","front_axis":"-Y","up_axis":"+Z",
        "bounds_min_m":bmin,"bounds_max_m":bmax,"dimensions_m":dims,
        "object_count":len(meshes),
        "high_poly_master":"NF_BW01_GATE02_HIGH_POLY_MASTER.blend",
        "inspection_glb":"NF_BW01_GATE02_INSPECTION_ONLY.glb",
        "game_ready":False,"owner_gate02_approved":False,
        "notes":["True Blender high-poly source and derivative GLB. No production UV/PBR/LOD.",
                 "Visual images are required before gate 02 can be accepted.",
                 "Robot kinematic and collision clearances not yet validated."]
    }
    (OUT/"model_manifest.json").write_text(json.dumps(master_manifest,indent=2))
    print("NF_BW01_GATE02_MASTER_PACKAGE_OK",len(meshes))
    raise SystemExit(0)

def position_camera(eye,target,scale=5.0):
    cam_obj.location=eye
    cam_obj.rotation_euler=(Vector(target)-cam_obj.location).to_track_quat("-Z","Y").to_euler()
    cam_data.ortho_scale=scale

views={
 "01_front_clay":((0,-10,1.70),(0,0,1.65),4.55),
 "02_rear_clay":((0,10,1.70),(0,0,1.65),4.55),
 "03_left_clay":((-10,0,1.70),(0,0,1.65),4.55),
 "04_right_clay":((10,0,1.70),(0,0,1.65),4.55),
 "05_top_clay":((0,0,10),(0,0,1.10),4.50),
 "06_underside_clay":((0,0,-10),(0,0,1.15),4.50),
 "07_front_three_quarter_clay":((7,-10,7),(0,0,1.50),5.15),
 "08_rear_three_quarter_clay":((-7,9,6),(0,0,1.50),5.15),
 "09_robot_joint_closeup":((-4,-5,4.8),(-.92,.46,1.93),2.35),
 "10_cradle_dock_closeup":((4,-6,4.0),(.12,-.12,.87),2.70),
}
for key,(eye,target,scale) in views.items():
    position_camera(eye,target,scale)
    scene.render.filepath=str(OUT/(key+".png"))
    bpy.ops.render.render(write_still=True)
    print("NF_BW01_RENDER_OK",key)
# Workbench Scene shading in Debian Blender 4.0 has no show_wireframes flag.
# Generate TRUE geometry-edge overlays from the actual master geometry instead.
# Do this only after saving the editable source + all clay renders.
wire_overlays=[]
for source in list(meshes):
    if source.type!="MESH":
        continue
    # Fasteners create high-frequency wire noise; they remain editable in master.
    if any(word in source.name.lower() for word in (
        "washer","hex fastener","captive shell bolt","mount bolt",
        "bearing cover","indicator","status diode","status strip")):
        continue
    outline=source.copy()
    outline.data=source.data.copy()
    STUDIO.objects.link(outline)
    outline.name="_STUDIO | TRUE mesh wire | "+source.name
    outline.data.materials.clear()
    outline.data.materials.append(M["DARK"])
    wire=outline.modifiers.new("Actual topology edge inspection","WIREFRAME")
    wire.use_replace=True
    wire.thickness=.0033
    wire.offset=.18
    wire.use_even_offset=True
    wire_overlays.append(outline)
print("NF_BW01_TRUE_MESH_WIRE_OVERLAYS",len(wire_overlays))
for key,(eye,target,scale) in {
    "11_front_wire":views["01_front_clay"],
    "12_three_quarter_wire":views["07_front_three_quarter_clay"],
    "13_robot_wire":views["09_robot_joint_closeup"],
}.items():
    position_camera(eye,target,scale)
    scene.render.filepath=str(OUT/(key+".png"))
    bpy.ops.render.render(write_still=True)
    print("NF_BW01_RENDER_OK",key)
# Inspection-only overlays are not part of the saved source or GLB.
for obj in wire_overlays:
    bpy.data.objects.remove(obj,do_unlink=True)

# count explicit evaluated polygons, record evidence without false runtime claims
dg=bpy.context.evaluated_depsgraph_get()
evaluated_triangles=0
for o in meshes:
    if o.type=="MESH":
        evaluated=o.evaluated_get(dg).to_mesh()
        evaluated.calc_loop_triangles()
        evaluated_triangles+=len(evaluated.loop_triangles)
        o.evaluated_get(dg).to_mesh_clear()

manifest={
 "asset_id":"NF-BW01",
 "revision":"Gate02-v01",
 "gate":"02",
 "status":"ACTUAL_BLENDER_MODEL_BUILT_VISUAL_APPROVAL_PENDING",
 "owner_approval_gate_01":"2026-11-23: Looks good proceed",
 "source":"Blender self-authored original geometry, no third-party meshes",
 "engine":"Blender 4.x",
 "unit":"m",
 "front_axis":"-Y",
 "up_axis":"+Z",
 "bounds_min_m":bmin,
 "bounds_max_m":bmax,
 "dimensions_m":dims,
 "object_count":len(meshes),
 "evaluated_render_triangles_approx":evaluated_triangles,
 "components":{c.name:len([o for o in c.objects if o.type in {"MESH","CURVE","FONT"}]) for c in machine_collections},
 "inspection_only":True,
 "game_ready":False,
 "high_poly_master":"NF_BW01_GATE02_HIGH_POLY_MASTER.blend",
 "inspection_glb":"NF_BW01_GATE02_INSPECTION_ONLY.glb",
 "renders":list(views.keys())+["11_front_wire","12_three_quarter_wire","13_robot_wire"],
 "notes":[
   "Actual Blender high-poly meshes with independent modules and edit pivots",
   "Neutral studio clay only. PBR/UV/LOD belongs to later gates",
   "Robot kinematic reach/collisions not verified. Display pose only",
   "Safety frame conceptual: interlocked mechanical enclosure not finalized",
   "No Unity garage integration, no APK, no mobile performance claim"
 ]
}
(OUT/"model_manifest.json").write_text(json.dumps(manifest,indent=2))
print("NF_BW01_GATE02_RENDER_PACKAGE_OK",len(meshes),evaluated_triangles)
