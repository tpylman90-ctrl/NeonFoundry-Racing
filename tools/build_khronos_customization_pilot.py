#!/usr/bin/env python3
"""Stage-01 real modular customization study from licensed Khronos CarConcept.

Not a production vehicle. Source CarConcept CC-BY-4.0; trademarks/logos excluded.
Original full car geometry is kept as reference; conventional wheel submeshes and
branding parts are omitted, donor imagery stripped for clay inspection. Parts
are exported as independent socket-local GLBs, ready for Godot installation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals

SOURCE_SHA = '659c592e20aba7afa920db7d14ad767874741384c215ee1df23a5e1c5e1c411c'
COLORS = {
    'body': ([174, 184, 194, 255], 0.76, 0.28),
    'trim': ([55, 65, 74, 255], 0.55, 0.48),
    'glass': ([45, 78, 96, 185], 0.18, 0.2),
    'duct': ([31, 34, 40, 255], 0.45, 0.63),
    'titanium': ([130, 139, 148, 255], 0.85, 0.35),
    'accent': ([219, 125, 72, 255], 0.40, 0.34),
    'glow': ([32, 190, 230, 255], 0.15, 0.22),
}


def material(key: str):
    rgba, metal, rough = COLORS[key]
    return PBRMaterial(name='NFR_Prototype_' + key, baseColorFactor=rgba,
                       metallicFactor=metal, roughnessFactor=rough,
                       doubleSided=(key == 'glass'))


def add(scene, name, mesh, mat='titanium'):
    assert name not in scene.geometry, name
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(name)
    assert len(mesh.faces) > 0, name
    mesh.visual = TextureVisuals(material=material(mat))
    scene.add_geometry(mesh, node_name=name, geom_name=name)
    return mesh


def box(scene, name, center, dimensions, mat='titanium'):
    mesh = trimesh.creation.box(extents=dimensions)
    mesh.apply_translation(center)
    return add(scene, name, mesh, mat)


def tube(scene, name, center, z0, z1, r_inner, r_outer, mat='titanium', segments=24):
    """Closed solid annulus with an actual longitudinal hollow bore."""
    assert 0 < r_inner < r_outer and z0 < z1
    vertices = []
    for z in (z0, z1):
        for radius in (r_outer, r_inner):
            for j in range(segments):
                a = j * math.tau / segments
                vertices.append([center[0]+radius*math.cos(a), center[1]+radius*math.sin(a), center[2]+z])
    faces=[]
    for ring in (0,1):
        a=ring*segments; b=(ring+2)*segments
        for i in range(segments):
            j=(i+1)%segments
            if ring==0:
                faces.extend([[a+i,a+j,b+j],[a+i,b+j,b+i]])
            else:
                faces.extend([[a+i,b+j,a+j],[a+i,b+i,b+j]])
    for base in (0,2*segments):
        for i in range(segments):
            j=(i+1)%segments
            if base==0:
                faces.extend([[base+i,base+segments+i,base+segments+j],
                              [base+i,base+segments+j,base+j]])
            else:
                faces.extend([[base+i,base+j,base+segments+j],
                              [base+i,base+segments+j,base+segments+i]])
    mesh=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
    trimesh.repair.fix_normals(mesh)
    assert mesh.is_watertight and mesh.is_winding_consistent
    return add(scene,name,mesh,mat)


def rod(scene, name, start, end, radius=.025, mat='titanium', sections=12):
    a,b=np.asarray(start,float),np.asarray(end,float)
    d=b-a
    length=np.linalg.norm(d)
    assert length>1e-3
    mesh=trimesh.creation.cylinder(radius=radius,height=length,sections=sections)
    mesh.apply_transform(trimesh.geometry.align_vectors([0,0,1],d/length))
    mesh.apply_translation((a+b)*.5)
    return add(scene,name,mesh,mat)


def fin(scene, name, sign, profile, thickness=.055, material_id='body'):
    """Manufactured plate in Y/Z with finite X thickness and inclined upper tip."""
    x=sign*.70
    coords=[(z,y) for z,y in profile]
    n=len(coords)
    verts=[]
    for sx in (-thickness*.5,thickness*.5):
        for z,y in coords:
            verts.append([x+sx+sign*(y-.1)*.23,y,z])
    faces=[]
    for i in range(1,n-1):
        faces.extend([[0,i+1,i],[n,n+i,n+i+1]])
    for i in range(n):
        j=(i+1)%n
        faces.extend([[i,j,n+j],[i,n+j,n+i]])
    mesh=trimesh.Trimesh(vertices=verts,faces=faces,process=False)
    trimesh.repair.fix_normals(mesh)
    assert mesh.is_watertight
    return add(scene,name,mesh,material_id)


def donor_body(source):
    s=trimesh.load(source,force='scene',process=False)
    result=trimesh.Scene()
    preserved=[]
    removed=[]
    for node in s.graph.nodes_geometry:
        T,key=s.graph[node]
        lower=node.lower()
        # Wheel shells have numeric export names but are independent meshes.
        discard=(lower.startswith('wheel') or node.startswith(('99_','94_','89_','84_'))
                 or lower in ('axles','license plate','interiorsteeringemblem'))
        if discard:
            removed.append(node)
            continue
        mesh=s.geometry[key].copy()
        mesh.apply_transform(T)
        kind=('glass' if 'window' in lower or 'windshield' in lower or 'rearwindow' in lower else
              'trim' if ('interior' in lower or 'under' in lower or 'grill' in lower or 'wiper' in lower) else 'body')
        add(result,'DONOR_'+node,mesh,kind)
        preserved.append(node)
    assert len(preserved)>60 and len(removed)>15
    return result, preserved, removed


def engine(tier):
    """Four REAL discrete rear cassettes, escalating bore / cooling / booster count."""
    scene=trimesh.Scene()
    specs=[(.175,.71,0),(.210,.84,0),(.245,.94,0),(.278,1.06,2)]
    radius,length,boosters=specs[tier]
    box(scene, 'CASSETTE_CORE_CRADLE', (0,0,-.06),(1.33,.20,.25),'trim')
    for side in (-1,1):
        x=side*.41
        box(scene,f'MAIN_{side}_ENGINE_BLOCK',(x,0,-.15),(.43,.36,.42),'body')
        for k in range(2):
            rod(scene,f'MAIN_{side}_MOUNT_{k}',(x,(-1 if k==0 else 1)*.17,.07),
                (x,(-1 if k==0 else 1)*.19,-.28),.030,'accent')
        tube(scene,f'MAIN_{side}_HOLLOW_BELL',(x,0,0),-.20-length,-.19, radius*.67,radius,'titanium')
        tube(scene,f'MAIN_{side}_INNER_RIM',(x,0,0),-.21-length,-.16-length,radius*.63,radius*.77,'duct')
        tube(scene,f'MAIN_{side}_EMITTER_RING',(x,0,0),-.15-length,-.11-length,radius*.48,radius*.57,'glow')
        for k in range(3+tier):
            z=-.32-k*(length-.26)/(3+tier)
            tube(scene,f'MAIN_{side}_HEAT_RING_{k}',(x,0,0),z-.026,z+.026,radius*.89,radius*1.07,'trim',16)
    if boosters:
        for side in (-1,1):
            x=side*.22
            tube(scene,f'UPPER_{side}_BOOSTER_BORE',(x,.23,0),-.77,-.13,.065,.102,'titanium',20)
            tube(scene,f'UPPER_{side}_BOOSTER_COIL',(x,.23,0),-.78,-.72,.056,.08,'glow',20)
            rod(scene,f'UPPER_{side}_BOOSTER_BRACKET',(x,.09,-.15),(x,.23,-.15),.026,'accent')
    return scene


def fins(kit):
    scene=trimesh.Scene()
    profiles=[
        [(-.55,0),(.15,0),(.04,.22),(-.36,.19)],
        [(-.60,0),(.22,0),(-.02,.46),(-.16,.54),(-.48,.34)],
        [(-.66,0),(.23,0),(.11,.50),(-.13,.67),(-.52,.58)],
    ]
    for side in (-1,1):
        fin(scene,f'{kit}_FIN_{side}',side,profiles[kit],.06 if kit<2 else .09, 'body')
        box(scene,f'{kit}_FIN_MOUNT_{side}',(side*.70,.0,-.16),(.22,.09,.39),'titanium')
        if kit==2:
            for k in range(2):
                rod(scene,f'{kit}_FIN_BRACE_{side}_{k}',(side*.70,.03,-.49+k*.36),
                    (side*.7,.29,-.34+k*.22),.027,'trim')
    return scene


def intakes(kit):
    scene=trimesh.Scene()
    radius=[.18,.22,.27][kit]
    for side in (-1,1):
        center=(side*1.03,.015,0)
        tube(scene,f'{kit}_SIDE_INTAKE_BORE_{side}',center,-.27,.33,radius*.67,radius,'duct',16)
        tube(scene,f'{kit}_SIDE_INTAKE_LIP_{side}',center,.29,.40,radius*.73,radius*1.18,'body',16)
        box(scene,f'{kit}_INTAKE_MOUNT_PLATE_{side}',(side*.96,-.12,.10),(.19,.09,.72),'titanium')
        for k in range(2+kit):
            z=-.18+k*.14
            rod(scene,f'{kit}_INTAKE_SPLITTER_{side}_{k}',(side*.97,-.10,z),
                (side*1.12,.14,z-.04),.020,'trim')
    return scene


def splitters(kit):
    scene=trimesh.Scene()
    box(scene,f'{kit}_FRONT_SPLITTER_CENTER',(0,0,.03),(1.8,.065,.21),'body')
    for side in (-1,1):
        reach=[.12,.25,.38][kit]
        box(scene,f'{kit}_FRONT_SPLITTER_CANARD_{side}',(side*(.91+reach*.28),.02,-.045),
            (.40+reach,.07,.34),'titanium')
        if kit>0:
            rod(scene,f'{kit}_CANARD_SUPPORT_{side}',(side*.84,.10,-.12),
                (side*(.92+reach*.46),-.03,-.12),.026,'trim')
    return scene


def skirts(kit):
    scene=trimesh.Scene()
    for side in (-1,1):
        width=[.07,.13,.19][kit]
        box(scene,f'{kit}_ROCKER_SKIRT_{side}',(side*.01,-.015,0),(.01,.01,.01),'trim') if False else None
        box(scene,f'{kit}_ROCKER_BLADE_{side}',(side*(1.02+width*.5),-.015,-.12),
            (width,.08,1.85),'body')
        if kit>0:
            for k in range(2):
                rod(scene,f'{kit}_ROCKER_TRUSS_{side}_{k}',(side*1.0,.10,-.60+k*.88),
                    (side*(1.03+width),-.04,-.48+k*.88),.027,'titanium')
    return scene


def lift_module():
    scene=trimesh.Scene()
    # In FRONT wheel locations, retains and occupies wheel arch for hybrid.
    box(scene,'FRONT_LIFT_MOUNT',(0,0,0),(.31,.23,.38),'trim')
    # Downward hover emitter is ring in X/Z horizontal plane. Cylinder about
    # local Z by default, rotate to vertical Y for actual downward lift.
    body=trimesh.creation.cylinder(radius=.22,height=.17,sections=24)
    body.apply_transform(trimesh.transformations.rotation_matrix(math.pi*.5,[1,0,0]))
    body.apply_translation((0,-.16,0))
    add(scene,'FRONT_LIFT_ARMOR_SHROUD',body,'body')
    for i in range(12):
        angle=i*math.tau/12
        x,z=.17*math.cos(angle),.17*math.sin(angle)
        rod(scene,f'FRONT_LIFT_RIB_{i}',(x,-.16,z),(x*.79,-.24,z*.79),.021,'titanium')
    return scene


def rear_lift():
    scene=trimesh.Scene()
    tube(scene,'AFT_LIFT_EMITTER', (0,0,0),-.16,.16,.15,.23,'titanium')
    # rotate all parts to face DOWN, so not a sideways fake wheel.
    rot=trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0])
    for mesh in scene.geometry.values():
        mesh.apply_transform(rot)
    box(scene,'AFT_LIFT_CARRIER',(0,.14,0),(.37,.12,.48),'trim')
    return scene


SOCKETS={
    'rear_engine':[0,.57,-1.83],
    'rear_fins':[0,1.02,-1.05],
    'side_intakes':[0,.49,.15],
    'front_splitter':[0,.18,2.24],
    'side_skirts':[0,.27,0],
    'front_lift_port':[-1.03,.38,1.47],
    'front_lift_starboard':[1.03,.38,1.47],
    'rear_lift_port':[-.84,.22,-1.30],
    'rear_lift_starboard':[.84,.22,-1.30],
}


def compose(base, modules):
    result=base.copy()
    for slot, (scene, _) in modules.items():
        offset=np.array(SOCKETS[slot])
        for name,m in scene.geometry.items():
            g=m.copy();g.apply_translation(offset)
            add(result,f'INSTALLED_{slot}_{name}',g,
                'glass' if 'GLASS' in name else 'accent' if 'EMITTER' in name or 'COIL' in name else 'titanium')
    return result


def export(scene,path):
    scene.export(file_obj=path,file_type='glb')
    reload=trimesh.load(path,force='scene',process=False)
    assert len(reload.geometry)==len(scene.geometry)
    assert all(np.isfinite(m.vertices).all() for m in reload.geometry.values())
    return sum(len(m.faces) for m in reload.geometry.values())


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,default=Path('build/khronos_donor/CarConcept_ORIGINAL.glb'))
    p.add_argument('--out',type=Path,default=Path('build/khronos_modular'))
    a=p.parse_args()
    assert a.source.is_file(),a.source
    actual=hashlib.sha256(a.source.read_bytes()).hexdigest()
    assert actual==SOURCE_SHA,(actual,SOURCE_SHA)
    a.out.mkdir(parents=True,exist_ok=True)
    base,preserved,removed=donor_body(a.source)
    basepath=a.out/'modular_base_clay.glb'
    triangles=export(base,basepath)
    manifest={
        'schema_version':1,'vehicle':'NF-H01 Khronos automotive donor conversion study',
        'source':'KhronosGroup/glTF-Sample-Assets/Models/CarConcept',
        'license':'CC-BY-4.0, original contributors must be credited; Khronos trademarks excluded',
        'donor_sha256':actual,'stage':'interchangeable module test; NOT a finished FORGE racer',
        'model_forward':'+Z','units':'meters','donor_meshes_preserved':len(preserved),
        'removed_nodes':removed,'donor_base_triangles':triangles,
        'base_scene':'res://assets/vehicle_modular/modular_base_clay.glb',
        'sockets':{name:{'position_m':v} for name,v in SOCKETS.items()},
        'slots':{},'default_loadout':{},'preview_loadouts':{},
        'limitations':['Original rear wheel arch topology not yet reconstructed; no cosmetic covers claimed as seamless.',
                       'Existing donor paint materials replaced with unbranded inspection clay.',
                       'First stage is high-poly; game-ready LOD and collision not completed.',
                       'Sculpted donor body/roof untouched; kit exterior seams and mounts still need visual inspection.']
    }
    def mod(slot,part_id,display,scene,style='',stats=None):
        filename=f'{part_id}.glb'
        assert slot in SOCKETS
        t=export(scene,a.out/filename)
        item={'id':part_id,'name':display,'scene':'res://assets/vehicle_modular/'+filename,
              'triangles':t,'style':style}
        if stats is not None:item['stats']=stats
        manifest['slots'].setdefault(slot,[]).append(item)
        return scene,item
    catalog={}
    engines=['Foundry Pulse','Vortex Twin','Titan Vector','Nova Overdrive']
    for tier,name in enumerate(engines):
        ident=['engine_stock','engine_vortex','engine_titan','engine_nova'][tier]
        catalog[ident]=mod('rear_engine',ident,name,engine(tier),stats={
            'thrust':1.0+tier*.18,'heat':1.0+tier*.26,'mass':1.0+tier*.16,
            'boost':1.0+tier*.21,'tier':tier})
    kits=['Street Phantom','Aero Strike','Industrial Forge']
    for kit,style in enumerate(kits):
        for slot,prefix,func in [('rear_fins','fins',fins),('side_intakes','intakes',intakes),
                                  ('front_splitter','splitter',splitters),('side_skirts','skirts',skirts)]:
            ident=f'{prefix}_{kit}'
            catalog[ident]=mod(slot,ident,f'{style} {slot.replace("_"," ")}',func(kit),style)
    lift=lift_module()
    aft=rear_lift()
    for slot in ('front_lift_port','front_lift_starboard'):
        ident=slot+'_stock';catalog[ident]=mod(slot,ident,'Factory forward hover cassette',lift,'factory')
    for slot in ('rear_lift_port','rear_lift_starboard'):
        ident=slot+'_stock';catalog[ident]=mod(slot,ident,'Factory underside lift emitter',aft,'factory')
    manifest['default_loadout']={
        'rear_engine':'engine_stock', 'rear_fins':'fins_0',
        'side_intakes':'intakes_0','front_splitter':'splitter_0','side_skirts':'skirts_0',
        **{p:p+'_stock' for p in ('front_lift_port','front_lift_starboard','rear_lift_port','rear_lift_starboard')}
    }
    for label,k,eng in [('street',0,'engine_stock'),('aero',1,'engine_vortex'),('industrial',2,'engine_nova')]:
        preset=manifest['default_loadout'].copy()
        preset.update({'rear_engine':eng,'rear_fins':f'fins_{k}','side_intakes':f'intakes_{k}',
                       'front_splitter':f'splitter_{k}','side_skirts':f'skirts_{k}'})
        manifest['preview_loadouts'][label]=preset
        selected={slot:catalog[pid] for slot,pid in preset.items()}
        preview=compose(base,selected)
        preview_tris=export(preview,a.out/f'preview_{label}.glb')
        print('NFR_KHRONOS_PREVIEW',label,len(preview.geometry),preview_tris,flush=True)
    (a.out/'module_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # Diagnostics and reproducible attribution kept with the downloadable GLBs.
    (a.out/'LICENSE_ATTRIBUTION.txt').write_text(
        'Car Concept original contributed to the Khronos glTF-Sample-Assets project; '
        'CC BY 4.0. Source: https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/CarConcept\n'
        'Original geometry modified by removal of wheels/branding nodes and neutral-material substitution; '
        'new FORGE modular engine, intake, aero, and lift objects added separately.\n'
        'Khronos logos and trademarks are not licensed with the model.\n'
    )
    assert len(manifest['slots']['rear_engine'])==4
    assert len(manifest['slots']['rear_fins'])==3
    assert len(manifest['slots']['side_intakes'])==3
    assert len(manifest['slots'])==9
    print('NFR_KHRONOS_MODULAR_PILOT_OK',json.dumps({'base_meshes':len(base.geometry),
          'base_triangles':triangles,'slots':len(SOCKETS), 'modular_scenes':sum(map(len,manifest['slots'].values()))}),flush=True)

if __name__=='__main__':main()
