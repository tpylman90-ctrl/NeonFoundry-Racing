#!/usr/bin/env python3
"""FORGE V18.04 - independent cockpit glazing, roof armor, and mounted rear cowl.

Builds real editable, solid-part GLB from V18.03 frame + hood assembly without
changing their meshes. X=width, Y=up, Z=forward. Owner review, NOT production.
"""
from __future__ import annotations
import os, math, json, hashlib
from pathlib import Path
import numpy as np
import trimesh
from scipy.interpolate import PchipInterpolator
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals

SCRIPT=Path(__file__).resolve()
ROOT=SCRIPT.parent
SOURCE=Path(os.environ.get('NFR_STAGE03_GLB', str(SCRIPT.parent.parent/'art/hero_01/experiments/V18_Stage03/FORGE_V18_03_Hood_Intakes_Modular.glb')))
OUT=Path(os.environ.get('NFR_STAGE04_OUT', str(SCRIPT.parent.parent/'build/forge_v18_stage04')))
OUT.mkdir(parents=True,exist_ok=True)
assert SOURCE.is_file(), 'Missing actual FORGE V18.03 inspection GLB'
base=trimesh.load(SOURCE, force='scene', process=False)
assert len(base.geometry)==396, ('Unexpected V18.03 baseline',len(base.geometry))
scene=base.copy()
baseline_names=set(base.geometry)
new={}
materials={
    'body': ([201,202,202,255],.66,.38,'OPAQUE'),
    'body_shadow': ([121,125,131,255],.76,.45,'OPAQUE'),
    'body_light':([224,223,219,255],.58,.42,'OPAQUE'),
    'trim':([77,86,99,255],.74,.30,'OPAQUE'),
    'dark':([35,44,54,255],.35,.59,'OPAQUE'),
    'glass':([57,101,120,175],.10,.16,'BLEND'),
    'glass_dark':([37,76,92,192],.07,.19,'BLEND'),
    'glass_roof':([54,85,102,210],.15,.20,'BLEND'),
    'rubber':([42,45,51,255],.04,.81,'OPAQUE'),
    'machined':([148,160,168,255],.88,.29,'OPAQUE'),
    'fastener':([178,163,137,255],.75,.40,'OPAQUE'),
    'seat':([57,62,69,255],.04,.83,'OPAQUE'),
    'pad':([91,97,104,255],.03,.93,'OPAQUE'),
    'hud':([39,183,200,220],.0,.28,'BLEND'),
}

def node(group):
    n='ASSEMBLY_'+group
    if n not in scene.graph.nodes:
        scene.graph.update(frame_from=scene.graph.base_frame,frame_to=n,matrix=np.eye(4))
    return n

def add(name,mesh,group,why,mat='body'):
    if name in scene.geometry:raise ValueError('Duplicate '+name)
    mesh=mesh.copy()
    if not mesh.is_winding_consistent or not mesh.is_watertight or mesh.volume < 0:
        trimesh.repair.fix_normals(mesh)
    assert mesh.is_watertight and mesh.is_winding_consistent,(name,mesh.euler_number,len(mesh.faces))
    rgba,metal,rough,alpha=materials[mat]
    mesh.visual=TextureVisuals(material=PBRMaterial(name='NFR_V18_04_'+mat,
        baseColorFactor=rgba, metallicFactor=metal,roughnessFactor=rough,
        alphaMode=alpha, doubleSided=(alpha=='BLEND')))
    scene.add_geometry(mesh,node_name=name,geom_name=name,parent_node_name=node(group))
    new[name]={'group':group,'role':why,'material':mat,'tris':len(mesh.faces),
               'bounds':np.round(mesh.bounds,4).tolist(),'closed':True}
    return mesh

def box(name,c,ext,grp,why,mat='trim'):
    m=trimesh.creation.box(extents=ext);m.apply_translation(c)
    return add(name,m,grp,why,mat)

def beam(name,p,q,r,grp,why,mat='trim',sections=12):
    p=np.asarray(p,float);q=np.asarray(q,float)
    vec=q-p;length=np.linalg.norm(vec)
    assert length>1e-4
    m=trimesh.creation.cylinder(radius=r,height=length+.35*r,sections=sections)
    m.apply_transform(trimesh.geometry.align_vectors([0,0,1],vec/length))
    m.apply_translation((p+q)/2)
    return add(name,m,grp,why,mat)

