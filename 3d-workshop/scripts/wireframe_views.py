# Run: blender -b --python wireframe_views.py -- <file.mesh> <out_dir> [prefix]
# Shaded + wireframe renders of a PDX mesh (hull/turret close-ups) to study how its shapes are built.
import os
import sys

import addon_utils
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
path, out_dir = args[:2]
prefix = args[2] if len(args) > 2 else "wf"
os.makedirs(out_dir, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable("io_pdx_mesh")
bpy.ops.io_pdx_mesh.import_mesh(filepath=path, chk_mesh=True, chk_skel=False, chk_locs=False)
objs = []
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    if "collision" in o.name.lower() or o.name.startswith("pCube"):
        bpy.data.objects.remove(o)
        continue
    o.data.materials.clear()
    objs.append(o)
bpy.context.view_layer.update()
ys = [(o.matrix_world @ v.co).y for o in objs for v in o.data.vertices]
k = 8.0 / (max(ys) - min(ys))
for o in list(objs):
    o.scale = (k, k, k)
    o.color = (0.80, 0.77, 0.70, 1)
    wire = o.copy()
    bpy.context.scene.collection.objects.link(wire)
    mod = wire.modifiers.new("wf", "WIREFRAME")
    mod.thickness = 0.006 / k
    mod.use_even_offset = False
    wire.color = (0.08, 0.08, 0.08, 1)
scn = bpy.context.scene
scn.render.engine = "BLENDER_WORKBENCH"
sh = scn.display.shading
sh.light, sh.color_type = "STUDIO", "OBJECT"
sh.show_cavity = True
scn.render.resolution_x, scn.render.resolution_y = 1400, 1000
scn.world = bpy.data.worlds.new("w")
scn.world.color = (0.3, 0.32, 0.34)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scn.collection.objects.link(cam)
scn.camera = cam
cam.data.lens = 60
for name, pos, tgt in (("hull34", (-6.5, -8.0, 4.6), (0, -1.2, 1.0)), ("turret34", (-4.2, -5.2, 4.8), (0, -0.4, 2.0)),
                        ("rear34", (6.0, 8.0, 4.4), (0, 1.5, 1.1)), ("side_low", (-9.0, -1.0, 1.4), (0, 0, 1.1))):
    cam.location = pos
    cam.rotation_euler = (Vector(tgt) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = os.path.join(out_dir, f"{prefix}_{name}.png")
    bpy.ops.render.render(write_still=True)
print("RENDERED", out_dir)
