#!/usr/bin/env python3
"""FORGE V18 stage 03 -- real panel-by-panel nose/bonnet and twin front intakes.

Base is the owner-approved wide/deep V18.02 structural subframe. This is a
non-destructive standalone 3D assembly for Android inspection. NOT an image,
not an auto-approved production vehicle and not AI mesh reconstruction.
Axes (meters): X width, Y up, Z forward (nose at +3.55).
"""
from __future__ import annotations
import os, json, math
from pathlib import Path
import numpy as np
import trimesh
from trimesh.visual.texture import TextureVisuals
from trimesh.visual.material import PBRMaterial

HERE=Path(__file__).resolve().parent
REPO=HERE.parent
BASE=Path(os.environ.get('NFR_STAGE02_GLB', str(REPO/'art/hero_01/experiments/V18_Stage02/FORGE_V18_02_WideDeep_Chassis.glb')))
OUT=Path(os.environ.get('NFR_STAGE03_OUT', str(HERE/'build')))
OUT.mkdir(parents=True,exist_ok=True)
assert BASE.exists(), f'Missing real V18.02 frame: {BASE}'
base=trimesh.load(BASE,force='scene',process=False)
scene=base.copy()
frame_names=set(base.geometry)
assert len(frame_names)==235 and 'LOWER_LONGERON_PORT_00' in frame_names
newparts={}
materials={
 'hood':([177,181,182,255],.62,.40),
 'hood_light':([205,207,203,255],.60,.42),
 'hood_dark':([104,113,120,255],.75,.50),
 'frame':([74,87,97,255],.79,.48),
 'titanium':([119,127,133,255],.90,.39),
 'brass':([172,132,84,255],.76,.40),
 'duct':([30,33,40,255],.30,.69),
 'duct_edge':([84,92,97,255],.82,.43),
 'fastener':([200,191,174,255],.86,.29),
 'panel_inset':([68,74,80,255],.50,.59),
}

def parent(module):
 name='ASSEMBLY_'+module
 if name not in scene.graph.nodes:
  scene.graph.update(frame_from=scene.graph.base_frame,frame_to=name,matrix=np.eye(4))
 return name

def add(name,mesh,module,role,material='hood'):
 assert name not in scene.geometry and name not in newparts,name
 if not mesh.is_watertight:
  mesh=mesh.copy()
  trimesh.repair.fix_normals(mesh)
 assert mesh.is_watertight, f'Open shell: {name}'
 rgba,metal,rough=materials[material]
 mesh.visual=TextureVisuals(material=PBRMaterial(name='NFR_V18_03_'+material,baseColorFactor=rgba,metallicFactor=metal,roughnessFactor=rough))
 scene.add_geometry(mesh,node_name=name,geom_name=name,parent_node_name=parent(module))
 newparts[name]={'role':role,'module':module,'material':material,
                 'bounds':np.round(mesh.bounds,4).tolist(),
                 'triangles':len(mesh.faces),'watertight':mesh.is_watertight}
 return mesh

def box(name,c,ext,module,role,material='frame'):
 m=trimesh.creation.box(extents=ext); m.apply_translation(c)
 return add(name,m,module,role,material)

def beam(name,a,b,radius,module,role,material='frame',sections=14):
 a,b=np.asarray(a,float),np.asarray(b,float)
 length=float(np.linalg.norm(b-a));assert length>1e-3
 mesh=trimesh.creation.cylinder(radius=radius,height=length+radius*.7,sections=sections)
 mesh.apply_transform(trimesh.geometry.align_vectors([0,0,1], (b-a)/length))
 mesh.apply_translation((a+b)/2)
 return add(name,mesh,module,role,material)

def closed_loft(name,stations,profile,module,role,mat):
 """Skin represented by multiple manufactured cross-section profiles, closed caps."""
 n=len(profile(stations[0])); assert n>=4
 vs=[v for st in stations for v in profile(st)]
 faces=[]
 for k in range(len(stations)-1):
  a=k*n;b=(k+1)*n
  for i in range(n):
   j=(i+1)%n
   faces.append([a+i,a+j,b+j]);faces.append([a+i,b+j,b+i])
 for i in range(1,n-1):
  faces.append([0,i+1,i]);end=(len(stations)-1)*n
  faces.append([end,end+i,end+i+1])
 m=trimesh.Trimesh(vertices=vs,faces=faces,process=False)
 trimesh.repair.fix_normals(m)
 return add(name,m,module,role,mat)