def connected_closed_patch(name,rows,group,why,mat):
    """Physical double-sided sheet with genuine thickness, edge hems and closed ends.

    rows is [outer row of 3D positions sampled along a cross-width]
    inner is displaced inward toward centerline by per-vertex radial vector.
    """
    a=np.asarray(rows,float)
    assert a.ndim==3 and a.shape[0]>=2 and a.shape[1]>=2 and a.shape[-1]==3
    nl,nw=a.shape[:2]
    v=a.reshape(-1,3).tolist()
    # use constant Y-based offset: glass is 14mm thick, steel 52mm; user sees real edges
    th=.017 if mat.startswith('glass') or mat=='hud' else .052
    inner=a.copy();inner[:,:,1]-=th
    v+=inner.reshape(-1,3).tolist()
    offset=nl*nw
    faces=[]
    for z in range(nl-1):
      for t in range(nw-1):
        p=z*nw+t;q=(z+1)*nw+t
        faces.extend([[p,q,p+1],[q,q+1,p+1]])
        faces.extend([[offset+p,offset+p+1,offset+q],[offset+q,offset+p+1,offset+q+1]])
    # closed long edges
    for z in range(nl-1):
      for t in [0,nw-1]:
        p=z*nw+t; q=(z+1)*nw+t
        faces.extend([[p,offset+p,q],[q,offset+p,offset+q]] if t==0
                     else [[p,q,offset+p],[q,offset+q,offset+p]])
    # close short edges
    for t in range(nw-1):
      p=t;q=t+1
      faces.extend([[p,q,offset+p],[q,offset+q,offset+p]])
      p=(nl-1)*nw+t;q=p+1
      faces.extend([[p,offset+p,q],[q,offset+p,offset+q]])
    m=trimesh.Trimesh(vertices=np.array(v),faces=faces,process=False)
    trimesh.repair.fix_normals(m)
    return add(name,m,group,why,mat)

# Smooth, measured canopy stations. The front windshield sits behind the
# actual V18.03 bonnet, while broad roof contour clears existing cage hoops.
# [z, half width, roof crown Y, lower window sill Y]
control=np.array([
  [-2.62,1.075,1.775,1.425],
  [-2.45,1.055,1.966,1.455],
  [-2.27,1.015,2.127,1.483],
  [-2.02,.968,2.266,1.500],
  [-1.70,.936,2.329,1.508],
  [-1.36,.922,2.347,1.512],
  [-.92,.872,2.296,1.523],
  [-.56,.818,2.189,1.505],
  [-.26,.702,1.983,1.477],
  [0.04,.546,1.776,1.457],
  [0.29,.360,1.601,1.430],
  [0.47,.170,1.495,1.412],
],float)
assert np.all(np.diff(control[:,0])>0)
fs=[PchipInterpolator(control[:,0],control[:,i]) for i in range(1,4)]

def cp(z,u):
    """Superelliptic automotive cross section; upper surface clears actual cage."""
    w,ymax,ymin=(float(f(z)) for f in fs)
    u=float(np.clip(u,-1,1))
    t=(1-abs(u)**4)**.32
    return [w*u,ymin+(ymax-ymin)*t,z]

def patch(name,zstart,zend,ustart,uend,grp,why,material,nz=15,nu=9):
    zlist=np.linspace(zstart,zend,nz)
    ulist=np.linspace(ustart,uend,nu)
    return connected_closed_patch(name,[[cp(z,u) for u in ulist] for z in zlist],grp,why,material)

