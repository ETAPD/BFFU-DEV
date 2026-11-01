"""Enhance a GEO World War 2 Models Mod tank (workshop 3132985068) into a BFFU model.

What GEO models lack and this adds:
  * mipmaps (GEO DDS files ship with a single level, which is what makes them shimmer and look jagged)
  * smooth shading: welded vertices + weighted normals, so wheels/barrels/cupolas read round, flat plates stay crisp
  * 2x textures: cubic upscale + light unsharp mask, with ambient occlusion baked from the geometry multiplied in
  * true-to-life size relative to other vehicles (GEO models are all roughly the same length)
  * synced animations: wheel spin derived from each wheel's real radius, track scroll matched to it
"""

import math
import os
import subprocess

import addon_utils
import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import build

GEO_ROOT = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3132985068"
TEX_DIRS = [os.path.join(GEO_ROOT, "gfx", "models", "units", "tanks"), os.path.join(GEO_ROOT, "gfx", "models", "units", "vehicles")]


def log(*a):
    print("[geo_enhance]", *a, flush=True)


def texconv(src, out_dir, fmt, size=None, ext=None, flt="CUBIC"):
    cmd = [os.path.abspath(build.TEXCONV), "-nologo", "-y", "-m", "1" if ext == "png" else "0", "-f", fmt,
           "-if", flt, "-o", out_dir]
    if size:
        cmd += ["-w", str(size[0]), "-h", str(size[1])]
    if ext:
        cmd += ["-ft", ext]
    cmd.append(src)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stdout + r.stderr)
    return os.path.join(out_dir, os.path.splitext(os.path.basename(src))[0] + "." + (ext or "dds"))


def find_texture(name):
    for d in TEX_DIRS:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return p
    raise FileNotFoundError(name)


def dds_size(path):
    import struct
    with open(path, "rb") as f:
        h = f.read(20)
    height, width = struct.unpack("<II", h[12:20])
    return width, height


def load_png(path):
    img = bpy.data.images.load(path)
    img.colorspace_settings.name = "Non-Color"
    return build.pixels(img).copy()


def blur(a, radius):
    """Separable box-ish blur (3 passes approximates a gaussian)."""
    out = a
    for _ in range(3):
        for axis in (0, 1):
            k = 2 * radius + 1
            pad = [(0, 0)] * out.ndim
            pad[axis] = (radius, radius)
            p = np.pad(out, pad, mode="wrap")
            c = np.cumsum(p, axis=axis, dtype=np.float64)
            zero_shape = list(c.shape)
            zero_shape[axis] = 1
            c = np.concatenate([np.zeros(zero_shape), c], axis=axis)
            idx = np.arange(out.shape[axis])
            out = (np.take(c, idx + k, axis=axis) - np.take(c, idx, axis=axis)) / k
    return out.astype(np.float32)


def weld_and_shade(obj, sharp_deg=38.0):
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    # PDX meshes arrive split at every UV/normal seam; weld so shading can average across them (UVs live on loops,
    # so they survive the weld)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    for e in bm.edges:
        e.smooth = not (len(e.link_faces) != 2 or e.calc_face_angle(math.pi) > math.radians(sharp_deg) or e.seam)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()
    mod = obj.modifiers.new("wn", "WEIGHTED_NORMAL")
    mod.keep_sharp = True
    mod.mode = "FACE_AREA"
    mod.weight = 60
    build.select_only([obj])
    bpy.ops.object.modifier_apply(modifier=mod.name)


def material_textures(mat):
    names = {"diffuse": None, "spec": None, "normal": None}
    for n in mat.node_tree.nodes:
        if n.type == "TEX_IMAGE" and n.image:
            low = n.image.name.lower()
            for key in names:
                if key in low:
                    names[key] = n.image.name
    return names


