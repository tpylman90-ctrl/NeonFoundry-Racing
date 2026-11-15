#!/usr/bin/env python3
"""FORGE V18.05 — truly modeled lower-fairings and canopy-to-aft armor integration.

Preserves original V18.04 chassis, hood, intake and cockpit component mesh data.
Adds separate fitted side/underbody armor and longer roof-cowl shoulder assemblies
against the owner's garage screenshot. No flattened decals or single-piece shell.
Axes: X lateral, Y height, Z forward/nose (+). All dimensions meters.
"""
from __future__ import annotations
import json, os, hashlib, math
from pathlib import Path
import numpy as np
import trimesh
from trimesh.visual.texture import TextureVisuals
from trimesh.visual.material import PBRMaterial

ROOT=Path(__file__).resolve().parents[1]
BASE=Path(os.environ.get('NFR_BASE_GLB', ROOT/'art/hero_01/experiments/V18_Stage04/FORGE_V18_04_Cockpit_Assembly.glb'))
OUT=Path(os.environ.get('NFR_OUTPUT_DIR', ROOT/'build/forge_v18_stage05'))
OUT.mkdir(parents=True,exist_ok=True)
assert BASE.is_file(),f'Missing V18.04 GLB: {BASE}'
base=trimesh.load(BASE,force='scene',process=False)
assert len(base.geometry)==557, len(base.geometry)
scene=base.copy()
initial_geometry={key:(mesh.vertices.copy(),mesh.faces.copy()) for key,mesh in base.geometry.items()}
newparts={}
modules={}
materials={
 'shell':([174,181,187,255],.53,.48),
 'shell_highlight':([202,207,205,255],.48,.43),
 'shell_dark':([118,129,136,255],.72,.49),
 'sill':([68,79,88,255],.73,.56),
 'titanium':([133,146,154,255],.89,.4),
 'hardware':([176,147,99,255],.78,.38),
 'duct':([38,46,52,255],.56,.64),
 'accent':([105,142,164,255],.48,.40),
}

def assembly(tag):
 name='ASSEMBLY_V18_05_'+tag
 if name not in scene.graph.nodes:
  scene.graph.update(frame_from=scene.graph.base_frame,frame_to=name,matrix=np.eye(4))
 return name

def add(name,mesh,module,mat,role):
 assert name not in scene.geometry
 if not mesh.is_watertight:trimesh.repair.fix_normals(mesh)
 assert mesh.is_watertight,(name,mesh.euler_number)
 if mesh.volume<0:mesh.invert()
 rgba,metal,rough=materials[mat]
 mesh.visual=TextureVisuals(material=PBRMaterial(name='NFR_V18_05_'+mat,baseColorFactor=rgba,metallicFactor=metal,roughnessFactor=rough,doubleSided=False))
 scene.add_geometry(mesh,node_name=name,geom_name=name,parent_node_name=assembly(module))
 newparts[name]={'module':module,'material':mat,'role':role,'triangles':len(mesh.faces),'bounds_m':np.round(mesh.bounds,3).tolist()}
 modules[module]=modules.get(module,0)+1
 return mesh

def loft(name,stations,points,module,mat,role):
 """Fitted, capped solid with separate cross-sectional loops, not a plane."""
 rings=[np.asarray(points(st),float) for st in stations]
 assert len(rings)>=2
 n=len(rings[0]);assert n>=4 and all(len(r)==n for r in rings)
 v=np.concatenate(rings,axis=0)
 faces=[]
 for i in range(len(rings)-1):
  a,b=n*i,n*(i+1)
  for j in range(n):
   k=(j+1)%n
   faces.extend([(a+j,a+k,b+k),(a+j,b+k,b+j)])
 for i in range(1,n-1):
  faces.append((0,i+1,i))
  e=(len(rings)-1)*n
  faces.append((e,e+i,e+i+1))
 mesh=trimesh.Trimesh(vertices=v,faces=np.array(faces),process=False)
 trimesh.repair.fix_normals(mesh)
 return add(name,mesh,module,mat,role)