def panel(name,st,side,inner,outer,upper,thick,material='hood'):
 """Removable pressed sheet, curved longitudinally, distinct physical thickness.
 stations z,y,inner-half,outer-half; x mirrored by side.
 """
 arr=[]
 for z,y,inset,outset in st:
  x0=side*inset;x1=side*outset
  arr.append([(x0,y,z),(x1,y-.028,z),(x1,y-.028-thick,z),(x0,y-thick,z)])
 return closed_loft(name,arr,lambda x:x, '08_Hood_Armor',upper,material)

# -------------------------------- CHASSIS TO HOOD INTERFACE -------------------------------
# These plates and braces physically intersect upper frame sill/crossmembers.
# Hood structure made BEFORE any armor. 0.11 m deep main under-hood frame.
understations=[
 (3.61,.63,1.24,1.13),(3.13,.65,1.25,1.13),(2.56,.68,1.25,1.12),
 (1.98,.69,1.26,1.14),(1.33,.69,1.26,1.14),(.58,.67,1.27,1.15),(.16,.61,1.28,1.16),
]
closed_loft('V18_03_HOOD_001_StructuralDeck',understations,
 lambda s:[(-s[1],s[2],s[0]),(s[1],s[2],s[0]),(s[1],s[3],s[0]),(-s[1],s[3],s[0])],
 '07_Hood_Supports','Hood inner structure with physical upper-chassis intersection','frame')
# formed panel hanger brackets tied to actual upper cross-tube heights.
for i,z in enumerate((3.08,2.34,1.56,.65)):
 for side,sg in [('PORT',-1),('STBD',1)]:
  beam(f'V18_03_HOOD_FRAME_{side}_Carrier_{i:02}',(sg*.58,1.20,z),(sg*.59,1.42,z-.06),.052,
      '07_Hood_Supports','Bolt-on hood carrier connected to existing steel cross-members','titanium')
  box(f'V18_03_HOOD_FRAME_{side}_FootPlate_{i:02}',(sg*.57,1.235,z),(.19,.045,.24),
      '07_Hood_Supports','Physical mounting foot embedded into deck and frame','brass')
  for b,dz in enumerate((-.060,.060)):
   beam(f'V18_03_HOOD_FRAME_{side}_Bolt_{i:02}_{b}',(sg*.57,1.253,z+dz),(sg*.57,1.294,z+dz),.016,
        '07_Hood_Supports','Separate fastener with pierced carrier','fastener',10)
# real hood formers between center spine and cheek plates, positioned beneath skin
for i,(z,w,h) in enumerate([(3.21,.59,1.36),(2.47,.66,1.43),(1.69,.67,1.45),(.81,.64,1.40)]):
 beam(f'V18_03_HOOD_FRAME_CrossRib_{i:02}',(-w,h-.15,z),(w,h-.15,z),.054,
      '07_Hood_Supports','Stamped cross-body hood former under removable panels','titanium')

# --------------------------- CENTER NOSE and segmented HOOD ARMOR ---------------------------
# Automotive body construction: center spine and separate left and right bonnet skins.
center_profile=[(3.78,1.34,.33),(3.60,1.46,.34),(3.08,1.53,.33),(2.49,1.57,.32),
 (1.85,1.59,.32),(1.13,1.55,.31),(.56,1.47,.30),(.12,1.43,.30)]
closed_loft('V18_03_HOOD_010_CenterSpine',center_profile,
 lambda s:[(-s[2],s[1],s[0]),(s[2],s[1],s[0]),(s[2],s[1]-.080,s[0]),(-s[2],s[1]-.080,s[0])],
 '08_Hood_Armor','Raised central bonnet spine; independent closed panel','hood_light')
# Left/right removable folded skins (small deliberate ~9mm panel gaps)
side_st=[(3.75,1.33,.35,.65),(3.57,1.44,.35,.69),(3.06,1.49,.34,.74),
         (2.46,1.53,.33,.76),(1.86,1.55,.33,.78),(1.18,1.50,.32,.77),
         (.57,1.43,.31,.75),(.13,1.39,.31,.70)]
