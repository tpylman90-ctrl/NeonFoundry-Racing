#!/usr/bin/env python3
"""FORGE V17 — physically tie floating hood/raised panels into the V16 chassis.

Loads V16 without replacing the original. Corrects front hood rear termination,
adds closed cross-section bridge components with deliberate overlaps with existing
hood, chassis and intake volumes, and connects upper rear cowl to side chassis.
The GLB remains an inspection experiment, not production approval.
"""
from pathlib import Path
import numpy as np
import trimesh
import copy
import json
import os
from shapely import affinity

ROOT=Path(os.environ.get('NFR_WORK_ROOT',str(Path(__file__).resolve().parents[1])))
SRC=Path(os.environ.get('NFR_SOURCE_GLB',str(ROOT/'art/hero_01/experiments/V16/FORGE_V16_ReferenceFit.glb')))
OUT=Path(os.environ.get('NFR_OUTPUT_GLB',str(ROOT/'build/FORGE_V17_ConnectedPanels.glb')))
REPORT=Path(os.environ.get('NFR_OUTPUT_REPORT',str(ROOT/'build/FORGE_V17_Attachment_Audit.json')))
OUT.parent.mkdir(parents=True,exist_ok=True)
REPORT.parent.mkdir(parents=True,exist_ok=True)
scene=trimesh.load(SRC,force='scene',process=False)
assert len(scene.geometry)==319,'Unexpected V16 starting mesh count'
initial_names=set(scene.geometry)

hood=scene.geometry['V15_002_NoseHoodContinuousFoldedShell']
hull=scene.geometry['V15_001_ReferenceDerivedLowerArmoredHull']
assert hood.is_watertight and hull.is_watertight
pre=hood.vertices.copy()
# Extend the trailing shell behind the initial z=.48 ring into the
# forward greenhouse base at z=.18, with a substantially supported volume.
rear=(np.abs(hood.vertices[:,2]-.48)<.005)
assert int(rear.sum())==10
hood.vertices[rear,2]=.17
hood.vertices[rear,1]+=.018
hood.vertices[rear,0]*=.94
hood.fix_normals()
assert hood.is_watertight

mats={
'panel':copy.copy(scene.geometry['V15_002_NoseHoodContinuousFoldedShell'].visual.material),
'iron':copy.copy(scene.geometry['V15_001_ReferenceDerivedLowerArmoredHull'].visual.material),
'copper':copy.copy(scene.geometry['V16_PORT_PressedIntakeShoulderSkin'].visual.material),
'machined':copy.copy(scene.geometry['V16_NoseCenterSpineForgedSection'].visual.material),
}

new_components=[]
def add(name,verts,faces,mat):
    mesh=trimesh.Trimesh(vertices=np.asarray(verts,dtype=float),faces=np.asarray(faces,dtype=int),process=False)
    trimesh.repair.fix_normals(mesh)
    assert mesh.is_watertight,(name,'not watertight',mesh.euler_number)
    mesh.visual=trimesh.visual.TextureVisuals(material=copy.copy(mats[mat]))
    scene.add_geometry(mesh,geom_name=name,node_name=name)
    new_components.append(name)
    return mesh


def loft(name,stations,section,mat):
    """Loft closed octagonal cross-sections with reliable triangle winding."""
    num=None;verts=[]
    for s in stations:
        profile=section(*s)
        num = len(profile) if num is None else num
        assert len(profile)==num
        verts.extend(profile)
    faces=[]
    for i in range(len(stations)-1):
        for j in range(num):
            nj=(j+1)%num
            a,b=i*num+j,i*num+nj
            c,d=(i+1)*num+nj,(i+1)*num+j
            faces.extend([[a,b,c],[a,c,d]])
    for j in range(1,num-1):
        faces.append([0,j+1,j])
        off=(len(stations)-1)*num
        faces.append([off,off+j,off+j+1])
    return add(name,verts,faces,mat)

# Longitudinal, faceted upper nose-to-fender connectors; their inner flanges
# penetrate the existing hood while their outer flanges penetrate the raised
# front intake shrouds. Bottom halves penetrate original fuselage armor.
# Each closed bridge is a real load-bearing solid, NOT a floating ribbon.
hood_station=[(.42,.62,1.11),(.85,.65,1.13),(1.23,.68,1.14),
              (1.75,.66,1.17),(2.18,.59,1.16),(2.58,.54,1.12),
              (2.95,.50,1.065),(3.19,.48,1.01)]

