#!/usr/bin/env python3
"""Independent mesh and cross-sectional attachment audit for FORGE V18.04."""
import argparse,hashlib,json,struct
from pathlib import Path
import trimesh,numpy as np

p=argparse.ArgumentParser()
p.add_argument('--base',type=Path,required=True)
p.add_argument('--model',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
base=trimesh.load(a.base,force='scene',process=False)
model=trimesh.load(a.model,force='scene',process=False)
assert len(base.geometry)==396 and len(model.geometry)==557
assert sum(len(m.faces) for m in model.geometry.values())==38596
assert set(base.geometry).issubset(model.geometry)
for name in base.geometry:
    m,n=base.geometry[name],model.geometry[name]
    assert np.array_equal(m.vertices,n.vertices),('Source vertices changed',name)
    assert np.array_equal(m.faces,n.faces),('Source faces changed',name)
assert all(m.is_watertight and m.is_winding_consistent for m in model.geometry.values())

raw=a.model.read_bytes()
magic,version,total=struct.unpack_from('<4sII',raw,0)
assert (magic,version,total)==(b'glTF',2,len(raw))
size,kind=struct.unpack_from('<I4s',raw,12)
assert kind==b'JSON'
gltf=json.loads(raw[20:20+size])
blend_materials=sum(1 for mat in gltf.get('materials',[]) if mat.get('alphaMode')=='BLEND')
assert blend_materials>=3,('Missing physically translucent canopy/HUD materials',blend_materials)


def cross_area(m,z):
    s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    if s is None: raise AssertionError(('No physical section at z',z))
    polygons=s.to_2D()[0].polygons_full
    assert polygons
    return polygons[0]

def contact(first,second,z,minimum):
    assert first in model.geometry and second in model.geometry,(first,second)
    s1=cross_area(model.geometry[first],z)
    s2=cross_area(model.geometry[second],z)
    area=float(s1.intersection(s2).area)
    assert area>=minimum, (first,second,z,area,minimum)
    return round(area,7)

contacts={}
for side in ('PORT','STBD'):
    tests=[
      ('canopy mount ↔ approved upper sill',f'UPPER_SILL_{side}_06',f'V18_04_MOUNT_{side}_SillClamp_02',-1.24,.006),
      ('aft cowl saddle ↔ approved upper sill',f'UPPER_SILL_{side}_08',f'V18_04_COWL_{side}_004_SaddleFoot_1',-3.12,.006),
      ('front fairing ↔ approved upper sill',f'UPPER_SILL_{side}_06',f'V18_04_CANOPY_{side}_PressedSillFairing_0',-1.24,.002),
      ('rear fairing ↔ approved upper sill',f'UPPER_SILL_{side}_07',f'V18_04_CANOPY_{side}_PressedSillFairing_1',-1.89,.002),
      ('canopy foot ↔ preserved rear hood',f'V18_03_HOOD_011_{side}_PressedOuterBonnet',f'V18_04_MOUNT_{side}_BonnetInterface',.22,.012),
    ]
    for label,x,y,z,minimum in tests:
        contacts[f'{side} {label} at z={z}m']=contact(x,y,z,minimum)
    assert f'V18_04_GLASS_{side}_ForwardLaminatedWindscreen' in model.geometry
    assert f'V18_04_INTERIOR_{side}_HarnessWeb' in model.geometry
    assert f'V18_04_COWL_{side}_002_SplitSidePlate_0' in model.geometry
assert len(contacts)==10

report={
 'asset':'FORGE V18.04 - modular canopy, cockpit, and aft roof transition',
 'gate':'Unapproved inspection experiment',
 'base_mesh_count':396,
 'new_mesh_count':161,
 'total_mesh_count':557,
 'triangle_count':38596,
 'part_materials_with_alpha_blend':blend_materials,
 'all_parts_closed_with_consistent_normals':True,
 'previous_meshes_exactly_unchanged':True,
 'verified_cross_section_contacts_m2':contacts,
 'contact_measurement':'Positive XY area shared by independent solid meshes at stated Z planes; proves interpenetration, not a global boolean union or structural load rating',
 'base_sha256':hashlib.sha256(a.base.read_bytes()).hexdigest(),
 'export_sha256':hashlib.sha256(raw).hexdigest(),
 'source_geometry_modified':False,
 'production_replacement':False,
}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(report,indent=2)+'\n')
print('NFR_V18_04_INDEPENDENT_GEOMETRY_QA_OK',len(contacts),'contacts',len(model.geometry),'meshes',flush=True)