def sweep_tube(name,points,radius,grp,why,mat='trim',segments=12):
    """One continuous fabricated tube per actual part, not 24 GLB draw calls."""
    points=np.asarray(points,float)
    assert len(points)>1
    verts=[]
    for i,p in enumerate(points):
        tangent=(points[min(i+1,len(points)-1)] - points[max(i-1,0)])
        tangent/=np.linalg.norm(tangent)
        guide=np.array([0.,0.,1.]) if abs(np.dot(tangent,[0,0,1]))<.85 else np.array([0.,1.,0.])
        a=np.cross(tangent,guide);a/=np.linalg.norm(a)
        b=np.cross(tangent,a)
        for t in np.linspace(0,2*np.pi,segments,endpoint=False):
            verts.append(p+radius*(np.cos(t)*a+np.sin(t)*b))
    faces=[]
    for k in range(len(points)-1):
        for i in range(segments):
            p=k*segments+i; q=k*segments+(i+1)%segments
            r=(k+1)*segments+i; t=(k+1)*segments+(i+1)%segments
            faces.extend([[p,r,q],[q,r,t]])
    for i in range(1,segments-1):
        faces.append([0,i+1,i])
        at=(len(points)-1)*segments
        faces.append([at,at+i,at+i+1])
    m=trimesh.Trimesh(vertices=np.array(verts),faces=faces,process=False)
    trimesh.repair.fix_normals(m)
    return add(name,m,grp,why,mat)

def rail(name,z0,z1,u,grp,why,mat='trim',radius=.033,segments=24):
    pts=[cp(z,u) for z in np.linspace(z0,z1,segments)]
    return sweep_tube(name,pts,radius,grp,why,mat)

def arch(name,z,grp,why,mat='trim',radius=.042,n=16):
    pts=[cp(z,u) for u in np.linspace(-.98,.98,n)]
    return sweep_tube(name,pts,radius,grp,why,mat)

# 1) Structural base plates / cowl hardpoints FIRST, not floating shells.
for side,sg in [('PORT',-1),('STBD',1)]:
    for j,z in enumerate([.22,-.48,-1.24,-1.89,-2.42]):
        # box/arms overlap the existing UPPER_SILL rails, physically anchoring
        # the outside canopy weather seal and hinge support.
        box(f'V18_04_MOUNT_{side}_SillClamp_{j:02}',
            (sg*1.00,1.42,z),(.28,.24,.21),'14_Cab_Mounting',
            'Machined mount straddling the actual V18.02 upper structural sill','machined')
        beam(f'V18_04_MOUNT_{side}_ClampToGlassRail_{j:02}',
            (sg*1.01,1.44,z),(sg*1.07,1.61,z-.05),.054,
            '14_Cab_Mounting','Braced load transfer from side sill into canopy support','trim')
        for k,xoff in enumerate([-.065,.065]):
            box(f'V18_04_MOUNT_{side}_BoltHead_{j:02}_{k}',
                (sg*(.94+xoff),1.554,z),(.055,.029,.055),
                '14_Cab_Mounting','Independent hex-style mount fastener','fastener')
    # Front greenhouse foot connects to existing removable hood at z=.25,
    # not merely the frame rail behind it.
    box(f'V18_04_MOUNT_{side}_BonnetInterface',(sg*.49,1.49,.22),(.24,.13,.30),
        '14_Cab_Mounting','Physical glass-frame to rear hood hinge-interface plate','machined')
    beam(f'V18_04_MOUNT_{side}_FrontCantilever',(sg*.49,1.50,.23),
         (sg*.63,1.62,-.18),.058,'14_Cab_Mounting',
         'A-pillar foot bridged to bonnet and cage','trim')

# 2) GLASS: independently fabricated, real 17mm thick translucent shells.
# Each half-windscreen, side window, and roof transparency is a unique part.
for side,umin,umax in [('PORT',-.98,-.02),('STBD',.02,.98)]:
    patch(f'V18_04_GLASS_{side}_ForwardLaminatedWindscreen',.40,-.79,umin,umax,
          '15_Canopy_Transparent','Independently curved laminated windshield half','glass_dark',24,12)
    for j,(z0,z1) in enumerate([(-.805,-1.47),(-1.50,-2.24)]):
        u0,u1=(-.98,-.57) if side=='PORT' else (.57,.98)
        patch(f'V18_04_GLASS_{side}_DoorSideLight_{j:02}',z0,z1,u0,u1,
              '15_Canopy_Transparent','Side glazing sealed in its own removable aperture','glass',15,6)
    for j,(z0,z1) in enumerate([(-.805,-1.43),(-1.48,-2.26)]):
        u0,u1=(-.57,-.02) if side=='PORT' else (.02,.57)
        patch(f'V18_04_GLASS_{side}_RoofQuarter_{j:02}',z0,z1,u0,u1,
              '15_Canopy_Transparent','Glazed roof segment with manufactured physical thickness','glass_roof',14,8)