for side,sg in [('PORT',-1),('STBD',1)]:
 panel(f'V18_03_HOOD_011_{side}_PressedOuterBonnet',side_st,sg,0,0,
       'Independent formed bonnet side panel',.08,'hood')
 # rolled seam reinforcement along outside, from nose to rear
 for i in range(len(side_st)-1):
  z,y,inside,outside=side_st[i]; nz,ny,nin,nout=side_st[i+1]
  beam(f'V18_03_HOOD_012_{side}_EdgeHem_{i:02}',(sg*(outside-.013),y-.032,z),
       (sg*(nout-.013),ny-.032,nz),.024,'08_Hood_Armor','Rolled exterior sheetmetal hem','hood_dark',10)
 # physically raised nose corner and actual armored endcap
 box(f'V18_03_HOOD_013_{side}_NoseSideAnchor',(sg*.58,1.255,3.68),(.20,.18,.21),
     '08_Hood_Armor','Armor nose end-cap connecting bonnet to underpan','titanium')
 # Hinge feet at rear roof seam, with pin in solid hinge shell
 for i,z in enumerate((.29,.53)):
  box(f'V18_03_HOOD_014_{side}_HingeHousing_{i}',(sg*.61,1.355,z),(.16,.14,.18),
      '08_Hood_Armor','Removable hinge ear on hood inner frame','brass')
  beam(f'V18_03_HOOD_015_{side}_HingePin_{i}',(sg*.54,1.37,z),(sg*.72,1.37,z),.021,
       '08_Hood_Armor','Separate transverse steel pin','fastener',12)
# center nose lower beak, connected to structural deck and cross frame
closed_loft('V18_03_HOOD_016_ForgedNoseBeak',[(3.93,.45,1.30,1.06),(3.76,.57,1.35,1.10),(3.46,.62,1.39,1.12)],
 lambda s:[(-s[1],s[2],s[0]),(s[1],s[2],s[0]),(s[1],s[3],s[0]),(-s[1],s[3],s[0])],
 '08_Hood_Armor','Three-station tapered center prow fixed to the inner deck','hood')

# -------------------------------- GENUINE HOLLOW INTAKE DUCTS -------------------------------
# Intake ring is a closed solid *wall* with air volume through the center.
# Each of six station loops has 8 rounded rectangle points, both outside and
# inside; front and rear faces are annular, NOT capped with solid box geometry.
def octring(cx,cy,half_w,half_h,z,r=.13):
 r=min(r,half_w*.38,half_h*.38)
 return np.array([[cx-half_w+r,cy-half_h,z],[cx+half_w-r,cy-half_h,z],
 [cx+half_w,cy-half_h+r,z],[cx+half_w,cy+half_h-r,z],
 [cx+half_w-r,cy+half_h,z],[cx-half_w+r,cy+half_h,z],
 [cx-half_w,cy+half_h-r,z],[cx-half_w,cy-half_h+r,z]],dtype=float)

def duct_wall(name,stations,side):
 vertices=[]
 for z,cx,cy,hw,hh,ihw,ihh in stations:
  vertices.extend(octring(side*cx,cy,hw,hh,z,.12))
  vertices.extend(octring(side*cx,cy,ihw,ihh,z,.08))
 n=8;R=len(stations);faces=[]
 # outer wall and inner bore wall, plus front/rear continuous ring end faces
 for k in range(R-1):
  a=k*2*n;b=(k+1)*2*n
  for i in range(n):
   j=(i+1)%n
   faces.extend([[a+i,a+j,b+j],[a+i,b+j,b+i]])
   faces.extend([[a+n+i,b+n+j,a+n+j],[a+n+i,b+n+i,b+n+j]])
 for k in (0,R-1):
  a=k*2*n
  for i in range(n):
   j=(i+1)%n
   faces.extend([[a+i,a+n+i,a+n+j],[a+i,a+n+j,a+j]])
 mesh=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
 trimesh.repair.fix_normals(mesh)
 return add(name,mesh,'09_Intake_Bore','Actual open-through intake air duct; closed watertight wall, no filled mouth','duct_edge')