def bake_ao(obj, mats_sizes, samples=128):
    """One AO bake writing each material's faces into its own image (sized to that material's texture)."""
    build.setup_cycles()
    images = {}
    for mat, (w, h) in mats_sizes.items():
        img = bpy.data.images.new("ao_" + mat.name, w, h, alpha=False)
        img.colorspace_settings.name = "Non-Color"
        nt = mat.node_tree
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = img
        for n in nt.nodes:
            n.select = False
        node.select = True
        nt.nodes.active = node
        images[mat] = img
    bpy.context.scene.cycles.samples = samples
    bpy.context.scene.world = bpy.context.scene.world or bpy.data.worlds.new("bake")
    build.select_only([obj])
    bpy.context.scene.render.bake.margin = 12
    bpy.ops.object.bake(type="AO")
    return images


def run(geo_mesh, name, out_dir, work_dir, real_length_m=None, up=2, max_res=2048):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable("io_pdx_mesh")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(work_dir, exist_ok=True)
    bpy.ops.io_pdx_mesh.import_mesh(filepath=geo_mesh, chk_mesh=True, chk_skel=True, chk_locs=True)
    rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    render_meshes = [o for o in meshes if not any(s.material and s.material.get("shader") == "Collision"
                                                  for s in o.material_slots)]

    # ---- true-to-life size --------------------------------------------------------------------------------------
    bpy.context.view_layer.update()
    ys = [(o.matrix_world @ v.co).y for o in render_meshes for v in o.data.vertices]
    geo_len = max(ys) - min(ys)
    factor = (real_length_m * build.SCALE / geo_len) if real_length_m else 1.0
    log(f"GEO length {geo_len:.2f} -> {geo_len * factor:.2f} game units (x{factor:.3f})")
    if abs(factor - 1) > 1e-3:
        # scale the whole hierarchy and apply it so bones, locators and meshes all carry real dimensions
        rig.scale = (factor,) * 3
        bpy.context.view_layer.update()
        build.select_only([rig] + meshes + [o for o in bpy.data.objects if o.type == "EMPTY"], active=rig)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        for o in bpy.data.objects:
            if o.type == "EMPTY":
                o.scale = (1, 1, 1)

    # ---- shading ------------------------------------------------------------------------------------------------
    for o in render_meshes:
        weld_and_shade(o)
    tris = sum(len(p.vertices) - 2 for o in render_meshes for p in o.data.polygons)
    log("tris", tris)

    # ---- textures -----------------------------------------------------------------------------------------------
    body_mats, track_mats, sizes = [], [], {}
    for o in render_meshes:
        for s in o.material_slots:
            m = s.material
            if m is None or m in body_mats or m in track_mats:
                continue
            (track_mats if m.get("shader") == "PdxMeshAdvancedAnim" else body_mats).append(m)
    for m in body_mats + track_mats:
        tex = material_textures(m)
        w, h = dds_size(find_texture(tex["diffuse"]))
        sizes[m] = (min(max_res, w * up), min(max_res, h * up)) if m in body_mats else (w, h)

    ao_images = bake_ao(render_meshes[0], {m: sizes[m] for m in body_mats})
    log("baked AO for", [m.name for m in body_mats])

    renames = {}
    for i, m in enumerate(body_mats + track_mats):
        tex = material_textures(m)
        is_track = m in track_mats
        part = "track" if is_track else ("body" if i == 0 else f"part{i}")
        prefix = f"{name}_{part}"
        w, h = sizes[m]
        # diffuse: cubic upscale, unsharp mask, AO multiplied in (body only)
        png = texconv(find_texture(tex["diffuse"]), work_dir, "R8G8B8A8_UNORM", (w, h), "png")
        d = load_png(png)
        rgb = d[..., :3]
        if not is_track:
            soft = blur(rgb, 1)
            rgb = np.clip(rgb + (rgb - soft) * 0.6, 0, 1)
            ao = build.pixels(ao_images[m])[..., :1]
            rgb = rgb * (0.55 + 0.45 * ao)
        d[..., :3] = rgb
        d[..., 3] = 1.0
        out = build.save_png("d", d, os.path.join(work_dir, prefix + "_diffuse.png"))
        build.to_dds_rect(out, out_dir, "BC1_UNORM")
        # normal and spec: upscale and regenerate the mip chain; renormalise the normal's X/Y after filtering
        for key, suffix in (("normal", "normal"), ("spec", "spec")):
            src = find_texture(tex[key])
            png = texconv(src, work_dir, "R8G8B8A8_UNORM", (w, h), "png")
            a = load_png(png)
            if key == "normal":
                x, y = a[..., 1] * 2 - 1, a[..., 3] * 2 - 1
                ln = np.maximum(1.0, np.sqrt(x * x + y * y))
                a[..., 0] = a[..., 1] = (x / ln) * 0.5 + 0.5
                a[..., 3] = (y / ln) * 0.5 + 0.5
                a[..., 2] = np.where(a[..., 2] < 0.5, 0.0, a[..., 2])
            out = build.save_png(key, a, os.path.join(work_dir, f"{prefix}_{suffix}.png"))
            build.to_dds_rect(out, out_dir, "BC3_UNORM")
        renames[m] = prefix

    for m, prefix in renames.items():
        shader = m.get("shader")
        new = build.pdx_material(prefix, shader, prefix)
        for o in render_meshes:
            for s in o.material_slots:
                if s.material == m:
                    s.material = new
    log("textures written", list(renames.values()))

    # ---- export mesh -------------------------------------------------------------------------------------------
    mesh_path = os.path.join(out_dir, name + ".mesh")
    build.select_only(meshes)
    bpy.ops.io_pdx_mesh.export_mesh(filepath=mesh_path, chk_mesh=True, chk_skel=True, chk_locs=True,
                                    chk_selected=False)
    log("mesh", mesh_path)

    # ---- animations ------------------------------------------------------------------------------------------
    wheel_info = wheel_radii(rig, render_meshes)
    track_speed = None
    anims = []
    if wheel_info:
        anims, track_speed = build.animations(None, rig, wheel_info, out_dir, name)
    v_density = track_uv_density(render_meshes, track_mats)
    anim_speed = round(track_speed * v_density / 2.0, 3) if (track_speed and v_density) else None
    log("track v/unit", v_density, "texture_anim_speed", anim_speed)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(work_dir, name + ".blend"))
    return {"mesh": mesh_path, "anims": anims, "texture_anim_speed": anim_speed, "tris": tris,
            "length": geo_len * factor}


