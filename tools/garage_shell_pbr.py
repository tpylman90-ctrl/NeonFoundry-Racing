"""Physically authored, pre-baked PBR textures for Foundry Lot Stage 01.

All images are original project assets generated offline in Blender with NumPy.
Normal maps come from high-resolution geometric height-field profiles (panel
recesses, fastener dimples, surface grain). Geometry is NOT displaced at
runtime. The glTF ORM is R=Occlusion, G=Roughness, B=Metallic.

Keep this generator deterministic and free of paid external texture assets.
"""
from __future__ import annotations

import math
import numpy as np
import bpy

W, D, H = 39.8, 32.3, 14.78
LEFT, BACK = -19.9, -17.9
SEED = 20261115


def smooth_noise(n: int, grid: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = rng.random((grid, grid)).astype(np.float32)
    uv = np.arange(n, dtype=np.float32) * (grid / n)
    i0 = np.floor(uv).astype(np.int32) % grid
    i1 = (i0 + 1) % grid
    weight = uv - np.floor(uv)
    weight = weight * weight * (3.0 - 2.0 * weight)
    a = base[np.ix_(i0, i0)]
    b = base[np.ix_(i0, i1)]
    c = base[np.ix_(i1, i0)]
    d = base[np.ix_(i1, i1)]
    x = weight[np.newaxis, :]
    y = weight[:, np.newaxis]
    out = (a * (1.0 - x) * (1.0 - y)
           + b * x * (1.0 - y) + c * (1.0 - x) * y + d * x * y)
    out -= out.mean()
    out /= max(float(out.std()), 1e-5)
    return out


def smoothstep(edge_a, edge_b, v):
    t = np.clip((v - edge_a) / (edge_b - edge_a), 0, 1)
    return t * t * (3 - 2 * t)


def seam_profile(coord, count: int, radius: float = 0.014):
    # Signed groove mask measured relative to the physical panel grid.
    frac = np.mod(coord * count, 1.0)
    dis = np.minimum(frac, 1.0 - frac)
    return 1.0 - smoothstep(0.0, radius, dis)


def relief_maps(kind: str, n: int) -> dict:
    u = (np.arange(n, dtype=np.float32) + 0.5) / n
    xx, yy = np.meshgrid(u, u)
    low = smooth_noise(n, 11, 119 + len(kind))
    medium = smooth_noise(n, 41, 251 + len(kind))
    fine = smooth_noise(n, 137, 563 + len(kind))
    rng = np.random.default_rng(SEED + len(kind) * 181)
    ao = np.full((n, n), 0.98, dtype=np.float32)

    if kind == "floor":
        # One unwrapped 39.8m x 32.3m atlas, not the same repeated panel!
        X = LEFT + xx * W
        Z = BACK + yy * D
        dx = W / n
        dz = D / n
        height = 0.0011 * low + 0.00055 * medium + 0.0002 * fine
        base = np.array([0.326, 0.343, 0.355], dtype=np.float32)
        tone = 0.012 * low + 0.006 * medium + 0.0028 * fine
        albedo = np.clip(base[np.newaxis, np.newaxis, :] + tone[:, :, np.newaxis],
                         0.05, 0.95)
        rough = (0.75 + 0.025 * low + 0.012 * medium).astype(np.float32)
        metal = np.full((n, n), 0.065, dtype=np.float32)

        # Small seams near existing physically separated floor tiles. These
        # reinforce those edges, rather than drawing a distracting grid.
        sx = seam_profile(xx, 10, 0.022)
        sy = seam_profile(yy, 8, 0.023)
        seam = np.maximum(sx, sy)
        height -= 0.0035 * seam
        ao -= 0.13 * seam
        albedo *= (1.0 - 0.050 * seam[..., None])

        # Stretched high-gloss maintenance oil drips, broadly distributed
        # and subtle. Polished oil changes ROUGHNESS much more than color.
        oil = np.zeros((n, n), dtype=np.float32)
        for k in range(11):
            x0 = float(rng.uniform(LEFT + 3.0, LEFT + W - 3.0))
            z0 = float(rng.uniform(BACK + 2.5, BACK + D - 2.5))
            angle = float(rng.uniform(-1.4, 1.4))
            length = float(rng.uniform(0.9, 2.3))
            width = float(rng.uniform(0.13, 0.39))
            xc = (X - x0) * math.cos(angle) + (Z - z0) * math.sin(angle)
            yc = -(X - x0) * math.sin(angle) + (Z - z0) * math.cos(angle)
            patch = np.exp(-0.5 * ((xc / length) ** 2 + (yc / width) ** 2))
            oil = np.maximum(oil, patch.astype(np.float32))
        oil *= (0.76 + 0.09 * np.clip(low, -1, 1))
        rough = rough * (1.0 - oil) + 0.27 * oil
        albedo *= (1.0 - 0.075 * oil[..., None])
        metal *= (1.0 - 0.80 * oil)

        # Two directionally scuffed thruster landing areas: fine soot, not
        # solid black rectangles or broad checkerboard textures.
        scuff = np.zeros((n, n), dtype=np.float32)
        for x0, z0, direction in [(-4.0, 1.6, -0.48), (4.1, 1.5, 0.48)]:
            a = (X - x0) * math.cos(direction) + (Z - z0) * math.sin(direction)
            b = -(X - x0) * math.sin(direction) + (Z - z0) * math.cos(direction)
            scuff = np.maximum(scuff, np.exp(-0.5 * ((a / 2.05) ** 2
                                                    + (b / 0.30) ** 2)))
        scuff *= (0.53 + 0.17 * np.clip(medium, -1, 1))
        albedo *= (1.0 - 0.055 * scuff[..., None])
        rough = rough * (1.0 - scuff) + 0.86 * scuff

        # Paint lives ON the floor in the shell texture. This is a ring
        # marking the FUTURE turntable clearance, not a turntable prop.
        r = np.hypot(X, Z + 0.8)
        ring = smoothstep(6.05, 6.16, r) * (1.0 - smoothstep(6.72, 6.83, r))
        theta = np.arctan2(Z + 0.8, X)
        warning_segment = (np.cos(theta * 28.0) > -0.22).astype(np.float32)
        amber = np.array([0.70, 0.385, 0.145], dtype=np.float32)
        graphite = np.array([0.165, 0.177, 0.187], dtype=np.float32)
        stripe_rgb = (warning_segment[..., None] * amber
                      + (1 - warning_segment[..., None]) * graphite)
        wear = 0.91 + 0.05 * np.clip(medium, -1, 1)
        paint = np.clip(ring * wear, 0, 1)
        albedo = albedo * (1.0 - paint[..., None]) + stripe_rgb * paint[..., None]
        rough = rough * (1.0 - paint) + (0.37 + 0.05 * (1.0 - warning_segment)) * paint
        metal *= (1.0 - paint * 0.94)
        height += 0.00025 * paint
        metrics = {"oil_minimum_roughness": float(rough.min()),
                   "painted_hazard_fraction": float(np.mean(paint > 0.15))}

    elif kind.startswith("wall"):
        # Coated precast concrete / satin steel panels. No repeated vertical
        # sin-wave grating or strong directional grooves.
        bays = 10 if kind == "wall_long" else 8
        dx = (W if bays == 10 else D) / n
        dz = H / n
        base = np.array([0.405, 0.426, 0.427], dtype=np.float32)
        tone = 0.011 * low + 0.004 * medium + 0.0015 * fine
        albedo = np.clip(base[np.newaxis, np.newaxis, :] + tone[:, :, np.newaxis],
                         0.08, 0.90)
        rough = (0.765 + 0.030 * low + 0.012 * fine).astype(np.float32)
        metal = np.full((n, n), 0.11, dtype=np.float32)
        height = 0.0006 * low + 0.00025 * medium + 0.00014 * fine

        # Recessed panel seams are high-resolution height details baked
        # into tangent-space normals; no individual groove meshes needed.
        sx = seam_profile(xx, bays, 0.018)
        sy = seam_profile(yy, 3, 0.019)
        seam = np.maximum(sx, sy)
        height -= 0.0045 * seam
        ao -= 0.16 * seam
        albedo *= 1.0 - 0.033 * seam[..., None]

        # 2x2 small stamped fasteners per panel, subtly inset in the paint.
        fy = np.mod(yy * 3, 1.0)
        fx = np.mod(xx * bays, 1.0)
        fasteners = np.zeros((n, n), dtype=np.float32)
        for ax in (0.09, 0.91):
            for ay in (0.12, 0.88):
                rx = (fx - ax) * ((W if bays == 10 else D) / bays)
                ry = (fy - ay) * (H / 3)
                rr = np.sqrt(rx * rx + ry * ry)
                fasteners = np.maximum(fasteners, 1.0 - smoothstep(0.02, 0.055, rr))
        height -= 0.0014 * fasteners
        ao -= 0.055 * fasteners
        rough += 0.025 * fasteners
        metrics = {"seam_coverage": float(np.mean(seam > 0.5))}

    else:
        # Ceiling acoustic cassette trays; understated roughness relief,
        # visible edge recesses but no sinusoidal roof stripes.
        dx = W / n
        dz = D / n
        base = np.array([0.245, 0.271, 0.281], dtype=np.float32)
        tone = 0.010 * low + 0.0035 * medium + 0.0010 * fine
        albedo = np.clip(base[np.newaxis, np.newaxis, :] + tone[:, :, np.newaxis],
                         0.05, 0.95)
        rough = (0.78 + 0.025 * low + 0.010 * fine).astype(np.float32)
        metal = np.full((n, n), 0.24, dtype=np.float32)
        height = 0.0008 * low + 0.00035 * medium + 0.00015 * fine
        seam = np.maximum(seam_profile(xx, 10, 0.021),
                          seam_profile(yy, 8, 0.022))
        height -= 0.0030 * seam
        ao -= 0.12 * seam
        albedo *= 1.0 - 0.045 * seam[..., None]
        metrics = {"seam_coverage": float(np.mean(seam > 0.5))}

    # Tangent-space OpenGL normal pre-bake of high-resolution signed
    # geometric relief, replacing runtime seams/bolts/displacement.
    d_v, d_u = np.gradient(height.astype(np.float32), dz, dx)
    nx = np.clip(-d_u * 0.65, -0.65, 0.65)
    ny = np.clip(-d_v * 0.65, -0.65, 0.65)
    nz = np.ones_like(nx)
    magnitude = np.sqrt(nx * nx + ny * ny + nz * nz)
    normals = np.stack(((nx / magnitude) * 0.5 + 0.5,
                        (ny / magnitude) * 0.5 + 0.5,
                        (nz / magnitude) * 0.5 + 0.5), axis=-1)
    color = np.clip(albedo, 0.0, 1.0).astype(np.float32)
    orm = np.stack((np.clip(ao, 0.60, 1.0),
                    np.clip(rough, 0.22, 0.91),
                    np.clip(metal, 0.0, 0.56)), axis=-1).astype(np.float32)
    assert float(orm[:, :, 0].min()) >= 0.60
    assert float(orm[:, :, 1].std()) > 0.007, "Roughness lacks useful variation"
    assert float(np.max(np.abs(normals[:, :, 0] - 0.5))) < 0.31
    metrics.update({"roughness_range": (float(orm[:, :, 1].min()), float(orm[:, :, 1].max())),
                    "normal_max_slope": float(np.max(np.abs(nx))),
                    "ao_minimum": float(orm[:, :, 0].min())})
    print(f"NEON_FOUNDRY_SHELL_PBR_METRICS {kind} {metrics}")
    return color, orm, normals.astype(np.float32)


def write_image(dest, name: str, pixels: np.ndarray, color_space: str):
    n = pixels.shape[0]
    rgba = np.ones((n, n, 4), dtype=np.float32)
    rgba[:, :, :3] = pixels
    image = bpy.data.images.new(name, width=n, height=n, alpha=True)
    # Non-Color MUST be assigned before saving normals and packed ORM;
    # otherwise Blender's sRGB transfer would corrupt numeric channels.
    image.colorspace_settings.name = color_space
    image.pixels.foreach_set(rgba.reshape(-1))
    image.filepath_raw = str(dest / (name + ".png"))
    image.file_format = "PNG"
    image.save()
    image.pack()
    return image


def shell_material(name: str, kind: str, meters: float, dest):
    size = 2048 if kind == "floor" else 1024
    color, packed_orm, baked_normal = relief_maps(kind, size)
    albedo = write_image(dest, "NF_SHELL_" + kind + "_albedo", color, "sRGB")
    orm = write_image(dest, "NF_SHELL_" + kind + "_ORM", packed_orm, "Non-Color")
    normal = write_image(dest, "NF_SHELL_" + kind + "_bakedNormalGL", baked_normal, "Non-Color")
    del color, packed_orm, baked_normal

    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (0.48, 0.53, 0.54, 1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    links = mat.node_tree.links
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (610, 30)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (335, 30)
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    def tex(image, y):
        node = nodes.new("ShaderNodeTexImage")
        node.image = image
        node.interpolation = "Linear"
        node.extension = "REPEAT"
        node.location = (-600, y)
        return node

    albedo_tex = tex(albedo, 300)
    orm_tex = tex(orm, 10)
    normal_tex = tex(normal, -280)
    split = nodes.new("ShaderNodeSeparateColor")
    split.location = (-300, 0)
    normal_node = nodes.new("ShaderNodeNormalMap")
    normal_node.space = "TANGENT"
    normal_node.inputs["Strength"].default_value = 0.55 if kind == "floor" else 0.40
    normal_node.location = (75, -240)

    links.new(albedo_tex.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(orm_tex.outputs["Color"], split.inputs["Color"])
    links.new(split.outputs["Green"], bsdf.inputs["Roughness"])
    links.new(split.outputs["Blue"], bsdf.inputs["Metallic"])
    links.new(normal_tex.outputs["Color"], normal_node.inputs["Color"])
    links.new(normal_node.outputs["Normal"], bsdf.inputs["Normal"])

    # Blender 5.2 glTF exporter hook. A direct link from the identical ORM
    # Image Texture also permits the exporter to reuse it as AO in red.
    group = bpy.data.node_groups.get("glTF Material Output")
    if group is None:
        group = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
        group.interface.new_socket(name="Occlusion", in_out="INPUT",
                                   socket_type="NodeSocketFloat")
    ao_output = nodes.new("ShaderNodeGroup")
    ao_output.node_tree = group
    ao_output.location = (100, -450)
    links.new(orm_tex.outputs["Color"], ao_output.inputs["Occlusion"])

    mat["surface"] = kind
    mat["uv_texel_metres"] = meters
    mat["maps_packed"] = "R=AO; G=Roughness; B=Metallic"
    mat["normal_origin"] = "Prebaked high-resolution procedural relief (Y+)"
    return mat
