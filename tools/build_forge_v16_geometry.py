#!/usr/bin/env python3
"""FORGE V16 / reference-driven, part-resolved physical geometry.

This script reads the *real* V15 GLB and original artwork-derived constraints.
It adds engineered physical intake mouths, a continuous structural dorsal cowl,
canopy seals, shoulder supports, deep side machinery, and layered armor.
It never overwrites V15 nor approves production integration. No invented
monocular metric measurements; DINO/depth are supporting qualitative evidence.
"""
import json, math, collections, os
from pathlib import Path
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

ROOT=Path(os.environ.get('NFR_WORKSPACE', '/mnt/data'))
BASE=Path(os.environ.get('NFR_BASE_GLB', str(ROOT/'FORGE_V15_ReferenceRebuild.glb')))
OUTPUT=Path(os.environ.get('NFR_OUTPUT_GLB', str(ROOT/'FORGE_V16_ReferenceFit.glb')))
REPORT=Path(os.environ.get('NFR_OUTPUT_REPORT', str(ROOT/'FORGE_V16_geometry_manifest.json')))
assert BASE.is_file()
base=trimesh.load(BASE, force='scene',process=False)
result=trimesh.Scene()
materials={}
for g in base.geometry.values():
    if hasattr(g.visual,'material'):
        mat=g.visual.material
        if mat: materials[mat.name]=mat

def material(name,color,metal=.5,rough=.5):
    if name not in materials:
        materials[name]=PBRMaterial(name=name,baseColorFactor=np.array((*color,255),dtype=np.uint8),metallicFactor=metal,roughnessFactor=rough)
    return materials[name]

metal=material('V16_TitaniumFabricated',(108,111,112),.8,.47)
panel=material('V16_ChamferedBrushedMetal',(133,126,119),.78,.4)
copper=material('V16_MachinedCopper',(142,102,78),.7,.51)
rubber=material('V16_SealGraphite',(26,29,31),.18,.8)
nearblack=material('V16_RecessedIntakeCavity',(10,13,15),.08,.85)
liner=material('V16_DuctLiner',(40,45,49),.58,.6)
bright=material('V16_ForgedEdge',(164,158,145),.83,.34)
fastener=material('V16_FastenerSteel',(87,93,99),.75,.44)

components=[]
exclude=('V15_100_','V15_101_','V15_103_','V15_220_','V15_225_', 'V15_400_','V15_410_')
modified=[]
for node in base.graph.nodes_geometry:
    if node.startswith(exclude): continue
    tf,geom=base.graph.get(node)
    mesh=base.geometry[geom].copy()
    mesh.apply_transform(tf)
    # Decrease spindly canopy stripe prominence without erasing the real rails.
    if node.startswith('V15_211_') or node.startswith('V15_212_') or node.startswith('V15_213_'):
        # deliberately preserve the fit; only shift its material to darker satin
        mat=metal if node.startswith('V15_212_') else fastener
        modified.append(node)
    else:
        mat=mesh.visual.material
    # V15 original bronze panels and nozzles retained intact.
    mesh.visual=trimesh.visual.TextureVisuals(material=mat)
    result.add_geometry(mesh,geom_name=node,node_name=node)
    components.append(node)


def add(name,mesh,mat,fix=True):
    assert name not in components,name
    m=mesh.copy()
    if fix:
        if m.is_watertight:
            trimesh.repair.fix_normals(m)
            if m.volume<-1e-8:m.invert()
    assert np.isfinite(m.vertices).all(),name
    m.visual=trimesh.visual.TextureVisuals(material=mat)
    result.add_geometry(m,geom_name=name,node_name=name)
    components.append(name)
    return m

def loft(name,rings,mat,cap_start=True,cap_end=True):
    p=np.asarray(rings,dtype=float)
    assert p.ndim==3 and len(p)>1 and len(p[0])>=3,(name,p.shape)
    n=len(p[0]);v=p.reshape(-1,3)
    faces=[]
    for k in range(len(p)-1):
        for j in range(n):
            a=k*n+j;b=k*n+(j+1)%n
            faces.append((a,b,b+n));faces.append((a,b+n,a+n))
    if cap_start:
        faces.extend([(0,j+1,j) for j in range(1,n-1)])
    if cap_end:
        i=(len(p)-1)*n
        faces.extend([(i,i+j,i+j+1) for j in range(1,n-1)])
    m=trimesh.Trimesh(vertices=v,faces=np.array(faces),process=False)
    return add(name,m,mat)

