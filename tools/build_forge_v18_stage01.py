#!/usr/bin/env python3
"""FORGE V18 stage 01: frame-first modular construction study.

Reference: user-supplied exploded/parts layout (4223/4224) and actual V17
mesh scale. Builds a *new* load-bearing-style frame as independent physical
components with named connection graph and mounting hardpoints. Not a
manufacturable stress-validated frame, not a finished V18 exterior.
"""
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
import trimesh
import networkx as nx
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals

ROOT=Path(__file__).resolve().parent
SOURCE=Path(__file__).resolve().parents[1]/'art/hero_01/experiments/V17/FORGE_V17_ConnectedPanels.glb'
OUT=Path(__file__).resolve().parents[1]/'build/forge_v18_stage01'
OUT.mkdir(parents=True,exist_ok=True)
orig=trimesh.load(SOURCE,force='scene',process=False)
COLORS={
  'frame': ([66,78,89,255],0.75,0.52),
  'secondary':([102,117,126,255],0.71,0.42),
  'joint':([157,137,110,255],0.80,0.42),
  'mount':([188,132,72,255],0.72,0.42),
  'armor':([121,102,86,255],0.62,0.55),
  'glass':([65,109,131,255],0.12,0.25),
  'dark':([42,45,52,255],0.45,0.72)
}

def shade(mesh,mat):
    c,metal,rough=COLORS[mat]
    mesh.visual=TextureVisuals(material=PBRMaterial(name='FORGE V18 '+mat,baseColorFactor=c,metallicFactor=metal,roughnessFactor=rough))
    return mesh

frame=trimesh.Scene()
frame_meta=[]
part_names=set()
layout={}

def parent_for(scene, category):
    """Explicit editable hierarchy (not simply hundreds of flat meshes)."""
    name='ASSEMBLY_'+category.replace('/','_').replace(' ','_')
    if name not in scene.graph.nodes:
        scene.graph.update(frame_to=name,frame_from=scene.graph.base_frame,matrix=np.eye(4))
    return name

# x: lateral, y: vertical height, z: front (+) to aft (-).
P={}
def node(key,x,y,z):
    if key in P: raise ValueError('Duplicate node '+key)
    P[key]=np.array([x,y,z],dtype=float)

def add(name,geom,category,role,mat='frame'):
    if name in part_names: raise ValueError('Duplicate assembly part '+name)
    part_names.add(name)
    mesh=shade(geom,mat)
    if not mesh.is_watertight: raise ValueError('Nonwatertight component '+name)
    frame.add_geometry(mesh,node_name=name,geom_name=name,parent_node_name=parent_for(frame,category))
    frame_meta.append({'part':name,'module':category,'role':role,'faces':int(len(mesh.faces)),
                       'bbox_m':np.round(mesh.bounds,3).tolist(),'watertight':True})
    return mesh

edges=[]
def beam(name,a,b,group,role,radius=.052,sections=12,mat='frame'):
    pa,pb=P[a],P[b]
    length=np.linalg.norm(pb-pa)
    if length<.07:raise ValueError('Short segment '+name)
    # Overshoot endpoints by radius, so structural rods meet in physical space.
    cyl=trimesh.creation.cylinder(radius=radius,height=length+2*radius,sections=sections)
    T=trimesh.geometry.align_vectors([0,0,1],(pb-pa)/length)
    cyl.apply_transform(T)
    cyl.apply_translation((pa+pb)/2)
    add(name,cyl,group,role,mat)
    edges.append((a,b,name,group))

def box(name,center,extents,group,role,mat='secondary'):
    ob=trimesh.creation.box(extents=extents)
    ob.apply_translation(center)
    add(name,ob,group,role,mat)

def joint(name,point,group='00/Chassis',radius=.092):
    ob=trimesh.creation.icosphere(subdivisions=1,radius=radius)
    ob.apply_translation(P[point])
    add(name,ob,group,'Fabricated weld-node / gusset clearance','joint')

def bolt(name,center,group,axis='y',radius=.035):
    o=trimesh.creation.cylinder(radius=radius,height=.025,sections=6)
    if axis=='y':
        rot=trimesh.geometry.align_vectors([0,0,1],[0,1,0]);o.apply_transform(rot)
    elif axis=='x':
        rot=trimesh.geometry.align_vectors([0,0,1],[1,0,0]);o.apply_transform(rot)
    o.apply_translation(center)
    add(name,o,group,'Separate hex-head fastener','joint')

