# Run: blender -b --python preview_geo.py -- <spec module> <out_dir>
# Builds a vehicle from a spec and renders workbench previews (front 3/4, side, top-down HOI4 angle, rear 3/4).
import importlib
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector

from tankgen import vehicle

spec_name, out_dir = sys.argv[sys.argv.index("--") + 1:]
os.makedirs(out_dir, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
spec = importlib.import_module("tankgen.specs." + spec_name)
v = vehicle.Vehicle(spec.NAME)
spec.build(v)
v.preview_materials()
v.shade()
print("TRIS", v.triangle_count(), "PARTS", len(v.parts))

scn = bpy.context.scene
scn.render.engine = "BLENDER_WORKBENCH"
scn.display.shading.light = "STUDIO"
scn.display.shading.color_type = "MATERIAL"
scn.display.shading.show_cavity = True
scn.display.shading.show_shadows = True
scn.render.resolution_x, scn.render.resolution_y = 1400, 900
scn.render.film_transparent = False
world = bpy.data.worlds.new("w"); scn.world = world
world.color = (0.55, 0.58, 0.6)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scn.collection.objects.link(cam); scn.camera = cam
cam.data.lens = 70

views = {"front34": (-7.5, -9.5, 4.5), "side": (-13.0, 0.0, 1.6), "hoi4": (-6.0, -6.0, 11.0), "rear34": (7.5, 9.0, 4.0)}
target = Vector((0, -0.3, 1.0))
for name, pos in views.items():
    cam.location = pos
    cam.rotation_euler = (target - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = os.path.join(out_dir, name + ".png")
    bpy.ops.render.render(write_still=True)
print("RENDERED", out_dir)
