"""Full pipeline for one vehicle: geometry -> UVs -> bakes -> DDS -> rig -> animations -> .mesh/.anim.

Run through scripts/build_tank.py.
"""

import math
import os
import re
import subprocess

import addon_utils
import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

from . import geo, materials, vehicle

SCALE = 1.28  # game units per metre: matches vanilla GER medium tank proportions at entity scale 0.5
FPS = 15
BAKE_RES = 2048
OUT_RES = 1024
TEXCONV = os.path.join(os.path.dirname(__file__), "..", "..", "bin", "texconv.exe")

# parts that are identical copies share one UV island (running gear and small fittings only;
# big panels keep unique islands so the camo doesn't repeat)
INSTANCED = ("roadwheel_disc", "roadwheel_tyre", "roller", "sprocket", "idler", "sprocket_hub", "idler_hub", "bogie",
             "spare_link", "tow_front", "tow_rear", "skirt_bracket", "skirt_mount")


def log(*a):
    print("[tankgen]", *a, flush=True)


# ---- scene helpers ---------------------------------------------------------------------------------------------
def select_only(objs, active=None):
    bpy.ops.object.mode_set(mode="OBJECT") if bpy.context.object and bpy.context.object.mode != "OBJECT" else None
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active or (objs[0] if objs else None)


def group_key(name):
    return re.sub(r"(_-?\d+|_[lr])+$", "", name)