# Underfloor ladder: a proper continuous load path between nose and rear.
z_stations=[3.55,3.06,2.34,1.56,.65,-.16,-.89,-1.75,-2.66,-3.44]
for sign,side in ((-1,'PORT'),(1,'STBD')):
    for i,z in enumerate(z_stations):
        x=sign*(.71 if z>.2 else (.83 if z>-2.66 else .93))
        node(f'L_{side}_{i}',x,.48 if z>-.5 else .50,z)
        node(f'U_{side}_{i}',x,.95 if z>.2 else (1.05 if z>-2.66 else 1.14),z)
    for i in range(len(z_stations)-1):
        beam(f'LOWER_LONGERON_{side}_{i:02}',f'L_{side}_{i}',f'L_{side}_{i+1}',
             '01/Ladder','Primary lower chassis longitudinal rail',.073,16)
        beam(f'UPPER_SILL_{side}_{i:02}',f'U_{side}_{i}',f'U_{side}_{i+1}',
             '01/Ladder','Continuous armor/cockpit mounting rail',.047,12)
    for i in (0,2,3,4,6,8,9):
        beam(f'BULKHEAD_UPRIGHT_{side}_{i:02}',f'L_{side}_{i}',f'U_{side}_{i}',
             '01/Ladder','Lower-to-upper load member',.048,12)
    for i in (1,3,5,7):
        beam(f'WEB_DIAGONAL_{side}_{i:02}',f'L_{side}_{i}',f'U_{side}_{i+1}',
             '01/Ladder','Triangulated side rail bracing',.035,12,'secondary')
for i in range(len(z_stations)):
    beam(f'FLOOR_CROSSMEMBER_{i:02}','L_PORT_'+str(i),'L_STBD_'+str(i),
         '01/Ladder','Transverse frame connector',.059,12)
    if i in (0,2,4,6,8,9):
        beam(f'UPPER_CROSSBRACE_{i:02}','U_PORT_'+str(i),'U_STBD_'+str(i),
             '01/Ladder','Upper transverse structure',.042,12,'secondary')

# Real nose backbone, central mount spine, and A-pillar cage geometry.
for i,z in enumerate((3.62,2.91,2.15,1.34,.52,-.42,-1.31,-2.33,-3.34)):
    node(f'C_{i}',0,.56,z)
for i in range(8):
    beam(f'CENTRAL_SPINE_{i:02}',f'C_{i}',f'C_{i+1}','02/Keel',
         'Independent full-length structural centerline',.054,12)
for i,j in ((0,0),(1,1),(2,2),(3,3),(4,4),(6,6),(8,9)):
    beam(f'KEEL_TRIANGULATION_PORT_{i:02}',f'C_{i}',f'L_PORT_{j}',
         '02/Keel','Centerline-to-perimeter tie',.037,12,'secondary')
    beam(f'KEEL_TRIANGULATION_STBD_{i:02}',f'C_{i}',f'L_STBD_{j}',
         '02/Keel','Centerline-to-perimeter tie',.037,12,'secondary')

for sign,side in ((-1,'PORT'),(1,'STBD')):
    # Actual cockpit hoop, rather than decorative strips glued to glass.
    cps=[('A',sign*.55,1.40,-.20),('R1',sign*.40,1.74,-.82),
         ('R2',sign*.43,1.81,-1.45),('R3',sign*.58,1.69,-2.12),
         ('R4',sign*.82,1.20,-2.91)]
    for label,x,y,z in cps: node('CAB_'+side+'_'+label,x,y,z)
    beam('A_PILLAR_'+side,'U_'+side+'_4','CAB_'+side+'_A',
         '03/CockpitCage','Tubular A-pillar mounting to sill',.051,16)
    for start,end in [('A','R1'),('R1','R2'),('R2','R3'),('R3','R4')]:
        beam('CANOPY_ROOF_FRAME_'+side+'_'+start,'CAB_'+side+'_'+start,'CAB_'+side+'_'+end,
             '03/CockpitCage','Integrated canopy upper rail',.05,16)
    beam('REAR_CAGE_STAY_'+side,'CAB_'+side+'_R4','U_'+side+'_8',
         '03/CockpitCage','Rear roof to chassis support',.06,16)
    beam('CAB_DASH_BRACE_'+side,'CAB_'+side+'_A','L_'+side+'_4',
         '03/CockpitCage','A-pillar diagonal/dash bracket',.035,12,'secondary')
    beam('ROLLBAR_SUPPORT_'+side,'CAB_'+side+'_R2','U_'+side+'_6',
         '03/CockpitCage','B-pillar triangulation',.043,12,'secondary')
    beam('REAR_ROLLBAR_SUPPORT_'+side,'CAB_'+side+'_R3','U_'+side+'_7',
         '03/CockpitCage','Rear-arch triangulation',.046,12,'secondary')
