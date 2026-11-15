#!/usr/bin/env python3
"""NFR Khronos donor Stage02: real interchangeable quarter canards, aero fins and rear jets.
License: NFR-generated parts CC0. Khronos donor CC BY-4.0; source marks excluded.
Builds from pre-existing verified Khronos modular pilot assets. No edits to donor meshes.
"""
import argparse,copy,json,math,struct
from pathlib import Path
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

C={
 'body':([0.46,0.54,0.59,1.0],.68,.31),
 'dark':([0.062,0.075,0.093,1.0],.53,.46),
 'trim':([0.24,0.31,0.36,1.0],.8,.28),
 'accent':([0.04,0.82,0.87,1.0],.2,.34),
 'heated':([0.6,0.28,0.12,1.0],.65,.45),
}
M={}
for k,(rgba,metal,rough) in C.items():
 M[k]=PBRMaterial(name='NFR_Stage02_'+k,baseColorFactor=rgba,metallicFactor=metal,roughnessFactor=rough,
                   emissiveFactor=([.03,.40,.42] if k=='accent' else None))

def register(out,name,mesh,mat='body'):
 if not isinstance(mesh,trimesh.Trimesh) or not len(mesh.faces): raise ValueError(name)
 mesh.visual=trimesh.visual.TextureVisuals(material=M[mat])
 out[name]=mesh

def box(out,name,center,size,mat='trim'):
 mesh=trimesh.creation.box(extents=size);mesh.apply_translation(center);register(out,name,mesh,mat)

def cylinder_between(out,name,a,b,radius=0.025,segments=12,mat='dark'):
 a,b=np.array(a,float),np.array(b,float)
 mesh=trimesh.creation.cylinder(radius=radius,segment=np.vstack((a,b)),sections=segments)
 register(out,name,mesh,mat)

def tube_z(out,name,x,y,z0,z1,r0o,r1o,r0i,r1i,mat='trim',n=24):
 """Open, actual hollow 4-ring annular tapered nozzle (incl. interior wall)."""
 assert r0o>r0i>0 and r1o>r1i>0 and z0!=z1
 angle=np.arange(n)*2*math.pi/n
 rings=[]
 for z,r in ((z0,r0o),(z1,r1o),(z0,r0i),(z1,r1i)):
  rings.append(np.column_stack((x+r*np.cos(angle),y+r*np.sin(angle),np.full(n,z))))
 v=np.concatenate(rings)
 faces=[]
 for a,b,reverse in [(0,1,False),(2,3,True),(0,2,True),(1,3,False)]:
  for i in range(n):
   j=(i+1)%n
   p,q,u,w=a*n+i,a*n+j,b*n+i,b*n+j
   faces.extend(([p,u,q],[q,u,w]) if reverse else ([p,q,u],[q,w,u]))
 mesh=trimesh.Trimesh(vertices=v,faces=np.array(faces,dtype=int),process=True)
 trimesh.repair.fix_normals(mesh)
 register(out,name,mesh,mat)

def airfoil(out,name,sweep,mat='body'):
 """Loft from four 3D wing sections; six chord stations, top and bottom, enclosed."""
 vertices=[];faces=[];n=16
 for span,zfront,zback,height,thick in sweep:
  for j in range(n):
   a=j/n*2*math.pi
   f=(1-math.cos(a))/2
   z=zfront+(zback-zfront)*f
   t=math.sin(a) * thick * (0.42+0.58*math.sin(math.pi*f))
   vertices.append((span,height+t,z))
 for k in range(len(sweep)-1):
  for j in range(n):
   p=k*n+j;q=k*n+(j+1)%n;u=(k+1)*n+j;w=(k+1)*n+(j+1)%n
   faces.extend(([p,u,q],[q,u,w]))
 for k,rev in [(0,True),(len(sweep)-1,False)]:
  base=k*n; center=np.mean(np.array(vertices[base:base+n]),axis=0)
  ci=len(vertices);vertices.append(center)
  for j in range(n):
   if rev:faces.append([ci,base+j,base+(j+1)%n])
   else:faces.append([ci,base+(j+1)%n,base+j])
 m=trimesh.Trimesh(vertices=np.array(vertices),faces=np.array(faces),process=True)
 trimesh.repair.fix_normals(m)
 register(out,name,m,mat)

