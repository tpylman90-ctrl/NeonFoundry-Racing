"""NF-BW01 Gate 04 MATERIAL LOOKDEV candidate.

Needs the Gate03 approved derivative Blender source file opened in Blender 4.3.
Produces authored PBR base-color, metallic/smoothness, procedural micro-normal
textures per material family and real Cycles studio render(s). This is NOT the
high->low geometry-detail bake (that is a remaining Gate04 acceptance item).
No UV/LOD/kinematic change and no Unity scene integration. Original materials
are preserved in the Gate02/03 sources; this creates a derivative .blend/GLB.
"""
import bpy, sys, math, json
import numpy as np
from mathutils import Vector
from pathlib import Path

OUT=Path(__file__).resolve().parent/"gate04_output"
if "--out" in sys.argv:OUT=Path(sys.argv[sys.argv.index("--out")+1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
TDIR=OUT/"textures";TDIR.mkdir(exist_ok=True)
RES=512
# The shader works in UV0 local [0,1] tiles. Approved LOD0 has 68 renderers,
# each with its own UV tiles. Do not call this a unified high->low normal bake.
SURFACES={
    "HOUSING":{"title":"Graphite microtexture powdercoat","rgb":(.17,.19,.215),"metal":.38,"smooth":.46,"grain":.15,"type":"powder"},
    "STEEL":{"title":"Cold machined tool steel","rgb":(.46,.50,.53),"metal":.94,"smooth":.65,"grain":.09,"type":"brushed"},
    "BRUSH":{"title":"Brushed bright aerospace aluminum","rgb":(.59,.64,.67),"metal":.93,"smooth":.74,"grain":.10,"type":"brushed"},
    "DARK":{"title":"Black polymer and recessed steel","rgb":(.06,.074,.085),"metal":.12,"smooth":.31,"grain":.14,"type":"polymer"},
    "ARMOR":{"title":"Safety orange formed robot shell","rgb":(.82,.255,.067),"metal":.42,"smooth":.62,"grain":.09,"type":"paint"},
    "SEAL":{"title":"Nitrile elastomer and corrugated hoses","rgb":(.052,.063,.068),"metal":.0,"smooth":.22,"grain":.19,"type":"rubber"},
    "MARK":{"title":"Light gray insulated ceramic signage","rgb":(.73,.74,.69),"metal":.02,"smooth":.40,"grain":.16,"type":"ceramic"},
    "GLAZE":{"title":"Deep navy diagnostic interface glass","rgb":(.039,.112,.145),"metal":.17,"smooth":.84,"grain":.035,"type":"glass"},
}
def save_image(name,values,color_space="sRGB"):
    arr=np.array(values,dtype=np.float32)
    assert arr.shape==(RES,RES,4)
    arr=np.ascontiguousarray(np.clip(arr,0,1),dtype=np.float32)
    im=bpy.data.images.new(name,width=RES,height=RES,alpha=True, float_buffer=False)
    im.pixels.foreach_set(arr.reshape(-1))
    im.filepath_raw=str(TDIR/(name+".png"))
    im.file_format="PNG"
    im.save()
    im.colorspace_settings.name=color_space
    bpy.data.images[name].pack()
    return im

xs,ys=np.meshgrid(np.arange(RES),np.arange(RES))
base_rng=np.random.default_rng(70041)
hnoise=base_rng.normal(0,1,(RES,RES)).astype("float32")
# Flat tiling microdetail only, no false high-poly detail claim.
for key,meta in SURFACES.items():
    seed=1111+sum(map(ord,key))
    rng=np.random.default_rng(seed)
    n=rng.normal(0,1,(RES,RES)).astype("float32")
    # tileable periodic low frequency grain plus short fine-frequency pattern
    wave=np.sin(xs*math.tau*7/RES)*np.cos(ys*math.tau*11/RES)
    micro=np.sin(xs*math.tau*109/RES+np.cos(ys*.11))*.32
    if meta["type"]=="brushed":
        detail=(.55*n+.45*np.sin(ys*math.tau*180/RES))*.045
        h=.65*n+.35*np.sin(ys*math.tau*180/RES)
    elif meta["type"]=="rubber":
        detail=(.6*n+.4*wave)*.09
        h=n*.55+wave*.45
    else:
        detail=(.67*n+.25*wave+.08*micro)*.055
        h=n*.75+wave*.25
    v=np.clip(1+detail, .74,1.18)
    rgba=np.ones((RES,RES,4),dtype=np.float32)
    for i,ch in enumerate(meta["rgb"]):
        rgba[:,:,i]=np.clip(ch*v,0,1)
    base_img=save_image("NF_BW01_"+key+"_BASE",rgba)
    packed=np.ones((RES,RES,4),dtype=np.float32)
    packed[:,:,0]=np.clip(meta["metal"]+detail*.055,0,1)
    packed[:,:,1]=packed[:,:,2]=0.
    packed[:,:,3]=np.clip(meta["smooth"]+detail*.20,0,1)
    mr_img=save_image("NF_BW01_"+key+"_URP_METAL_SMOOTH",packed,"Non-Color")
    # Derivatives from an artificial micro-height, normal in tangent
    # orientation. Crucially: NOT a selected-to-active geometry normal bake.
    dx=(np.roll(h,-1,1)-np.roll(h,1,1))*.5*meta["grain"]
    dy=(np.roll(h,-1,0)-np.roll(h,1,0))*.5*meta["grain"]
    zz=np.ones_like(dx)
    norm=np.sqrt(dx*dx+dy*dy+zz*zz)
    nm=np.ones((RES,RES,4),dtype=np.float32)
    nm[:,:,0]=(((-dx/norm)*.5)+.5)
    nm[:,:,1]=(((-dy/norm)*.5)+.5)
    nm[:,:,2]=.5*(zz/norm+1)
    norm_img=save_image("NF_BW01_"+key+"_MICRO_NORMAL_NOT_BAKED",nm,"Non-Color")
    meta["textures"]={
        "albedo":Path(base_img.filepath_raw).name,
        "urp_metal_smooth":Path(mr_img.filepath_raw).name,
        "procedural_micro_normal_not_highlow_bake":Path(norm_img.filepath_raw).name
    }

# Only change the derivative Gate03 LOD0 meshes.
LOD="GATE03_LOD0"
if LOD not in bpy.data.collections:raise RuntimeError("LOD0 absent in Gate03 source")
meshes=[o for o in bpy.data.collections[LOD].objects if o.type=="MESH"]
if len(meshes)<50:raise RuntimeError("Unexpectedly few approved LOD0 renderer groups")

def lookdev_mat(key):
    meta=SURFACES[key]
    m=bpy.data.materials.new("NF_BW01_PBR_"+key)
    m.use_nodes=True
    m.diffuse_color=(*meta["rgb"],1)
    n=m.node_tree.nodes
    n.clear();ln=m.node_tree.links
    output=n.new("ShaderNodeOutputMaterial");output.location=(580,0)
    bsdf=n.new("ShaderNodeBsdfPrincipled");bsdf.location=(330,0)
    ln.new(bsdf.outputs["BSDF"],output.inputs["Surface"])
    base=n.new("ShaderNodeTexImage")
    base.image=bpy.data.images["NF_BW01_"+key+"_BASE"]
    base.location=(-640,280);base.label="Authored tiled base color"
    packed=n.new("ShaderNodeTexImage")
    packed.image=bpy.data.images["NF_BW01_"+key+"_URP_METAL_SMOOTH"]
    packed.location=(-640,-40);packed.label="URP Metallic R / Smoothness A (1-roughness)"
    micro=n.new("ShaderNodeTexImage")
    micro.image=bpy.data.images["NF_BW01_"+key+"_MICRO_NORMAL_NOT_BAKED"]
    micro.location=(-640,-330);micro.label="Procedural tangent micro normal (NOT high-low bake)"
    nm=n.new("ShaderNodeNormalMap")
    nm.location=(-60,-290);nm.inputs["Strength"].default_value=.35
    ln.new(micro.outputs["Color"],nm.inputs["Color"])
    metal_split=n.new("ShaderNodeSeparateColor")
    metal_split.location=(-220,-45)
    rough=n.new("ShaderNodeMath");rough.operation="SUBTRACT"
    rough.inputs[0].default_value=1.
    rough.location=(-60,-125)
    ln.new(packed.outputs["Color"],metal_split.inputs["Color"])
    ln.new(metal_split.outputs["Red"],bsdf.inputs["Metallic"])
    ln.new(packed.outputs["Alpha"],rough.inputs[1])
    ln.new(rough.outputs["Value"],bsdf.inputs["Roughness"])
    ln.new(base.outputs["Color"],bsdf.inputs["Base Color"])
    ln.new(nm.outputs["Normal"],bsdf.inputs["Normal"])
    return m

materials={key:lookdev_mat(key) for key in SURFACES}
assignments={}
for o in meshes:
    # Original Gate03 grouping: "NF_BW01_LOD0 | <assembly> | <pivot> | CLAY | <name>"
    tokens=o.name.split(" | ")
    origin=" ".join(tokens[3:]).lower()
    key="HOUSING"
    for candidate,word in (
        ("STEEL","machined alloy"),("BRUSH","brushed aluminum"),
        ("DARK","dark recess"),("ARMOR","formed robot shell"),
        ("SEAL","gasket rubber"),("MARK","indicator"),
        ("GLAZE","recessed screen"),("HOUSING","cast body")
    ):
        if word in origin:
            key=candidate;break
    if o.data.materials:
        original=o.data.materials[0].name.lower()
        for candidate,word in (
            ("STEEL","machined alloy"),("BRUSH","brushed aluminum"),
            ("DARK","dark recess"),("ARMOR","formed robot shell"),
            ("SEAL","gasket rubber"),("MARK","indicator"),
            ("GLAZE","recessed screen"),("HOUSING","cast body")
        ):
            if word in original:key=candidate;break
    o.data.materials.clear()
    o.data.materials.append(materials[key])
    assignments[o.name]=key
if not {"HOUSING","STEEL","ARMOR","DARK"}.issubset(set(assignments.values())):
    raise RuntimeError("Expected original cast/steel/orange/dark surface families")
print("NF_BW01_PBR_ASSIGNMENTS_OK",len(assignments),dict(__import__("collections").Counter(assignments.values())))

# Hide high-poly, LOD1/2, collision and studio objects from Cycles.
for o in bpy.context.scene.objects:
    if o.type in {"MESH","CURVE","FONT"} and o not in meshes:
        o.hide_render=True

# Keep actual geometry mesh and named groups independent in export.
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
bpy.ops.export_scene.gltf(
    filepath=str(OUT/"NF_BW01_GATE04_PBR_LOOKDEV_ONLY.glb"),
    export_format="GLB",use_selection=True,export_apply=False,
    export_normals=True,export_texcoords=True,export_materials="EXPORT")
print("NF_BW01_GATE04_LOOKDEV_GLB_OK")

scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_x=1040
scene.render.resolution_y=780
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
# The studio backdrop is visible only for final beauty, never in glTF.
floor=bpy.data.objects.get("_STUDIO | matte backdrop")
if floor:floor.hide_render=False
world=scene.world
if world:
    world.use_nodes=True
    bg=world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value=(.18,.21,.24,1)
        bg.inputs["Strength"].default_value=.68

def area(name,loc,power,color,shape,size,target=(0,0,1.1)):
    data=bpy.data.lights.new(name,"AREA")
    ob=bpy.data.objects.new(name,data)
    bpy.context.scene.collection.objects.link(ob)
    ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler()
    data.energy=power
    data.color=color
    data.shape=shape
    data.size=size
    return ob

area("LOOKDEV | large softbox",(-4,-6,6),1350,(1,.95,.85),"DISK",5)
area("LOOKDEV | cold rim",(4,4,5),1450,(.64,.81,1),"DISK",4)
area("LOOKDEV | top strip",(-1,0,6),850,(1,1,1),"DISK",3)

camera=bpy.data.objects.get("Inspection orthographic")
if not camera or camera.type!="CAMERA":
    raise RuntimeError("Approved scene studio camera missing")
scene.camera=camera
views={
 "NF_BW01_GATE04_THREE_QUARTER":((7,-10,7),(0,0,1.50),5.15),
 "NF_BW01_GATE04_REAR_THREE_QUARTER":((-7,9,6),(0,0,1.50),5.15),
 "NF_BW01_GATE04_ROBOT_DETAIL":((1.5,-5,4.3),(-.9,.3,1.8),3.0),
 "NF_BW01_GATE04_GRIPPER_DETAIL":((1.0,-4.0,3.1),(-.25,-.21,2.12),1.58),
 "NF_BW01_GATE04_CASSETTE_DETAIL":((3.6,-4.8,3.6),(-.12,-.15,1.12),2.38),
}
for name,(eye,target,scale) in views.items():
    camera.location=eye
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.type="ORTHO";camera.data.ortho_scale=scale
    scene.render.filepath=str(OUT/(name+".png"))
    bpy.ops.render.render(write_still=True)
    print("NF_BW01_GATE04_RENDER_OK",name)

# Persist derivative authored shader scene after rendering only: source untouched.
scene.render.filepath=""
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"NF_BW01_GATE04_PBR_LOOKDEV.blend"),compress=True)
manifest={
 "asset_id":"NF-BW01","gate":4,"status":"MATERIAL_LOOKDEV_REVIEW_PENDING",
 "approved_source":"Gate03 LOD0 visual master", "renderer_groups":len(meshes),
 "material_families":SURFACES,"texture_resolution":RES,
 "texture_family_count":len(SURFACES),
 "channel_packing":{"urp_metallic":"R","urp_smoothness":"A = 1 - roughness",
 "base_color":"sRGB RGB","micro_normal":"RGB, tangent, Non-Color",
 "ao":"NOT GENERATED YET","high_to_low_normal":"NOT GENERATED YET"},
 "uvs":"Reusable UV0 per output renderer mesh. Not global non-overlap atlas.",
 "baked_geometry_detail":False,
 "revision":"Gate04 lookdev R2: 32-sample Cycles detail inspection views",
 "validation_needed":[
    "Cycles rendered beauty and metallic/roughness visual review",
    "Proper high-to-low normal selected-to-active cage/UV construction",
    "Actual AO bake and seam/padding audit",
    "URP texture importer and matching Unity screenshot at Gate05",
    "Actual Android performance at Gate07"
 ],
 "files":[x.name for x in sorted(OUT.glob("*.glb"))]+
         [x.name for x in sorted(TDIR.glob("*.png"))]
}
(OUT/"gate04_manifest.json").write_text(json.dumps(manifest,indent=2))
print("NF_BW01_GATE04_MATERIAL_LOOKDEV_OK",len(meshes),len(SURFACES),len(list(TDIR.glob("*.png"))))