def wheel_radii(rig, meshes):
    """{bone: (radius, None)} from the vertices each wheel bone carries, measured in the axle's YZ plane."""
    info = {}
    for b in rig.data.bones:
        if not b.name.startswith("wheel_") or b.name == "wheel_suspention":
            continue
        head = rig.matrix_world @ b.head_local
        r = 0.0
        for o in meshes:
            vg = o.vertex_groups.get(b.name)
            if vg is None:
                continue
            for v in o.data.vertices:
                for g in v.groups:
                    if g.group == vg.index and g.weight > 0.5:
                        p = o.matrix_world @ v.co
                        r = max(r, math.hypot(p.y - head.y, p.z - head.z))
        if r > 0.05:
            info[b.name] = r
    if not info:
        return {}
    # road wheels are the most common radius: they spin whole turns per loop (their texture is directional);
    # sprocket, idler and rollers round to whole turns as well, so nothing pops at the loop point
    buckets = {}
    for bone, r in info.items():
        buckets.setdefault(round(r / 0.04), []).append(bone)
    road = set(max(buckets.values(), key=len))
    return {bone: (r, None if bone in road else 2 * math.pi) for bone, r in info.items()}


def track_uv_density(meshes, track_mats):
    """Median texture V per game unit along the track belt (for texture_anim_speed)."""
    vals = []
    for o in meshes:
        me = o.data
        uv = me.uv_layers[0].data
        idx = [i for i, s in enumerate(o.material_slots) if s.material and s.material.get("shader") == "PdxMeshAdvancedAnim"]
        for p in me.polygons:
            if p.material_index not in idx:
                continue
            ls = list(p.loop_indices)
            for a, b in zip(ls, ls[1:] + ls[:1]):
                pa, pb = me.vertices[me.loops[a].vertex_index].co, me.vertices[me.loops[b].vertex_index].co
                d = (pa - pb).length
                dv = abs(uv[a].uv[1] - uv[b].uv[1])
                if d > 0.05 and dv > 1e-4 and abs(pa.x - pb.x) < 0.02:
                    vals.append(dv / d)
    return float(np.median(vals)) if vals else None
