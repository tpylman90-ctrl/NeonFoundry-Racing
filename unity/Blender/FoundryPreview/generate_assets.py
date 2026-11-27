# Neon Foundry Racing — deterministic Blender-authored Unity preview meshes.
# Runs headlessly from the shared Eclipse Unity Android build runner.
# All objects are newly constructed; no third-party meshes or proprietary assets.
import bpy, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from upgrade_geometry import upgrade_craft, upgrade_garage, author_texture_maps, merge_by_material

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Assets" / "Resources" / "Foundry"
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name, rgba, metallic=0.0, rough=0.4, glow=0.0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgba,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*rgba,1)
    p.inputs["Metallic"].default_value=metallic
    p.inputs["Roughness"].default_value=rough
    if glow:
        for inp in ("Emission Color","Emission"):
            if inp in p.inputs: p.inputs[inp].default_value=(*rgba,1)
        if "Emission Strength" in p.inputs: p.inputs["Emission Strength"].default_value=glow
    return m

M={
 "CARBON":mat("NF_CARBON",(0.019,0.029,0.045),.20,.42),
 "ARMOR":mat("NF_ARMOR",(0.22,0.32,0.42),.67,.27),
 "STEEL":mat("NF_STEEL",(0.43,0.56,0.60),.80,.28),
 "GLASS":mat("NF_GLASS",(0.018,0.12,0.21),.42,.15),
 "CYAN":mat("NF_CYAN",(0.006,0.65,0.92),.10,.24,2.0),
 "AMBER":mat("NF_AMBER",(1.0,0.26,0.025),.12,.25,1.7),
 "FLOOR":mat("NF_FLOOR",(0.09,0.12,0.15),.22,.67),
 "WALL":mat("NF_WALL",(0.13,0.18,0.22),.41,.57),
 "RUBBER":mat("NF_RUBBER",(0.035,0.044,0.048),.02,.82),
 "BATTERY":mat("NF_BATTERY",(0.23,0.37,0.29),.32,.32),
 "RED":mat("NF_RED",(0.72,0.08,0.05),.42,.27)
}
def apply(o,name):
    o.data.materials.append(M[name]); return o