def box(name,center,size,module,mat,role):
 m=trimesh.creation.box(extents=size);m.apply_translation(center)
 return add(name,m,module,mat,role)

def tube(name,a,b,r,module,mat,role,sections=12):
 a=np.asarray(a,float);b=np.asarray(b,float);delta=b-a
 length=np.linalg.norm(delta)
 assert length>.005
 m=trimesh.creation.cylinder(radius=r,height=length+2*r*.42,sections=sections)
 m.apply_transform(trimesh.geometry.align_vectors([0,0,1],delta/length))
 m.apply_translation((a+b)/2)
 return add(name,m,module,mat,role)

# 1. REAL UNDERBODY PANELS: nose is physically connected to frame; center
# subfloor and two separate stepped rocker fairings stop the tubular chassis
# from protruding through the game's exterior inspection silhouette.
# Named, closed, replaceable service sections. Bottom sits at 0.235 m, just
# below the longerons. Front chin remains beneath (not inside) intake mouths.
for index,st in enumerate([
 [(3.67,.37,.38,.30),(3.17,.41,.40,.30),(2.57,.42,.41,.30)],
 [(2.55,.42,.41,.30),(1.74,.49,.43,.31),(1.04,.52,.44,.31)],
 [(1.02,.51,.44,.31),(.22,.54,.46,.31),(-.62,.53,.46,.31)],
 [(-.64,.54,.46,.31),(-1.57,.56,.46,.32),(-2.45,.56,.46,.31)],
 [(-2.48,.58,.46,.32),(-3.28,.59,.47,.33),(-3.86,.54,.44,.30)]
]):
 # z, half-width, upper panel Y, lower inner vertical Y
 loft('V18_05_UNDER_%02d_CenterUndertray'%index,st,
      lambda s:[(-s[1],s[2],s[0]),(s[1],s[2],s[0]),(s[1],.25,s[0]),(-s[1],.25,s[0])],
      '01_Belly_Pans','sill','Five separate thin armored belly-pan plates below the floor; leaves cabin interior open')