for label in ['A','R1','R2','R3','R4']:
    beam('COCKPIT_HOOP_TOP_'+label,'CAB_PORT_'+label,'CAB_STBD_'+label,
         '03/CockpitCage','Cross-car hoop for cockpit and canopy seal',.048,16,'secondary')

# Wing, intake, armor mounting points are actually tied back to the frame.
for sign,side in ((-1,'PORT'),(1,'STBD')):
    hardpoints=[('INTAKE_FWD',sign*1.33,.83,2.75,2),
                ('INTAKE_AFT',sign*1.34,.83,1.65,3),
                ('BODY_FWD',sign*1.61,.98,-1.01,6),
                ('BODY_AFT',sign*1.62,.96,-2.43,8),
                ('WING_ROOT',sign*1.82,.89,-2.65,8)]
    for label,x,y,z,j in hardpoints:
        a='MOUNT_'+side+'_'+label
        node(a,x,y,z)
        beam('LOAD_ARM_'+side+'_'+label,a,'U_'+side+'_'+str(j),
             '04/MountingHardpoints','Physical structure supporting removable panel',.045,12)
        # Each bracket has a separate plate, washer, and two bolts.
        center=P[a]+np.array([sign*.03,0,0])
        box('BRACKET_PLATE_'+side+'_'+label,center,[.16,.12,.24],
            '04/MountingHardpoints','Independent bolt-on mounting bracket','mount')
        for k,dz in enumerate((-.065,.065)):
            bolt('BRACKET_FASTENER_'+side+'_'+label+'_'+str(k),center+np.array([0,.067,dz]),
                 '04/MountingHardpoints')

# Separate aft engine cradle: cross-connected and tied to actual frame nodes.
for sign,side in ((-1,'PORT'),(1,'STBD')):
    for idx,z in enumerate((-2.75,-3.22,-3.8)):
        node('ENGINE_'+side+'_'+str(idx),sign*1.13,.59,z)
    for i in (0,1):
        beam('ENGINE_CARRIER_'+side+'_'+str(i),
             'ENGINE_'+side+'_'+str(i),'ENGINE_'+side+'_'+str(i+1),
             '05/EngineCradle','Main thruster cradle beam',.074,16)
    beam('ENGINE_CRADLE_STAY_'+side,'U_'+side+'_8','ENGINE_'+side+'_0',
         '05/EngineCradle','Engine cradle tied to aft body',.048,12)
    beam('ENGINE_AFT_STAY_'+side,'L_'+side+'_9','ENGINE_'+side+'_2',
         '05/EngineCradle','Rear propulsion cantilever support',.058,12)
    for i in (0,2):
        bolt('ENGINE_BOLT_'+side+'_'+str(i),P['ENGINE_'+side+'_'+str(i)]+[0,.10,0],
             '05/EngineCradle',radius=.048)
for i in range(3):
    beam('ENGINE_CROSSBAR_'+str(i),'ENGINE_PORT_'+str(i),'ENGINE_STBD_'+str(i),
         '05/EngineCradle','Pairwise twin-propulsion mounting plate',.062,12)

# Distinct closed floor sections with real spacing and flange lines.
for i,(z0,z1) in enumerate(((2.78,3.4),(.72,1.24),(-.85,-.35),(-1.8,-1.28),(-3.1,-2.63))):
    box('REMOVABLE_BELLY_PAN_'+str(i),[0,.41,(z0+z1)/2],[1.18,.045,abs(z1-z0)],
        '06/Undertray','Five independent underbody shield segments','secondary')

# Weld-node caps at selected actual junctions (exclude decorative free parts).
for key in ['L_PORT_0','L_STBD_0','L_PORT_3','L_STBD_3',
            'U_PORT_4','U_STBD_4','U_PORT_8','U_STBD_8',
            'CAB_PORT_R2','CAB_STBD_R2','CAB_PORT_R4','CAB_STBD_R4']:
    joint('JUNCTION_'+key,key)

