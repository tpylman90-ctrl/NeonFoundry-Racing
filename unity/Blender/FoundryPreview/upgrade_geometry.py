"""Foundry garage R2: authored architectural detail, mechanical visual hierarchy,
physically plausible trim, and baked procedural surface variation.

Only standard Blender/Python/Numpy modules. No licensed external assets.
All coordinates use Blender Z up; OBJ exporter converts them for Unity.
"""
import math
from pathlib import Path
import bpy
from mathutils import Vector


def bar_between(box, name, a, b, thickness, mat):
    a, b = Vector(a), Vector(b)
    diff = b - a
    if diff.length < .001:
        return None
    obj = box(name, tuple((a + b) * .5), (thickness, thickness, diff.length), mat, min(thickness*.18, .028))
    obj.rotation_euler = diff.to_track_quat('Z', 'Y').to_euler()
    return obj


def add_label(label, pos, size, material, M, rotation=(math.pi / 2, 0, 0)):
    curve = bpy.data.curves.new("Stencilled safety and zone type", "FONT")
    curve.body = label
    curve.size = size
    curve.extrude = .002
    curve.bevel_depth = .0005
    obj = bpy.data.objects.new("SIGN | " + label, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = pos
    obj.rotation_euler = rotation
    obj.data.materials.append(M[material])
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    return bpy.context.object


def upgrade_craft(box, cyl, tor, loft, M):
    """Build legible vehicle manufacturing details rather than extra rounded blobs."""
    # Multi-layer sill armour and a dark inset visually separate the canopy,
    # chassis and propulsion. Sides are intentionally mirrored.
    box("FORGE | forward split-line substructure", (0, 2.85, 1.23), (1.7, 2.25, .16), "CARBON", .035)
    box("FORGE | nose stamped lower skid", (0, 3.80, .68), (1.55, .61, .13), "STEEL", .035)
    box("FORGE | hood channel bevel edge", (0, 2.58, 1.58), (.40, 2.45, .052), "STEEL", .015)
    box("FORGE | dark cockpit windscreen lower seat", (0, 1.42, 1.78), (1.08, .12, .12), "CARBON", .015)
    for side in (-1, 1):
        x = side * 1.75
        # Horizontal continuity: flowing shoulder, lower dark hollow, skirt and
        # light ribbon. Stagger stepped plates to keep intentional gap lines.
        box("FORGE | continuous black rocker inset", (x, -.09, .62), (.74, 5.56, .13), "CARBON", .045)
        box("FORGE | sill lower aero fin", (side*1.98, -.18, .29), (.59, 5.25, .11), "ARMOR", .03)
        box("FORGE | inset blue optical stripe", (side*2.11, -.17, .72), (.025, 4.48, .042), "CYAN", .005)
        for sy in (-2.06, -.84, .62, 1.66):
            box("FORGE | interlocking shoulder plate", (side*1.67, sy, 1.42),
                (.69, .75, .085), "ARMOR", .022)
            box("FORGE | dark shoulder break line", (side*2.015, sy, 1.36),
                (.029, .64, .05), "CARBON", .005)
        # Detailed but low polygon covered maglev pods: rings / bolting /
        # radial vanes; emissive central hub is smaller than the mechanical rim.
        for py in (-2.50, 2.15):
            tor("FORGE | machined pod outer groove", (x,py,.14), .415,.025,"CARBON",axis="Z")
            tor("FORGE | inner ion retainer", (x,py,.12), .253,.022,"STEEL",axis="Z")
            for i in range(8):
                a = i*math.tau/8
                px = x + math.sin(a)*.34
                yy = py + math.cos(a)*.34
                cyl("FORGE | torqued retainer bolt", (px,yy,.151), .026,.035,"CARBON",segments=8)
            for i in range(6):
                a = i*math.tau/6
                obj=box("FORGE | static vane under shroud",
                    (x+math.sin(a)*.14,py+math.cos(a)*.14,.077),
                    (.075,.23,.016),"STEEL",.005)
                obj.rotation_euler[2] = -a
        # Distinct real intake aperture with internal structural vanes.
        box("FORGE | left right nose duct wall", (side*.77,3.65,1.17),
            (.74,.58,.27), "CARBON",.045)
        for j in range(4):
            box("FORGE | vertical intake stator", (side*(.48+j*.16),3.94,1.17),
                (.037,.035,.18),"STEEL",.006)
        # Composite tail reinforcement, foil blade with exposed fixing points.
        box("FORGE | rear cross brace", (side*1.58,-3.15,1.68),(.77,.22,.16),"STEEL",.018)
        box("FORGE | thruster orange inspection latch", (side*1.01,-4.33,1.48),
            (.30,.035,.045),"AMBER",.008)
        for z in (.90,1.00,1.13,1.26):
            box("FORGE | recessed turbine heat fin", (side*1.01,-4.4,z),
                (.43,.022,.023),"STEEL",.006)
    # Seven precisely split bonnet micro-panels give a designed surface rhythm.
    for y in (2.16,2.49,2.82,3.15):
        for x in (-.99,.99):
            box("FORGE | surface fastener", (x,y,1.55),(.045,.08,.025),"CARBON",.006)


def upgrade_garage(box, cyl, tor, loft, M):
    """Large-scale construction comes before decorative particles and props."""
    # Clear central footprint: 11.8m cradle + 1.4m access each side.
    # Grid is structural surface segmentation, no raised obstacles in walk aisles.
    for x in range(-15, 17, 3):
        box("FLOOR | inset expansion joint X", (x,0,-.052),(.028,36.5,.012),"CARBON",.001)
    for y in range(-16, 18, 3):
        box("FLOOR | inset expansion joint Y", (0,y,-.052),(34.4,.029,.012),"CARBON",.001)
    for x in (-8.8,8.8):
        box("FLOOR | heavy service lane rail", (x,0,-.022),(.19,29.8,.048),"STEEL",.008)
        box("FLOOR | illuminated lane wayfinding", (x+(.15 if x>0 else -.15),0,-.012),
            (.045,25.9,.019),"CYAN",.003)
    for y in (-8.5,8.5):
        box("FLOOR | fore aft bay perimeter", (0,y,-.016),(17.8,.12,.03),"STEEL",.008)
    for x in (-7.2,7.2):
        for y in (-7.7,7.7):
            cyl("FLOOR | access service panel fastener", (x,y,-.02),
                .15,.021,"CARBON",segments=12)
    # Structural plinth under craft and anti-slip insets.
    for x in (-5.18, 5.18):
        for y in (-4.5,0,4.5):
            box("BAY | clamp hydraulic runner", (x,y,.09),(.26,1.6,.13),"CARBON",.025)
            box("BAY | actuator exposed ram", (x,y,.20),(.14,.60,.12),"STEEL",.018)
    for y in (-5.85,5.85):
        for i in range(11):
            x=-4.4+i*.88
            box("BAY | anti-slip plate", (x,y,.022),(.79,.29,.035),"RUBBER",.015)
    # Eight mobile-safe illuminated columns: heavy structural I-beam,
    # protective bumper and bracketed up-lighter, not floating cubes.
    for x in (-16.85,16.85):
        for y in (-15,-9,-3,3,9,15):
            box("SHELL | vertical load-bearing column", (x,y,3.56),
                (.44,.72,7.13),"STEEL",.055)
            box("SHELL | low collision bumper", (x-(-.22 if x<0 else .22),y,.69),
                (.26,.92,1.28),"CARBON",.035)
            box("SHELL | horizontal structural cleat", (x,y,5.97),
                (.57,1.12,.24),"ARMOR",.024)
            box("SHELL | amber vertical caution lamp", (x-(-.27 if x<0 else .27),y,2.65),
                (.038,.36,.62),"AMBER",.008)
    # 3D bays on both side walls: double-layer stamped skin and service grids.
    for x in (-17.20,17.20):
        for y in (-12,-6,0,6,12):
            box("WALL | recessed charcoal cassette", (x,y,3.76),
                (.064,4.72,3.73),"CARBON",.009)
            box("WALL | upper horizontal brushed facing", (x,y,6.05),
                (.077,4.50,.75),"ARMOR",.017)
            for dy in (-1.75,0,1.75):
                box("WALL | vertical reinforcement emboss", (x+(.06 if x<0 else -.06),y+dy,3.89),
                    (.093,.065,2.90),"STEEL",.012)
            for z in (2.10, 2.65, 3.20):
                box("WALL | horizontal inset vent aperture", (x+(.065 if x<0 else -.065),y,z),
                    (.079,2.65,.09),"RUBBER",.012)
    # Non-repeating electrical distribution running the rear/service wall.
    for x in (-13.7,-9.2,-4.7,-.2,4.3,8.8,13.3):
        box("BACK | stacked industrial trunk", (x,17.98,3.85),
            (3.80,.35,4.80),"CARBON",.032)
        box("BACK | machined cabinet face", (x,17.75,4.02),
            (3.4,.12,4.18),"WALL",.022)
        for z in (2.32,3.40,4.48,5.56):
            box("BACK | independent powered vent cavity", (x,17.66,z),
                (2.52,.09,.13),"CARBON",.007)
        box("BACK | overhead orange power bus", (x,17.68,6.28),
            (2.16,.09,.07),"AMBER",.007)
    # Separate thin cyan strips with metal optical housings: not giant beams
    # in the camera image, and a contrasting warm service rail.
    for y in (-12,-6,0,6,12):
        for x in (-11.5,0,11.5):
            box("CEILING | recessed light cartridge", (x,y,7.35),
                (5.1,.46,.17),"CARBON",.035)
            box("CEILING | white-blue diffused slot", (x,y,7.24),
                (4.7,.11,.028),"STEEL",.008)
            for sign in (-1,1):
                box("CEILING | subtle cooled emitter", (x,y+sign*.14,7.235),
                    (4.6,.029,.02),"CYAN",.003)
    # Fully enclosed overhead shell, interrupted by narrow dark service gaps.
    # This prevents the blue procedural sky from replacing the hangar roof.
    for x in (-8,-2.66,2.66,8):
        for y in (-15,-9,-3,3,9,15):
            box("CEILING | enclosed steel cassette", (x,y,7.76),
                (5.11,5.67,.13),"WALL",.027)
            box("CEILING | overhead darker acoustic inset", (x,y,7.655),
                (4.69,5.21,.039),"CARBON",.019)
    # Ceiling peripheral tile cassettes / exposed central spine gives depth.
    for x in (-13.7,13.7):
        for y in (-12,-6,0,6,12):
            box("CEILING | separated acoustic panel", (x,y,7.61),
                (5.15,5.4,.09),"CARBON",.03)
            box("CEILING | embedded edge extrusion", (x,y,7.48),
                (5.20,.055,.045),"STEEL",.01)

    # Battery works: machine families and physical routing, all with free aisles.
    # Power cabinets, cooling towers and visible stacked replaceable cells.
    for x in (-11.6,-6.6,-1.6,3.4):
        box("CELL | console upper diagnostic casing", (x,10.90,2.44),
            (2.68,.21,1.07),"CARBON",.045)
        box("CELL | diagnostic glass", (x,10.765,2.55),
            (2.29,.022,.71),"GLASS",.018)
        for v in range(7):
            box("CELL | diagnostic waveform bar", (x-.96+v*.32,10.737,2.35+(v%3)*.10),
                (.12,.012,.04),"CYAN",.006)
        box("CELL | footplate tread", (x,9.88,.018),
            (3.45,.32,.045),"RUBBER",.006)
        for s in (-1,1):
            cyl("CELL | articulated piston head", (x+s*1.31,12.94,2.46),
                .16,.25,"CARBON",segments=12)
            box("CELL | tool reel bearing", (x+s*1.31,12.94,2.75),
                (.33,.34,.13),"STEEL",.022)
        # Battery service cell tray with three matching guarded sockets.
        for k in range(3):
            bx=x-1.0+k
            box("CELL | cassette lock collar", (bx,12.17,2.48),
                (.80,1.26,.13),"STEEL",.026)
            box("CELL | graphite cell lid", (bx,12.17,2.57),
                (.55,.84,.045),"CARBON",.009)
            box("CELL | insulated high-voltage handle", (bx,11.87,2.65),
                (.35,.08,.092),"AMBER",.015)
    # 2 distinct industrial power towers at aisle edges; preserve separation.
    for x,yc in ((-14.3,6.5),(9.45,12.2)):
        box("CELL | power converter stone base", (x,yc,.48),
            (2.15,2.50,.89),"RUBBER",.06)
        box("CELL | standing converter steel shell", (x,yc,2.83),
            (1.90,2.30,3.95),"ARMOR",.085)
        box("CELL | access cut-out", (x,yc-1.21,3.20),
            (1.26,.04,2.54),"CARBON",.03)
        for iz in range(7):
            box("CELL | hot swap heat sink fin", (x,yc-1.27,2.15+iz*.36),
                (1.10,.055,.068),"STEEL",.011)
        for by in (yc-.86, yc-.05,yc+.76):
            cyl("CELL | cooling conduit", (x+1.02,by,4.25),
                .105,1.1,"STEEL",segments=12)
    # Ceiling-mounted service gantry and safe readable orange overhead signage.
    for x in (-14, -7,0,7,14):
        box("CELL | gantry overhead extrusion", (x,12.48,6.20),
            (.18,8.70,.22),"STEEL",.013)
        box("CELL | gantry trailing cable", (x,11.9,5.93),
            (.062,5.1,.065),"RUBBER",.008)
    for y in (9.3, 15.15):
        box("CELL | electrical distribution bus", (-3.5,y,6.02),
            (20.8,.10,.14),"AMBER",.016)
    add_label("CELL WORKS  /  BAY 04", (-12.9,17.44,6.65), .71,"STEEL",M)
    add_label("HIGH VOLTAGE     AUTHORIZED PERSONNEL", (-9.8,17.42,1.45), .36,"AMBER",M)
    # Proper overlook railing: edge facing central bay, with clear stair landing.
    for y in (9.48,10.71,11.94,13.17,14.40,15.53):
        box("DECK | internal balustrade mullion", (7.78,y,4.25),
            (.10,.10,1.43),"STEEL",.015)
    box("DECK | interior continuous grasp rail", (7.78,12.53,4.97),
        (.13,6.14,.11),"STEEL",.023)
    for x in (8.0,8.9,13.1,14.1,15.5):
        box("DECK | forward glazing rail post", (x,9.28,4.29),
            (.10,.10,1.42),"STEEL",.013)
    # Split front edge: 2.8m open passage at stair top, no guard blocking it.
    box("DECK | left guard run", (8.68,9.29,4.95),(1.65,.10,.10),"STEEL",.01)
    box("DECK | right guard run", (13.76,9.29,4.95),(3.14,.10,.10),"STEEL",.01)
    for side in (-1,1):
        sx=10.85+side*1.06
        start=(sx,2.45,.37)
        end=(sx,11.94,3.69)
        bar_between(box,"DECK | true continuous stair handrail",start,end,.10,"STEEL")
        for i in (1,4,7,10,13,16):
            y=2.55+i*.53
            z=.12+i*.184
            bar_between(box,"DECK | guard fixing post",
                (sx,y,z+.05),(sx,y,z+.95),.075,"STEEL")
    # Left wall auxiliary parts area: physical spare pods, armatures and tools.
    for y in (-12.5,-8.5,-4.5):
        box("PARTS | black wall rack carcass", (-14.30,y,2.33),
            (3.30,2.38,3.47),"CARBON",.035)
        for z in (1.04,2.21,3.35):
            box("PARTS | rack zinc support beam", (-14.30,y,z),
                (3.46,2.52,.10),"STEEL",.011)
        for dy in (-.61,.61):
            for z in (1.47,2.72):
                cyl("PARTS | maglev field coil spare", (-14.30,y+dy,z),
                    .40,.33,"ARMOR",axis="X",segments=18)
                tor("PARTS | coil steel fixing lip", (-14.53,y+dy,z),
                    .30,.06,"STEEL",axis="X")
                cyl("PARTS | recessed coil ion core", (-14.55,y+dy,z),
                    .17,.02,"CYAN",axis="X",segments=18)
    add_label("SERVICE   /   PARTS", (-15.8,17.43,6.68), .38,"AMBER",M)


def author_texture_maps(output_root):
    """Small, seamless shared albedo masks instead of large external PBR files.
    Geometry remains dominant; these add roughness illusion and scale on mobile."""
    import numpy as np
    out=Path(output_root)/"Textures"
    out.mkdir(parents=True, exist_ok=True)
    n=256
    y,x=np.indices((n,n),dtype=np.int32)
    rng=np.random.default_rng(157)
    high=rng.uniform(-1,1,(n,n)).astype(np.float32)
    macro=(np.sin(x*.11)*np.cos(y*.073)).astype(np.float32)
    def export(name,v,blue=.99):
        v=np.clip(v,.38,1.0).astype(np.float32)
        pixels=np.empty((n,n,4),dtype=np.float32)
        pixels[:,:,0]=v
        pixels[:,:,1]=v*.99
        pixels[:,:,2]=v*blue
        pixels[:,:,3]=1.
        image=bpy.data.images.new("NF_BAKED_"+name,width=n,height=n,alpha=True)
        image.pixels.foreach_set(pixels.ravel())
        image.filepath_raw=str(out/(name+".png"))
        image.file_format="PNG"
        image.save()
        bpy.data.images.remove(image)
    seams=((x%64 <2)|(y%64 <2))
    floor=.86+macro*.050+high*.035
    floor=np.where(seams,.46,floor)
    # Brushed metal, subtle elongated scratch pattern.
    steel=.91+np.sin(y*.37)*.018+high*.022
    wall=.87+macro*.045+high*.022
    wall=np.where((y%128<2)|(x%128<2),.62,wall)
    armor=.93+macro*.036+high*.025
    carbon=.79+( ((x+y)//3)%2 )*.048+high*.025
    export("NF_FLOOR_SURFACE",floor)
    export("NF_STEEL_BRUSHED",steel)
    export("NF_WALL_STAMPED",wall)
    export("NF_ARMOR_COATED",armor)
    export("NF_CARBON_WEAVE",carbon, .96)
    print("NEON_FOUNDRY_BAKED_TEXTURES_OK", len(list(out.glob("*.png"))))


def merge_by_material():
    """Mobile draw-call reduction: join disconnected solids into one mesh per
    PBR surface. Keep material assignments, visible geometry and UVs intact."""
    meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    # Bake the hard-surface bevel and weighted normals BEFORE joining, otherwise
    # Blender would drop the modifiers from the non-active mesh objects.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes: obj.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    bpy.ops.object.convert(target="MESH")
    meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    material_names=sorted(set(
        o.data.materials[0].name for o in meshes if o.data.materials
    ))
    result=[]
    for mat in material_names:
        group=[o for o in meshes if o.data.materials and o.data.materials[0].name==mat]
        bpy.ops.object.select_all(action="DESELECT")
        for obj in group: obj.select_set(True)
        bpy.context.view_layer.objects.active=group[0]
        bpy.ops.object.join()
        group[0].name="BATCHED | "+mat
        result.append(group[0])
    total=sum(len(o.data.polygons) for o in result)
    print("NEON_FOUNDRY_MOBILE_BATCHING_OK",len(result),"meshes",total,"faces")
    return result
