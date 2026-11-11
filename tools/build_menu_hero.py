"""Generate an original premium 3D hero menu in Blender 4.5.

Output:
 game/assets/menu/launch_scene.png   pre-rendered Android backdrop
 build/menu_hero.blend               editable authored Blender scene
The hero is a menu *presentation model*, not a finished playable garage craft.
All geometry is made in Blender; no reference game art is redistributed.
"""
import bpy
import math
import os
import random
from mathutils import Vector

random.seed(1905)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
GAME = os.path.join(OUT, "game", "assets", "menu")
BUILD = os.path.join(OUT, "build")
os.makedirs(GAME, exist_ok=True)
os.makedirs(BUILD, exist_ok=True)

def mat(name, color, metallic=0.0, roughness=0.5, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    if emit is not None:
        bs.inputs["Emission Color"].default_value = (*emit, 1)
        bs.inputs["Emission Strength"].default_value = strength
    return m

NIGHT = mat("01 · graphite titanium", (0.024,0.044,0.077), .88,.24)
GUN = mat("02 · satin machined gunmetal", (.082,.11,.155), .8,.32)
BLUE = mat("03 · lacquered deep petrol", (.014,.13,.23), .72,.19)
SILVER = mat("04 · milled light titanium", (.32,.45,.51), .88,.23)
GLASS = mat("05 · sealed blue-black canopy", (.014,.072,.105), .48,.09)
DARK = mat("06 · intake darkness", (.005,.012,.025), .45,.37)
ORANGE = mat("07 · hot copper anodized", (.74,.24,.08), .72,.25)
CYAN_L = mat("08 · cyan energy", (.02,.38,.56), .12,.19, (.09,.72,1), 8.0)
CYAN_SOFT = mat("09 · soft aqua", (.02,.24,.29), .1,.35, (.045,.37,.48), 2.5)
AMBER_L = mat("10 · amber racing light", (.69,.14,.03), .15,.24, (1,.19,.044), 9.0)
WINDOWS = mat("11 · distant cool windows", (.045,.1,.17), .1,.2, (.09,.47,.9), 3.3)
PINK_L = mat("12 · rose windows", (.35,.03,.19), .1,.2, (.8,.09,.4), 4.8)
CONCRETE = mat("13 · carbon deck", (.035,.051,.07), .62,.34)
STEEL_D = mat("14 · architectural graphite", (.015,.025,.052), .35,.52)
CITY_BLUE = mat("15 · rainy city blue", (.015,.042,.091), .43,.43)
CITY_GRAY = mat("16 · city secondary", (.035,.06,.095), .35,.47)

def cube(name, location, scale, material, bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    o.name = name
    if parent:
        o.parent = parent
    o.location = location
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b = o.modifiers.new("Machined radius", "BEVEL")
        b.width = bevel
        b.segments = 2
        n = o.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
        n.keep_sharp = True
    o.data.materials.append(material)
    return o

def circle(name, location, radius, depth, material, axis='Z', vertices=48, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth)
    o = bpy.context.object
    o.name = name
    if parent:
        o.parent = parent
    o.location = location
    if axis == 'Y':
        o.rotation_euler.x = math.pi / 2
    o.data.materials.append(material)
    b = o.modifiers.new("Machined edge", "BEVEL")
    b.width = min(.045, depth*.15)
    b.segments = 2
    o.modifiers.new("Face normals", "WEIGHTED_NORMAL")
    return o

def ring(name, location, major, minor, material, orient='Z', parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                    major_segments=48, minor_segments=8)
    o = bpy.context.object
    o.name = name
    if parent:
        o.parent = parent
    o.location = location
    if orient == 'Y':
        o.rotation_euler.x = math.pi/2
    o.data.materials.append(material)
    for face in o.data.polygons:
        face.use_smooth = True
    return o

def path(name, points, material, thickness=.035, resolution=2):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 2
    curve.bevel_depth = thickness
    curve.bevel_resolution = 3
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for i, p in enumerate(points):
        spline.points[i].co = (*p,1)
    o = bpy.data.objects.new(name,curve)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    return o

def section_mesh(name, rings, material, parent=None):
    # Each ring = (y, halfwidth, upper_z, lower_z, xcenter).
    verts=[]
    for y, half, upper, lower, xcenter in rings:
        verts += [(xcenter-half,y,upper),(xcenter+half,y,upper),
                  (xcenter-half,y,lower),(xcenter+half,y,lower)]
    faces=[]
    for i in range(len(rings)-1):
        a=i*4;b=(i+1)*4
        faces += [(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),
                  (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)]
    faces += [(0,1,3,2)]
    k=(len(rings)-1)*4
    faces += [(k+2,k+3,k+1,k)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    o=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(o)
    if parent:o.parent=parent
    mesh.materials.append(material)
    bevel=o.modifiers.new("Precision panels", "BEVEL")
    bevel.width=.042
    bevel.segments=2
    o.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return o

# An architectural launch platform that reads as *physical geometry* from
# the chase angle. The wet-look glossy deck reflects craft exhaust.
cube("Floating launch deck | hull", (5.0,0.3,1.65),(16.5,15.5,1.15), NIGHT,.18)
cube("Floating launch deck | inlaid metal", (5.0,0.3,2.24),(15.95,15.0,.06), CONCRETE,.08)
for i in range(15):
    x=-2.5+i*1.05
    cube("Panel seam %02d"%i,(x,.25,2.277),(.016,14.7,.009),GUN)
for j in range(11):
    y=-6.9+j*1.32
    cube("Panel cross seam %02d"%j,(5.0,y,2.28),(15.7,.016,.008),GUN)
for x, color in [(-3.05,AMBER_L),(13.04,CYAN_L)]:
    path("Raised optic edge",[(x,-7.15,2.44),(x,7.4,2.44)],color,.038)
    for yy in range(-6,7,2):
        cube("Rim light socket",(x,yy,2.36),(.13,.35,.025),color,.013)
for y in [-7.23,7.42]:
    path("Launch rim / crossbeam",[(-3.07,y,2.44),(13.06,y,2.44)],CYAN_SOFT,.025)
for x in [-1.3,1.1,3.5,5.9,8.3,10.7]:
    cube("Under deck I-beam",(x,0.25,.65),(.18,17.4,.45),GUN,.02)
for i in range(9):
    xx=-2.4+i*1.89
    path("Deck underglow",[(xx,-7.65,1.0),(xx,-8.15,.82)],CYAN_SOFT,.06)

# Stacked skyline. Windows share a single planar mesh for render speed.
window_verts=[]
window_faces=[]
pink_verts=[]
pink_faces=[]
def facade_quad(destv,destf,p1,p2,p3,p4):
    a=len(destv)
    destv.extend([p1,p2,p3,p4])
    destf.append((a,a+1,a+2,a+3))

for depth in range(4):
    for i in range(27):
        x=-53+i*4.8+random.uniform(-1.8,1.2)
        y=17+depth*18+random.uniform(-5,4)
        if -6 < x < 12 and depth == 0: # let hero silhouette read cleanly
            continue
        sx=random.uniform(2.1,5.0)
        sy=random.uniform(2.3,6.0)
        height=random.uniform(12,34)+(18 if depth>1 and i%3==0 else 0)
        basez=-6.0
        top=basez+height
        m=CITY_BLUE if i%3 else CITY_GRAY
        cube("Tower D%d %02d"%(depth,i),(x,y,basez+height*.5),(sx,sy,height),m)
        if i%4==0:
            cube("Tower service crown",(x,y,top+.36),(sx*.68,sy*.74,.74),STEEL_D)
            path("Roof edge light",[(x-sx*.47,y-sy*.51,top+.07),(x+sx*.47,y-sy*.51,top+.07)],CYAN_SOFT,.025)
        if i%8==0:
            path("Signal mast",[(x,y,top),(x,y,top+3.1)],GUN,.06)
            circle("Air traffic beacon",(x,y,top+3.16),.11,.18,AMBER_L,vertices=10)
        front=y-sy/2-.02
        rows=min(22,int((height-1.0)/1.6))
        columns=max(1,int(sx/0.75))
        for row in range(rows):
            for column in range(columns):
                if random.random() < (.46 if depth<2 else .32):
                    wx=x-sx*.44+(column+.5)*sx*.88/columns
                    wz=basez+.65+row*1.6
                    destv,destf=(pink_verts,pink_faces) if random.random()<.11 else (window_verts,window_faces)
                    facade_quad(destv,destf,(wx-.16,front,wz),(wx+.16,front,wz),
                                (wx+.16,front,wz+.45),(wx-.16,front,wz+.45))

def finish_windows(name,verts,faces,material):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    mesh.materials.append(material)
finish_windows("Thousands of distant cool windows",window_verts,window_faces,WINDOWS)
finish_windows("Sporadic rose windows",pink_verts,pink_faces,PINK_L)

# Two suspended aerial raceways loop through the skyline. Each is built
# with a dark underlying lane and independent luminous magenta/cyan rails.
def route(name, coords, m):
    path(name+" carbon lane",coords,GUN,.28)
    path(name+" luminous trim",[(x,y,z+.17) for x,y,z in coords],m,.063)

for band in range(2):
    pts=[]
    for i in range(45):
        t=i/44
        xx=-44+116*t
        yy=32+band*19+math.sin(t*math.pi*2+band)*9
        zz=12+band*9+math.sin(t*math.pi*3+band)*5
        pts.append((xx,yy,zz))
    route("Sky transit %d"%band,pts,CYAN_L if band==0 else AMBER_L)

# Distinct floating gate silhouettes along the far track.
for i in range(5):
    x=-31+i*20
    y=46+math.sin(i*1.2)*5
    z=19+math.sin(i*1.5)*5
    p=[]
    for j in range(33):
        a=math.pi*j/32.0
        p.append((x+math.cos(a)*4.5,y,z+math.sin(a)*5.0))
    path("Distant aerial gate %d"%i,p,CYAN_L if i%2==0 else AMBER_L,.095)

# Detailed original foreground hover racer. The first proper garage
# production craft will be designed separately; this remains a hero prop.
rig=bpy.data.objects.new("NFR / HERO HOVERCRAFT / original blender construction",None)
bpy.context.collection.objects.link(rig)
rig.location=(5.5,-.4,3.68)
rig.rotation_euler=(math.radians(2.0),math.radians(-1.1),math.radians(-17.0))

section_mesh("Layer 01 / structural fuselage",[
    (-3.75,.13,.70,.27,0),(-3.23,.54,.90,.22,0),(-2.53,1.18,1.05,.1,0),
    (-1.55,1.46,1.11,.04,0),(-.4,1.54,1.23,.05,0),
    (1.2,1.60,1.24,.07,0),(2.38,1.38,1.13,.14,0),
    (3.24,.86,.80,.31,0),(3.52,.48,.57,.32,0)],NIGHT,rig)
section_mesh("Layer 02 / raised center hood",[
    (-3.48,.08,.89,.82,0),(-2.83,.56,1.06,.86,0),
    (-1.64,.82,1.35,.95,0),(-.7,.89,1.49,1.08,0),
    (.9,.97,1.48,1.09,0),(2.37,.91,1.16,.92,0),
    (3.07,.52,.85,.74,0)],BLUE,rig)
# Contoured canopy roof and separately shaped metallic rake.
section_mesh("Cabin / tinted panoramic canopy",[
    (-1.62,.37,1.56,1.42,0),(-1.10,.68,1.93,1.47,0),
    (-.29,.78,2.12,1.61,0),(.84,.78,2.03,1.56,0),
    (1.57,.54,1.61,1.38,0)],GLASS,rig)
for side in [-1,1]:
    path("Cabin titanium pillar %s"%side,
         [(side*.38,-1.53,1.56),(side*.68,-1.06,1.94),
          (side*.78,-.25,2.12),(side*.77,.87,2.04),
          (side*.55,1.55,1.60)],SILVER,.025)
    path("Canopy orange seam %s"%side,[(side*.77,-.32,2.11),
                                       (side*.81,.77,2.03)],ORANGE,.02)
    # Side intake shrouds and angular overlapping fender flares.
    section_mesh("Layer 03 / outboard shoulder %s"%side,[
        (-2.63,.13,1.07,.71,side*1.13),(-2.0,.27,1.28,.69,side*1.20),
        (-.9,.34,1.35,.7,side*1.28),(.5,.38,1.39,.68,side*1.32),
        (2.0,.30,1.32,.67,side*1.30),(2.91,.12,1.08,.77,side*1.05)],SILVER,rig)
    section_mesh("Lower aero side channel %s"%side,[
        (-2.25,.17,.78,.35,side*1.41),(-1.32,.25,.71,.25,side*1.47),
        (.50,.29,.73,.23,side*1.53),(2.42,.18,.81,.42,side*1.48)],DARK,rig)
    path("Light blade / rocker %s"%side,[(side*1.61,-2.12,.43),
                                        (side*1.72,-.55,.35),
                                        (side*1.70,1.88,.47),
                                        (side*1.47,2.54,.69)],CYAN_L,.036)
    path("Upper shoulder copper crease %s"%side,[
        (side*1.29,-2.48,1.12),(side*1.55,-1.68,1.35),
        (side*1.69,.48,1.39),(side*1.49,2.28,1.31)],ORANGE,.024)
    for yy in [-2.05,1.89]:
        # Four real repulsor assemblies, rather than line-art circles.
        xx=side*1.81
        cube("Pod suspension cradle",(xx*.9,yy,.36),(.47,.67,.31),GUN,.11,rig)
        circle("Repulsor housing",(xx,yy,.10),.43,.37,DARK,parent=rig)
        ring("Repulsor plasma annulus",(xx,yy,-.07),.335,.048,CYAN_L,parent=rig)
        circle("Repulsor center diffuser",(xx,yy,-.11),.21,.035,CYAN_SOFT,parent=rig)
        for k in range(6):
            a=k*math.tau/6
            cube("Pod cooling bracket",(xx+math.cos(a)*.35,yy+math.sin(a)*.35,.12),
                 (.07,.13,.14),SILVER,.014,rig)
    for yy in [-2.15,-1.88,-1.61]:
        cube("Front side outlet slat",(side*1.24,yy,.92),(.13,.048,.18),DARK,.01,rig)
    # Rear wing stanchions and functional tail surface silhouette.
    cube("Wing vertical leg",(side*1.25,2.46,1.64),(.13,.35,.71),GUN,.045,rig)
    cube("Wing aerolet tip",(side*2.00,2.65,1.95),(.11,.66,.32),ORANGE,.03,rig)

cube("Layer 04 / elevated rear carbon wing",(0,2.7,2.03),(4.3,.62,.17),NIGHT,.08,rig)
cube("Layer 05 / trailing wing lip",(0,3.02,2.0),(4.1,.11,.08),AMBER_L,.02,rig)
# Paired reaction thrusters, motor rings, and dark centerline spoilers.
for side in [-1,1]:
    xx=side*.8
    circle("Twin vector exhaust / housing",(xx,3.45,.49),.44,.64,GUN,'Y',parent=rig)
    circle("Twin vector exhaust / cavity",(xx,3.80,.49),.322,.04,DARK,'Y',parent=rig)
    ring("Twin vector exhaust / burning optic",(xx,3.84,.49),.32,.065,AMBER_L,'Y',rig)
    ring("Twin vector exhaust / inner ion",(xx,3.86,.49),.19,.045,CYAN_L,'Y',rig)
    circle("Twin vector exhaust / reactor core",(xx,3.86,.49),.12,.02,CYAN_SOFT,'Y',parent=rig)
# Multi-piece front graphic detailing.
path("Front copper leading edge",[(-.51,-3.15,.85),(0,-3.57,.75),(.51,-3.15,.85)],AMBER_L,.032)
for side in [-1,1]:
    cube("Headlamp blade",(side*.86,-2.94,.84),(.42,.055,.09),CYAN_L,.025,rig)
    path("Front nose cutline",[(side*.09,-3.58,.73),(side*.84,-3.07,.95),
                               (side*1.3,-2.40,.99)],SILVER,.012)
# Fine service fasteners and engraved side vents.
for side in [-1,1]:
    for j in range(8):
        yy=-1.05+j*.31
        cube("Exposed machined grille",(side*1.70,yy,.90),
             (.055,.07,.26),GUN,.008,rig)

# Environment color and believable reflections: huge softbox lights on the craft,
# warm rear thrusters, cyan side fill, colored city atmosphere.
def area(name,location,energy,color,size,target):
    data=bpy.data.lights.new(name,'AREA')
    data.energy=energy
    data.color=color
    data.shape='DISK'
    data.size=size
    ob=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(ob)
    ob.location=location
    vec=Vector(target)-ob.location
    ob.rotation_euler=vec.to_track_quat('-Z','Y').to_euler()

area("Hero / cool key",(2,-9,13),2200,(.34,.78,1.0),11,(5,0,4))
area("Hero / copper rear rim",(13,5,10),1950,(1,.30,.16),8,(6,0,4))
area("Hero / soft overhead",(7,-1,15),1200,(.75,.90,1.0),9,(6,0,3))
area("City / blue horizon",(-35,18,28),3400,(.14,.38,1.0),18,(0,27,3))
area("City / warm bokeh",(43,31,21),2600,(1,.12,.24),17,(4,27,8))

# Additional light motes and machinery emissions on the foreground deck.
for i in range(130):
    x=random.uniform(-2.4,13)
    y=random.uniform(-7.0,7.1)
    z=random.uniform(2.3,8.5)
    if random.random()<.6 and x<2:
        continue
    rad=random.uniform(.014,.06)
    cube("Hot atmospheric mote",(x,y,z),(rad,rad,rad),AMBER_L if i%4==0 else CYAN_SOFT)
for i in range(14):
    x=random.uniform(0,12)
    y=random.uniform(-7,7)
    z=2.28
    cube("Deck fastening / chrome",(x,y,z),(.065,.045,.016),SILVER,.008)

camera_data=bpy.data.cameras.new("Cinematic 35mm / right-hand craft framing")
camera=bpy.data.objects.new("MENU HERO CAMERA",camera_data)
bpy.context.collection.objects.link(camera)
camera.location=(17.5,-26.0,14.4)
target=Vector((3.3,4.0,5.9))
direction=target-camera.location
camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
camera_data.type='PERSP'
camera_data.lens=41
camera_data.clip_end=400
# Force the hero rightward in frame so the left menu stays readable.
camera_data.shift_x=-.10
bpy.context.scene.camera=camera

world=bpy.data.worlds.new("Midnight blue atmosphere")
bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.012,.025,.071,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.38

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.device='CPU'
scene.cycles.samples=int(os.environ.get('NEON_MENU_SAMPLES','28'))
scene.cycles.use_denoising=True
scene.render.resolution_x=1600
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
try:
    scene.view_settings.look='AgX - Medium High Contrast'
except Exception:
    pass
scene.render.image_settings.color_depth='8'
scene.render.filepath=os.path.join(GAME,"launch_scene.png")
# Filmic glow through compositor where supported by the pinned Blender version.
scene.use_nodes=True
nodes=scene.node_tree.nodes
nodes.clear()
rl=nodes.new('CompositorNodeRLayers')
out=nodes.new('CompositorNodeComposite')
try:
    glare=nodes.new('CompositorNodeGlare')
    glare.glare_type='FOG_GLOW'
    glare.threshold=1.25
    glare.quality='HIGH'
    scene.node_tree.links.new(rl.outputs['Image'],glare.inputs['Image'])
    scene.node_tree.links.new(glare.outputs['Image'],out.inputs['Image'])
except Exception:
    scene.node_tree.links.new(rl.outputs['Image'],out.inputs['Image'])

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BUILD,"menu_hero.blend"))
bpy.ops.render.render(write_still=True)
assert os.path.getsize(scene.render.filepath)>150000, "Blender render output missing / unexpectedly small"
print("NEON_FOUNDRY_BLENDER_MENU_OK "+scene.render.filepath)