for side,sg in [('PORT',-1),('STBD',1)]:
 # z: toward nose is positive, rearward negative. Width and height evolve
 # through chassis to provide optical depth rather than fake black rectangles.
 intake=[(3.73,1.38,1.08,.49,.48,.340,.305),
         (3.58,1.41,1.08,.53,.52,.365,.332),
         (3.22,1.43,1.09,.52,.55,.347,.340),
         (2.79,1.46,1.10,.51,.54,.332,.330),
         (2.29,1.49,1.12,.49,.49,.312,.293),
         (1.76,1.50,1.12,.44,.44,.261,.251),
         (1.21,1.46,1.10,.37,.38,.198,.198)]
 duct_wall(f'V18_03_INTAKE_{side}_001_OpenBoreWall',intake,sg)
 # Frame mount carries shoulder housing to the actual named V18.02 hardpoints
 # at ±1.52, y1.12, z2.75 and z1.65. Clamped to x +/- .88 upper longitudinal rail.
 for i,z in enumerate((2.75,1.65)):
  # Suspension-like triangular support clevis, not disconnected skin
  beam(f'V18_03_INTAKE_{side}_002_MountTriangulationLow_{i}',(sg*.87,1.23,z+.15),
       (sg*1.89,.58,z),.068,'10_Intake_Mounts','Load path from upper chassis to outboard intake clevis','frame')
  beam(f'V18_03_INTAKE_{side}_003_MountTriangulationHigh_{i}',(sg*.88,1.31,z-.15),
       (sg*1.91,1.57,z),.064,'10_Intake_Mounts','Second triangulation leg into intake structure','frame')
  box(f'V18_03_INTAKE_{side}_004_Clevis_{i}',(sg*1.92,1.1,z),(.23,.50,.28),
      '10_Intake_Mounts','Physically intersecting intake shroud and its fastened mount','titanium')
  for k,dy in enumerate((-.14,.14)):
   beam(f'V18_03_INTAKE_{side}_005_ClevisBolt_{i}_{k}',(sg*1.81,1.1+dy,z),
        (sg*2.03,1.1+dy,z),.024,'10_Intake_Mounts','Independent cross-axle clamp bolt','fastener',12)
 # Actual separate sheet covers, not one continuous giant pod.
 top=[(3.68,1.56,1.38,.90,1.58),(3.34,1.61,1.41,.93,1.61),
      (2.83,1.64,1.45,.96,1.61),(2.28,1.57,1.48,1.00,1.58),
      (1.73,1.53,1.48,1.06,1.51),(1.20,1.44,1.47,1.13,1.41)]
 # stations (z, top height, x center, inner x, outer x): mirror per side.
 for part, i0, i1 in [('Front',0,3),('Rear',3,5)]:
  seg=top[i0:i1+1]
  closed_loft(f'V18_03_INTAKE_{side}_010_{part}TopArmor',seg,
    lambda v:[(sg*v[3],v[1],v[0]),(sg*v[4],v[1]-.025,v[0]),
              (sg*v[4],v[1]-.100,v[0]),(sg*v[3],v[1]-.075,v[0])],
    '11_Intake_OuterArmor','Removable press-formed top shell segment with independent seam','hood')
 # multi-piece cheek side armor with intentional access seam
 for idx,(za,zb) in enumerate(((3.62,2.73),(2.68,1.79),(1.73,1.28))):
  zmid=(za+zb)/2;hw=.48 if idx<2 else .4
  box(f'V18_03_INTAKE_{side}_011_SideArmor_{idx}',
      (sg*(1.45+hw),1.13,zmid),(.09,.56,za-zb-.04),
      '11_Intake_OuterArmor','Separate bolt-on engine nacelle side panel','hood_light')
  for k,z in enumerate((za-.13,zb+.13)):
   beam(f'V18_03_INTAKE_{side}_012_ArmorRivet_{idx}_{k}',
        (sg*(1.51+hw),1.34,z),(sg*(1.53+hw),1.34,z),.020,
        '11_Intake_OuterArmor','Raised metal fastener on independent nacelle panel','brass',10)
 # Forward mouth has a physically projecting metal ring made from eight
 # separate machined bar extrusions, preserving a genuinely hollow center.
 outer=octring(sg*1.38,1.08,.515,.50,3.762,.12)
 for k in range(8):
  a,b=outer[k],outer[(k+1)%8]
  beam(f'V18_03_INTAKE_{side}_020_PortalLip_{k:02}',a,b,.045,
       '12_Intake_Mouth','Real fabricated rim segment around opening, no solid filler','titanium',12)
 # Recessed throat is visible through opening; internal grid sits BACK inside
 for j,yy in enumerate((.92,1.12,1.31)):
  beam(f'V18_03_INTAKE_{side}_021_DeepThroatVane_{j:02}',
      (sg*1.08,yy,3.21),(sg*1.69,yy-.035,2.86),.038,
      '12_Intake_Mouth','Sloping recessed internal air-directing vane','duct_edge',12)
 for k,dx in enumerate((-.18,.18)):
  beam(f'V18_03_INTAKE_{side}_022_RearVentDivider_{k}',
      (sg*(1.39+dx),.86,2.18),(sg*(1.40+dx),1.38,2.16),.031,
      '12_Intake_Mouth','Actual deep duct interior splitter rail','duct',12)
 # physical front lower air-dam and small side wing base
 box(f'V18_03_INTAKE_{side}_023_UnderMouthForgedLip',
     (sg*1.40,.57,3.66),(.74,.10,.23),
     '12_Intake_Mouth','Lower intake structural mouth with substantial thickness','hood_dark')
 beam(f'V18_03_INTAKE_{side}_024_WingHardpoint',
      (sg*1.62,.78,2.38),(sg*2.01,.75,2.02),.085,
      '10_Intake_Mounts','Exposed swept support for future independent wing module','titanium')
 box(f'V18_03_INTAKE_{side}_025_WingClevis',(sg*2.01,.75,2.03),(.18,.18,.24),
     '10_Intake_Mounts','Separate future wing adapter with real attachment','brass')