# 3) REAL frame weatherstrips and distinct structural members. Fixed to cage.
for side,sg in [('PORT',-1),('STBD',1)]:
    rail(f'V18_04_CANOPY_{side}_LowerPerimeterSill',.38,-2.60,sg*.99,
         '16_Canopy_Frame','C-shaped continuous load-bearing window sill molding','body_shadow',.041,24)
    rail(f'V18_04_CANOPY_{side}_RoofEdge',-.77,-2.48,sg*.58,
         '16_Canopy_Frame','Upper roof-glass separator, separate extruded part','trim',.028,18)
    rail(f'V18_04_CANOPY_{side}_WaterChannel',.35,-2.55,sg*.98,
         '20_Cab_Weatherseal','Continuous EPDM glass-perimeter seal','rubber',.026,25)
    # gasket around independently hinged side window
    for j,(z0,z1) in enumerate([(-.81,-1.48),(-1.51,-2.22)]):
        beam(f'V18_04_CANOPY_{side}_DoorSeam_{j}',cp(z0,sg*.93),cp(z1,sg*.93),.026,
             '20_Cab_Weatherseal','Separate lower sash rail of two-piece cockpit glazing','trim')
    # A-pillars run from actual front hood seam to structural roof crown
    for k,u in enumerate([sg*.90,sg*.52]):
        rail(f'V18_04_CANOPY_{side}_A_Pillar_{k}',.37,-.82,u,
             '16_Canopy_Frame','Formed double-profile front cockpit pillar','machined',.041,16)
    # Visible B pillar, exterior hinge and actuator.
    beam(f'V18_04_CANOPY_{side}_RearRoofPivot',cp(-2.20,sg*.96),
         (sg*.99,1.54,-2.62),.072,'16_Canopy_Frame',
         'Bolted rear hoop base to owner-approved structural cage','body_shadow')
    box(f'V18_04_CANOPY_{side}_PrimaryHinge',(sg*.99,1.61,-2.45),(.19,.22,.24),
        '20_Cab_Weatherseal','Separate canopy hinge barrel with load-bearing lug','machined')
    beam(f'V18_04_CANOPY_{side}_HingeAxle',(sg*.85,1.65,-2.45),
         (sg*1.13,1.65,-2.45),.025,'20_Cab_Weatherseal',
         'Physical cross-axis pivot for canopy hinge','fastener')
    beam(f'V18_04_CANOPY_{side}_GasStrut',(sg*.83,1.52,-2.36),
         (sg*.69,1.83,-1.48),.028,'20_Cab_Weatherseal',
         'Visible canopy lift gas strut connected to rear hinge','machined')
    box(f'V18_04_CANOPY_{side}_Latch',(sg*.33,1.51,.35),(.15,.07,.11),
        '20_Cab_Weatherseal','Latch retaining canopy front edge to the new bonnet','fastener')

# Separate transverse frames, pressed/deburred ribs reveal cross-section quality.
for i,z in enumerate([.37,-.78,-1.48,-2.29,-2.60]):
    arch(f'V18_04_CANOPY_Arch_{i}',z,'16_Canopy_Frame',
         'Manufactured canopy perimeter hoop with connected cross-vehicle geometry',
         'machined' if i in (0,4) else 'body_shadow',.047 if i in (0,4) else .035,18)
# central glass seam on windshield + cross-brace above roof
rail('V18_04_CANOPY_CenterWindscreenSeparator',.36,-.78,0.,'16_Canopy_Frame',
     'Slim center windscreen mullion independent of the glazing','machined',.029,18)
rail('V18_04_CANOPY_CrownLongeron',-.80,-2.45,0.,'16_Canopy_Frame',
     'Aerodynamic central canopy roof member','body_shadow',.042,17)