def box(name,loc,scale,material,bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new("Manufactured edge radius","BEVEL")
        mod.width=bevel;mod.segments=2
        mod2=o.modifiers.new("Weighted body normals","WEIGHTED_NORMAL")
    return apply(o,material)
def cyl(name,loc,radius,depth,material,axis="Z",segments=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=radius,depth=depth,location=loc)
    o=bpy.context.object;o.name=name
    if axis=="Y":o.rotation_euler[0]=math.pi/2
    if axis=="X":o.rotation_euler[1]=math.pi/2
    return apply(o,material)
def tor(name,loc,major,minor,material,axis="Y"):
    bpy.ops.mesh.primitive_torus_add(major_segments=40,minor_segments=10,
        location=loc,major_radius=major,minor_radius=minor)
    o=bpy.context.object;o.name=name
    if axis=="Y":o.rotation_euler[0]=math.pi/2
    if axis=="X":o.rotation_euler[1]=math.pi/2
    return apply(o,material)
def loft(name,sections,material):
    # Each section is (longitudinal Y, half-width X, lower Z, shoulder Z)
    v=[];f=[]
    for y,w,zlo,zhi in sections:
        profile=[(0,zlo),(.67*w,zlo+.08),(w,zlo+.29),(w,zhi-.22),
                 (.72*w,zhi),(0,zhi+.15),(-.72*w,zhi),(-w,zhi-.22),
                 (-w,zlo+.29),(-.67*w,zlo+.08)]
        v += [(x,y,z) for x,z in profile]
    n=10
    f.append(tuple(range(n-1,-1,-1)))
    for s in range(len(sections)-1):
        for i in range(n):
            j=(i+1)%n
            f.append((s*n+i,s*n+j,(s+1)*n+j,(s+1)*n+i))
    f.append(tuple((len(sections)-1)*n+i for i in range(n)))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
    return apply(o,material)
def export_obj(name,selected):
    bpy.ops.object.select_all(action="DESELECT")
    for o in selected:o.select_set(True)
    bpy.context.view_layer.objects.active=selected[0]
    path=str(OUT/name)
    if hasattr(bpy.ops.wm,"obj_export"):
        bpy.ops.wm.obj_export(filepath=path,export_selected_objects=True,
            forward_axis="NEGATIVE_Z",up_axis="Y",apply_modifiers=True,export_materials=True)
    else:
        bpy.ops.export_scene.obj(filepath=path,use_selection=True,axis_forward="-Z",
            axis_up="Y",use_mesh_modifiers=True,use_materials=True)
    assert Path(path).stat().st_size>15000, "Model unexpectedly tiny: "+path
    print("NF_BLENDER_ASSET_OK",path,Path(path).stat().st_size)

# Hero-form review placeholder. Dimensions and distinctive parts reflect the
# engineering direction, but this is not a final approved vehicle.
loft("FORGE | central tapered, panelled fuselage",[
 (-4.20,.65,.72,1.28),(-3.28,1.12,.69,1.58),(-1.95,1.45,.66,1.75),
 (0.25,1.28,.66,1.67),(2.10,1.06,.70,1.43),(3.58,.84,.78,1.24),
 (4.20,.60,.82,1.06)],"ARMOR")
for side in (-1,1):
    x=side*1.71
    loft("FORGE | independent side sponson %s"%side,[
     (-3.70,.42,.39,.85),(-2.95,.50,.32,1.05),(-.65,.54,.34,1.21),
     (1.70,.47,.39,1.09),(3.32,.37,.46,.83)],"CARBON").location.x=x
    # Integrated armour shoulder with separated lower skirt
    box("FORGE | sculpts shoulder", (side*1.78,.10,1.21),(.74,4.92,.23),"ARMOR",.10)
    box("FORGE | swept rocker", (side*1.78,-.17,.39),(.61,5.3,.16),"STEEL",.025)
    for j in range(5):
        y=-1.30+j*.43
        box("FORGE | flank vent louvre", (side*2.22,y,.93),(.045,.26,.13),"STEEL",.015)
    # Covered hover pod and exposed lower turbine with non-inflatable concentric edges
    for y in (-2.5,2.15):
        box("FORGE | armored hover shroud",(side*1.77,y,.36),(.93,1.20,.28),"ARMOR",.09)
        cyl("FORGE | pod mechanical hub",(side*1.77,y,.22),.31,.13,"CARBON")
        tor("FORGE | machined hover rim",(side*1.77,y,.14),.35,.055,"STEEL",axis="Z")
        cyl("FORGE | hover ion core",(side*1.77,y,.12),.21,.08,"CYAN")
    box("FORGE | nose intake slot",(side*.72,3.31,1.21),(.69,.75,.14),"CARBON",.035)
    for j in range(3):
        box("FORGE | intake fin",(side*.72,3.25,1.15+j*.061),(.59,.49,.025),"STEEL",.012)
    # paired rectangular booster housings with a true black center and edge frame
    box("FORGE | rear thruster housing",(side*1.01,-3.82,1.12),(.93,.92,.80),"STEEL",.075)
    box("FORGE | thruster aperture",(side*1.01,-4.30,1.12),(.64,.05,.54),"CARBON",.015)
    box("FORGE | thruster core",(side*1.01,-4.35,1.12),(.42,.065,.35),"CYAN",.008)
    box("FORGE | stabiliser wing", (side*1.78,-2.76,1.88),(1.15,1.02,.13),"ARMOR",.04)
    box("FORGE | tail kicker",(side*1.9,-3.06,2.01),(.14,.72,.37),"STEEL",.02)
# Long roof/canopy with shaped stations, carbon lower edge, internal instrument lip
loft("FORGE | bubble canopy faceted side glazing",[
 (-1.52,.71,1.62,2.00),(-.52,.83,1.70,2.31),
 (.76,.71,1.73,2.26),(1.60,.48,1.72,1.89)],"GLASS")
box("FORGE | canopy central spine",(0,-.12,2.37),(.085,2.36,.08),"STEEL",.025)
box("FORGE | hood recessed channel",(0,2.84,1.45),(.25,1.94,.045),"CARBON",.015)
for y in (-2.70,-1.52,.9,2.78):
    box("FORGE | intentional panel-seam inset",(0,y,1.74),(.065,.065,.04),"CYAN",.006)
upgrade_craft(box,cyl,tor,loft,M)
craft=merge_by_material()
export_obj("ForgeReviewCraft.obj",craft)

# Dedicated walkable hangar — cell room has spaced machines and an accessible
# stair flight separated from the perimeter wall, rather than blocked stairs.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
box("GARAGE | plated floor",(0,0,-.22),(35,37,.32),"FLOOR",.02)
for x in (-17.45,17.45):
    box("GARAGE | perimeter longitudinal wall",(x,0,4.0),(.35,37,8),"WALL",.025)
for y in (-18.4,18.4):
    box("GARAGE | perimeter transverse wall",(0,y,4.0),(35,.35,8),"WALL",.025)
# Floor repair / cell-swap central ring and service inlays
for i in range(20):
    a=2*math.pi*i/20
    box("GARAGE | alternating bay safety markers",
        (math.sin(a)*6.2,math.cos(a)*6.2,.014),(.28,.95,.035),
        "AMBER" if i%2==0 else "STEEL",.008).rotation_euler[2]=-a
box("GARAGE | recessed craft cradle",(0,0,.025),(9.4,11.8,.21),"CARBON",.07)
for x in (-4.72,4.72):
    box("GARAGE | outer clamp track",(x,0,.16),(.18,10.7,.18),"STEEL",.02)
    for y in (-4.5,0,4.5):
        box("GARAGE | gliding clamp pad",(x,y,.34),(.75,.88,.22),"AMBER",.04)
# CelI works across far side of hanger at y=10+, with generous walk aisles
for x in (-11.6,-6.6,-1.6,3.4):
    y=12.25
    box("CELL | independent service station",(x,y,.95),(3.5,2.2,1.65),"STEEL",.10)
    box("CELL | service worktop",(x,y,1.82),(3.6,2.4,.16),"CARBON",.03)
    for k in range(3):
        box("CELL | removable energy cassette",(x-1+k, y,2.15),(.70,1.16,.58),"BATTERY",.06)
        box("CELL | charge status stripe",(x-1+k,y-.59,2.21),(.43,.03,.08),"CYAN",.006)
    # articulated robot arm: shoulder + elbow + wrist / gripping fixture
    cyl("CELL | robot shoulder",(x-1.50,y+1.23,2.10),.25,.66,"CARBON")
    cyl("CELL | robot first link",(x-1.50,y+.85,2.90),.19,1.15,"STEEL")
    cyl("CELL | robot elbow",(x-1.50,y+.85,3.52),.29,.25,"AMBER",axis="X")
    box("CELL | robot angled link",(x-1.00,y+.75,3.45),(1.15,.24,.25),"STEEL",.05)
    box("CELL | robot gripper",(x-.45,y+.75,3.20),(.35,.50,.55),"CARBON",.03)
# independent charger gantry, no machine overlap
for x in (-14,16.25):
    box("CELL | main high-voltage cabinet",(x,11.4,2.2),(1.35,3.0,4.4),"STEEL",.09)
    for z in (1.0,1.8,2.6,3.4):
        box("CELL | voltage indicator",(x,9.88,z),(.72,.075,.085),"CYAN",.012)
for x in (-15.7,-10.7,-5.7,-.7,4.3,9.3,14.3):
    box("GARAGE | ceiling service truss",(x,0,7.1),(.18,35,.18),"STEEL",.012)
for y in (-14,-7,0,7,14):
    box("GARAGE | overhead light rail",(0,y,7.00),(31,.18,.12),"CYAN",.02)
# Raised overlook: a genuine walk-under service bay at the right-hand
# end, with 3.9m+ headroom below the deck and enough clearance for NF-BW01.
# The stair ends on the deck, and the display/physics proxies share this plan.
DECK_Z=4.35
STAIR_X=9.35
STAIR_START_Y=-1.20
STAIR_STEP_RUN=.46
STAIR_RISE=.184
STAIR_COUNT=24
# Fill the corner exactly to the inner surfaces of the existing walls.
# Front edge remains Y=9.225 for the staircase landing and inspection aisle.
# Inner right wall X=17.275; inner back wall Y=18.225.
box("DECK | elevated overlook",(12.5125,13.725,DECK_Z),(9.525,9.0,.25),"STEEL",.06)
for x in (7.80,17.21):
    box("DECK | safety glazing",(x,13.725,DECK_Z+.87),(.09,8.68,1.6),"GLASS",.02)
for i in range(STAIR_COUNT):
    box("DECK | accessible stair tread",
        (STAIR_X,STAIR_START_Y+i*STAIR_STEP_RUN,.12+i*STAIR_RISE),
        (2.0,STAIR_STEP_RUN-.014,.16),"STEEL",.025)
# The top stair surface (4.432m) reaches the raised deck top (4.475m).
# No floating/hidden access slope is used in the physical scene.
for z in (1.5,3.3,5.2):
    box("GARAGE | wall panel light",(-17.16,-14,z),(.06,2.7,.11),"AMBER",.008)
upgrade_garage(box,cyl,tor,loft,M)
garage=merge_by_material()
author_texture_maps(OUT)
export_obj("FoundryGarage.obj",garage)
print("NEON_FOUNDRY_UNITY_BLENDER_OK")
