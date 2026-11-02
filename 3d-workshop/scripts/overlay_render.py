# Run: blender -b --python overlay_render.py -- <spec> <out_dir> <ppm> <view>=<drawing.png>,<origin_x>,<origin_y> ...
# Builds the spec's geometry (no bake), renders exact orthographic views at the drawing's scale with the model's
# datum (bow tip / ground / centreline) on the drawing's datum pixel, and writes <view>_render.png for
# blueprint.py overlay. The render is a line drawing: black = silhouettes and boundaries between parts, grey = creases
# inside a part (from a flat per-part colour pass and a studio-lit pass, compared pixel by pixel).
# Optional: OVERLAY_HIDE=<regex> leaves matching parts out, e.g. OVERLAY_HIDE='^skirt_-?1_' for the hull Schürzen
# plates, which the drawing omits.
#   side  = seen from the vehicle's left (+X), bow on the left   origin: bow x, ground y
#   top   = seen from above, bow on the left, vehicle left at the bottom   origin: bow x, centreline y
#   front = seen from the front, vehicle left on the right       origin: centreline x, ground y
#   rear  = seen from behind, vehicle left on the left             origin: centreline x, ground y
import importlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from mathutils import Matrix, Vector

from tankgen import vehicle

args = sys.argv[sys.argv.index("--") + 1:]
spec_name, out_dir, ppm = args[0], args[1], float(args[2])
views = {}
for a in args[3:]:
    name, rest = a.split("=", 1)
    path, ox, oy = rest.rsplit(",", 2)
    views[name] = (path, float(ox), float(oy))
os.makedirs(out_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
spec = importlib.import_module("tankgen.specs." + spec_name)
v = vehicle.Vehicle(spec.NAME)
spec.build(v)
v.preview_materials()
v.shade()

hide = os.environ.get("OVERLAY_HIDE")
for p in v.parts:
    if hide and re.search(hide, p.name):
        p.obj.hide_render = True
objs = [p.obj for p in v.parts] + [obj for obj, _ in v.details]
for i, obj in enumerate(objs):  # a unique flat colour per object: part boundaries become colour changes
    obj.color = ((i * 7 % 16) / 15, (i // 16 % 16) / 15, 0.2 + 0.6 * (i // 256 % 2), 1)

scn = bpy.context.scene
scn.render.engine = "BLENDER_WORKBENCH"
scn.display.render_aa = "OFF"  # exact pixels: edges are found by comparing neighbours
sh = scn.display.shading
sh.show_object_outline = False
sh.show_cavity = False
sh.show_specular_highlight = False
scn.render.film_transparent = True
scn.view_settings.view_transform = "Standard"
tmp = os.path.join(out_dir, "_pass.png")


def render_pass(light, color_type):
    sh.light, sh.color_type, sh.single_color = light, color_type, (1.0, 1.0, 1.0)
    scn.render.filepath = tmp
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(tmp, check_existing=False)
    a = np.empty(img.size[0] * img.size[1] * 4, np.float32)
    img.pixels.foreach_get(a)
    bpy.data.images.remove(img)
    return a.reshape(scn.render.resolution_y, scn.render.resolution_x, 4)


def changes(a, tol):
    """Pixels whose value differs from the right or lower neighbour by more than tol (any channel)."""
    e = np.zeros(a.shape[:2], bool)
    dx = np.abs(np.diff(a, axis=1)).max(-1) > tol
    dy = np.abs(np.diff(a, axis=0)).max(-1) > tol
    e[:, :-1] |= dx
    e[:-1, :] |= dy
    return e


def edge_render(path):
    """Black: silhouettes and part boundaries. Grey: creases inside a part (faces meeting at an angle)."""
    ids = render_pass("FLAT", "OBJECT")
    shade = render_pass("STUDIO", "SINGLE")
    outline = changes(ids, 0.02)
    crease = changes(shade[..., :3], 0.07) & ~outline
    out = np.zeros(ids.shape, np.float32)
    out[crease] = (0.45, 0.45, 0.45, 1.0)
    out[outline] = (0.0, 0.0, 0.0, 1.0)
    img = bpy.data.images.new(os.path.basename(path), out.shape[1], out.shape[0], alpha=True)
    img.pixels.foreach_set(out.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()


cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scn.collection.objects.link(cam)
scn.camera = cam
cam.data.type = "ORTHO"

half_l = spec.HULL_L / 2
for name, (path, ox, oy) in views.items():
    img = bpy.data.images.load(path)
    w, h = img.size
    scn.render.resolution_x, scn.render.resolution_y = w, h
    cam.data.ortho_scale = max(w, h) / ppm
    cx, cy = (w / 2 - ox) / ppm, (oy - h / 2) / ppm  # image centre relative to the datum, metres (right, up)
    if name == "side":
        # right = +Y (rear), up = +Z; datum = bow (Y = -half_l), ground
        cam.location = (30.0, -half_l + cx, cy)
        cam.rotation_euler = (Vector((0, -half_l + cx, cy)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    elif name == "top":
        # right = +Y, up = -X (vehicle left at the bottom); datum = bow, centreline
        cam.location = (-cy, -half_l + cx, 30.0)
        # camera axes as columns: screen right = +Y, screen up = -X, looking down -Z
        cam.rotation_euler = Matrix(((0, -1, 0), (1, 0, 0), (0, 0, 1))).to_euler()
    elif name == "front":
        # right = +X, up = +Z; datum = centreline, ground
        cam.location = (cx, -30.0, cy)
        cam.rotation_euler = (Vector((cx, 0, cy)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    elif name == "rear":
        # right = -X (vehicle left on the left), up = +Z; datum = centreline, ground
        cam.location = (-cx, 30.0, cy)
        cam.rotation_euler = (Vector((-cx, 0, cy)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    edge_render(os.path.join(out_dir, f"{name}_render.png"))
os.remove(tmp)
print("RENDERED", list(views))