def rectangular_octagon(cx,cy,halfwidth,halfheight,z,bevel=.15):
    # Counterclockwise when facing the source vehicle nose (+Z).
    x0=cx-halfwidth;x1=cx+halfwidth;y0=cy-halfheight;y1=cy+halfheight
    bx=halfwidth*bevel;by=halfheight*bevel
    return np.array([
        (x0+bx,y1,z),(x1-bx,y1,z),(x1,y1-by,z),
        (x1,y0+by,z),(x1-bx,y0,z),(x0+bx,y0,z),
        (x0,y0+by,z),(x0,y1-by,z)],float)

def ring_solid(name,outer,inner,mat):
    # physical annulus with four-point bevel cuts, no fake black front-face quad
    outer=np.asarray(outer,float);inner=np.asarray(inner,float)
    v=np.vstack([outer,inner])
    n=len(outer)
    f=[]
    for j in range(n):
        k=(j+1)%n
        f.extend([(j,k,n+k),(j,n+k,n+j)])
    m=trimesh.Trimesh(vertices=v,faces=f,process=False)
    add(name,m,mat,fix=False)

def path_tube(name, pts, r, mat,sections=10):
    for i,(a,b) in enumerate(zip(pts,pts[1:])):
        a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
        direction=b-a;norm=np.linalg.norm(direction)
        if norm<1e-7:continue
        cylinder=trimesh.creation.cylinder(radius=r,height=norm,sections=sections)
        cylinder.apply_transform(trimesh.geometry.align_vectors((0,0,1),direction))
        cylinder.apply_translation((a+b)/2)
        add(f'{name}_{i:02d}',cylinder,mat)

def box(name,center,dims,mat):
    m=trimesh.creation.box(extents=dims)
    m.apply_translation(center)
    add(name,m,mat)

def face_plate(name,outline,thickness,mat):
    # A closed, faceted sheet defined in 3D, with a centerline sheet normal.
    vs=np.asarray(outline,float)
    a=vs[1]-vs[0];b=vs[2]-vs[0]
    normal=np.cross(a,b)
    normal/=max(np.linalg.norm(normal),1e-12)
    vertices=np.vstack([vs-normal*thickness/2,vs+normal*thickness/2])
    n=len(vs)
    faces=[]
    for j in range(1,n-1):
        faces.extend([(0,j,j+1),(n,n+j+1,n+j)])
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j),(i,n+j,n+i)])
    add(name,trimesh.Trimesh(vertices=vertices,faces=faces,process=False),mat)

