"""Convert the published, verified R6 inspection GLB into Unity 6 FBX + LCD image.

Runs using Blender on the central Eclipse Unity Android runner.
Import/export is ONLY for the garage review: preserve original upstream GLB,
do not re-author the approved R6 asset, and record render mesh statistics.
"""
import bpy,sys,json,collections
from pathlib import Path
args=sys.argv[sys.argv.index("--")+1:]
if len(args)!=2:raise RuntimeError("Usage -- SOURCE_GLb UNITY_RESOURCES_DIRECTORY")
source,out=Path(args[0]).resolve(),Path(args[1]).resolve()
if not source.is_file() or source.stat().st_size<1_000_000:
    raise RuntimeError("Missing actual NF-BW01 R6 inspection GLB")
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(source))
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
if len(meshes)<100:
    raise RuntimeError("Unexpectedly few R6 workstation mesh components")
names=collections.Counter()
triangles=0
for o in meshes:
    names.update(m.name for m in o.data.materials)
    dg=bpy.context.evaluated_depsgraph_get()
    ev=o.evaluated_get(dg);m=ev.to_mesh()
    if m:
        m.calc_loop_triangles()
        triangles+=len(m.loop_triangles)
        ev.to_mesh_clear()
print("NF_BW01_R6_IMPORTED",len(meshes),triangles,list(names.items())[:25])
if triangles<150000 or triangles>450000:
    raise RuntimeError("Suspicious R6 geometry triangle count %d"%triangles)
# GLB glTF Blender-import shader is Principled with texture nodes.
# FBX material support is limited; Unity editor explicitly remaps materials
# to URP, and the HMI LCD gets the original extracted texture.
src_images=[i for i in bpy.data.images
            if "HMI_LCD" in i.name.upper() and i.size[0]>=1024]
if not src_images:raise RuntimeError("R6 original HMI LCD image missing")
lcd=src_images[0]
lcd.filepath_raw=str(out/"NF_BW01_R6_HMI_LCD.png")
lcd.file_format="PNG";lcd.save()
if (out/"NF_BW01_R6_HMI_LCD.png").stat().st_size<1500:
    raise RuntimeError("LCD PNG extraction unexpectedly empty")
# Store material role in the FBX object name: Unity's imported material
# asset names vary across FBX importer versions, but a mesh's hierarchy name
# remains deterministic for URP remapping and glass inspection toggles.
role_counts=collections.Counter()
for o in meshes:
    mats=[m.name.upper() for m in o.data.materials]
    joined=" ".join(mats)
    role="HOUSING"
    if "LCD" in joined and ("EMISSIVE" in joined or "HMI" in joined):
        role="LCD"
    elif "CLEAR INTERLOCKED POLYCARBONATE" in joined:
        role="GLASS"
    elif "MAINTENANCE DECAL" in joined:
        role="DECAL"
    elif "DIAGNOSTIC CYAN" in joined:
        role="CYAN"
    elif "WARNING AMBER" in joined:
        role="AMBER"
    else:
        for k in ("ARMOR","STEEL","BRUSH","DARK","SEAL","MARK","GLAZE","HOUSING"):
            if "NF_BW01_PBR_"+k in joined:
                role=k
                break
    o.name=o.name[:45]+"__NFSTYLE_"+role
    role_counts[role]+=1
if role_counts["LCD"]<1 or role_counts["GLASS"]<5:
    raise RuntimeError("R6 screen or guard material roles missing "+str(role_counts))
print("NF_BW01_UNITY_MATERIAL_ROLES",dict(role_counts))
# Unity FBX import receives Y-up scene; FBX bake_space_transform default
# false is correct for Unity. Transform has no global arbitrary re-centering.
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
dst=out/"NF_BW01_R6_UnityInspection.fbx"
bpy.ops.export_scene.fbx(filepath=str(dst),use_selection=True,
    object_types={"MESH"},axis_forward="-Z",axis_up="Y",
    apply_unit_scale=True,apply_scale_options="FBX_SCALE_UNITS",
    use_mesh_modifiers=True,add_leaf_bones=False,embed_textures=False,
    path_mode="AUTO",bake_anim=False)
if dst.stat().st_size<500000:raise RuntimeError("FBX too small")
manifest={
 "source_glb":source.name,"triangles":triangles,"meshes":len(meshes),
 "material_names":dict(names),"unity_material_roles":dict(role_counts),
 "lcd_source":lcd.name,
 "unity_scene":"FoundryGarage — review station only",
 "note":"FBX materials intentionally remapped to URP; original untouched",
}
(out/"NF_BW01_R6_Inspection_Source.json").write_text(json.dumps(manifest,indent=2))
print("NF_BW01_UNITY_ASSET_CONVERT_OK",dst.stat().st_size,triangles,len(meshes))