# 4) Actual cockpit: separate seat, restrained driver, console and instrument pod.
# All below the glazed roof and above actual steel floor/cross members.
box('V18_04_INTERIOR_000_SeatPedestal',(0,.71,-1.40),(.39,.22,.77),
    '17_Cockpit_Interior','Seat bolted to cockpit crossmembers','machined')
box('V18_04_INTERIOR_001_SeatPan',(0,.90,-1.22),(.65,.15,.82),
    '17_Cockpit_Interior','Padded independent single-driver seat cushion','seat')
box('V18_04_INTERIOR_002_SeatBack',(0,1.33,-1.69),(.65,.76,.16),
    '17_Cockpit_Interior','Reclined bolstered seat back shell','seat')
box('V18_04_INTERIOR_003_Headrest',(0,1.80,-1.82),(.40,.24,.19),
    '17_Cockpit_Interior','Individual headrest well below canopy crown','pad')
for side,sg in [('PORT',-1),('STBD',1)]:
    box(f'V18_04_INTERIOR_{side}_SeatShoulder',
        (sg*.31,1.36,-1.73),(.10,.66,.19),
        '17_Cockpit_Interior','Molded seat lateral bolsters','pad')
    box(f'V18_04_INTERIOR_{side}_SeatHip',
        (sg*.28,.98,-1.15),(.09,.28,.57),
        '17_Cockpit_Interior','Driver lateral hip support','pad')
    beam(f'V18_04_INTERIOR_{side}_HarnessWeb',(sg*.19,1.78,-1.78),
         (sg*.18,1.08,-1.05),.024,'17_Cockpit_Interior',
         'Independent harness strap retained by steel shoulder eyelet','fastener')
    beam(f'V18_04_INTERIOR_{side}_SideControl',(sg*.42,.95,-.85),
         (sg*.42,1.20,-.42),.036,'17_Cockpit_Interior',
         'Reachable cockpit-side control lever','machined')
box('V18_04_INTERIOR_010_DashBulkhead',(0,1.26,-.21),(1.18,.24,.32),
    '17_Cockpit_Interior','Machined instrument beam across cockpit front','body_shadow')
box('V18_04_INTERIOR_011_InstrumentPod',(0,1.42,-.38),(.72,.17,.22),
    '17_Cockpit_Interior','Recessed driver-facing control and instrument shroud','dark')
box('V18_04_INTERIOR_012_InstrumentGlass',(0,1.48,-.508),(.55,.085,.024),
    '17_Cockpit_Interior','Independent HUD instrumentation display','hud')
box('V18_04_INTERIOR_013_ControlYoke',(0,1.25,-.63),(.48,.09,.055),
    '17_Cockpit_Interior','Two-grip pilot steering yoke','machined')
for sg,side in [(-1,'PORT'),(1,'STBD')]:
    box(f'V18_04_INTERIOR_{side}_YokeGrip',(sg*.24,1.20,-.65),(.07,.19,.11),
        '17_Cockpit_Interior','Separate rubber-sleeved steering grip','rubber')

# 5) Aft cowling: NOT one closed opaque blob. Three independently formed
# longitudinal armor strips with structure underneath, leaving engine pockets
# and side-machine openings accessible for subsequent propulsion pass.
rearStations=[
    (-2.32,.96,2.04,1.53),
    (-2.48,1.02,1.97,1.53),
    (-2.72,1.09,1.92,1.51),
    (-3.03,1.14,1.91,1.49),
    (-3.35,1.12,1.87,1.49),
    (-3.63,1.07,1.80,1.47),
    (-3.78,1.02,1.77,1.46),
]
rear_stations=np.array(sorted(rearStations,key=lambda x:x[0]),float)
fr=[PchipInterpolator(rear_stations[:,0],rear_stations[:,i]) for i in range(1,4)]
def cowl(z,u):
    w,top,base=(float(f(z)) for f in fr)
    u=float(u)
    # planar-ish plate, car-like shoulders, physically separate root geometry
    return [w*u, base+(top-base)*(1-abs(u)**3)**.30,z]

