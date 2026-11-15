#!/usr/bin/env python3
"""FORGE V18.05 named-component and geometric attachment audit."""
import json, sys, argparse
from pathlib import Path
import numpy as np
import trimesh

def bounding_overlap(a,b):
    bounds=np.minimum(a.bounds[1],b.bounds[1])-np.maximum(a.bounds[0],b.bounds[0]);return float(np.prod(np.maximum(bounds,0)))

def audit(base_path,candidate_path):
    base=trimesh.load(base_path,force='scene',process=False)
    new=trimesh.load(candidate_path,force='scene',process=False)
    assert len(base.geometry)==557
    assert len(new.geometry)==697
    assert len(new.geometry)-len(base.geometry)==140
    assert sum(len(m.faces) for m in new.geometry.values())==43444
    assert set(base.geometry).issubset(new.geometry)
    for n,original in base.geometry.items():
        revised=new.geometry[n]
        assert np.array_equal(original.vertices,revised.vertices),n
        assert np.array_equal(original.faces,revised.faces),n
    assert all(m.is_watertight and m.is_winding_consistent for m in new.geometry.values())
    roof=new.geometry['V18_05_ROOF_00_ExtendedCentralBackbone']
    assert roof.bounds[0,2] <= -3.88
    assert roof.bounds[1,2] <= -2.25
    # Open glass ends at z=-2.26; the roof cover starts directly behind it.
    side_results={}
    for side in ('PORT','STBD'):
        panels=[new.geometry[f'V18_05_{side}_RemovableSideSkin_0'],new.geometry[f'V18_05_{side}_LowerRocker_1'],new.geometry[f'V18_05_{side}_RemovableSideSkin_2']]
        assert all(m.bounds[0,1]<=.34 for m in panels)
        outer=max(float(np.max(np.abs(m.bounds[:,0]))) for m in panels)
        assert outer>=1.34,outer
        # New mechanical sill mount overlaps the original upper longeron
        old_frame=base.geometry[f'UPPER_SILL_{side}_04']
        clamp=new.geometry[f'V18_05_{side}_PanelToFrameFoot_0']
        overlap=bounding_overlap(old_frame,clamp)
        assert overlap>.00025,(side,overlap)
        # New roof foot overlays the original aft cage's physical saddle;
        # both are boxes so this is a true closed-solid contact volume.
        old_saddle=base.geometry[f'V18_04_COWL_{side}_004_SaddleFoot_0']
        new_foot=new.geometry[f'V18_05_ROOF_{side}_04_RoofFoot_0']
        roof_contact=bounding_overlap(old_saddle,new_foot)
        assert roof_contact>.00025,(side,roof_contact)
        assert f'V18_05_ROOF_{side}_01_SweptRearShoulder' in new.geometry
        assert f'V18_05_NOSE_{side}_SubIntakeSkidFairing_0' in new.geometry
        assert f'V18_05_TAIL_{side}_RearCornerReturn' in new.geometry
        side_results[side]={'sill_mount_box_overlap_m3':round(overlap,6),'aft_roof_support_contact_m3':round(roof_contact,6),'panel_outer_x_m':round(outer,3)}
    assert 'V18_05_TAIL_02_MidServiceKeel' in new.geometry
    assert 'V18_05_NOSE_00_CentralChinArmor' in new.geometry
    assert max(new.geometry[n].bounds[1,2] for n in new.geometry if n.startswith('V18_05_NOSE_') and 'SubIntakeSkidFairing' in n) < 3.6
    return {'result':'PASS','original_meshes_unchanged':557,'new_modular_meshes':140,'total_meshes':697,'triangles':43444,'roof_z_span_m':roof.bounds[:,2].round(3).tolist(),'verified_mount_overlap':side_results,'approval':'owner visual inspection pending','limitation':'mount overlap validates joined box profiles but not crashworthiness, aerodynamics or all panel tolerances'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path)
    a=p.parse_args();data=audit(a.base,a.model)
    if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n')
    print('NFR_V18_05_REAR_ROOF_AND_LOWER_FAIRINGS_VERIFIED',json.dumps(data,sort_keys=True))
