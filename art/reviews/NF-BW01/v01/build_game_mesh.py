"""NF-BW01 Gate 03 -- independently reviewable low-poly LODs/UVs/colliders.

Run with Blender 4.3, --background NF_BW01_GATE02_HIGH_POLY_MASTER.blend
--python build_game_mesh.py -- --out <directory>. High-poly master never modified.

Produces three separate, modular game-mesh candidate GLBs and a collision
proxy GLB.  This is UV and geometry production ONLY; no normal/PBR baking,
no Unity integration, no claim of working robot movement or Android FPS.
"""
import bpy
import sys
import json
import math
import collections
from pathlib import Path
from mathutils import Vector
from mathutils import Matrix

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"gate03_output"
if "--out" in sys.argv:
    OUT=Path(sys.argv[sys.argv.index("--out")+1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)

def collection(name):
    c=bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

SOURCE=[c for c in bpy.data.collections
        if c.name.startswith("BW01_") and "Rendering" not in c.name]
if len(SOURCE)<11:
    raise RuntimeError("Expected editable BW01 assembly groups; found %d"%len(SOURCE))
source_objs=[o for c in SOURCE for o in c.objects
             if o.type in {"MESH","CURVE","FONT"}]
if len(source_objs)<500:
    raise RuntimeError("Approved R2 high-poly master should contain >=500 parts")
assert not any(o.name.startswith("_STUDIO") for o in source_objs)

def physical_bounds(objs):
    dg=bpy.context.evaluated_depsgraph_get()
    coords=[]
    for obj in objs:
        ev=obj.evaluated_get(dg)
        m=ev.to_mesh()
        if m is None:
            continue
        pts=[ev.matrix_world @ v.co for v in m.vertices]
        ev.to_mesh_clear()
        if pts: coords.extend(pts)
    if not coords:
        raise RuntimeError("no vertices")
    lo=[min(p[i] for p in coords) for i in range(3)]
    hi=[max(p[i] for p in coords) for i in range(3)]
    return lo,hi

src_min,src_max=physical_bounds(source_objs)
print("NF_BW01_GATE03_SOURCE_BOUNDS",src_min,src_max)
if max(abs(src_min[0]),src_max[0])>1.97 or max(abs(src_min[1]),src_max[1])>1.29:
    raise RuntimeError("Original source has unexpected dimensions")

def pivot_key(obj):
    p=obj.parent
    while p:
        if "PIVOT" in p.name:
            return p.name
        p=p.parent
    return "STATIC"

def name_to_zone(name):
    return name.split(" | ",1)[0] if " | " in name else name

def box_collision(name,loc,dim,outgroup):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    outgroup.objects.link(o)
    o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return o

# Simple independent BOX collider proxies; never a detailed mesh collider.
# Each remains individually selectable and named for later Unity prefab setup.
collider_collection=collection("GATE03_COLLISION_PREVIEW")
collision_specs=[
 ("Floor footprint", (0,0,.095),(3.72,2.28,.19)),
 ("Robot pedestal",(-1.10,.56,.46),(.85,.79,.76)),
 ("Linear shuttle",(-.17,-.26,.65),(1.40,1.72,.77)),
 ("Power cabinet",(1.61,.70,1.16),(.58,.62,2.26)),
 ("Cassette receiver rack",(1.07,.31,.94),(1.16,1.11,1.61)),
 ("HMI and mast",(1.46,-.82,1.10),(.70,.34,2.0)),
 ("Guard left post",(-1.78,-1.05,1.28),(.11,.12,2.52)),
 ("Guard right post",(1.78,-1.05,1.28),(.11,.12,2.52)),
 ("Robot upper arm approximate",(-1.25,.5,1.50),(.64,.56,1.20)),
 ("Robot elbow approximate",(-1.16,.34,2.18),(.73,.69,.93)),
 ("Robot toolhead approximate",(-.25,-.21,2.13),(.89,.39,.58)),
]
colliders=[box_collision("COLLISION | "+name,loc,dim,collider_collection)
           for name,loc,dim in collision_specs]
bpy.ops.object.select_all(action="DESELECT")
for o in colliders:o.select_set(True)
bpy.context.view_layer.objects.active=colliders[0]
collision_file=OUT/"NF_BW01_COLLISION_PROXIES_REVIEW.glb"
bpy.ops.export_scene.gltf(filepath=str(collision_file),export_format="GLB",
    use_selection=True,export_apply=False,export_materials="NONE")
print("NF_BW01_GATE03_COLLISION_OK",len(colliders))

# Object material groups selected from original source; retaining individual
# robot pivot clusters is essential for later editable/animatable rigs.
# Mechanical detail drops progressively without dropping main silhouette parts.
REMOVE_LOD1=(
 "washer","hex fastener","ring-gland screws","bearing cover",
 "captive shell bolt","structural fastener","anti-rotation",
 "rail mount bolt","status diode","status lamp",
 "indicator","stamped id","surface fastener","wire overlay",
 "captive fastener","stud","screw",
)
REMOVE_LOD2=REMOVE_LOD1+(
 "clamp","retainer","machined flange","fine","grip collar",
 "brace foot","service seam","pipe retainer","status",
 "pigtail","signal braid","dovetail slider",
 "rack tooth","groove","louvre","rubber gasket",
 "wire loom","parallel signal","tactile",
)
CORE_HINTS=("foundation","perimeter","column","frame","beam","shuttle",
            "cassette","robot","arm","joint","pedestal","cabinet","rack",
            "cooling","power","guard","panel","screen","actuator","finger",
            "underframe","underframe |","gripper")

def keep_obj(obj,detail_level):
    if detail_level==0:return True
    name=obj.name.lower()
    ban=REMOVE_LOD1 if detail_level==1 else REMOVE_LOD2
    if any(q in name for q in ban): return False
    # Keep large and core components; eliminate tiny subordinate silhouettes.
    dims=obj.dimensions
    longest=max(dims)
    if detail_level==2 and longest<.085 and not any(k in name for k in CORE_HINTS):
        return False
    if detail_level==1 and longest<.032 and not any(k in name for k in CORE_HINTS):
        return False
    return True

def make_evaluated_mesh(src,target,groupname):
    evaluated=src.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=bpy.data.meshes.new_from_object(
        evaluated, preserve_all_data_layers=True,
        depsgraph=bpy.context.evaluated_depsgraph_get())
    if mesh is None or len(mesh.polygons)==0:return None
    mesh.transform(src.matrix_world)
    dst=bpy.data.objects.new(groupname,mesh)
    target.objects.link(dst)
    return dst

def reduce_object(obj,level):
    # LOD0 must not exceed the high-poly master: preserve the visible silhouette
    # while reducing dense circular bearings/fasteners and modifier tessellation.
    # Avoid decimation on individual tiny parts that already have few faces.
    facecount=len(obj.data.polygons)
    if facecount<160:return
    target=.72 if level==0 else (.66 if level==1 else .35)
    modifier=obj.modifiers.new("Gate03 inspectable decimation","DECIMATE")
    modifier.decimate_type="COLLAPSE"
    modifier.ratio=target
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)

