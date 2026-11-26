"""NF-BW01 R6: compact real-mesh illuminated HMI, not an image concept.

Loads verified R5 .blend; preserves all R5 geometry and original compact HMI
housing; adds a *smaller-than-housing* inset display with a genuine 1024x512
UV image, emission shader, physical trim and tiny glass sheet. The display is
a STATIC illustrative diagnostic texture (not yet a running UI).
"""
import bpy, math, json, sys, numpy as np
from pathlib import Path
from mathutils import Vector

OUT=Path(__file__).resolve().parent/"gate04_r6_output"
if "--out" in sys.argv:OUT=Path(sys.argv[sys.argv.index("--out")+1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
TEX=OUT/"textures";TEX.mkdir(exist_ok=True)
if not bpy.data.collections.get("NF-BW01 R5 | Diagnostics and manufacturing finish"):
    raise RuntimeError("Expected real R5 source collection")
C=bpy.data.collections.new("NF-BW01 R6 | Compact HMI LCD upgrade")
bpy.context.scene.collection.children.link(C)
DARK=bpy.data.materials.get("NF_BW01_PBR_DARK")
STEEL=bpy.data.materials.get("NF_BW01_PBR_STEEL")
if not DARK or not STEEL:raise RuntimeError("Original machine PBR palette missing")

W,H=1024,512
pixel=np.zeros((H,W,4),dtype=np.float32)
pixel[:,:,:3]=(.008,.018,.027);pixel[:,:,3]=1.
def rect(x0,y0,x1,y1,col):
    a,b,c,d=[int(q) for q in (x0,y0,x1,y1)]
    a=max(0,min(W,a));c=max(0,min(W,c))
    b=max(0,min(H,b));d=max(0,min(H,d))
    if c>a and d>b:pixel[b:d,a:c,:3]=col
def line(x0,y0,x1,y1,col,t=2):
    steps=max(abs(int(x1-x0)),abs(int(y1-y0)),1)
    for k in range(steps+1):
        x=int(round(x0+(x1-x0)*k/steps))
        y=int(round(y0+(y1-y0)*k/steps))
        rect(x-t,y-t,x+t+1,y+t+1,col)
CYAN=(.13,.88,.97);WHT=(.73,.86,.90)
DIM=(.20,.37,.43);ORANGE=(1,.38,.07);GREEN=(.16,.87,.57)
# 5x7 compact pixel font, all labels actually written into the UV image.
FONT={
"A":("01110","10001","10001","11111","10001","10001","10001"),
"B":("11110","10001","10001","11110","10001","10001","11110"),
"C":("01111","10000","10000","10000","10000","10000","01111"),
"D":("11110","10001","10001","10001","10001","10001","11110"),
"E":("11111","10000","10000","11110","10000","10000","11111"),
"F":("11111","10000","10000","11110","10000","10000","10000"),
"G":("01111","10000","10000","10111","10001","10001","01111"),
"H":("10001","10001","10001","11111","10001","10001","10001"),
"I":("11111","00100","00100","00100","00100","00100","11111"),
"J":("00111","00010","00010","00010","10010","10010","01100"),
"K":("10001","10010","10100","11000","10100","10010","10001"),
"L":("10000","10000","10000","10000","10000","10000","11111"),
"M":("10001","11011","10101","10101","10001","10001","10001"),
"N":("10001","11001","10101","10011","10001","10001","10001"),
"O":("01110","10001","10001","10001","10001","10001","01110"),
"P":("11110","10001","10001","11110","10000","10000","10000"),
"Q":("01110","10001","10001","10001","10101","10010","01101"),
"R":("11110","10001","10001","11110","10100","10010","10001"),
"S":("01111","10000","10000","01110","00001","00001","11110"),
"T":("11111","00100","00100","00100","00100","00100","00100"),
"U":("10001","10001","10001","10001","10001","10001","01110"),
"V":("10001","10001","10001","10001","10001","01010","00100"),
"W":("10001","10001","10001","10101","10101","10101","01010"),
"X":("10001","10001","01010","00100","01010","10001","10001"),
"Y":("10001","10001","01010","00100","00100","00100","00100"),
"Z":("11111","00001","00010","00100","01000","10000","11111"),
"0":("01110","10001","10011","10101","11001","10001","01110"),
"1":("00100","01100","00100","00100","00100","00100","01110"),
"2":("01110","10001","00001","00010","00100","01000","11111"),
"3":("11110","00001","00001","01110","00001","00001","11110"),
"4":("10010","10010","10010","11111","00010","00010","00010"),
"5":("11111","10000","10000","11110","00001","00001","11110"),
"6":("01111","10000","10000","11110","10001","10001","01110"),
"7":("11111","00001","00010","00100","01000","01000","01000"),
"8":("01110","10001","10001","01110","10001","10001","01110"),
"9":("01110","10001","10001","01111","00001","00001","11110"),
" ":("00000",)*7,"-":("00000","00000","00000","11111","00000","00000","00000"),
"%":("11001","11010","00100","01000","10110","00110","00000"),
".":("00000","00000","00000","00000","00000","01100","01100"),
":":("00000","01100","01100","00000","01100","01100","00000"),
"/":("00001","00010","00010","00100","01000","01000","10000"),
}
def txt(x,y,text,scale=3,color=WHT):
    x0=x
    for ch in text.upper():
        if ch=="\n":y+=scale*10;x=x0;continue
        glyph=FONT.get(ch,FONT[" "])
        for row,bits in enumerate(glyph):
            for col,v in enumerate(bits):
                if v=="1":rect(x+col*scale,y+row*scale,
                               x+(col+1)*scale,y+(row+1)*scale,color)
        x+=scale*6
# Image pixels use bottom-left origin. Compose lower -> upper UI in texture
rect(0,0,W,52,(.018,.052,.067))
rect(0,52,W,55,(.12,.34,.40))
txt(28,16,"NF CELL CONTROL",4,CYAN)
txt(786,18,"NF-BW01",3,ORANGE)
rect(0,470,W,512,(.017,.054,.068))
txt(26,480,"SERVICE  SWAP  MONITOR  ALARM",3,WHT)
# charge area
txt(38,94,"BATTERY CHARGE",3,WHT)
txt(53,166,"87%",10,CYAN)
# segmented battery
rect(47,270,276,368,DIM)
rect(57,280,266,358,(.005,.020,.030))
for i in range(7):
    rect(64+i*27,291,86+i*27,347,CYAN if i<6 else DIM)
# right-column telemetry cards
rect(370,83,989,388,(.012,.041,.052))
txt(393,108,"CELL TEMPERATURE",3,DIM)
txt(395,145,"34.2",6,CYAN)
txt(600,153,"C",3,WHT)
txt(393,233,"CELL LOCK",3,DIM)
txt(635,230,"LOCKED",4,GREEN)
txt(393,305,"COOLING",3,DIM)
txt(635,305,"ACTIVE",4,GREEN)
# bottom progress / waveform and data
rect(43,403,953,407,DIM)
rect(43,403,512,407,ORANGE)
txt(45,424,"SWAP CYCLE  00:42 / 02:15",3,ORANGE)
for i in range(17):
    x=725+i*14
    y=439+int(math.sin(i*.93)*9+math.sin(i*.36)*4)
    if i:line(px,py,x,y,CYAN,1)
    px,py=x,y
im=bpy.data.images.new("NF_BW01_R6_HMI_LCD_1024",W,H,alpha=True)
im.pixels.foreach_set(np.ascontiguousarray(pixel).reshape(-1))
im.filepath_raw=str(TEX/"NF_BW01_R6_HMI_LCD.png")
im.file_format="PNG";im.save();im.pack()
# Create screen material with emissive image, NOT a flat colored rectangle.
mat=bpy.data.materials.new("NF_BW01_R6 | UV LCD emissive image")
mat.use_nodes=True;mat.diffuse_color=(.04,.10,.12,1.)
nodes=mat.node_tree.nodes;nodes.clear()
out=nodes.new("ShaderNodeOutputMaterial")
emi=nodes.new("ShaderNodeEmission")
emi.inputs["Strength"].default_value=1.35
image=nodes.new("ShaderNodeTexImage");image.image=im
mat.node_tree.links.new(image.outputs["Color"],emi.inputs["Color"])
mat.node_tree.links.new(emi.outputs["Emission"],out.inputs["Surface"])
# Physically small: the original HMI border is 0.56m wide x 0.424m tall,
# with actual front face towards camera at negative Y.
cx,cy,cz=1.45,-1.122,1.858
screen_w,screen_h=.462,.288
def box(name,loc,dim,material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name="R6 | "+name
    o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection):c.objects.unlink(o)
    C.objects.link(o);o.data.materials.append(material)
    return o
# Back plate covers former empty bars in original compact recess.
box("existing-size shadow bezel",(cx,cy+.023,cz),(.505,.009,.341),DARK)
box("LCD diffuser backplane",(cx,cy+.010,cz),(.476,.010,.300),DARK)
# Plane is vertical in X/Z; normal faces -Y, matching front operator.
mesh=bpy.data.meshes.new("R6 LCD front UV panel")
x0,x1=cx-screen_w/2,cx+screen_w/2
z0,z1=cz-screen_h/2,cz+screen_h/2
mesh.from_pydata([(x0,cy,z0),(x1,cy,z0),(x1,cy,z1),(x0,cy,z1)],[],
                 [(0,1,2,3)])
mesh.update()
uv=mesh.uv_layers.new(name="LCD_UV")
# quad loop order corresponds bottom-left -> bottom-right -> top-right -> top-left
for li,p in zip(mesh.polygons[0].loop_indices,((0,0),(1,0),(1,1),(0,1))):
    uv.data[li].uv=p
o=bpy.data.objects.new("R6 | genuine UV emissive HMI panel",mesh);C.objects.link(o)
mesh.materials.append(mat)
# Thin visible rim and flush glass corner surface, no oversize floating HMI.
for zz in (cz-.158,cz+.158):
    box("LCD horizontal metal trim %.3f"%zz,(cx,cy-.002,zz),(.493,.012,.010),STEEL)
for xx in (cx-.244,cx+.244):
    box("LCD vertical metal trim %.3f"%xx,(xx,cy-.002,cz),(.010,.012,.317),STEEL)
# Existing three physical controls and orange emergency control stay intact.
# Verify new objects do not exceed original HMI physical exterior silhouette.
assert .505<.56 and .341<.424
assert len(C.objects)==7,len(C.objects)
bpy.context.view_layer.update()
# Save editable version and one actual-geometry glTF.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"NF_BW01_R6_COMPACT_HMI.blend"),compress=True)
include=["GATE03_LOD0","NF-BW01 R3 | Reversible mechanical refinement",
         "NF-BW01 R4 | Clear guard + industrial subassemblies",
         "NF-BW01 R5 | Diagnostics and manufacturing finish",
         "NF-BW01 R6 | Compact HMI LCD upgrade"]
objs=[o for key in include for o in bpy.data.collections[key].objects
      if o.type in {"MESH","CURVE","FONT"}]
bpy.ops.object.select_all(action="DESELECT")
for obj in objs:obj.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
bpy.ops.export_scene.gltf(filepath=str(OUT/"NF_BW01_R6_HMI_INSPECTION.glb"),
    export_format="GLB",use_selection=True,export_normals=True,
    export_texcoords=True,export_materials="EXPORT")
print("NF_BW01_R6_HMI_GEOMETRY_OK",len(C.objects),screen_w,screen_h)
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1040
scene.render.resolution_y=780
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
camera=bpy.data.objects.get("Inspection orthographic")
if not camera:raise RuntimeError("Studio camera absent")
scene.camera=camera
r3=bpy.data.collections["NF-BW01 R3 | Reversible mechanical refinement"]
glazing=[o for o in r3.objects if o.type=="MESH" and any(k in o.name
          for k in ("clear guarding","safety glazing","sliding transparent gate"))]
views={
    "R6_HMI_CLOSEUP":((4.5,-5,3.1),(1.45,-.96,1.85),1.49,True),
    "R6_HMI_FRONT":((4,-8,3.5),(1.1,-.1,1.7),3.25,True),
    "R6_COMPLETE_ENCLOSED":((7,-10,7),(0,0,1.5),5.15,False),
}
for name,(eye,target,scale,cutaway) in views.items():
    for guard in glazing:guard.hide_render=cutaway
    camera.location=eye
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.type="ORTHO";camera.data.ortho_scale=scale
    scene.render.filepath=str(OUT/(name+".png"))
    bpy.ops.render.render(write_still=True)
    print("NF_BW01_R6_HMI_RENDER_OK",name)
for guard in glazing:guard.hide_render=False
(OUT/"R6_HMI_REVIEW.json").write_text(json.dumps({
  "asset":"NF-BW01","gate":4,"revision":"R6 compact LCD",
  "source":"verified R5 Blender release, unchanged",
  "original_hmi_frame_m":[.56,.424],
  "added_lcd_dimensions_m":[screen_w,screen_h],
  "texture_px":[W,H],"lcd_static":True,
  "original_physical_hmi_enlarged":False,
  "status":"ACTUAL_3D_MODEL_VISUAL_REVIEW_PENDING",
  "views":list(views.keys()),
  "still_required":["real-time telemetry or animation","Unity URP screen import",
    "LOD and bake integration","Android device performance"]
},indent=2))
print("NF_BW01_R6_HMI_PACKAGE_OK")