# 2. TWO OUTER LOWER SILL BANKS. Side trusses remain intact beneath removable
# coverplates. In central z length, top and lower panels have a literal open
# service channel for visible engine/tube details rather than a painted rectangle.
for side,sg in [('PORT',-1),('STBD',1)]:
 # Front gusseted shoulder transitions from outer intake envelope back to
 # canopy sidewall so the eye sees one physically supported surface.
 blend=[(1.52,1.60,1.54,1.58,.54),(.98,1.48,1.26,1.36,.47),(.57,1.45,1.09,1.32,.37)]
 loft(f'V18_05_{side}_FrontIntakeToCockpitShoulder',blend,
      lambda a:[(sg*.92,a[1],a[0]),(sg*a[2],a[1]+.03,a[0]),(sg*a[3],a[1]-.15,a[0]),(sg*a[3],a[4],a[0]),(sg*(a[3]-.13),a[4],a[0]),(sg*.94,a[4]+.08,a[0])],
      '02_Side_Armor','shell','Raised physically mounted bridge from rear intake to broad cockpit shoulder')
 # Individual forward cheek, two center service armor sheets, rear skirt.
 for i,stations in enumerate([
  [(.58,1.53,1.06,1.27,.32),(.10,1.53,1.09,1.28,.29),(-.62,1.53,1.10,1.29,.28)],
  [(-.67,1.55,1.11,1.30,.26),(-1.42,1.55,1.12,1.31,.25),(-2.23,1.54,1.13,1.31,.26)],
  [(-2.28,1.60,1.14,1.33,.26),(-3.03,1.61,1.17,1.35,.26),(-3.76,1.59,1.18,1.35,.27)]
 ]):
  # z, top height, x inner, x outer, bottom y
  # central side armor panels are separately folded, with visible splits.
  if i==1:
   # Instead of a huge center cheek, leave a 0.49m high real open louver bay.
   loft(f'V18_05_{side}_OuterUpperBelt_{i}',stations,
    lambda a:[(sg*a[2],a[1],a[0]),(sg*a[3],a[1]-.095,a[0]),(sg*a[3],1.18,a[0]),(sg*(a[3]-.13),1.11,a[0]),(sg*a[2],1.20,a[0])],
    '02_Side_Armor','shell_highlight','Formed upper cockpit side door armor, real open lower machinery section')
   loft(f'V18_05_{side}_LowerRocker_{i}',stations,
    lambda a:[(sg*a[2],.79,a[0]),(sg*a[3],.80,a[0]),(sg*a[3],a[4],a[0]),(sg*(a[3]-.13),a[4],a[0]),(sg*a[2],.39,a[0])],
    '03_Lower_Side_Fairings','sill','Deep rocker/belly side rail skirt covering low frame with genuine open service bay')
   # Actual exposed machinist ribs/coils inside recess, not decorations outside.
   for j,z in enumerate((-.91,-1.15,-1.39,-1.63,-1.87,-2.11)):
    box(f'V18_05_{side}_ServiceBayRecessRib_{j}',(sg*1.13,1.00,z),(.105,.30,.105),
       '04_Service_Bays','titanium','Independent recessed structural rib behind real side-opening')
   for j,z in enumerate((-.83,-1.27,-1.71,-2.15)):
    tube(f'V18_05_{side}_ServiceBayInnerCoil_{j}',(sg*1.09,.94,z),(sg*1.09,1.07,z-.12),.061,
         '04_Service_Bays','shell_dark','Engine conduit mounted deep inside open service band')
   for y,k in ((1.13,'top'),(.85,'lower')):
    tube(f'V18_05_{side}_ServiceBayHeader_{k}',(sg*1.26,y,-.71),(sg*1.26,y,-2.20),.026,
      '04_Service_Bays','titanium','Machined edge bead framing actual service aperture')
  else:
   loft(f'V18_05_{side}_RemovableSideSkin_{i}',stations,
    lambda a:[(sg*a[2],a[1],a[0]),(sg*a[3],a[1]-.10,a[0]),(sg*a[3],.76,a[0]),(sg*(a[3]-.05),a[4],a[0]),(sg*(a[3]-.16),a[4],a[0]),(sg*a[2],.77,a[0])],
    '02_Side_Armor','shell' if i==0 else 'shell_dark','Independent deep structural sidewall armor hiding protruding tubular longerons')
  # Actual steel panel mounting interface to existing upper/mid/lower sill
  # at z-positions within chosen panel range.
  z=(stations[0][0]+stations[-1][0])/2
  box(f'V18_05_{side}_PanelToFrameFoot_{i}',(sg*1.11,1.38,z),(.26,.28,.24),
      '05_Mounts','titanium','Internal panel mount overlapping original upper longeron')
  tube(f'V18_05_{side}_PanelSupportDiagonal_{i}',(sg*.99,1.36,z+.13),
       (sg*1.28,.80,z-.10),.062,'05_Mounts','titanium','Formed diagonal carrier bolted inside deep side fairing')
 # Continuous sill lip is split at both panel seams so no giant element.
 for i,(za,zb) in enumerate(((.50,-.58),(-.69,-2.20),(-2.30,-3.74))):
  tube(f'V18_05_{side}_LowerSillHem_{i}',(sg*1.30,.32,za),(sg*1.35,.32,zb),.036,
       '03_Lower_Side_Fairings','shell_dark','Manufactured rolled rocker lip following lower sidewall contour')
 # Non-cosmetic rear haunch/mount also ties into the rear roof seam.
 for i,z in enumerate((-2.66,-3.16,-3.59)):
  tube(f'V18_05_{side}_RearHaunchDiagonal_{i}',(sg*1.05,1.43,z+.12),
       (sg*1.20,1.91,z-.18),.064,'05_Mounts','titanium','Gusseted roof/body shoulder strut anchored to V18 sill')