def vertical_fin(out,name,profile,xc,width,mat='body'):
 """Y/Z polygon extruded across X, retains aerodynamic rake and face chamfer."""
 n=len(profile)
 vs=[(xc-width/2,y,z) for y,z in profile]+[(xc+width/2,y,z) for y,z in profile]
 # triangle fan valid only for convex profile; authored convex surfaces
 fs=[]
 for i in range(1,n-1): fs.append([0,i,i+1]);fs.append([n,n+i+1,n+i])
 for i in range(n):
  j=(i+1)%n
  fs.extend(([i,j,n+i],[j,n+j,n+i]))
 m=trimesh.Trimesh(vertices=vs,faces=fs,process=True);trimesh.repair.fix_normals(m);register(out,name,m,mat)

def build_quarters(style):
 out={}
 # Donor's actual +Z-facing hood shoulder at x≈±1.03,y≈0.85,z≈1.30
 for sign in [-1,1]:
  tag='PORT' if sign<0 else 'STARBOARD'
  # Real mounting base with 2 separately visible fasteners, set into sculpted shoulder
  box(out,f'QUARTER_{tag}_ROOT_SHOE',(sign*1.036,.858,1.30),(.14,.055,.39),'trim')
  box(out,f'QUARTER_{tag}_ROOT_GASKET',(sign*1.046,.827,1.30),(.15,.014,.40),'dark')
  for zi in [1.18,1.42]:
   cylinder_between(out,f'QUARTER_{tag}_CAPSCREW_{zi}',(sign*1.069,.895,zi),(sign*1.069,.914,zi),.014,10,'dark')
  if style==0:
   lengths=[(.995,1.52,1.10,.890,.027),(1.14,1.48,1.07,.91,.031),(1.31,1.31,.99,.93,.024)]
   airfoil(out,f'QUARTER_{tag}_STREET_SWEEP',[(sign*x,zf,zb,y,t) for x,zf,zb,y,t in lengths],'body')
  if style>=1:
   dims=([(1.00,1.53,1.09,.905,.036),(1.18,1.49,1.03,.929,.044),(1.38,1.30,.91,.951,.018)]
      if style==1 else [(1.00,1.57,1.05,.906,.048),(1.18,1.51,1.0,.94,.050),(1.51,1.29,.80,.997,.022)])
   airfoil(out,f'QUARTER_{tag}_MAIN_CANARD',[(sign*x,zf,zb,y,t) for x,zf,zb,y,t in dims],'body')
   # Two separate structural tie-rods, not floating appendages
   for i,z in enumerate((1.14,1.36)):
    cylinder_between(out,f'QUARTER_{tag}_UNDERSTRUT_{i}',
         (sign*1.05,.81,z),(sign*(1.32 if style==1 else 1.42),.916,z-.12),.014,12,'trim')
   if style==1:
    airfoil(out,f'QUARTER_{tag}_UPPER_SPLIT',[
       (sign*1.08,1.40,1.17,.991,.018),
       (sign*1.19,1.35,1.105,1.04,.021),
       (sign*1.30,1.20,1.04,1.07,.010)],'dark')
   else:
    vertical_fin(out,f'QUARTER_{tag}_ARMORED_FENCE',
       [(.93,1.18),(.93,1.50),(1.16,1.32),(1.21,1.03)],sign*1.19,.033,'dark')
    box(out,f'QUARTER_{tag}_CHAMFERED_REINFORCEMENT',(sign*1.16,.93,1.26),(.045,.045,.27),'trim')
 return out