# Validate main centerline connectivity. No edges with detached endpoints.
G=nx.Graph()
G.add_nodes_from(P)
for a,b,_,_ in edges:
    G.add_edge(a,b)
if not nx.is_connected(G):
    comps=sorted([len(c) for c in nx.connected_components(G)],reverse=True)
    raise RuntimeError('Disconnected frame node graph '+str(comps))

# Ensure all new meshes are watertight and internal engineering zones clear.
assert len(frame.geometry)>135
assert all(m.is_watertight for m in frame.geometry.values())
assert frame.bounds[0][2]>=-4.0 and frame.bounds[1][2]<=3.9
for side in ('PORT','STBD'):
    for ident in ('INTAKE_FWD','INTAKE_AFT','BODY_FWD','BODY_AFT','WING_ROOT'):
        target='MOUNT_'+side+'_'+ident
        assert G.degree(target)>=1 and np.linalg.norm(P[target]-P['U_'+side+'_3'])<6

metadata={
    'prototype':'FORGE V18 — Stage 01 inner structure and hardpoints',
    'source':'V17 dimensions and exploded component sheet 4223/4224',
    'purpose':'Replace one-piece-first approach with inspectable structural subassemblies',
    'gate':'Design experiment, not production vehicle or engineering-certified chassis',
    'mesh_count':len(frame.geometry),
    'triangles':int(sum(len(m.faces) for m in frame.geometry.values())),
    'frame_nodes':len(P),'frame_edges':len(edges),
    'single_connected_load_path_graph':nx.is_connected(G),
    'watertight_independent_parts':len(frame.geometry),
    'bounds_m':np.round(frame.bounds,3).tolist(),
    'distinct_mounts':sorted(x for x in P if x.startswith('MOUNT_')),
    'modules':{k:len([x for x in frame_meta if x['module']==k]) for k in sorted(set(x['module'] for x in frame_meta))},
    'note':'Physical frame members overlap at named joints. No FEM structural strength analysis; not CAD toleranced for manufacture.',
}
(OUT/'V18_Subframe_Manifest.json').write_text(json.dumps({'summary':metadata,'parts':frame_meta},indent=2))
frame.export(OUT/'FORGE_V18_01_Structural_Subframe.glb')

# A diagnostic assembly uses *selected* physical V17 components but does
# NOT add back its continuous lower hull. The exposed cage therefore remains
# visible. Existing art meshes remain separate for future cleanup/refinement.
study=trimesh.Scene()
module_for_part={v['part']:v['module'] for v in frame_meta}
for name,mesh in frame.geometry.items():
    category=module_for_part[name]
    study.add_geometry(mesh.copy(),node_name=name,geom_name=name,
                       parent_node_name=parent_for(study,category))
reuse=[]
for name,mesh in orig.geometry.items():
    keep=(name.startswith('THRUST_') and (any(key in name for key in
           ('HollowMainNozzle','MetalRetainingRing','CradleBrace','UpperTwinExhaustHousing'))))
    keep=keep or ('PhysicalIntakeOuterHousing' in name)
    keep=keep or ('FormedBronzeFuselageArmor' in name)
    keep=keep or ('IntegratedSweptRearSideWing' in name)
    keep=keep or ('ReferenceAlignedOnePieceGreenhouse' in name)
    if keep:
        if 'PhysicalIntakeOuterHousing' in name:
            category='07/PilotIntakeHousings'
        elif 'Greenhouse' in name:
            category='08/PilotCanopyPlaceholder'
        elif 'FormedBronzeFuselageArmor' in name or 'IntegratedSweptRearSideWing' in name:
            category='09/PilotRemovableArmor'
        else:
            category='10/PilotRearPropulsion'
        study.add_geometry(mesh.copy(),node_name=name,geom_name=name,
                           parent_node_name=parent_for(study,category))
        reuse.append(name)
study.export(OUT/'FORGE_V18_01_Frame_With_Modules.glb')
metadata['study_module_meshes']=len(reuse)
(OUT/'V18_Stage01_Summary.json').write_text(json.dumps(metadata,indent=2))
print('V18_FRAME_FIRST_STUDY_OK',json.dumps(metadata,sort_keys=True))