# 3. LONG ALMOST LEVEL CANOPY-TO-ENGINE ARMORED ROOF, with pressed central
# roof cowl and separated blended port/stbd shoulder braces. Forward station
# overlaps existing hoop at z~-2.3 but starts behind roof glass (ends z -2.26).
# This closes the visible bare framework behind the greenhouse without
# swallowing the canopy glazing or consuming twin inner booster pockets.
center_roof=[
 (-2.28,.54,2.25,1.95),(-2.47,.64,2.29,1.96),
 (-2.70,.72,2.25,1.94),(-3.02,.75,2.21,1.92),
 (-3.36,.77,2.17,1.91),(-3.67,.79,2.12,1.90),
 (-3.90,.76,2.07,1.85)]
loft('V18_05_ROOF_00_ExtendedCentralBackbone',center_roof,
 lambda a:[(-a[1]*.68,a[2],a[0]),(a[1]*.68,a[2],a[0]),
   (a[1]*.98,a[2]-.08,a[0]),(a[1],a[3],a[0]),
   (a[1]*.84,a[3]-.03,a[0]),(-a[1]*.84,a[3]-.03,a[0]),
   (-a[1],a[3],a[0]),(-a[1]*.98,a[2]-.08,a[0])],
 '06_Rear_Roof','shell_highlight',
 'Long contoured armored canopy-to-rear roof extending aft; no cut through final roof glass')

for side,sg in [('PORT',-1),('STBD',1)]:
 # Upper crown-to-shoulder transitions, deliberately separate port/stbd panels,
 # continuous shoulder flare, subtle downsloping roof from cabin back to aft deck.
 but=[(-2.28,.57,1.09,2.18,1.67),(-2.48,.65,1.19,2.19,1.64),
      (-2.77,.71,1.24,2.18,1.62),(-3.07,.75,1.30,2.16,1.58),
      (-3.43,.78,1.34,2.11,1.54),(-3.78,.80,1.32,2.05,1.53),
      (-3.90,.78,1.29,2.02,1.52)]
 loft(f'V18_05_ROOF_{side}_01_SweptRearShoulder',but,
      lambda a:[(sg*a[1],a[3],a[0]),(sg*(a[2]-.1),a[3]-.12,a[0]),
                (sg*a[2],a[4]+.20,a[0]),(sg*a[2],a[4],a[0]),
                (sg*(a[2]-.15),a[4]-.015,a[0]),(sg*a[1],a[3]-.24,a[0])],
      '07_Rear_Shoulders','shell',
      'Long formed and curved roof-to-side bridge aligned to cockpit rear arch and aft armor')
 # Side shoulder is large but composed of independent upper/lower manufactured
 # panels with minor seams, not a one-piece body. The panels cover upper cage.
 for i,sub in enumerate((but[:4],but[3:])):
  loft(f'V18_05_ROOF_{side}_02_AftArmorHaunch_{i}',sub,
   lambda a:[(sg*(a[2]-.13),a[3]-.14,a[0]),(sg*(a[2]+.04),a[3]-.18,a[0]),
             (sg*(a[2]+.045),a[4]-.14,a[0]),(sg*(a[2]-.085),a[4]-.16,a[0])],
   '07_Rear_Shoulders','shell_dark',
   'Pressed two-stage rear roof armor haunch, extending to rear engine structure')
  za,zb=sub[0][0],sub[-1][0]
  tube(f'V18_05_ROOF_{side}_03_RidgeSeam_{i}',(sg*(sub[0][2]-.04),sub[0][3]-.12,za),
      (sg*(sub[-1][2]-.04),sub[-1][3]-.14,zb),.024,
      '07_Rear_Shoulders','titanium','Separate rolled armor seam on engineered shoulder')
 # Cross braces hold roof at former hoop and original rear cowl rails
 for i,z in enumerate((-2.47,-2.91,-3.44,-3.78)):
  box(f'V18_05_ROOF_{side}_04_RoofFoot_{i}',(sg*1.09,1.61,z),(.24,.23,.24),
      '08_Roof_Hardpoints','titanium','Real support foot physically intersecting legacy rear cowl saddle')
  tube(f'V18_05_ROOF_{side}_05_AftRoofGusset_{i}',(sg*1.08,1.63,z),(sg*.87,1.99,z-.15),.049,
      '08_Roof_Hardpoints','titanium','Transverse strut directly beneath new armored rear roof')
  for j,dz in enumerate((-.062,.062)):
   tube(f'V18_05_ROOF_{side}_06_RoofFootFastener_{i}_{j}',(sg*1.17,1.70,z+dz),
        (sg*1.22,1.70,z+dz),.020,'08_Roof_Hardpoints','hardware','Separate bolt in retained roof bracket')
 # Upper rear haunch and lower side body physically aligned around aft cage
 # to visually integrate rather than exposing mechanical frame at the tail.
 tube(f'V18_05_ROOF_{side}_07_AftBodyTransitionHem',(sg*1.30,1.55,-2.40),
     (sg*1.34,1.49,-3.81),.031,'07_Rear_Shoulders','titanium',
     'Deliberate pressed seam between raised roof haunch and lower armor')