def apply_modifiers(obj):
    select_only([obj])
    for m in list(obj.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


# ---- UVs -------------------------------------------------------------------------------------------------------
CULL_KINDS = {"paint", "skirt", "paint_cast", "steel", "exhaust", "track_steel", "wood"}


def cull_hidden(v, below_z=-0.5):
    """Drop downward-facing faces of plate-like parts: the HOI4 camera never looks up at them, and every one
    removed frees texture space for surfaces that are seen. Round parts (wheels, gun) keep their undersides."""
    removed = 0
    for p in v.parts:
        if p.kind not in CULL_KINDS or p.name.startswith(("gun", "muffler", "tailpipe", "aux_muffler")):
            continue
        bm = bmesh.new()
        bm.from_mesh(p.obj.data)
        bm.normal_update()
        dead = [f for f in bm.faces if f.normal.z < below_z]
        if dead and len(dead) < len(bm.faces):
            bmesh.ops.delete(bm, geom=dead, context="FACES")
            removed += len(dead)
            bm.to_mesh(p.obj.data)
        bm.free()
    log("culled", removed, "hidden downward faces")


def unwrap(v):
    body = [p for p in v.parts if p.kind != "track"]
    masters, copies = {}, []
    for p in body:
        key = group_key(p.name)
        if key in INSTANCED:
            m = masters.get((key, len(p.obj.data.loops)))
            if m is None:
                masters[(key, len(p.obj.data.loops))] = p
            else:
                copies.append((p, m))
                continue
    copy_set = {id(c[0]) for c in copies}
    unique = [p.obj for p in body if id(p) not in copy_set]
    for o in unique:
        if not o.data.uv_layers:
            o.data.uv_layers.new(name="UVMap")
    select_only(unique)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.002, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.pack_islands(rotate=True, margin=0.0035, merge_overlap=True, shape_method="CONCAVE")
    bpy.ops.object.mode_set(mode="OBJECT")
    for p, m in copies:
        if not p.obj.data.uv_layers:
            p.obj.data.uv_layers.new(name="UVMap")
        src, dst = m.obj.data.uv_layers[0].data, p.obj.data.uv_layers[0].data
        for i in range(len(dst)):
            dst[i].uv = src[i].uv
    log("unwrapped", len(unique), "unique parts,", len(copies), "instances")


# ---- joining, skinning -----------------------------------------------------------------------------------------
def join_parts(v, kind_filter, name, bake_mats):
    objs = []
    for p in v.parts:
        if not kind_filter(p.kind):
            continue
        o = p.obj
        vg = o.vertex_groups.get(p.bone) or o.vertex_groups.new(name=p.bone)
        vg.add(range(len(o.data.vertices)), 1.0, "REPLACE")
        o.data.materials.clear()
        o.data.materials.append(bake_mats[p.kind])
        # triangulate first: tangents (needed by the normal map) can't be computed on n-gons, and the bake
        # must see the same triangles the exporter writes
        tri = o.modifiers.new("tri", "TRIANGULATE")
        tri.quad_method, tri.ngon_method, tri.keep_custom_normals = "BEAUTY", "BEAUTY", True
        o.modifiers.move(len(o.modifiers) - 1, 0)
        apply_modifiers(o)
        objs.append(o)
    select_only(objs)
    bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    joined.name = name
    joined.data.name = name
    return joined


# ---- baking ----------------------------------------------------------------------------------------------------
def setup_cycles():
    scn = bpy.context.scene
    scn.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for backend in ("OPTIX", "CUDA", "HIP", "ONEAPI"):
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
            gpus = [d for d in prefs.devices if d.type == backend]
            if gpus:
                for d in prefs.devices:
                    d.use = d.type == backend
                scn.cycles.device = "GPU"
                log("baking on", backend, [d.name for d in gpus])
                break
        except TypeError:
            continue
    else:
        scn.cycles.device = "CPU"
        log("baking on CPU")
    scn.render.bake.margin = 8
    scn.render.bake.use_clear = True


def new_image(name, res, non_color=True, alpha=False):
    img = bpy.data.images.new(name, res, res, alpha=alpha, float_buffer=False)
    img.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
    return img


def set_bake_target(obj, image):
    for mat in obj.data.materials:
        nt = mat.node_tree
        node = nt.nodes.get("bake_target") or nt.nodes.new("ShaderNodeTexImage")
        node.name = "bake_target"
        node.image = image
        node.location = (-400, -400)
        for n in nt.nodes:
            n.select = False
        node.select = True
        nt.nodes.active = node


def bake(obj, image, bake_type, samples, high=None):
    """Bake into `obj`'s UVs; with `high`, rays from obj pick up the detailed copy (selected-to-active)."""
    scn = bpy.context.scene
    scn.cycles.samples = samples
    set_bake_target(obj, image)
    kw = {"type": bake_type}
    if bake_type == "NORMAL":
        kw.update(normal_space="TANGENT")
    if high is not None:
        select_only([high, obj], active=obj)
        kw.update(use_selected_to_active=True, cage_extrusion=0.065 * SCALE, max_ray_distance=0.13 * SCALE)
    else:
        select_only([obj])
    bpy.ops.object.bake(**kw)
    log("baked", bake_type, image.name)


def make_high(v, bake_mats):
    """Detailed bake source: a copy of every body part (same UVs) plus the detail-only geometry, joined."""
    objs = []
    for p in v.parts:
        if p.kind == "track":
            continue
        dup = p.obj.copy()
        dup.data = p.obj.data.copy()
        v.collection.objects.link(dup)
        dup.data.materials.clear()
        dup.data.materials.append(bake_mats[p.kind])
        objs.append(dup)
    for obj, kind in v.details:
        obj.data.materials.clear()
        obj.data.materials.append(bake_mats.setdefault(kind, bpy.data.materials.new("bake_" + kind)))
        objs.append(obj)
    for o in objs:
        apply_modifiers(o)
    select_only(objs)
    bpy.ops.object.join()
    high = bpy.context.view_layer.objects.active
    high.name = v.name + "_high"
    log("high-poly bake source:", len(high.data.polygons), "faces,", len(v.details), "detail groups")
    return high


def hide_from_rays(obj, hidden=True):
    for attr in ("visible_camera", "visible_diffuse", "visible_glossy", "visible_transmission",
                 "visible_volume_scatter", "visible_shadow"):
        setattr(obj, attr, not hidden)


def build_bake_materials(mats, ctx, mode):
    for kind, m in mats.items():
        materials.build(m, kind, mode, ctx)


def pixels(img):
    a = np.empty(img.size[0] * img.size[1] * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(img.size[1], img.size[0], 4)


def save_png(name, arr, path, srgb=False):
    h, w = arr.shape[:2]
    img = bpy.data.images.new(name, w, h, alpha=True)
    img.colorspace_settings.name = "sRGB" if srgb else "Non-Color"
    img.pixels.foreach_set(np.ascontiguousarray(arr, dtype=np.float32).ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    return path


def to_dds(png, out_dir, fmt, res):
    cmd = [os.path.abspath(TEXCONV), "-nologo", "-y", "-m", "0", "--ignore-srgb", "-f", fmt, "-w", str(res),
           "-h", str(res), "-o", out_dir, png]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stdout + r.stderr)
    return os.path.join(out_dir, os.path.splitext(os.path.basename(png))[0] + ".dds")


def bake_body(mats, body, high, work, out_dir, tex_name, ctx_extra):
    """mats: {kind: material} used by both the joined body and the high-poly source."""
    setup_cycles()
    ctx = {"scale": SCALE, **ctx_extra}
    bpy.context.scene.world = bpy.context.scene.world or bpy.data.worlds.new("bake")
    # the low body sits exactly on the high copy: keep it out of AO/edge rays or it would shadow itself
    hide_from_rays(body)

    nrm = new_image(tex_name + "_nrm_raw", BAKE_RES)
    build_bake_materials(mats, ctx, "normal")
    bake(body, nrm, "NORMAL", 8, high)

    color = new_image(tex_name + "_col_raw", BAKE_RES, non_color=False)
    build_bake_materials(mats, ctx, "color")
    bake(body, color, "EMIT", 96, high)

    spec = new_image(tex_name + "_spec_raw", BAKE_RES)
    build_bake_materials(mats, ctx, "spec")
    bake(body, spec, "EMIT", 16, high)
    gloss = new_image(tex_name + "_gloss_raw", BAKE_RES)
    build_bake_materials(mats, ctx, "gloss")
    bake(body, gloss, "EMIT", 16, high)
    hide_from_rays(body, False)

    # pack into the PdxMeshAdvanced layouts
    c = pixels(color).copy()
    c[..., 3] = 1.0
    n_raw = pixels(nrm)
    n = np.zeros_like(n_raw)
    n[..., 0] = n_raw[..., 0]
    n[..., 1] = n_raw[..., 0]
    n[..., 2] = 0.0
    n[..., 3] = n_raw[..., 1]
    s = pixels(spec).copy()
    s[..., 0] = 0.0
    s[..., 3] = pixels(gloss)[..., 0]

    out = []
    out.append(to_dds(save_png("d", c, os.path.join(work, tex_name + "_diffuse.png"), srgb=True), out_dir, "BC1_UNORM", OUT_RES))
    out.append(to_dds(save_png("n", n, os.path.join(work, tex_name + "_normal.png")), out_dir, "BC3_UNORM", OUT_RES))
    out.append(to_dds(save_png("s", s, os.path.join(work, tex_name + "_spec.png")), out_dir, "BC3_UNORM", OUT_RES))
    log("textures", out)
    return out


def track_textures(work, out_dir, tex_name, width_m, tile_m, pitch_m):
    """Procedural Kgs-style track tile: plates, grousers, link gaps. u 0..0.75 = outer face, 0.75..1 = inner/sides."""
    W, H = 256, 512
    u = (np.arange(W) + 0.5) / W
    vv = (np.arange(H) + 0.5) / H
    U, V = np.meshgrid(u, vv)
    x = U / 0.75 * width_m  # across the track (outer strip)
    y = V * tile_m  # along the track
    ph = (y % pitch_m) / pitch_m
    gap = np.clip(np.minimum(ph, 1 - ph) * pitch_m / 0.006, 0, 1)  # dark gap between links
    grouser = np.exp(-((ph - 0.5) * pitch_m / 0.014) ** 2)  # raised cleat across each link
    edge = np.clip(np.minimum(x, width_m - x) / 0.02, 0, 1)
    hole = np.exp(-(((x - width_m / 2) / 0.03) ** 2 + ((ph - 0.2) * pitch_m / 0.02) ** 2))
    rng = np.random.default_rng(7)
    grain = rng.normal(0, 0.03, (H, W))
    height = (0.35 + 0.45 * grouser) * gap * edge - 0.3 * hole + grain * 0.3
    inner = U > 0.75
    height[inner] = (0.5 + 0.3 * np.exp(-((ph[inner] - 0.5) * pitch_m / 0.03) ** 2)) * gap[inner] + grain[inner] * 0.2
    # normals from the height field, OpenGL: +V = image up = increasing row index (Blender rows are bottom-up)
    k = 6.0
    dhx = np.gradient(height, axis=1) * k
    dhy = np.gradient(height, axis=0) * k
    nx, ny, nz = -dhx, -dhy, np.ones_like(height)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny = nx / ln, ny / ln
    nrm = np.zeros((H, W, 4), np.float32)
    nrm[..., 0] = nrm[..., 1] = nx * 0.5 + 0.5
    nrm[..., 3] = ny * 0.5 + 0.5
    # colour: dark steel, polished cleat tops, rust and dirt in recesses (sRGB values)
    polish = np.clip(grouser * gap * edge * 1.4 - 0.3, 0, 1)
    rust = np.clip(1 - height * 1.6 + rng.normal(0, 0.15, (H, W)), 0, 1)
    col = np.zeros((H, W, 4), np.float32)
    base = np.array([0.24, 0.21, 0.19])
    rustc = np.array([0.36, 0.20, 0.11])
    shiny = np.array([0.55, 0.53, 0.50])
    for i in range(3):
        col[..., i] = base[i] * (0.55 + 0.6 * height) * (1 - 0.5 * rust) + rustc[i] * 0.5 * rust
        col[..., i] = col[..., i] * (1 - polish) + shiny[i] * polish
    col[..., 3] = 1
    spec = np.zeros((H, W, 4), np.float32)
    spec[..., 1] = 0.35 + 0.35 * polish
    spec[..., 2] = 0.45 + 0.45 * polish - 0.3 * rust
    spec[..., 3] = 0.25 + 0.45 * polish
    out = []
    for suffix, arr, fmt, srgb in (("diffuse", col, "BC1_UNORM", True), ("normal", nrm, "BC3_UNORM", False),
                                   ("spec", spec, "BC3_UNORM", False)):
        png = save_png(suffix, np.clip(arr, 0, 1), os.path.join(work, f"{tex_name}_{suffix}.png"), srgb=srgb)
        out.append(to_dds_rect(png, out_dir, fmt))
    log("track textures", out)
    return out


def to_dds_rect(png, out_dir, fmt):
    cmd = [os.path.abspath(TEXCONV), "-nologo", "-y", "-m", "0", "--ignore-srgb", "-f", fmt, "-o", out_dir, png]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stdout + r.stderr)
    return os.path.join(out_dir, os.path.splitext(os.path.basename(png))[0] + ".dds")


# ---- PDX materials, rig, animation, export --------------------------------------------------------------------
def pdx_material(name, shader, tex_prefix):
    m = bpy.data.materials.new(name)
    m["shader"] = shader
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    for socket, suffix in (("Base Color", "diffuse"), ("Roughness", "spec")):
        img = bpy.data.images.new(f"{tex_prefix}_{suffix}.dds", 4, 4)
        img.filepath = f"//{tex_prefix}_{suffix}.dds"
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = img
        nt.links.new(node.outputs["Color"], bsdf.inputs[socket])
    img = bpy.data.images.new(f"{tex_prefix}_normal.dds", 4, 4)
    img.filepath = f"//{tex_prefix}_normal.dds"
    node = nt.nodes.new("ShaderNodeTexImage")
    node.image = img
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(node.outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def make_rig(v):
    arm = bpy.data.armatures.new(v.name + "_rig")
    rig = bpy.data.objects.new(v.name + "_rig", arm)
    bpy.context.scene.collection.objects.link(rig)
    select_only([rig])
    bpy.ops.object.mode_set(mode="EDIT")
    order = []

    def visit(name):
        if name in order:
            return
        parent = v.bones[name][1]
        if parent:
            visit(parent)
        order.append(name)

    for name in v.bones:
        visit(name)
    for name in order:
        head, parent = v.bones[name]
        eb = arm.edit_bones.new(name)
        eb.head = head
        eb.tail = head + Vector((0, 0.15, 0))
        eb.roll = 0.0
        if parent:
            eb.parent = arm.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return rig


def skin(obj, rig):
    obj.parent = rig
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = rig


def add_locators(v, rig):
    bpy.context.view_layer.update()
    for name, (xyz, bone) in v.locators.items():
        e = bpy.data.objects.new(name, None)
        bpy.context.scene.collection.objects.link(e)
        e.parent = rig
        e.parent_type = "BONE"
        e.parent_bone = bone
        bpy.context.view_layer.update()
        e.matrix_world = Matrix.Translation(xyz)


def keyframes(rig, frames, pose_fn):
    rig.animation_data_create()
    rig.animation_data.action = bpy.data.actions.new("anim")
    scn = bpy.context.scene
    for f in range(1, frames + 1):
        t = (f - 1) / frames  # 0..1, loop end excluded so frame N+1 == frame 1
        for pb in rig.pose.bones:
            pb.location = (0, 0, 0)
            pb.rotation_quaternion = (1, 0, 0, 0)
        pose_fn(rig.pose.bones, t, f)
        for pb in rig.pose.bones:
            pb.keyframe_insert("location", frame=f)
            pb.keyframe_insert("rotation_quaternion", frame=f)
            pb.keyframe_insert("scale", frame=f)
    scn.frame_start, scn.frame_end = 1, frames


def animations(v, rig, wheel_info, out_dir, prefix):
    """wheel_info: {bone: (radius_game, symmetry_step_rad or None)}"""
    scn = bpy.context.scene
    scn.render.fps = FPS
    scn.render.fps_base = 1.0
    road_r = min(r for r, step in wheel_info.values() if step is None and r > 0.2 * SCALE) if wheel_info else 0.3
    move_frames = 30
    travel = 2 * math.pi * road_r  # road wheels make exactly one turn per loop

    def wheel_angle(bone, t):
        r, step = wheel_info[bone]
        total = travel / r
        if step:
            total = round(total / step) * step
        elif abs(r - road_r) > 1e-4:
            total = max(1, round(total / (2 * math.pi))) * 2 * math.pi
        return total * t

    # pose values are in each bone's local space; imported rigs don't have world-aligned bones, so convert
    def rot(pb, axis_world, angle):
        axis = (pb.bone.matrix_local.to_3x3().inverted() @ Vector(axis_world)).normalized()
        pb.rotation_quaternion = Quaternion(axis, angle)

    def loc(pb, vec_world):
        pb.location = pb.bone.matrix_local.to_3x3().inverted() @ Vector(vec_world)

    def move(pbs, t, f):
        for b in wheel_info:
            rot(pbs[b], (1, 0, 0), wheel_angle(b, t))
        rot(pbs["chassie"], (1, 0, 0), math.radians(0.35) * math.sin(2 * math.pi * 2 * t))
        loc(pbs["chassie"], (0, 0, 0.012 * math.sin(2 * math.pi * 3 * t + 0.7)))

    def idle(pbs, t, f):
        if "turret" in pbs:
            rot(pbs["turret"], (0, 0, 1), math.radians(4) * math.sin(2 * math.pi * t))
        loc(pbs["chassie"], (0, 0, 0.004 * math.sin(2 * math.pi * 4 * t)))

    def attack(pbs, t, f):
        k = f - 1
        recoil = [0.0, 0.32, 0.30, 0.24, 0.17, 0.11, 0.07, 0.04, 0.02, 0.01] + [0.0] * 20
        if "barrel_base" in pbs:
            loc(pbs["barrel_base"], (0, recoil[k] * SCALE * 0.9, 0))
        rock = [0.0, 1.4, 1.6, 1.1, 0.5, -0.2, -0.4, -0.25, -0.1, 0.0] + [0.0] * 20
        rot(pbs["chassie"], (1, 0, 0), math.radians(-rock[k]))

    files = []
    select_only([rig])
    for name, frames, fn in (("idle", 60, idle), ("moving", move_frames, move), ("attack", 20, attack)):
        keyframes(rig, frames, fn)
        path = os.path.join(out_dir, f"{prefix}_{name}.anim")
        select_only([rig])
        bpy.ops.io_pdx_mesh.export_anim(filepath=path, int_start=1, int_end=frames)
        files.append(path)
    rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
    log("animations", files, "track speed (game units/s):", round(travel / (move_frames / FPS), 3))
    return files, travel / (move_frames / FPS)


def run(spec, out_dir, work_dir, skip_bake=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable("io_pdx_mesh")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(work_dir, exist_ok=True)

    v = vehicle.Vehicle(spec.NAME)
    spec.build(v)
    v.shade()
    v.scale_all(SCALE)
    log("parts", len(v.parts), "tris", v.triangle_count())

    # wheel radii (game units) and rotational symmetry for the move animation
    wheel_info = spec.wheel_info(SCALE)

    cull_hidden(v)
    unwrap(v)
    bake_mats = {k: bpy.data.materials.new("bake_" + k) for k in {p.kind for p in v.parts}}
    for k, m in bake_mats.items():
        m.use_nodes = True
    high = None if skip_bake else make_high(v, bake_mats)
    tracks = join_parts(v, lambda k: k == "track", spec.NAME + "_tracks", bake_mats)
    body = join_parts(v, lambda k: k != "track", spec.NAME + "_body", bake_mats)
    for m in bake_mats.values():
        m.use_nodes = True
    body_mats = {k: m for k, m in bake_mats.items() if k != "track"}

    tex = spec.NAME
    if not skip_bake:
        crosses = [(sx, y * SCALE, z * SCALE) for sx, y, z in getattr(spec, "CROSSES", [])]
        bake_body(body_mats, body, high, work_dir, out_dir, tex,
                  {"crosses": crosses, "cross_size": getattr(spec, "CROSS_SIZE", 0.5) * SCALE,
                   "camo": getattr(spec, "CAMO", "dunkelgelb_1943"), "zimmerit": getattr(spec, "ZIMMERIT", True),
                   "cross_kinds": getattr(spec, "CROSS_KINDS", ("skirt",))})
        track_textures(work_dir, out_dir, tex + "_track", spec.TRACK_W, 0.48, spec.TRACK_PITCH)
        bpy.data.objects.remove(high)

    body.data.materials.clear()
    body.data.materials.append(pdx_material(tex, "PdxMeshAdvanced", tex))
    tracks.data.materials.clear()
    tracks.data.materials.append(pdx_material(tex + "_track", "PdxMeshAdvancedAnim", tex + "_track"))

    rig = make_rig(v)
    skin(body, rig)
    skin(tracks, rig)
    add_locators(v, rig)
    col = collision_box_from(body)

    mesh_path = os.path.join(out_dir, tex + ".mesh")
    select_only([body, tracks, col])
    bpy.ops.io_pdx_mesh.export_mesh(filepath=mesh_path, chk_mesh=True, chk_skel=True, chk_locs=True,
                                    chk_selected=False)
    log("mesh", mesh_path)
    anims, speed = animations(v, rig, wheel_info, out_dir, tex)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(work_dir, tex + ".blend"))
    return {"mesh": mesh_path, "anims": anims, "track_speed": speed}


def collision_box_from(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), 0.0))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    c, size = (lo + hi) / 2, hi - lo
    o = geo.new_object("collision", geo.box(c.x, c.y, c.z, size.x, size.y, size.z))
    m = bpy.data.materials.new("collision")
    m["shader"] = "Collision"
    o.data.materials.append(m)
    return o