def build_fins(style):
 out={}
 for sign in [-1,1]:
  t='PORT' if sign<0 else 'STARBOARD'
  root=sign*(.70 if style!=2 else .76)
  box(out,f'TAIL_{t}_BOLTED_PEDESTAL',(root,1.038,-1.34),(.19,.065,.52),'trim')
  for z in [-1.52,-1.16]:
   cylinder_between(out,f'TAIL_{t}_M8_CAPTURE_{z}',(root,1.075,z),(root,1.09,z),.021,10,'dark')
  top=[1.23,1.42,1.58][style]
  # Low swept fin: broad chord at the base, taper rearward, not vertical slab
  profile=[(1.08,-1.01),(1.08,-1.66),(top,-1.91 if style>0 else -1.78),
           (top+.055,-1.85 if style>0 else -1.73),(1.15,-1.22)]
  vertical_fin(out,f'TAIL_{t}_SWEPT_STABILIZER',profile,root+sign*.035,[.037,.031,.047][style],'body')
  cylinder_between(out,f'TAIL_{t}_LOAD_BRACE',(root,1.085,-1.53),(root+sign*.09,top-.08,-1.65),.017,10,'trim')
  if style>=1:
   airfoil(out,f'TAIL_{t}_LATERAL_VANE',[
     (sign*.72,-1.10,-1.62,1.07,.025),
     (sign*.96,-1.18,-1.79,1.10,.027),
     (sign*(1.12 if style==1 else 1.25),-1.32,-1.85,1.15,.012)],'dark')
  if style==2:
   for i in range(2):
    box(out,f'TAIL_{t}_ARMOR_RIB_{i}',(root+sign*.073,1.19+i*.12,-1.44-i*.11),(.014,.052,.22),'trim')
 return out

def build_engine(tier):
 out={}
 size=[.225,.245,.272,.29][tier]
 length=[.50,.61,.74,.88][tier]
 end=-2.13-length
 box(out,'ENGINE_MODULAR_CASSETTE_CRADLE',(0,.575,-1.91),(1.42,.20,.47),'dark')
 # Common standardized 4-point socket physically ties the rear hull to modules
 for sg in [-1,1]:
  for z in [-1.75,-2.04]:
   box(out,f'ENGINE_HARDPOINT_{sg}_{z}',(sg*.48,.58,z),(.13,.13,.14),'trim')
  x=sg*.41;y=.57
  # Support nacelle machined chassis cage, not a continuous primitive cylinder
  for a in [0,math.pi/2,math.pi,math.pi*3/2]:
   ox=math.cos(a)*.245;oy=math.sin(a)*.245
   cylinder_between(out,f'ENGINE_{sg}_SUSPENSION_RAIL_{a:.2f}',
                   (x+ox,y+oy,-1.88),(x+ox*1.11,y+oy*1.11,end+.05),.025,10,'trim')
  tube_z(out,f'ENGINE_{sg}_STRUCTURAL_CHAMBER',x,y,-2.03,end+.15,
         .27,size+.065,.185,size*.76,'dark',n=24)
  # Stepped pressure-safe exhaust with real hollow throat, independent heat rings
  tube_z(out,f'ENGINE_{sg}_THROAT',x,y,end+.29,end+.025,size+.005,size+.052,size*.66,size*.76,'trim',n=32)
  tube_z(out,f'ENGINE_{sg}_RECESSED_BELL',x,y,end+.055,end-.025,size+.048,size+.090,size*.73,size*.82,'dark',n=32)
  tube_z(out,f'ENGINE_{sg}_HEATED_INNER_LIP',x,y,end+.08,end-.028,size*.69,size*.805,size*.58,size*.70,'heated',n=32)
  for j in range(2+tier):
   z=-2.1-j*(length-.1)/(2+tier)
   tube_z(out,f'ENGINE_{sg}_SERVICE_COLLAR_{j}',x,y,z,z-.032,
           size+.085,size+.085,size+.035,size+.035,'trim',n=24)
  # Armor segments spaced to expose cooling mechanism; hard faceted plates
  for q in range(6):
   a=(q+.5)*2*math.pi/6; xoff=math.cos(a)*(size+.12);yoff=math.sin(a)*(size+.12)
   cylinder_between(out,f'ENGINE_{sg}_EXTERNAL_HEAT_CHANNEL_{q}',
        (x+xoff,y+yoff,-2.13),(x+xoff*1.02,y+yoff*1.02,end+.1),.014,8,'heated' if q%2 else 'body')
  # Forged side anti-roll cradles and heat shielding visible from profile
  box(out,f'ENGINE_{sg}_SPLIT_SIDE_ARMOR',(x+sg*(size+.11),y-.025,-2.13-length*.31),
      (.048,.215,.38+length*.25),'body')
  if tier>=2:
   for j in range(4):
    z=-2.14-.095*j
    box(out,f'ENGINE_{sg}_HEAT_SINK_FIN_{j}',(x+sg*(size+.14),y+.09,z),(.08,.17,.022),'trim')
  if tier==3:
   bx=sg*.205;by=.93
   tube_z(out,f'ENGINE_UPPER_{sg}_BOOSTER',bx,by,-2.02,-2.62,.132,.151,.09,.109,'dark',n=24)
   tube_z(out,f'ENGINE_UPPER_{sg}_BRONZE_LIP',bx,by,-2.57,-2.63,.15,.17,.105,.123,'heated',n=24)
   box(out,f'ENGINE_UPPER_{sg}_BOOSTER_BRACKET',(bx,.855,-2.17),(.1,.22,.45),'trim')
 return out