# 4. SHELL BREAKUP / ACCESS and hardware. Raised narrow service embosses are
# actual shallow closed volumes, not surface color patterns; their positions
# avoid glass and the intake mouth openings.
for side,sg in [('PORT',-1),('STBD',1)]:
 for j,z in enumerate((-2.74,-3.04,-3.34)):
  box(f'V18_05_ROOF_{side}_08_RecessedAccessPlate_{j}',
      (sg*.94,1.997,z),(.24,.065,.18),
      '07_Rear_Shoulders','shell_dark','Separate maintenance hatch within aft roof shoulder')
 for j,z in enumerate((.31,-.37,-2.57,-3.26)):
  tube(f'V18_05_SIDE_{side}_09_LowerSkirtFastener_{j}',(sg*1.315,.52,z),
       (sg*1.37,.52,z),.020,'03_Lower_Side_Fairings','hardware',
       'Retained side armor rivet on deep removable skirt')

# 4B. NOSE UNDERFRAME AND TAIL ENDCAP: the previous nose image still showed
# exposed front crossbars below the hood. Fit segmented protection under the
# intakes without closing either actual air opening, then a rear service
# transom which leaves genuine open bays for future thruster hardware.
for side,sg in [('PORT',-1),('STBD',1)]:
 for i,stations in enumerate((
  [(3.45,.69,.98,.38),(3.15,.72,1.08,.49),(2.68,.75,1.17,.69)],
  [(2.65,.75,1.17,.75),(1.89,.78,1.20,.91),(1.15,.84,1.22,1.12)],
 )):
  loft(f'V18_05_NOSE_{side}_SubIntakeSkidFairing_{i}',stations,
       lambda a:[(sg*a[1],a[3],a[0]),(sg*a[2],a[3]-.025,a[0]),
                 (sg*a[2],.23,a[0]),(sg*(a[2]-.115),.22,a[0]),
                 (sg*a[1],.26,a[0])],
       '09_Nose_Frame_Covers','sill',
       'Segmented armored lower front frame cover, clear of open upper air duct')
  za,zb=stations[0][0],stations[-1][0]
  tube(f'V18_05_NOSE_{side}_InternalCrossSupport_{i}',
       (sg*.83,.42,za-.16),(sg*1.05,.53,zb+.15),.053,
       '09_Nose_Frame_Covers','titanium','Physical bracing under fitted front fairing')
 # Tail corner protection connects lower skirt to the rear cage end.
 loft(f'V18_05_TAIL_{side}_RearCornerReturn',
      [(-3.61,1.15,1.36),(-3.88,1.10,1.34)],
      lambda a:[(sg*(a[1]-.13),1.48,a[0]),(sg*a[2],1.47,a[0]),
                (sg*a[2],.30,a[0]),(sg*(a[2]-.13),.27,a[0])],
      '10_Aft_Cradle_Closure','shell_dark',
      'Rear vertical side corner shroud fitted to lower and upper aft rails')
 for k,y in enumerate((.48,1.53)):
  box(f'V18_05_TAIL_{side}_RearBulkheadSupport_{k}',
      (sg*.99,y,-3.79),(.28,.22,.28),
      '10_Aft_Cradle_Closure','titanium',
      'Bolted tail-frame support for removable aft transom')