def bridge_section(z,hw,roof,sign):
    # At +/-hw the current hood upper surface is close to roof;
    # inboard edge underlaps the existing sheet by >=8 cm.
    # x_out is physically inside intake housing inner perimeter at all
    # stations beyond z~.87. Intersect the vehicle body for z<.87.
    out=0.95 if z<.70 else (1.12 if z<1.6 else 1.06)
    xi=hw-.19
    xm=hw+.11
    # Trace the body valley, then climb into intake shoulder.
    pts=[
        (xi,roof-.08),
        (hw-.005,roof+.030),
        (xm,roof+.067),
        (out,roof+.18),
        (out,roof-.14),
        (xm,roof-.25),
        (hw-.005,roof-.27),
        (xi,roof-.22),
    ]
    return [(sign*x,y,z) for x,y in pts]
for side,sign in [('PORT',-1),('STBD',1)]:
    loft(f'V17_{side}_HoodShoulderIntegratedWeb',
         [(*s,sign) for s in hood_station],bridge_section,'panel')

# Forged transverse hood-to-greenhouse cowl. Overlaps the modified rear
# hood station and the lower windshield frame by physical volume.
def apron_section(z,hw,top):
    profile=[
        (-hw*.84,top), (hw*.84,top),
        (hw,top-.045), (hw,top-.18),
        (hw*.64,top-.26),(-hw*.64,top-.26),
        (-hw,top-.18),(-hw,top-.045),
    ]
    return [(x,y,z) for x,y in profile]
loft('V17_ForgedHoodToWindshieldLoadBridge',
     [(-.28,.47,1.14),(-.09,.56,1.16),(.10,.61,1.155),
      (.35,.64,1.147),(.57,.64,1.15)],apron_section,'machined')

# Steel gusset blocks under the intake-hood bridge where it meets the
# central hull. Added under the visible skin, not standing free above it.
for side,sign in [('PORT',-1),('STBD',1)]:
    def rib_section(z,inner,outer,upper,lower):
        pts=[(inner,upper),(outer,upper-.025),(outer,lower),
             (inner,lower)]
        return [(sign*x,y,z) for x,y in pts]
    for idx,(za,zb) in enumerate([(.73,1.32),(1.72,2.22),(2.65,2.98)]):
        loft(f'V17_{side}_HoodStructuralRib_{idx}',
             [(za,.67,1.08,1.125,.77),(zb,.64,1.08,1.125,.77)],
             rib_section,'iron')

# The existing rear cowl's outer panel lower edge visibly floats above the
# fuselage in places. These continuous lower shoulder saddles underlap the
# upper rear cowl and end below the original hull's upper surface.
rear_stations=[(-3.64,.83,1.38,1.42),(-3.25,.88,1.44,1.47),
               (-2.85,.91,1.48,1.51),(-2.42,.84,1.43,1.50),
               (-2.04,.77,1.36,1.45)]
for side,sign in [('PORT',-1),('STBD',1)]:
    def rear_section(z,inner,outer,top):
        pts=[(inner,top-.015),(inner+.12,top+.015),
             (outer-.13,top-.06),(outer,top-.15),
             (outer,1.08),(outer-.18,1.06),
             (inner+.12,1.115),(inner,1.14)]
        return [(sign*x,y,z) for x,y in pts]
    loft(f'V17_{side}_RearCowlStructuralSaddle',
         [(*s,) for s in rear_stations],rear_section,'iron')

assert len(scene.geometry)==319+len(new_components)
assert all(n in scene.geometry for n in ['V15_320_PORT_IntegratedSweptRearSideWing',
                                        'V15_320_STBD_IntegratedSweptRearSideWing',
                                        'V16_PORT_PhysicalIntakeOuterHousing',
                                        'V16_STBD_PhysicalIntakeOuterHousing',
                                        'V16_FabricatedDorsalCowlHollowUSection'])

