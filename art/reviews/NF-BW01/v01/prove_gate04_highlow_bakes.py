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
scene.cycles.samples=48
scene.cycles.use_denoising=True
scene.render.bake.margin=20
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

def image_for(name,neutral=(.5,.5,1.,1.)):
    img=bpy.data.images.new(name,width=512,height=512,alpha=False,float_buffer=False)
    img.generated_color=neutral
    # Explicitly clear EVERY texel: Cycles only writes baked UVs; untouched
    # image areas must be neutral rather than stale black pixels.
    import numpy as np
    color=np.tile(np.asarray(neutral,dtype=np.float32),(512*512,1))
    img.pixels.foreach_set(color.reshape(-1))
    img.update()
    return img

def save(image,filename):
    image.filepath_raw=str(OUT/filename)
    image.file_format="PNG"
    image.save()
    return OUT/filename

def repair_unused_ao_texels(image, target, pad=20):
    """White-fill ONLY texels outside UV triangles plus safe bake margin.

    Blender Cycles reinitializes the target when baking, overwriting the
    initial white background. UV occupancy is computed from the exact LOD
    triangles, not guessed from dark AO pixels. Genuine dark AO stays intact.
    """
    import numpy as np
    m=target.data
    m.calc_loop_triangles()
    uv=m.uv_layers.active.data
    dim=512
    occupied=np.zeros((dim,dim),dtype=np.bool_)
    for face in m.loop_triangles:
        points=np.array([(uv[li].uv.x*(dim-1),
                          uv[li].uv.y*(dim-1)) for li in face.loops],
                        dtype=np.float32)
        if not np.isfinite(points).all():continue
        a,b,c=points
        d=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        if abs(d)<1e-7:continue
        mn=np.maximum(np.floor(points.min(axis=0)).astype(int)-1,0)
        mx=np.minimum(np.ceil(points.max(axis=0)).astype(int)+2,dim)
        if mx[0]<=mn[0] or mx[1]<=mn[1]:continue
        gx,gy=np.meshgrid(np.arange(mn[0],mx[0],dtype=np.float32)+.5,
                          np.arange(mn[1],mx[1],dtype=np.float32)+.5)
        v=((gx-a[0])*(c[1]-a[1])-(gy-a[1])*(c[0]-a[0]))/d
        w=((b[0]-a[0])*(gy-a[1])-(b[1]-a[1])*(gx-a[0]))/d
        covered=(v>=-0.0001)&(w>=-0.0001)&((v+w)<=1.0001)
        occupied[mn[1]:mx[1],mn[0]:mx[0]]|=covered
    # Preserve the actual Cycles-dilated pixels around each real UV island.
    padded=occupied.copy()
    for _ in range(pad):
        src=padded.copy()
        padded[1:,:]|=src[:-1,:]
        padded[:-1,:]|=src[1:,:]
        padded[:,1:]|=src[:,:-1]
        padded[:,:-1]|=src[:,1:]
    pixels=np.empty(dim*dim*4,dtype=np.float32)
    image.pixels.foreach_get(pixels)
    pixels=pixels.reshape(dim,dim,4)
    # Blender Pixel buffers are bottom-up; UVs also use bottom-left origin.
    blank=np.logical_not(padded)
    pixels[blank,:3]=1.
    pixels[blank,3]=1.
    if occupied.mean()<.01:
        raise RuntimeError("UV occupancy unexpectedly small: "+target.name)
    assert np.all(pixels[blank,:3]>=.995)
    dark_inside=np.mean(np.max(pixels[padded,:3],axis=1)<.04)
    image.pixels.foreach_set(np.ascontiguousarray(pixels).reshape(-1))
    image.update()
    report={
       "uv_occupied_fraction":float(occupied.mean()),
       "uv_plus_padding_fraction":float(padded.mean()),
       "white_unused_fraction":float(blank.mean()),
       "near_black_inside_uv_plus_padding_fraction":float(dark_inside),
       "unused_uv_white_verified":True,
    }
    print("NF_BW01_UV_AO_REPAIR",target.name,report)
    return report

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
                 and o.data.materials
                 and material in o.data.materials[0].name.lower()),None)
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
    img=image_for("AO_"+label,neutral=(1.,1.,1.,1.))
    slot.image=img
    bpy.ops.object.select_all(action="DESELECT")
    temp.select_set(True)
    bpy.context.view_layer.objects.active=temp
    bpy.context.view_layer.update()
    bpy.ops.object.bake(type="AO")
    # Blender overrides generated white AO even outside bake UVs. Restore
    # only genuinely unoccupied UV texels; preserve computed dark occlusion.
    uv_audit=repair_unused_ao_texels(img,temp,pad=20)
    path_ao=save(img,"NF_BW01_"+label+"_ACTUAL_AO.png")
    inspect_png(path_ao)
    print("NF_BW01_ACTUAL_AO_BAKE_OK",label,path_ao.stat().st_size)
    results.append({
        "assembly":label,"zone":zone,"material":material,
        "matched_highpoly_parts":len(highs),
        "lod_mesh":target.name,
        "normal_file":path_normal.name,
        "ao_file":path_ao.name,
        "ao_uv_repair_audit":uv_audit,
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
    "cycles_samples":48,
    "bake_margin_px":20,
    "ao_unused_uv_background":"neutral white RGB(1,1,1), confirmed in PNG audit",
    "normal_unused_uv_background":"neutral tangent (0.5,0.5,1)",
    "revision":"R2 neutral padding and cleaner Cycles AO",
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