def join_group(objects,name,parent_collection):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.join()
    target=objects[0]
    target.name=name
    return target

def generate_lod(level):
    col=collection("GATE03_LOD%d"%level)
    groups=collections.defaultdict(list)
    counts=collections.Counter()
    for c in SOURCE:
        for src in c.objects:
            if src.type not in ("MESH","CURVE","FONT"):continue
            if not keep_obj(src,level):continue
            material=src.data.materials[0].name if src.data.materials else "UNASSIGNED"
            # One mesh/URP material per physical machine zone and kinematic
            # pivot group, not a scene-wide single joined culling object.
            group=(name_to_zone(c.name),pivot_key(src),material)
            groupstr="|".join(group)
            obj=make_evaluated_mesh(src,col,"TEMP "+groupstr)
            if not obj:continue
            groups[group].append(obj)
            counts["source_parts"]+=1
    if not groups:
        raise RuntimeError("No LOD meshes generated")
    outputs=[]
    for (zone,pivot,material),items in sorted(groups.items()):
        name="NF_BW01_LOD%d | %s | %s | %s"%(level,zone,pivot,material)
        joined=join_group(items,name,col)
        reduce_object(joined,level)
        outputs.append(joined)
    # Smart UV project *per logical group*, not 579 separate calls; assigns
    # non-overlapping faces on the unique UV0 island set of each mesh.
    # No production bake is made until Gate 04.
    for obj in outputs:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(island_margin=.017,correct_aspect=True,
                                 scale_to_bounds=True)
        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.context.view_layer.update()
    tri_count=0
    uv_missing=[]
    invalid_uv=[]
    for obj in outputs:
        m=obj.data
        m.calc_loop_triangles()
        tri_count+=len(m.loop_triangles)
        if not m.uv_layers or len(m.uv_layers.active.data)!=len(m.loops):
            uv_missing.append(obj.name)
        else:
            for uv in m.uv_layers.active.data:
                if not math.isfinite(uv.uv.x) or not math.isfinite(uv.uv.y):
                    invalid_uv.append(obj.name)
                    break
    if uv_missing or invalid_uv:
        raise RuntimeError("UV audit failed missing=%s invalid=%s"%(uv_missing[:3],invalid_uv[:3]))
    bboxmin,bboxmax=physical_bounds(outputs)
    if (bboxmin[0]<-1.98 or bboxmax[0]>1.98 or
        bboxmin[1]<-1.30 or bboxmax[1]>1.30 or
        bboxmin[2]<-.05 or bboxmax[2]>3.43):
        raise RuntimeError("LOD%d bounds outside approved machine envelope"%level)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in outputs:obj.select_set(True)
    bpy.context.view_layer.objects.active=outputs[0]
    file=OUT/("NF_BW01_LOD%d_INSPECTION_ONLY.glb"%level)
    bpy.ops.export_scene.gltf(filepath=str(file),
                              export_format="GLB",use_selection=True,
                              export_apply=False,export_normals=True,
                              export_texcoords=True,export_materials="EXPORT")
    print("NF_BW01_GATE03_LOD_OK",level,tri_count,len(outputs),file.stat().st_size)
    return {
        "level":level,"triangles":tri_count,"renderers":len(outputs),
        "source_parts":counts["source_parts"],
        "uv_meshes_validated":len(outputs),
        "uv_missing":len(uv_missing),"uv_invalid":len(invalid_uv),
        "bounds_min_m":bboxmin,"bounds_max_m":bboxmax,
        "glb":file.name,
        "material_names":sorted(set(o.data.materials[0].name if o.data.materials
                                    else "UNASSIGNED" for o in outputs)),
        "rig_groups":sorted(set(pivot for _,pivot,_ in groups))
    }