def cowl_sheet(name,za,zb,ua,ub,mat,role,nz=12,nu=8):
    rows=[[cowl(z,u) for u in np.linspace(ua,ub,nu)]
         for z in np.linspace(za,zb,nz)]
    return connected_closed_patch(name,rows,'18_AftRoof_Armor',role,mat)

cowl_sheet('V18_04_COWL_001_CentralArmoredDeck',-2.38,-3.77,-.38,.38,
           'body_light','Formed separate center dorsal deck above rear inner booster frame',17,10)
for side,a,b in [('PORT',-.99,-.42),('STBD',.42,.99)]:
    for i,(za,zb) in enumerate([(-2.38,-3.09),(-3.11,-3.76)]):
        cowl_sheet(f'V18_04_COWL_{side}_002_SplitSidePlate_{i}',za,zb,a,b,
                   'body','Independently pressed left/right upper aft cowl with service seam',12,8)
    # Each ridge is a single curved machined extrusion with its own node.
    for i,(za,zb) in enumerate([(-2.40,-3.12),(-3.13,-3.75)]):
        points=[cowl(z, -.405 if side=='PORT' else .405) for z in np.linspace(za,zb,18)]
        sweep_tube(f'V18_04_COWL_{side}_003_SplineRidge_{i}',points,.027,
                   '18_AftRoof_Armor','Continuous independent raised shoulder ridge','trim')
    for i,z in enumerate([-2.66,-3.12,-3.53]):
        sg=-1 if side=='PORT' else 1
        # Base bracket seats overlap existing rear sill x~1.10, y~1.46
        box(f'V18_04_COWL_{side}_004_SaddleFoot_{i}',
            (sg*1.12,1.51,z),(.27,.16,.26),
            '19_AftRoof_EngineMounts','Mechanical shoe embracing original rear upper chassis tube','machined')
        beam(f'V18_04_COWL_{side}_005_Gusset_{i}',(sg*1.11,1.53,z),
             (sg*.80,1.86,z-.12),.063,
             '19_AftRoof_EngineMounts','Gusseted load path into removable aft cowl armor','trim')
        for j,dz in enumerate([-.065,.065]):
            box(f'V18_04_COWL_{side}_006_Bolt_{i}_{j}',
                (sg*1.13,1.61,z+dz),(.047,.03,.046),
                '19_AftRoof_EngineMounts','Individual saddle fastening hardware','fastener')
    # Service-access cavity below cowl rather than a sealed solid side block.
    # Two genuine machine cavity rails await booster installation.
    for i,y in enumerate([1.57,1.71]):
        beam(f'V18_04_COWL_{side}_007_BoosterPocketRail_{i}',
             (sg*.69,y,-2.79),(sg*.66,y,-3.71),.040,
             '19_AftRoof_EngineMounts',
             'Separate internal reinforcement and reserved small-booster pocket','body_shadow')
    box(f'V18_04_COWL_{side}_008_CowlRearClosure',
        (sg*.80,1.70,-3.70),(.36,.19,.09),
        '19_AftRoof_EngineMounts','Rear cowl terminating plate as removable part','body_shadow')

# Crown center cooling hardware: genuine individually fastened vent slots;
# cutouts would need boolean process in next detail stage (not falsely claimed).
for i,z in enumerate([-3.09,-3.29,-3.49]):
    box(f'V18_04_COWL_010_RecessMarker_{i}',(0,1.879,z),(.27,.033,.075),
        '18_AftRoof_Armor','Separate inset cooling cover plate, not an actual bored opening','dark')