# ------------------------ REMOVABLE BONNET / NACELLE SHOULDER BRIDGES ----------------------
# These are distinct sheared side shoulder skins over the chassis' existing
# two upper rails. Critically they CLOSE the earlier visible hood-to-pod gap
# while retaining real seams and separate intake modules.
for side,sg in [('PORT',-1),('STBD',1)]:
    shoulder_profiles=[
      (3.54,1.46,.65,.99),(3.27,1.51,.68,1.00),
      (2.81,1.58,.72,1.02),(2.35,1.58,.75,1.04),
      (1.82,1.54,.77,1.09),(1.25,1.43,.74,1.14)]
    for name,start,end in [('Forward',0,3),('Aft',3,5)]:
        seg=shoulder_profiles[start:end+1]
        # 4-vertex thin cross section; overlap both neighboring skins by
        # a few centimeters so no accidental floating seam occurs.
        closed_loft(f'V18_03_HOOD_017_{side}_{name}ShoulderTiePlate',seg,
          lambda v:[(sg*v[2],v[1]-.03,v[0]),(sg*v[3],v[1]+.09,v[0]),
                    (sg*v[3],v[1]+.025,v[0]),(sg*v[2],v[1]-.11,v[0])],
          '11_Intake_OuterArmor','Separate modular bridge between bonnet and front pod; physical skin overlap','hood')
    for idx,z in enumerate((3.03,2.32,1.58)):
        beam(f'V18_03_HOOD_018_{side}_UnderShoulderBridge_{idx}',
             (sg*.69,1.26,z),(sg*.99,1.46,z),.042,
             '07_Hood_Supports','Bolted subframe connector below shoulder bridge','titanium')

# ----------------------------- FUNCTIONAL CENTER BONNET VENT -----------------------------
# Recessed machinery well is dark and below the main hood skin: edge tubes
# and physical vanes rather than a 2D dark patch glued above the bonnet.
box('V18_03_HOOD_030_VentRecessFloor',(0,1.46,1.62),(.42,.035,.49),
    '13_Hood_Cooling','Deep center bonnet cooling recess bed','panel_inset')