# ---------------------------------------------------------
# 1: physically open heavy-intake grille housings
# ---------------------------------------------------------
# Profile controls from the actual side/top source; rebuild instead of layering
# a drawn dark rectangle on a solid extrusion. Outermost silhouette unchanged.
for sign,tag in ((-1.,'PORT'),(1.,'STBD')):
    stations=[(0.87,1.42,.34,.95,.47),
              (1.31,1.43,.45,.955,.525),
              (1.99,1.43,.47,.945,.515),
              (2.69,1.39,.46,.95,.49),
              (3.12,1.34,.42,.94,.45),
              (3.36,1.30,.31,.96,.29)]
    outer=[]
    for z,cx,half,cy,hy in stations:
        # outer ring at real shroud surface with broad chamfers
        outer.append(rectangular_octagon(sign*cx,cy,half,hy,z,.19))
    loft(f'V16_{tag}_PhysicalIntakeOuterHousing',outer,metal,cap_start=True,cap_end=False)
    # mouth is sufficiently open to show multiple deep surfaces:
    # an actual 8-gon annulus, a tapered structural tunnel and rear backplate.
    front=outer[-1]
    mouth=rectangular_octagon(sign*1.30,.96,.225,.205,3.371,.20)
    ring_solid(f'V16_{tag}_MetalMouthFace',front,mouth,bright)
    lip_inner=rectangular_octagon(sign*1.30,.96,.216,.196,3.35,.20)
    inset=rectangular_octagon(sign*1.32,.955,.186,.170,2.76,.20)
    loft(f'V16_{tag}_RealRecessedTunnel',
         [lip_inner,inset],liner,cap_start=False,cap_end=False)
    # Dark physical rear cap at *actual rear* of the duct, not a sticker
    darkcap=trimesh.Trimesh(vertices=inset,faces=[(0,i,i+1) for i in range(1,7)],process=False)
    add(f'V16_{tag}_CavityBackFace',darkcap,nearblack,fix=False)
    # The baffles are 3 individually machined swept bars inside that tunnel.
    for k,y in enumerate((.83,.965,1.095)):
        # Place baffles behind the rim at two different depths, with a
        # supporting shell and physically visible leading edge chamfer.
        m=trimesh.creation.box((.37,.031,.24))
        m.apply_translation((sign*1.30,y,3.06-k*.033))
        add(f'V16_{tag}_IntakeVane_{k:02d}',m,metal)
        box(f'V16_{tag}_IntakeVaneLip_{k:02d}',(sign*1.30,y+.018,3.19-k*.033),(.36,.012,.035),bright)
    # Industrial bolt flanges attach to outer sidewall at front corners
    for k,y in enumerate((.74,1.175)):
        box(f'V16_{tag}_MouthFastener_{k:02d}',(sign*1.58,y,3.378),(.052,.052,.035),fastener)
    # shoulder plate extending smoothly behind the intake with deeper relief
    # rather than a pile of square blocks.
    shoulder=[(sign*1.13,1.255,3.19),(sign*1.54,1.285,3.12),
              (sign*1.64,1.33,2.36),(sign*1.51,1.33,1.77),
              (sign*1.11,1.27,1.75),(sign*1.01,1.25,2.72)]
    face_plate(f'V16_{tag}_PressedIntakeShoulderSkin',shoulder,.044,copper)
    # edge-broken seam from shroud along the mid-body body line
    path_tube(f'V16_{tag}_IntakeShoulderTrim',
              [(sign*1.19,1.27,3.18),(sign*1.46,1.355,2.86),
               (sign*1.55,1.39,2.28),(sign*1.50,1.35,1.74)],.019,bright)

# ---------------------------------------------------------
# 2: nose armor break-up by surface transitions, not simply decorative squares
# ---------------------------------------------------------
# An embedded center segmented narrow nose, with lowered leading edge.
central=[(3.85,.245,1.18,1.105),(3.54,.28,1.25,1.12),
         (3.14,.34,1.32,1.17),(2.64,.35,1.40,1.23),
         (2.20,.39,1.435,1.235),(1.95,.38,1.435,1.23)]

def simple_quad(z,half,top,bottom):
    return [(-half,bottom,z),(half,bottom,z),(half,top-.06,z),
            (half*.78,top,z),(-half*.78,top,z),(-half,top-.06,z)]
loft('V16_NoseCenterSpineForgedSection',[simple_quad(*s) for s in central],metal)
for sign,tag in ((-1.,'PORT'),(1.,'STBD')):
    # Narrow inboard nose cheek armor forms a proper panel next to nose hood.
    outline=[(sign*.40,1.13,3.72),(sign*.58,1.24,3.27),
             (sign*.72,1.35,2.64),(sign*.70,1.35,1.92),
             (sign*.49,1.30,1.89),(sign*.40,1.20,2.98)]
    face_plate(f'V16_{tag}_NoseCheekArmoredExtrusion',outline,.044,panel)
    path_tube(f'V16_{tag}_NoseCornerHighlight',outline[:4],.011,bright)

# functional-looking 3-slot hood scoop; actual U-section sides + sunken back
# positioned above existing hood, no unsupported 'depth map to 3D'.
for k,z in enumerate((2.46,2.23,2.00)):
    box(f'V16_NoseCoolingRecess_{k}',(0,1.443,z),(.48,.024,.133),nearblack)
    box(f'V16_NoseCoolingVane_{k}',(0,1.457,z-.032),(.44,.031,.022),metal)