# 6) Individually pressed canopy-to-sidewall fairing pieces close the lower
# visible weather-gap while leaving the cockpit cage and mechanical bays open.
# Lower outboard end crosses the actual upper-sill rails; inboard end follows
# the independently curved glass edge instead of a primitive strip.
for side,sg in [('PORT',-1),('STBD',1)]:
    for seg,(z0,z1) in enumerate([(-.30,-1.35),(-1.38,-2.53)]):
        rows=[]
        for z in np.linspace(z0,z1,15):
            w,ymax,ymin=(float(f(z)) for f in fs)
            lip=np.array(cp(z,sg*.999),float)
            rows.append([lip,
                np.array([sg*(w+.038),max(1.48,lip[1]-.08),z]),
                np.array([sg*1.09,1.438,z])])
        connected_closed_patch(
            f'V18_04_CANOPY_{side}_PressedSillFairing_{seg}',rows,
            '16_Canopy_Frame',
            'Independent shaped outer sill connecting canopy glazing to original frame and machined mounts','body_light')
        # Removable line fasteners along new attachment flange.
        for j,z in enumerate(np.linspace(z0+.10,z1-.10,3)):
            box(f'V18_04_CANOPY_{side}_SillFairingScrew_{seg}_{j}',
                (sg*1.077,1.451,float(z)),(.036,.033,.040),
                '20_Cab_Weatherseal',
                'Accessible fastener at removable canopy-to-chassis fairing','fastener')

# Physical anchor audit: explicit overlap of hood seal with bonnet rear edge
# plus sidewall mounts and rear cowl saddle into the base frame. Shape agreement
# still awaits owner review, and there is no structural FEM validation.
for side in ('PORT','STBD'):
    foot=new[f'V18_04_MOUNT_{side}_SillClamp_03']['bounds']
    frame=base.geometry[f'UPPER_SILL_{side}_06'].bounds
    overlap=np.minimum(np.array(foot[1]),frame[1])-np.maximum(np.array(foot[0]),frame[0])
    assert np.all(overlap>.01),(side,overlap)
    heel=new[f'V18_04_COWL_{side}_004_SaddleFoot_1']['bounds']
    rear=base.geometry[f'UPPER_SILL_{side}_08'].bounds
    overlap=np.minimum(np.array(heel[1]),rear[1])-np.maximum(np.array(heel[0]),rear[0])
    assert np.all(overlap>.01),(side,overlap)

# Explicit approval gate: no changes to V18.03 geometry accepted on inference
# alone. This is a separate Stage 04 cockpit/cowl assembly.
assert set(base.geometry)==baseline_names
assert all(np.array_equal(base.geometry[k].faces,scene.geometry[k].faces) for k in baseline_names)
assert all(np.allclose(base.geometry[k].vertices,scene.geometry[k].vertices,atol=0,rtol=0) for k in baseline_names)
assert len(new)>100
assert all(m.is_watertight and m.is_winding_consistent for m in scene.geometry.values())
path=OUT/'FORGE_V18_04_Cockpit_Assembly.glb'
scene.export(path,file_type='glb')
check=trimesh.load(path,force='scene',process=False)
assert len(check.geometry)==396+len(new)
assert sum(len(m.faces) for m in check.geometry.values())>18056
assert all(m.is_watertight for m in check.geometry.values())
assert any('GLASS_PORT_Forward' in n for n in check.geometry)
assert any('COWL_STBD_002' in n for n in check.geometry)

summary={
 'name':'FORGE V18.04 independent cockpit and rear cowl',
 'source':SOURCE.name,
 'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'base_meshes_preserved':len(baseline_names),
 'new_part_meshes':len(new),
 'total_meshes':len(check.geometry),
 'triangles':sum(len(m.faces) for m in check.geometry.values()),
 'materials':len(check.graph.nodes),
 'watertight_parts':len(check.geometry),
 'new_groups':{g:sum(v['group']==g for v in new.values()) for g in sorted(set(v['group'] for v in new.values()))},
 'geometry_semantics':'individual glazing shells, arches, side rails, mounts, seat/interior, independently pressed three-strip aft cowl and engine-bay mounting pockets',
 'verified_source_geometry_unchanged':True,
 'engineered_cowl_structure':'physical overlap at original upper-sill members; not stress-validated',
 'gate':'STAGE 04 EXPERIMENT - pending owner visual review before production or subsequent full body armor',
 'reference':'4227.jpg and original 8-view artwork plus owner exploded assembly diagram',
 'parts':new,
}
(OUT/'FORGE_V18_04_Parts_Manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
print('FORGE_V18_04_MESH_OK',json.dumps({k:summary[k] for k in ['base_meshes_preserved','new_part_meshes','total_meshes','triangles','new_groups']},sort_keys=True),flush=True)