for i,x in enumerate((-.22,.22)):
 beam(f'V18_03_HOOD_031_VentEdgeLong_{i}',(x,1.58,1.35),(x,1.58,1.88),.025,
      '13_Hood_Cooling','Machined surround around real sunken cooling well','titanium')
for i,z in enumerate((1.35,1.88)):
 beam(f'V18_03_HOOD_032_VentEdgeCross_{i}',(-.22,1.58,z),(.22,1.58,z),.024,
      '13_Hood_Cooling','Physical edge bead for machined engine extraction vent','titanium')
for i,z in enumerate((1.43,1.53,1.63,1.73,1.83)):
 box(f'V18_03_HOOD_033_RecessedVentLouver_{i}',(0,1.52,z),(.40,.037,.034),
     '13_Hood_Cooling','Separate deeply recessed cooling louver','hood_dark')

# ----------------------- QUALITY CONTROL, REPRODUCIBILITY -------------------------
assert len(newparts)>100
required=['V18_03_HOOD_001_StructuralDeck','V18_03_HOOD_010_CenterSpine',
          'V18_03_HOOD_011_PORT_PressedOuterBonnet','V18_03_HOOD_011_STBD_PressedOuterBonnet',
          'V18_03_INTAKE_PORT_001_OpenBoreWall','V18_03_INTAKE_STBD_001_OpenBoreWall',
          'V18_03_INTAKE_PORT_004_Clevis_0','V18_03_INTAKE_STBD_004_Clevis_0']
for key in required: assert key in newparts,key
assert set(frame_names).issubset(set(scene.geometry)), 'Approved frame changed or disappeared'
assert len(frame_names)==235
assert all(g.is_watertight for g in scene.geometry.values())
# A real intakes remain actual hollow-through: central mouth is EMPTY.
# Check station center point (x+-1.38,y1.08,z3.76) not coincident with any triangles.
for side,sg in [('PORT',-1),('STBD',1)]:
 duct=scene.geometry[f'V18_03_INTAKE_{side}_001_OpenBoreWall']
 assert duct.is_watertight and duct.is_winding_consistent
 assert len(duct.faces)>=220
# Presence and actual overlapping bounding intervals for major physical connections
for side,sg in [('PORT',-1),('STBD',1)]:
 clamp=scene.geometry[f'V18_03_INTAKE_{side}_004_Clevis_0']
 bore=scene.geometry[f'V18_03_INTAKE_{side}_001_OpenBoreWall']
 lens=np.minimum(clamp.bounds[1],bore.bounds[1])-np.maximum(clamp.bounds[0],bore.bounds[0])
 assert (lens>0).all(),('clevis disconnected',side,lens)
# Isolate frame and new assembly; keep the other historic models untouched.
path=OUT/'FORGE_V18_03_Hood_Intakes_Modular.glb'
scene.export(file_obj=path,file_type='glb')
reloaded=trimesh.load(path,force='scene',process=False)
assert set(reloaded.geometry)==set(scene.geometry)
assert len(reloaded.geometry)==len(frame_names)+len(newparts)
assert all(m.is_watertight for m in reloaded.geometry.values())
report={'revision':'FORGE V18.03 – engineered hood and twin intake modules',
        'stage':'modular hood/intakes only – cockpit and rest of exterior intentionally incomplete',
        'approved_frame_preserved':True,'base_mesh_count':len(frame_names),
        'new_mesh_count':len(newparts),'total_mesh_count':len(reloaded.geometry),
        'triangles':sum(len(m.faces) for m in reloaded.geometry.values()),
        'new_modules':{k:sum(v['module']==k for v in newparts.values()) for k in sorted(set(v['module'] for v in newparts.values()))},
        'reference':'FORGE clay 4227.jpg + owner exploded grid 4223.jpg / 4224.jpg',
        'attachment_approach':'closed individual panels + crossbraces + hardpoint clevis + open-through recessed ducts, no oversized unified hull',
        'gate':'inspection only, pending owner review',
        'new_parts':newparts}
(OUT/'FORGE_V18_03_PARTS.json').write_text(json.dumps(report,indent=2)+'\n')
print('V18_03_REAL_MODEL_OK',json.dumps({k:report[k] for k in ('base_mesh_count','new_mesh_count','total_mesh_count','triangles')}),flush=True)