# Audit transverse and longitudinal continuity on source and new geometry,
# checking explicit interference margins and mesh quality rather than AABB only.
# The new hood ring extends back 0.31 m; stern edges inboard of the glass.
assert hood.bounds[0,2]<.18 and hood.bounds[1,2]>3.7
assert all(scene.geometry[n].is_watertight for n in new_components)
assert all(scene.geometry[n].volume>0 for n in new_components)

# Physical connection audit: verify non-zero overlapping *section areas*
# against the chassis, hood, intake and rear haunches at calibrated stations.
# Unlike AABB checks, this inspects actual cross-sectional polygons.
def section_poly(mesh, z):
    path=mesh.section(plane_origin=[0,0,z], plane_normal=[0,0,1])
    if path is None:
        return None
    planar, transform=path.to_2D()
    polygons=planar.polygons_full
    if not polygons:
        return None
    return affinity.translate(polygons[0],xoff=transform[0,3],yoff=transform[1,3])

def section_contact(a,b,z):
    sa=section_poly(a,z);sb=section_poly(b,z)
    return float(sa.intersection(sb).area) if (sa is not None and sb is not None) else 0.0

contacts={}
for side in ['PORT','STBD']:
    bridge=scene.geometry[f'V17_{side}_HoodShoulderIntegratedWeb']
    intake=scene.geometry[f'V16_{side}_PhysicalIntakeOuterHousing']
    saddle=scene.geometry[f'V17_{side}_RearCowlStructuralSaddle']
    cowl=scene.geometry[f'V16_{side}_IntegratedRearCowlHaunch']
    for z in [1.0,1.45,1.8,2.3,2.75,3.0]:
        measurements={
            'hood':section_contact(bridge,hood,z),
            'hull':section_contact(bridge,hull,z),
            'intake':section_contact(bridge,intake,z),
        }
        contacts[f'{side}_hood_bridge_z_{z}']=measurements
        assert measurements['hood']>.008,('Disconnected hood',side,z,measurements)
        assert measurements['hull']>.04,('Disconnected central hull',side,z,measurements)
        assert measurements['intake']>.008,('Disconnected intake housing',side,z,measurements)
    for z in [-3.45,-3.1,-2.65,-2.2]:
        measurements={
            'cowl':section_contact(saddle,cowl,z),
            'hull':section_contact(saddle,hull,z),
        }
        contacts[f'{side}_rear_saddle_z_{z}']=measurements
        assert measurements['cowl']>.025 and measurements['hull']>.025,(side,z,measurements)

apron=scene.geometry['V17_ForgedHoodToWindshieldLoadBridge']
for z in [.25,.4]:
    assert section_contact(apron,hood,z)>.07
    assert section_contact(apron,hull,z)>.1
for z in [-.22,-.05,.16]:
    assert section_contact(apron,scene.geometry['V15_200_ReferenceAlignedOnePieceGreenhouse'],z)>.025

# GLB export. No in-scene reference images included.
data=scene.export(file_type='glb')
OUT.write_bytes(data)
saved=trimesh.load(OUT,force='scene',process=False)
assert len(saved.geometry)==len(scene.geometry)
assert set(saved.geometry)==set(scene.geometry)
ntris=sum(len(m.faces) for m in saved.geometry.values())
summary={
 'source_model':SRC.name,
 'model':OUT.name,
 'inspection_only':True,
 'unchanged_original_mesh_names':len(initial_names),
 'new_components':new_components,
 'hood_rear_station_m_before':.48,
 'hood_rear_station_m_after':.17,
 'hood_extension_m':.31,
 'mesh_count':len(saved.geometry),
 'triangles':ntris,
 'watertight_new_components':sum(saved.geometry[n].is_watertight for n in new_components),
 'body_parts_preserved':True,
 'verified_section_contacts_m2':contacts,
 'physical_section_checks':len(contacts),
 'known_limitation':'Separate overlapping armor pieces form an engineered assembly, not a single boolean-unioned/manifold chassis; visual inspection and in-game collision audit still needed.',
 'gate':'Gate 02 owner visual review pending',
}
REPORT.write_text(json.dumps(summary,indent=2)+'\n')
print('NFR_V17_CONNECTED_HOOD_GLB_OK',json.dumps({k:summary[k] for k in ['model','mesh_count','triangles','hood_extension_m','watertight_new_components']}))