# ---------------------------------------------------------
# 3: new sweeping U-section formed dorsal armor shell, replacing V15 slab
# ---------------------------------------------------------
# Roof references indicate a slight rising contour behind the glass, near
# horizontal upper surface, and sides sweeping into rear shoulder armor.
# Each station has outer/inner profiles, giving the canopy clearance rather
# than merely intersecting a solid block.
roof=[
    (-1.79,.47,1.735,1.33,.31,1.61),
    (-1.99,.54,1.80,1.32,.34,1.65),
    (-2.27,.65,1.86,1.31,.41,1.71),
    (-2.70,.75,1.89,1.32,.46,1.73),
    (-3.15,.79,1.875,1.32,.49,1.72),
    (-3.52,.77,1.85,1.34,.49,1.70),
    (-3.84,.69,1.83,1.36,.45,1.67),
]
def u_ring(z,half,top,bottom,inner,inner_top):
    # Closed sectional perimeter traces EXTERIOR and INNER undersurface.
    return [(-half*.65,top,z),(half*.65,top,z),(half*.94,top-.043,z),
            (half,top-.16,z),(half,bottom+.11,z),
            (half*.85,bottom,z),(inner,bottom,z),(inner,inner_top-.05,z),
            (inner*.7,inner_top,z),(-inner*.7,inner_top,z),
            (-inner,inner_top-.05,z),(-inner,bottom,z),(-half*.85,bottom,z),
            (-half,bottom+.11,z),(-half,top-.16,z),(-half*.94,top-.043,z)]
loft('V16_FabricatedDorsalCowlHollowUSection',[u_ring(*v) for v in roof],panel)
# Raised near-level outer roof shoulder crest, partially covering greenhouse's
# rear C-pillars and meeting rear deck support wings organically.
for sign,tag in ((-1.,'PORT'),(1.,'STBD')):
    haunch=[(-1.72,1.00,.16,1.72,1.23),
            (-2.04,1.08,.20,1.76,1.19),
            (-2.40,1.15,.25,1.73,1.16),
            (-2.81,1.25,.30,1.71,1.14),
            (-3.28,1.31,.32,1.66,1.13),
            (-3.72,1.29,.26,1.59,1.15)]
    def octagonal_side(z,cx,hw,top,bottom):
        # x is transformed by sign; y upward
        ymid=(top+bottom)/2
        return rectangular_octagon(sign*cx,ymid,hw,(top-bottom)/2,z,bevel=.20)
    loft(f'V16_{tag}_IntegratedRearCowlHaunch',
         [octagonal_side(*s) for s in haunch],metal)
    path_tube(f'V16_{tag}_AftCowlRidge',
        [(sign*.48,1.77,-1.84),(sign*.69,1.87,-2.33),
         (sign*.76,1.88,-2.92),(sign*.73,1.86,-3.62)],.024,bright)
    # Inboard aerodynamic closure plate between aft greenhouse and shoulder
    side_skin=[(sign*.78,1.68,-1.87),(sign*1.10,1.70,-2.18),
               (sign*1.43,1.53,-2.81),(sign*1.40,1.39,-3.55),
               (sign*.90,1.43,-3.52),(sign*.63,1.61,-2.30)]
    face_plate(f'V16_{tag}_CowlShoulderBlendSkin',side_skin,.038,panel)

# Rear dorsal louvers recessed INTO rear crown silhouette, not broad exposed prisms
for k,z in enumerate((-3.17,-3.37,-3.55)):
    box(f'V16_AftDorsalCoolingCutout_{k}',(0,1.896,z),(.43,.023,.099),nearblack)
    box(f'V16_AftDorsalCoolerLip_{k}',(0,1.91,z-.033),(.38,.023,.016),fastener)

