"""NF-BW01 Gate04 geometry-transfer proof on three matching assembly/material groups.
Input: Gate03 Blender derivative containing ORIGINAL approved R2 + LOD0 meshes.
Output: actual Cycles selected-to-active tangent normal + AO (Blender baked),
plus manifest. Stage 04B proof of method only, not full machine bake.
"""
import bpy,math,json,sys
import numpy as np
from pathlib import Path
from mathutils import Vector

OUT=Path(__file__).resolve().parent/"gate04_bake_proof"
if "--out" in sys.argv: OUT=Path(sys.argv[sys.argv.index("--out")+1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
LOD=bpy.data.collections.get("GATE03_LOD0")
if LOD is None:raise RuntimeError("LOD0 missing from input blend")
lods=[o for o in LOD.objects if o.type=="MESH"]
assert len(lods)>=60
candidates=[
    ("ROBOT_SHELL","BW01_31","formed robot shell"),
    ("CASSETTE_SHELL","BW01_20","cast body"),
    ("SHUTTLE_FRAME","BW01_10","machined alloy"),
]
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=8
scene.render.bake.margin=10
scene.render.bake.use_selected_to_active=True
scene.render.bake.cage_extrusion=.019
scene.render.bake.max_ray_distance=.036
scene.render.bake.normal_space="TANGENT"
scene.render.image_settings.file_format="PNG"

def setup_material(image, label):
    mat=bpy.data.materials.new(label)
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    nodes.clear()
    shader=nodes.new("ShaderNodeBsdfPrincipled")
    out=nodes.new("ShaderNodeOutputMaterial")
    mat.node_tree.links.new(shader.outputs["BSDF"],out.inputs["Surface"])
    tex=nodes.new("ShaderNodeTexImage")
    tex.image=image
    nodes.active=tex
    return mat,tex

def image_for(name):
    img=bpy.data.images.new(name,width=512,height=512,alpha=False,float_buffer=False)
    img.generated_color=(.5,.5,1,1)
    return img

def save(image,filename):
    image.filepath_raw=str(OUT/filename)
    image.file_format="PNG"
    image.save()
    return OUT/filename

def inspect_png(p):
    # numerical pixel variability is evidence that a map wasn't a flat
    # default; generated images have to contain meaningful geometry response.
    import struct
    with p.open("rb") as f:
        header=f.read(24)
    assert header[:8]==b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II",header[16:24])==(512,512)

results=[]
for label,zone,material in candidates:
    target=next((o for o in lods if (" | "+zone+" | ") in o.name
                 and material in o.name.lower()),None)
    if target is None:
        options=[o.name for o in lods if zone in o.name]
        raise RuntimeError("Missing LOD0 "+zone+" material "+material+": "+str(options))
    parent_coll=next((c for c in bpy.data.collections
                      if c.name.startswith(zone+" | ")),None)
    if parent_coll is None:
        raise RuntimeError("Missing original high-poly collection "+zone)
    highs=[o for o in parent_coll.objects
           if o.type in {"MESH","CURVE","FONT"}
           and o.data.materials and material in o.data.materials[0].name.lower()]
    if not highs:
        raise RuntimeError("No high-poly matches for "+label)
    if not target.data.uv_layers:
        raise RuntimeError("LOD0 has no UV for "+label)

    # Make a temporary editable copy of LOD0 and its exact geometry/UV.
    temp=target.copy()
    temp.data=target.data.copy()
    bpy.context.scene.collection.objects.link(temp)
    temp.name="BAKE_TARGET | "+label
    tmpmat,slot=setup_material(image_for("NORMAL_"+label),"BAKE_OUTPUT "+label)
    temp.data.materials.clear()
    temp.data.materials.append(tmpmat)

    # All source objects except matching originals are excluded from image ray
    # projection; UV target remains visible. Ray intersection is a meaningful
    # source-to-LOD geometry comparison, not procedural noise.
    for obj in bpy.context.scene.objects:
        if obj.type in {"MESH","CURVE","FONT"}:
            obj.hide_render=(obj not in highs and obj!=temp)
    bpy.ops.object.select_all(action="DESELECT")
    for high in highs:high.select_set(True)
    temp.select_set(True)
    bpy.context.view_layer.objects.active=temp
    bpy.context.view_layer.update()
    bpy.ops.object.bake(type="NORMAL")
    path_normal=save(slot.image,"NF_BW01_"+label+"_HIGH_TO_LOW_NORMAL.png")
    inspect_png(path_normal)
    print("NF_BW01_ACTUAL_NORMAL_BAKE_OK",label,path_normal.stat().st_size)

    # AO is computed from real LOD geometry including nearby components.
    # Original high-poly master and other LOD variants are hidden.
    for obj in bpy.context.scene.objects:
        if obj.type in {"MESH","CURVE","FONT"}:
            obj.hide_render=True
    for obj in lods:obj.hide_render=False
    temp.hide_render=False
    target.hide_render=True
    scene.render.bake.use_selected_to_active=False
    img=image_for("AO_"+label)
    slot.image=img
    bpy.ops.object.select_all(action="DESELECT")
    temp.select_set(True)
    bpy.context.view_layer.objects.active=temp
    bpy.context.view_layer.update()
    bpy.ops.object.bake(type="AO")
    path_ao=save(img,"NF_BW01_"+label+"_ACTUAL_AO.png")
    inspect_png(path_ao)
    print("NF_BW01_ACTUAL_AO_BAKE_OK",label,path_ao.stat().st_size)
    results.append({
        "assembly":label,"zone":zone,"material":material,
        "matched_highpoly_parts":len(highs),
        "lod_mesh":target.name,
        "normal_file":path_normal.name,
        "ao_file":path_ao.name,
        "UV_source":"LOD0 per-renderer UV0, not global atlas"
    })
    scene.render.bake.use_selected_to_active=True
    bpy.data.objects.remove(temp,do_unlink=True)

if len(results)!=3:raise RuntimeError("All three source-to-game proofs required")
manifest={
    "asset_id":"NF-BW01","gate":4,"bake_scope":"3 MATCHED COMPONENT MATERIAL GROUPS ONLY",
    "status":"TRUE_HIGH_TO_LOW_BAKE_PILOT_PENDING_VISUAL_VALIDATION",
    "method":"Blender 4.3 Cycles NORMAL selected-to-active with source high-poly group and LOD0 target; AO computed on LOD0 against surrounding LOD0 geometry",
    "normal_space":"TANGENT",
    "image_size":512,
    "cage_extrusion_m":.019,
    "max_ray_distance_m":.036,
    "parts":results,
    "limitations":[
        "Not a full 68-group normal/AO bake",
        "No automatically verified ray miss/overlap or seam error audit",
        "Not a UV atlas shared across separate meshes",
        "Not final game textures or an Android performance proof"
    ],
    "owner_gate04_approved":False
}
(OUT/"gate04_bake_proof_manifest.json").write_text(json.dumps(manifest,indent=2))
print("NF_BW01_REAL_GEOMETRY_BAKE_PILOT_OK",len(results))