lods=[generate_lod(n) for n in (0,1,2)]
if lods[0]["triangles"]>=182600:
    raise RuntimeError("LOD0 must be lighter than approved 182600-triangle source")
if not (lods[0]["triangles"]>lods[1]["triangles"]>lods[2]["triangles"]):
    raise RuntimeError("LOD triangle counts must strictly decrease "+str(lods))
if lods[1]["triangles"]>lods[0]["triangles"]*.82:
    raise RuntimeError("LOD1 not sufficiently reduced")
if lods[2]["triangles"]>lods[0]["triangles"]*.60:
    raise RuntimeError("LOD2 not sufficiently reduced")

# UV limitation: UV0 islands are non-overlapping INSIDE each output mesh, but
# multiple meshes reuse the 0..1 tile. They are not a universal baked atlas.
# Gate 04 must bake by material/assembly texture set with ray cages and UV
# grouping; do NOT claim this is final production texture packing.
report={
 "asset_id":"NF-BW01","gate":"03","status":"GAME_MESH_CANDIDATES_AWAITING_VISUAL_APPROVAL",
 "source":"Approved R2 579-part Blender master",
 "source_part_count":len(source_objs),"source_bounds_min_m":src_min,
 "source_bounds_max_m":src_max,
 "LODs":lods,
 "collision":{"format":"BOX","count":len(colliders),
              "file":collision_file.name,
              "names":[o.name for o in colliders],
              "status":"SIMPLE_PROXIES_UNVALIDATED_BY_GAME_PHYSICS"},
 "uv_strategy":"Smart UV non-overlapping per output mesh; cross-mesh 0..1 tile reused; baking pending Gate04",
 "materials":"Neutral gray clay from Gate02; no final PBR",
 "rigging":"Pivot-group partition retained in named mesh metadata; animation/hierarchy verification pending",
 "approval":"Gate03 PENDING; no Unity scene import, APK or mobile performance claim",
}
(OUT/"gate03_manifest.json").write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"NF_BW01_GATE03_OPTIMIZED_CANDIDATE.blend"),
                           compress=True)
# Same-angle real 3D comparisons, no concept renders or invented materials.
# Keep clay workbench and studio from approved Gate02 master, but isolate the
# selected LOD so its real silhouette can be compared with source.
if "--render" in sys.argv:
    scene=bpy.context.scene
    studio_floor=bpy.data.objects.get("_STUDIO | matte backdrop")
    cams=bpy.data.objects.get("Inspection orthographic")
    if cams is None:
        raise RuntimeError("Source Blender studio camera missing")
    scene.camera=cams
    scene.render.engine="BLENDER_WORKBENCH"
    scene.render.resolution_x=1400
    scene.render.resolution_y=1000
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    visible_sets={"MASTER":source_objs}
    for i in range(3):
        visible_sets["LOD%d"%i]=list(bpy.data.collections["GATE03_LOD%d"%i].objects)
    all_renderable=list({o for arr in visible_sets.values() for o in arr})+colliders
    views={
        "THREE_QUARTER":((7,-10,7),(0,0,1.50),5.15),
        "SIDE":((10,0,1.70),(0,0,1.65),4.55),
    }
    for variant,objs in visible_sets.items():
        for obj in all_renderable:obj.hide_render=True
        for obj in objs:obj.hide_render=False
        if studio_floor:studio_floor.hide_render=False
        for view,(eye,target,scale) in views.items():
            if view=="SIDE" and variant in ("LOD1","LOD2"):
                continue
            cams.location=eye
            cams.rotation_euler=(Vector(target)-cams.location).to_track_quat("-Z","Y").to_euler()
            cams.data.type="ORTHO"
            cams.data.ortho_scale=scale
            bpy.context.view_layer.update()
            name="GATE03_%s_%s"%(variant,view)
            scene.render.filepath=str(OUT/(name+".png"))
            bpy.ops.render.render(write_still=True)
            print("NF_BW01_GATE03_COMPARISON_RENDER_OK",name)
    for obj in all_renderable:obj.hide_render=False
print("NF_BW01_GATE03_PACKAGE_OK",[(x["level"],x["triangles"],x["renderers"]) for x in lods])