def scene_from_parts(parts,origin=(0,0,0),nodeprefix=''):
 s=trimesh.Scene()
 for name,mesh in parts.items():
  g=mesh.copy();g.apply_translation(-np.array(origin,float))
  s.add_geometry(g,geom_name=nodeprefix+name,node_name=nodeprefix+name)
 return s

def write_glb(scene,path):
 blob=scene.export(file_type='glb')
 assert blob[:4]==b'glTF' and struct.unpack_from('<I',blob,8)[0]==len(blob)
 Path(path).write_bytes(blob)
 return len(scene.geometry),sum(len(m.faces) for m in scene.geometry.values())

def preview(base,mode,mods):
 orig=trimesh.load(base,force='scene',process=False)
 result=trimesh.Scene()
 for node in orig.graph.nodes_geometry:
  if node.startswith('INSTALLED_rear_engine_') or node.startswith('INSTALLED_rear_fins_'):
   continue
  tr,key=orig.graph[node]
  result.add_geometry(orig.geometry[key].copy(),node_name=node,geom_name=node,transform=tr)
 for slot,parts in mods.items():
  for name,geo in parts.items():
   result.add_geometry(geo.copy(),node_name=f'STAGE02_{slot}_{name}',geom_name=f'STAGE02_{slot}_{name}')
 return result

