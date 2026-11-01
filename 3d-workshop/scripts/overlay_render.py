# Run: blender -b --python overlay_render.py -- <spec> <out_dir> <ppm> <view>=<drawing.png>,<origin_x>,<origin_y> ...
# Builds the spec's geometry (no bake), renders exact orthographic views at the drawing's scale with the model's
# datum (bow tip / ground / centreline) on the drawing's datum pixel, and writes <view>_render.png for
# blueprint.py overlay.
#   side  = seen from the vehicle's left (+X), bow on the left   origin: bow x, ground y
#   top   = seen from above, bow on the left, vehicle left at the bottom   origin: bow x, centreline y
#   front = seen from the front, vehicle left on the right       origin: centreline x, ground y
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
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

scn = bpy.context.scene
scn.render.engine = "BLENDER_WORKBENCH"
sh = scn.display.shading
sh.light, sh.color_type, sh.single_color = "FLAT", "SINGLE", (1.0, 1.0, 1.0)  # white fill: only outlines survive
sh.show_object_outline = True
sh.object_outline_color = (0.0, 0.0, 0.0)
sh.show_cavity = False
scn.render.film_transparent = True
scn.view_settings.view_transform = "Standard"  # true white fill, so the overlay only picks up the outlines
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
    scn.render.filepath = os.path.join(out_dir, f"{name}_render.png")
    bpy.ops.render.render(write_still=True)
print("RENDERED", list(views))
