#!/usr/bin/env python3
"""Independent geometry QA of V18.03, including physical section contacts.

Reports actual CAD-like planar cross-section overlap instead of pretending that
axis-aligned bounding boxes prove the front intakes are attached.
"""
import argparse
import json
import struct
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point


def section_polygon(mesh, z):
    section=mesh.section(plane_origin=[0,0,float(z)],plane_normal=[0,0,1])
    if section is None: raise ValueError(f'No section at z {z}')
    paths=[]
    for pts in section.discrete:
        p=Polygon(pts[:,:2])
        if p.is_valid and p.area>1e-10:paths.append(p)
    if not paths:raise ValueError('Section polygon is empty')
    paths.sort(key=lambda x:x.area,reverse=True)
    outer=paths[0]
    for sub in paths[1:]:
        if outer.contains(sub.representative_point()):outer=outer.difference(sub)
        else:outer=outer.union(sub)
    return outer


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--frame',type=Path,required=True)
    p.add_argument('--model',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    raw=args.model.read_bytes()
    magic,version,size=struct.unpack_from('<4sII',raw,0)
    assert (magic,version,size)==(b'glTF',2,len(raw))
    old=trimesh.load(args.frame,force='scene',process=False)
    new=trimesh.load(args.model,force='scene',process=False)
    assert len(old.geometry)==235
    assert len(new.geometry)==396,(len(new.geometry))
    assert set(old.geometry).issubset(new.geometry)
    assert all(g.is_watertight and g.is_winding_consistent and g.is_volume for g in new.geometry.values())
    for name,a in old.geometry.items():
        b=new.geometry[name]
        assert np.array_equal(a.faces,b.faces),name
        assert np.array_equal(a.vertices,b.vertices),name
    contacts={}
    def check(k,a,b,z,threshold):
        area=section_polygon(new.geometry[a],z).intersection(section_polygon(new.geometry[b],z)).area
        assert area>=threshold,(k,area,threshold)
        contacts[k]=round(float(area),7)
    check('central_deck_to_approved_crossmember', 'V18_03_HOOD_001_StructuralDeck','UPPER_CROSSBRACE_00',3.55,.045)
    for side,sg in (('PORT',-1),('STBD',1)):
        pre=f'V18_03_HOOD_017_{side}_ForwardShoulderTiePlate'
        check(side+'_hood_to_bridge',f'V18_03_HOOD_011_{side}_PressedOuterBonnet',pre,3.05,.0008)
        check(side+'_bridge_to_intake_top',pre,f'V18_03_INTAKE_{side}_010_FrontTopArmor',3.05,.0035)
        check(side+'_intake_to_real_clevis',f'V18_03_INTAKE_{side}_001_OpenBoreWall',f'V18_03_INTAKE_{side}_004_Clevis_0',2.75,.08)
        opening=section_polygon(new.geometry[f'V18_03_INTAKE_{side}_001_OpenBoreWall'],3.68)
        assert not opening.contains(Point(sg*1.40,1.08)), 'Intake face is sealed, not hollow'
    result={
        'frame_meshes_unmodified':235,
        'added_separate_components':161,
        'total_meshes':396,
        'total_triangles':sum(len(m.faces) for m in new.geometry.values()),
        'all_objects_individually_manifold':True,
        'real_ducts_open_to_air':True,
        'verified_planar_cross_section_overlap_m2':contacts,
        'approval':'pending owner visual inspection',
    }
    assert result['total_triangles']==18056
    args.out.parent.mkdir(exist_ok=True,parents=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print('NFR_V18_03_INTAKE_HOOD_PHYSICAL_CONTACTS_VERIFIED',json.dumps(result))

if __name__=='__main__':main()