def process_assets(root,preview_inputs,out,write_manifest=True):
 root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 # Materials and center positions must match original 9-socket rig.
 sockets={'rear_engine':[0,.57,-1.83],'rear_fins':[0,1.02,-1.05],'front_quarter_fins':[0,.86,1.30]}
 variants={}
 for s in range(3):
  variants[f'quarter_fins_{s}']=('front_quarter_fins',build_quarters(s))
  variants[f'fins_{s}_v2']=('rear_fins',build_fins(s))
 for i,n in enumerate(('engine_stock','engine_vortex','engine_titan','engine_nova')):
  variants[n+'_v2']=('rear_engine',build_engine(i))
 dimensions={}
 for n,(slot,parts) in variants.items():
  scene=scene_from_parts(parts,sockets[slot])
  dimensions[n]=write_glb(scene,out/(n+'.glb'))
  assert all(m.is_watertight for m in scene.geometry.values()),n
 manifest_file=root/'module_manifest.json'
 if manifest_file.exists():
  man=json.loads(manifest_file.read_text())
  for i,item in enumerate(man['slots']['rear_engine']):
   key=item['id']+'_v2';item['scene']='res://assets/vehicle_modular/'+key+'.glb';item['triangles']=dimensions[key][1]
  for i,item in enumerate(man['slots']['rear_fins']):
   key=f'fins_{i}_v2';item['scene']='res://assets/vehicle_modular/'+key+'.glb';item['triangles']=dimensions[key][1]
  man['sockets']['front_quarter_fins']={'position_m':sockets['front_quarter_fins']}
  names=['Street shoulder blades','Aero split quarter canards','Industrial armored quarter fins']
  man['slots']['front_quarter_fins']=[dict(id=f'quarter_fins_{i}',name=names[i],
     scene=f'res://assets/vehicle_modular/quarter_fins_{i}.glb',triangles=dimensions[f'quarter_fins_{i}'][1],style=['street','aero','industrial'][i]) for i in range(3)]
  man['default_loadout']['front_quarter_fins']='quarter_fins_0'
  for i,n in enumerate(['street','aero','industrial']):man['preview_loadouts'][n]['front_quarter_fins']=f'quarter_fins_{i}'
  man['stage']='Stage02: refined hollow rear propulsion + swept stabilizers + integrated front quarter canards'
  man['limitations']+=[
    'New interchangeable fin modules are separate mechanically fitted surfaces, not boolean-fused to original donor.',
    'Rear wheelhouse openings remain unmodified; proper fender retopology required.',
    'High-poly donor retained for visual review, requires mobile LOD/collision before racing.'
  ]
  if write_manifest: (out/'module_manifest_stage02.json').write_text(json.dumps(man,indent=2)+'\n')
 for i,mode in enumerate(['street','aero','industrial']):
  parts={'front_quarter_fins':variants[f'quarter_fins_{i}'][1],
         'rear_fins':variants[f'fins_{i}_v2'][1],
         'rear_engine':variants[['engine_stock_v2','engine_vortex_v2','engine_nova_v2'][i]][1]}
  base=Path(preview_inputs)/f'preview_{mode}.glb'
  if not base.exists(): base=Path(preview_inputs)/f'NFR_{["Street_Phantom","Aero_Strike","Industrial_Forge"][i]}_ANDROID.glb'
  if not base.exists():continue
  s=preview(base,mode,parts)
  dimensions[f'preview_{mode}_stage02']=write_glb(s,out/f'preview_{mode}_stage02.glb')
  for required in ('DONOR_BodyHood','DONOR_BodyRoofPanel','DONOR_BodyWindshield'):
   assert required in s.geometry,required
  assert not any(q.startswith('INSTALLED_rear_engine_') for q in s.geometry)
  print('NFR_STAGE02_PREVIEW',mode,dimensions[f'preview_{mode}_stage02'])
 report={'source':'Khronos Car Concept (CC BY 4.0, logo excluded)','parts':{k:{'slot':variants[k][0],'meshes':v[0],'triangles':v[1]} for k,v in dimensions.items() if k in variants},
         'previews':{k:v for k,v in dimensions.items() if k.startswith('preview_')},'new_slot':sockets['front_quarter_fins'],'preserves_donor_surfaces':True}
 (out/'STAGE02_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 print('NFR_STAGE02_MODULAR_HARDWARE_OK',json.dumps({'modules':len(variants),'preview_count':len(report['previews'])}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='game/assets/vehicle_modular');p.add_argument('--previews',default=None);p.add_argument('--output',default='build/khronos_stage02');a=p.parse_args()
 process_assets(a.root,a.previews or a.root,a.output)
