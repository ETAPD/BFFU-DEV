# Run: blender -b --python compare_shapes.py -- <a.mesh> <b.mesh> <out_dir>
# Untextured side-by-side of two PDX meshes (normalised to the same length) from front, side, top and 3/4,
# with edges drawn, to compare shapes rather than paint.
import math
import os
import sys

import addon_utils
import bpy
from mathutils import Vector

a_path, b_path, out_dir = sys.argv[sys.argv.index("--") + 1:]
os.makedirs(out_dir, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable("io_pdx_mesh")


def load(path, offset_x):
    before = set(bpy.data.objects)
    bpy.ops.io_pdx_mesh.import_mesh(filepath=path, chk_mesh=True, chk_skel=False, chk_locs=False)
    objs = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    for o in objs:
        if "collision" in o.name.lower() or o.name.startswith("pCube") or any(
                s.material and s.material.get("shader") == "Collision" for s in o.material_slots):
            bpy.data.objects.remove(o)
    objs = [o for o in bpy.data.objects if o.type == "MESH" and o not in before]
    bpy.context.view_layer.update()
    ys = [(o.matrix_world @ v.co).y for o in objs for v in o.data.vertices]
    k = 8.0 / (max(ys) - min(ys))
    for o in objs:
        o.scale = (k, k, k)
        o.location.x += offset_x
        o.data.materials.clear()
    return objs


load(a_path, -2.6)
load(b_path, 2.6)
scn = bpy.context.scene
scn.render.engine = "BLENDER_WORKBENCH"
sh = scn.display.shading
sh.light, sh.color_type, sh.single_color = "STUDIO", "SINGLE", (0.75, 0.72, 0.65)
sh.show_cavity, sh.cavity_type, sh.show_shadows = True, "BOTH", False
sh.show_object_outline = True
scn.render.resolution_x, scn.render.resolution_y = 1600, 800
scn.world = bpy.data.worlds.new("w")
scn.world.color = (0.32, 0.34, 0.36)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scn.collection.objects.link(cam)
scn.camera = cam
cam.data.type = "ORTHO"
views = {"front": ((0, -30, 1.6), 10.5), "side": ((-30, 0, 1.6), 11.0), "top": ((0, 0, 30), 11.0),
         "front34": ((-14, -18, 11), 12.0)}
for name, (pos, scale) in views.items():
    cam.location = pos
    target = Vector((0, 0, 1.3))
    if name == "side":
        # side by side doesn't work from the side: stack the two models instead
        continue
    cam.data.ortho_scale = scale
    up = "Y" if name != "top" else "Y"
    cam.rotation_euler = (target - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = os.path.join(out_dir, name + ".png")
    bpy.ops.render.render(write_still=True)

# side view: move model B up above model A
objs = [o for o in bpy.data.objects if o.type == "MESH"]
for o in objs:
    if o.location.x > 0:
        o.location = (0, 0, 3.6)
    else:
        o.location = (0, 0, 0)
cam.location = (-30, 0, 3.4)
cam.data.ortho_scale = 10.5
scn.render.resolution_x, scn.render.resolution_y = 1400, 1100
cam.rotation_euler = (Vector((0, 0, 3.4)) - cam.location).to_track_quat("-Z", "Y").to_euler()
scn.render.filepath = os.path.join(out_dir, "side.png")
bpy.ops.render.render(write_still=True)
print("RENDERED", out_dir)
