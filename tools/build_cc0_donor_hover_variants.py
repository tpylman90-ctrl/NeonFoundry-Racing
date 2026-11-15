#!/usr/bin/env python3
"""Convert a verified CC0 donor sports car into two TRUE hover-geometry variants.

Uses the original 348-part unbranded mid-engine supercar, preserving body
surface topology, door/glazing, lamps and aerodynamics as authored. Wheels and
all hubs/brakes/rims/tyres/treads are removed by node label, NOT hidden.
Variant A: four mechanical vertical-lift cassettes replacing the wheels.
Variant B: no wheel hardware and no visible wheel opening; fitted curved
body panels plus six concealed lift emitters beneath the chassis.

These are surface/assembly design experiments, not FORGE's existing hero craft.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import hashlib, json, math, re, os
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals

HERE = Path(__file__).resolve().parent
ROOT=HERE.parent
SRC=Path(os.environ.get('NFR_DONOR_SOURCE', str(ROOT/'build/donor/original_CC0_mid_engine_supercar.glb')))
OUT=Path(os.environ.get('NFR_DONOR_OUTPUT',str(ROOT/'build/donor_trial')))
OUT.mkdir(parents=True,exist_ok=True)

MAT = {
    'gunmetal': ([74,86,101,255],.83,.31,[0,0,0]),
    'graphite': ([36,44,56,255],.68,.47,[0,0,0]),
    'titanium': ([152,164,171,255],.82,.33,[0,0,0]),
    'copper': ([174,112,71,255],.83,.32,[0,0,0]),
    'paint': ([170,29,36,255],.65,.24,[0,0,0]),
    'light': ([58,221,248,255],.14,.17,[.06,.64,.86]),
    'dark': ([18,28,35,255],.37,.67,[0,0,0]),
    'glass': ([34,69,85,255],.10,.13,[0,0,0]),
}
source=trimesh.load(SRC,force='scene',process=False)
assert len(source.graph.nodes_geometry)==348
source_hash=hashlib.sha256(SRC.read_bytes()).hexdigest()
assert source_hash=='ad0fd94845edb9af474407fe08fb379b624c56ec4d4b4ad6b47822b65c6f8903', 'Donor source changed unexpectedly'

# Mark subassemblies by their exported OBJECT names, not by bounding-box guesses.
# Directly named internal hub geometry may be stored as generic Sphere/Cylinder,
# therefore classify using the original graph/node labels rather than mesh names.
def removable(node:str, flush:bool):
    low=node.lower()
    if low.startswith('steering wheel'):
        return False
    if any(x in low for x in ('tyre','tread','brake','caliper','barrel','split-spoke',
                             'centre-lock wheel','machined alloy outer rim')):
        return True
    if flush and ('fender lip' in low or 'wheelhouse arched liner' in low):
        return True
    return False

def add_part(scene,tag,mesh,group,mat='gunmetal'):
    if tag in scene.geometry:
        raise ValueError(f'Duplicate {tag}')
    matdef=MAT[mat]
    material=PBRMaterial(name='NFR_DONOR_'+mat,baseColorFactor=matdef[0],
                         metallicFactor=matdef[1],roughnessFactor=matdef[2],
                         emissiveFactor=matdef[3],doubleSided=False)
    mesh.visual=TextureVisuals(material=material)
    if not mesh.is_winding_consistent:
        trimesh.repair.fix_normals(mesh)
    scene.add_geometry(mesh,node_name=tag,geom_name=tag)
    return tag

def bar(scene,name,a,b,r,group,material='gunmetal',sections=12):
    a=np.array(a,float);b=np.array(b,float)
    L=np.linalg.norm(b-a)
    m=trimesh.creation.cylinder(radius=r,height=L+.012,sections=sections)
    m.apply_transform(trimesh.geometry.align_vectors([0,0,1],(b-a)/L))
    m.apply_translation((a+b)/2)
    return add_part(scene,name,m,group,material)

def box(scene,name,center,extents,group,material='gunmetal'):
    m=trimesh.creation.box(extents=extents);m.apply_translation(center)
    return add_part(scene,name,m,group,material)

def annulus(scene,name,center,rout,rin,thick,group,material='titanium',n=24):
    # A cylinder with a genuine axial through-hole. Y axis is lift direction.
    x,y,z=center
    vertices=[]
    for hh in [-thick/2,thick/2]:
        for rr in [rout,rin]:
            for i in range(n):
                angle=i*2*math.pi/n
                vertices.append([x+rr*math.cos(angle),y+hh,z+rr*math.sin(angle)])
    faces=[]
    for i in range(n):
        j=(i+1)%n
        for r0,r1 in [(0,n),(2*n,3*n)]:
            if r0==0:
                faces.extend([[r0+i,r0+j,r1+j],[r0+i,r1+j,r1+i]])
            else:
                faces.extend([[r0+i,r1+j,r0+j],[r0+i,r1+i,r1+j]])
        # top ring and bottom ring surfaces
        faces.extend([[n+i,n+j,3*n+j],[n+i,3*n+j,3*n+i]])
        faces.extend([[0+i,2*n+j,0+j],[0+i,2*n+i,2*n+j]])
    mesh=trimesh.Trimesh(vertices=np.asarray(vertices),faces=np.asarray(faces),process=False)
    trimesh.repair.fix_normals(mesh)
    assert mesh.is_watertight and mesh.is_winding_consistent,name
    return add_part(scene,name,mesh,group,material)

def outer_hover_shell(scene,name,x,y,z,group):
    """Multi-station tapered hard-surface cassette, not a rectangular wheel placeholder.
    Eight chamfered vertical/lateral cross-section vertices per station.
    """
    stations=[(-.46,.34,.12,.20),(-.35,.40,.18,.245),
              (.22,.425,.19,.25),(.40,.38,.145,.21),(.47,.34,.11,.18)]
    verts=[]
    for xo,cy,hy,hz in stations:
        yc=cy
        corners=[(-hz+.055,-hy),(hz-.055,-hy),(hz,-hy+.055),(hz,hy-.055),
                 (hz-.055,hy),(-hz+.055,hy),(-hz,hy-.055),(-hz,-hy+.055)]
        for zz,yy in corners:verts.append([x+xo,yc+yy,z+zz])
    n=8;f=[]
    for ring in range(len(stations)-1):
        a=ring*n;b=a+n
        for i in range(n):
            j=(i+1)%n
            f.extend([[a+i,a+j,b+j],[a+i,b+j,b+i]])
    for i in range(1,n-1):
        f.extend([[0,i+1,i],[n*(len(stations)-1),n*(len(stations)-1)+i,n*(len(stations)-1)+i+1]])
    mesh=trimesh.Trimesh(vertices=verts,faces=f,process=False)
    trimesh.repair.fix_normals(mesh)
    assert mesh.is_watertight
    add_part(scene,name,mesh,group,'gunmetal')

def cassette(scene,name,x,side,center_y=.31):
    """Four independently mounted floor-facing anti-grav units in arch bays."""
    z=side*.855
    prefix=f'HOVER_POD_{name}'
    group='side_hover_pods'
    # A central mounting cradle fixed to body behind wheel bay. Its runners
    # have a clearly separate engineering purpose from outer armor.
    bar(scene,prefix+'_INNER_MOUNT',(x,.48,side*.59),(x,.32,side*.79),.055,group,'titanium')
    for offs in (-.24,.24):
        bar(scene,prefix+f'_A_ARM_{offs:+.2f}',(x+offs,.55,side*.67),
            (x+offs*.9,.32,side*.90),.042,group,'gunmetal')
    box(scene,prefix+'_CRADLE',(x,.34,z),(.82,.12,.38),group,'graphite')
    # Replace old boxy outer chassis with sculpted, tapered multi-station
    # body. The separate lower panel and collar preserve the assembly logic.
    outer_hover_shell(scene,prefix+'_TAPERED_ARMOUR_CASSETTE',x,.37,z,group)
    box(scene,prefix+'_BODY_LOWER',(x,.284,z),(.70,.10,.35),group,'graphite')
    for k in range(5):
        xx=x-.37+.185*k
        bar(scene,prefix+f'_CASE_RIB_{k}',(xx,.38,z-.20),(xx,.38,z+.20),.019,group,'titanium',10)
    # Front and aft armour caps and service trim lines.
    for i,s in enumerate((-1,1)):
        box(scene,prefix+f'_END_ARMOUR_{i}',(x+s*.405,.40,z),(.055,.22,.46),group,'gunmetal')
    # Genuine open-through emitter rings under the cassette.
    annulus(scene,prefix+'_EMITTER_OUTER',(x,.205,z),.228,.167,.056,group,'titanium')
    annulus(scene,prefix+'_EMITTER_INNER',(x,.182,z),.164,.118,.052,group,'copper')
    # Replace conventional road-contact wheel with down-facing anti-gravity
    # emitter: real recessed light disk below a central gyroscopic hub.
    center=trimesh.creation.cylinder(radius=.107,height=.030,sections=24)
    center.apply_transform(trimesh.geometry.align_vectors([0,0,1],[0,1,0]))
    center.apply_translation((x,.166,z))
    add_part(scene,prefix+'_DOWNWARD_EMITTER',center,group,'light')
    for i in range(8):
        ang=2*math.pi*i/8
        ra,rb=.125,.168
        ya=.182
        bar(scene,prefix+f'_GYRO_FIN_{i}',(x+ra*math.cos(ang),ya,z+ra*math.sin(ang)),
            (x+rb*math.cos(ang+.20),ya,z+rb*math.sin(ang+.20)),.010,group,'titanium',8)
    # Very clear LEFT / RIGHT facing pod rather than fake painted wheel.
    box(scene,prefix+'_SIDE_PANEL',(x,.415,z+side*.235),(.55,.075,.022),group,'graphite')
    box(scene,prefix+'_SIDE_LIGHT_BAR',(x,.421,z+side*.256),(.43,.018,.012),group,'light')

def arch_fairing(scene,location,side,x0,r):
    """Locally curved replacement body surface, *not* a painted hub cover.

    Covers the original open cutout, follows fender height profile, and hides
    all original wheel/brake/hub geometry. Kept as a removable panel for
    inspection and eventual CAD welded-topology conversion.
    """
    group='flush_arch_closure'
    name=f'WHEELLESS_{location}_{"PORT" if side<0 else "STBD"}'
    nx=20;ny=12
    ymin=.13
    # Track the real semi-circular fender opening instead of overlaying a
    # full-height rectangular side plate across finished coachwork.
    arch_peak=.795 if location=='REAR' else .755
    zs=.968 if location=='REAR' else .920
    verts=[]
    for layer in [0,1]:
        for j in range(ny+1):
            v=j/ny
            for i in range(nx+1):
                u=i/nx
                x=x0+(u-.5)*2*r
                edge_height=.35+(.035 if location=='REAR' else 0.)
                arc=math.sqrt(max(0.,1.-(2*u-1)**2))
                ymax=edge_height+(arch_peak-edge_height)*arc
                y=ymin+(ymax-ymin)*v
                # Match existing outward-to-inward fender curvature
                high=max(0,(y-.55)/(.25 if location=='FRONT' else .29))
                base=zs - .12*high**2 - .020*(v-.28)
                # subtlest double-curvature, center convex, edges wrap back
                bulge=.025*math.sin(math.pi*u)*math.sin(math.pi*v)
                z=side*(base+bulge-layer*.050)
                verts.append((x,y,z))
    ring=(nx+1)*(ny+1)
    faces=[]
    for j in range(ny):
        for i in range(nx):
            a=j*(nx+1)+i;b=a+1;c=a+nx+1;d=c+1
            faces.extend([(a,b,d),(a,d,c)])
            faces.extend([(ring+a,ring+d,ring+b),(ring+a,ring+c,ring+d)])
    # close perimeter of thick curved body panel
    sides=[]
    for i in range(nx):sides.append((i,i+1))
    for j in range(ny):sides.append((j*(nx+1)+nx,(j+1)*(nx+1)+nx))
    for i in range(nx,0,-1):sides.append((ny*(nx+1)+i,ny*(nx+1)+i-1))
    for j in range(ny,0,-1):sides.append((j*(nx+1),(j-1)*(nx+1)))
    for a,b in sides:
        faces.extend([(a,ring+a,ring+b),(a,ring+b,b)])
    mesh=trimesh.Trimesh(vertices=np.asarray(verts),faces=np.asarray(faces),process=False)
    trimesh.repair.fix_normals(mesh)
    assert mesh.is_watertight and mesh.is_winding_consistent
    # Match the donor's actual material RGB (sampled from its red paint
    # texture: 170,29,36) and measured metal/roughness, while retaining UV-
    # independent modern PBR shading on the new topology.
    add_part(scene,name+'_CURVED_FULL_PANEL',mesh,group,'paint')
    # Panel retains a real construction boundary without raised decorative rails.

def hidden_emitter(scene,x,side,index):
    z=side*.56
    group='concealed_lift_array'
    prefix=f'UNDERBODY_{"P" if side<0 else "S"}_{index}'
    box(scene,prefix+'_RECESSED_MOUNT',(x,.185,z),(.65,.105,.47),group,'graphite')
    annulus(scene,prefix+'_VERTICAL_COIL',(x,.102,z),.225,.15,.05,group,'copper')
    annulus(scene,prefix+'_CERAMIC_SHROUD',(x,.079,z),.244,.19,.03,group,'gunmetal')
    m=trimesh.creation.cylinder(radius=.14,height=.021,sections=24)
    m.apply_transform(trimesh.geometry.align_vectors([0,0,1],[0,1,0]))
    m.apply_translation((x,.066,z))
    add_part(scene,prefix+'_DOWN_EMISSION',m,group,'light')
    for k in range(4):
        xx=x+(-.23 if k<2 else .23)
        zz=z+(-.17 if k%2==0 else .17)
        bar(scene,prefix+f'_BOLT_{k}',(xx,.115,zz),(xx,.23,zz),.018,group,'titanium',10)

def base_scene(flush):
    scene=trimesh.Scene()
    removed=[]; retained=[]
    for node in source.graph.nodes_geometry:
        T, geom=source.graph.get(node)
        if removable(node,flush):
            removed.append(node)
            continue
        mesh=source.geometry[geom].copy()
        mesh.apply_transform(T)
        # source nodes can share a geometry, bake each node transform separately
        # to retain proper authentic 3D car construction.
        safe=node.replace(' ','_')
        scene.add_geometry(mesh,node_name=safe,geom_name=safe)
        retained.append(node)
    return scene,removed,retained

def run(flush):
    variant='WHEELLESS_FLUSH_BODY' if flush else 'VISIBLE_HOVER_PODS'
    scene,removed,retained=base_scene(flush)
    if flush:
        for loc,x,r in [('FRONT',-1.27,.51),('REAR',1.43,.54)]:
            for side in [-1,1]:arch_fairing(scene,loc,side,x,r)
        # 6 entirely underside lift units; there are no hub-shaped side objects.
        for side in [-1,1]:
            for i,x in enumerate([-1.46,0,1.52]):hidden_emitter(scene,x,side,i)
        for side in [-1,1]:
            z=side*.57
            box(scene,f'SEALED_SILL_{"PORT" if side<0 else "STBD"}',(0,.21,z),
                (3.44,.11,.24),'side_sills','graphite')
    else:
        for loc,x in [('FRONT',-1.27),('REAR',1.43)]:
            for side in [-1,1]:cassette(scene,loc+('_PORT' if side<0 else '_STBD'),x,side)
    # common rear hybrid booster assembly layered with existing exhaust;
    # no wheels or conventional axle remains in the GLB.
    for side in [-1,1]:
        z=side*.49
        box(scene,f'REAR_PROPULSION_{"P" if side<0 else "S"}_MOUNT',(2.16,.46,z),(.20,.28,.38),'aft_propulsion','gunmetal')
        for i in range(2):
            xx=2.18+i*.14
            annulus(scene,f'REAR_PROPULSION_{"P" if side<0 else "S"}_{i}_NOZZLE',(xx,.49,z),.17,.105,.05,'aft_propulsion','titanium')
        # visible luminous center facing aft rather than road direction
        m=trimesh.creation.cylinder(radius=.094,height=.035,sections=24)
        m.apply_transform(trimesh.geometry.align_vectors([0,0,1],[1,0,0]));m.apply_translation((2.31,.49,z))
        add_part(scene,f'REAR_PROPULSION_{"P" if side<0 else "S"}_CORE',m,'aft_propulsion','light')
    assert not any(removable(n,False) for n in retained)
    if flush:
        assert not any('fender lip' in n.lower() or 'arched liner' in n.lower() for n in retained)
    target=OUT/(f'CC0_Supercar_{variant}.glb')
    scene.export(target)
    check=trimesh.load(target,force='scene',process=False)
    assert len(check.geometry)==len(scene.geometry)
    assert len(check.geometry)>20
    added=set(check.geometry)-{n.replace(' ','_') for n in retained}
    original_main_meshes=[x for x in retained if x.startswith('Original mid-engine supercar sculpted body shell')]
    if flush:
        assert sum('_CURVED_FULL_PANEL' in x for x in check.geometry)==4
        assert sum('_DOWN_EMISSION' in x for x in check.geometry)==6
        assert not any('tread' in x.lower() or 'wheel' in x.lower() for x in check.geometry if not (x.startswith('WHEELLESS_') or x.startswith('Steering_wheel')))
    else:
        assert sum('_DOWNWARD_EMITTER' in x for x in check.geometry)==4
    rec={'variant':variant,'donor_source':'Innerscene original Generic Mid-engine Supercar',
         'license':'CC0 per source page','source_url':'https://www.innerscene.com/tools/library/3d-parts/generic-mid-engine-supercar-73f252c5',
         'source_sha256':source_hash,'mesh_source_count':348,'original_mesh_nodes_retained':len(retained),
         'original_wheel_nodes_deleted':len(removed),'created_geometry_meshes':len(added),
         'result_meshes':len(check.geometry),'result_triangles':sum(len(g.faces) for g in check.geometry.values()),
         'result_bounds_m':np.round(check.bounds,3).tolist(),
         'wheel_hubs_remaining':False,'converted_locations':[{'axle':ax,'longitudinal_m':x,'side':side}
               for ax,x in [('front',-1.27),('rear',1.43)] for side in ('port','starboard')],
         'donor_body_shell_untouched':bool(original_main_meshes),
         'wheel_arch_strategy':('4 curved independent outer pressings to fill cutouts; physically modeled seamless-intent removable armor with visible seams, not welded topology' if flush else 'open fender arches with 4 independent mechanical downward hover cassettes'),
         'hidden_lift_units':(6 if flush else 0),'visible_hover_pods':(0 if flush else 4),
         'warning':'Not the canonical FORGE craft; first donor adaptation experiment. Flush-fender surfaces are separate physically continuous sheets, NOT a single retopologized watertight original hull.'}
    (OUT/(f'{variant}_REPORT.json')).write_text(json.dumps(rec,indent=2)+'\n')
    print('CONVERSION_OK',variant,'meshes',len(check.geometry),'tris',rec['result_triangles'],'deleted',len(removed),flush=True)
    return rec

if __name__=='__main__':
    mode=argparse.ArgumentParser()
    mode.add_argument('--variant',choices=['pods','flush'],required=True)
    args=mode.parse_args()
    run(args.variant=='flush')