# ---------------------------------------------------------
# 4: side mechanical depth layering and cast armor attachment
# ---------------------------------------------------------
for sign,tag in ((-1.,'PORT'),(1.,'STBD')):
    # Missing offset engine-side intake throat near FRONT of long side armor
    # Real long formed lower recess, segmented by separate cross-braces.
    p=[(sign*1.705,.85,-.88),(sign*1.765,.86,-1.08),
       (sign*1.77,.84,-2.52),(sign*1.715,.82,-2.77),
       (sign*1.72,.64,-2.77),(sign*1.79,.64,-1.05)]
    face_plate(f'V16_{tag}_LowerMachineryBayOuterRim',p,.034,metal)
    for j,z in enumerate(np.linspace(-1.10,-2.53,7)):
        box(f'V16_{tag}_SideCylinderShadow_{j}',
            (sign*1.803,.726,float(z)),(.037,.21,.108),nearblack)
        box(f'V16_{tag}_CoolingPipeHollowBracket_{j}',
            (sign*1.833,.72,float(z)),(.037,.23,.063),bright)
    # lower armor skirt ending at exposed machinery as a layered physical part
    skirt=[(sign*1.55,.68,-.82),(sign*1.72,.64,-1.08),
           (sign*1.72,.58,-2.78),(sign*1.59,.62,-3.02),
           (sign*1.48,.63,-2.76),(sign*1.47,.67,-1.13)]
    face_plate(f'V16_{tag}_LowerArmoredSkirt',skirt,.05,panel)
    # Panel-break fastening at front/rear ends of copper side fuselage
    for j,z in enumerate((-.75,-1.23,-2.78,-3.27)):
        box(f'V16_{tag}_SideArmorRivet_{j:02d}',(sign*1.744,1.10,z),(.032,.03,.035),fastener)
    # Rounded bridge supports to rear wing root, two genuinely separate braces
    for i,z in enumerate((-2.36,-2.87)):
        path_tube(f'V16_{tag}_RearWingAnchor_{i}',
            [(sign*1.48,1.07,z+.08),(sign*1.74,1.04,z),
             (sign*2.02,.91,z-.18)],.060,metal,sections=8)

# Open shells use deliberate outward-facing normals for strict one-sided
# Android GLB viewers. Face normals are flipped away from the ring loft's
# default (which points inward for this station ordering).
for side in ('PORT','STBD'):
    for part in ('PhysicalIntakeOuterHousing','MetalMouthFace',
                 'RealRecessedTunnel','CavityBackFace'):
        key=f'V16_{side}_{part}'
        result.geometry[key].invert()

# ---------------------------------------------------------
# Export and invariant audits
# ---------------------------------------------------------
assert len(result.geometry)>len(base.geometry)
assert all(np.isfinite(m.vertices).all() for m in result.geometry.values())
for tag in ('PORT','STBD'):
    for fragment in (f'V16_{tag}_MetalMouthFace',f'V16_{tag}_RealRecessedTunnel',
                     f'V16_{tag}_CavityBackFace',f'V16_{tag}_IntegratedRearCowlHaunch'):
        assert fragment in result.geometry,fragment
for mandatory in ['THRUST_PORT_HollowMainNozzle','THRUST_STBD_HollowMainNozzle',
                  'V15_320_PORT_IntegratedSweptRearSideWing','V15_320_STBD_IntegratedSweptRearSideWing',
                  'V15_200_ReferenceAlignedOnePieceGreenhouse']:
    assert mandatory in result.geometry,mandatory
assert max(abs(result.bounds[0][0]),result.bounds[1][0])<2.55

result.export(OUTPUT)
probe=trimesh.load(OUTPUT,force='scene',process=False)
assert len(probe.geometry)==len(result.geometry)
assert sum(len(g.faces) for g in probe.geometry.values())>sum(len(g.faces) for g in base.geometry.values())
manifest={
  'model':'FORGE V16',
  'baseline':'FORGE_V15_ReferenceRebuild.glb',
  'reference':'4209.jpg (eight-view owner artwork)',
  'source_ai':'DINOv2-small patch correspondences and Depth Anything V2 relative depth reviewed; AI results are not metric coordinates',
  'new_meshes':len(result.geometry)-len(base.geometry),
  'meshes':len(probe.geometry),'triangles':int(sum(len(g.faces) for g in probe.geometry.values())),
  'bounds':probe.bounds.tolist(),
  'changes':['Replaced capped intake-front facades with physical open duct liners and real internal louvers',
             'Rebuilt swept dorsal armor as hollow U-section with independent side haunches',
             'Additional nose shoulder fabrication and real side-machinery assemblies',
             'Preserved main engines, lift modules, rear wings, canopy geometry and cockpit location'],
  'gate':'Gate 02 experimental inspection only; no production approval',
  'completed_via':'Procedural construction and image-guided geometry; not automatic DINO-to-mesh',
}
REPORT.write_text(json.dumps(manifest,indent=2)+'\n')
print('FORGE_V16_GLTF_READY',json.dumps({k:manifest[k] for k in ['meshes','triangles','new_meshes','bounds']}))