# Nose center structural chin remains below high intake mouths.
loft('V18_05_NOSE_00_CentralChinArmor',
     [(3.67,.49,.55),(3.46,.56,.62),(3.14,.62,.69)],
     lambda a:[(-a[1],a[2],a[0]),(a[1],a[2],a[0]),
               (a[1],.26,a[0]),(-a[1],.26,a[0])],
     '09_Nose_Frame_Covers','shell_dark',
     'Forged front center underframe armor, leaves both pod intake openings clear')
# Rear end is a modular service transom with open booster bays.
box('V18_05_TAIL_00_LowerTransomSill',(0,.35,-3.81),
    (2.33,.22,.24),'10_Aft_Cradle_Closure','shell_dark',
    'Rear transverse undersill; leaves port and starboard engine apertures open')
box('V18_05_TAIL_01_UpperCrossBeam',(0,1.54,-3.82),
    (1.98,.15,.20),'10_Aft_Cradle_Closure','titanium',
    'Segmented open-engine-bay aft upper beam')
box('V18_05_TAIL_02_MidServiceKeel',(0,.93,-3.81),
    (.34,.93,.20),'10_Aft_Cradle_Closure','sill',
    'Rear bulkhead center spine between genuine open future booster bays')

# 5. Verify original component preservation, and basic visual safety envelope.
assert len(scene.geometry)==557+len(newparts)
for name,(vertices,faces) in initial_geometry.items():
 m=scene.geometry[name]
 assert np.array_equal(vertices,m.vertices) and np.array_equal(faces,m.faces),name
assert len(newparts)>75,len(newparts)
assert all(m.is_watertight and m.is_winding_consistent for m in scene.geometry.values())
# The raised roof must not overlap the forward windshield/glass, and must end
# at the rear end of the body rather than terminate at the cockpit hinge.
roof=scene.geometry['V18_05_ROOF_00_ExtendedCentralBackbone']
assert roof.bounds[1,2] < -2.25 and roof.bounds[0,2] <= -3.85
assert scene.bounds[0,1] >= .15 # no new geometry below hover plane
# Tall lower panels cover main frame lower and upper rails in silhouette
for side in ('PORT','STBD'):
 names=[f'V18_05_{side}_RemovableSideSkin_0',f'V18_05_{side}_LowerRocker_1',f'V18_05_{side}_RemovableSideSkin_2']
 for name in names:
  assert scene.geometry[name].bounds[0,1] <= .35,name
  assert abs(scene.geometry[name].bounds[0 if side=='PORT' else 1,0])>=1.2,name

path=OUT/'FORGE_V18_05_Body_Integration.glb'
scene.export(path,file_type='glb')
roundtrip=trimesh.load(path,force='scene',process=False)
assert len(roundtrip.geometry)==len(scene.geometry)
assert set(roundtrip.geometry)==set(scene.geometry)
assert all(m.is_watertight and m.is_winding_consistent for m in roundtrip.geometry.values())
triangles=sum(len(m.faces) for m in roundtrip.geometry.values())
summary={
 'revision':'FORGE V18.05 cockpit-to-rear integration and fitted lower fairings',
 'model':'FORGE_V18_05_Body_Integration.glb',
 'base_model':'FORGE V18.04 preserved, 557 original meshes vertex-for-vertex',
 'original_meshes_unchanged':len(initial_geometry),
 'added_separate_meshes':len(newparts),
 'total_meshes':len(roundtrip.geometry),'total_triangles':triangles,
 'new_modules':modules,
 'underbody':'5-piece central undertray, fitted side fairings, service recesses with real openings',
 'rear_roof':'extended center crown, separate long swept left/right shoulders, armor haunch panels, real attachment feet',
 'caution':'Retained original frame; multi-part overlaps and closed meshes, not a boolean-union or engineering-grade FEA',
 'owner_review_status':'pending',
 'new_parts':newparts,
}
(OUT/'V18_05_Manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
print('NFR_V18_05_BODY_PANELS_OK',json.dumps({key:summary[key] for key in ('original_meshes_unchanged','added_separate_meshes','total_meshes','total_triangles','new_modules')}))
