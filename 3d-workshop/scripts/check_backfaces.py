# Run: blender -b --python check_backfaces.py -- <out_dir> <file.mesh> [<file.mesh> ...]
# HOI4 culls back faces, so any inside-out face, open surface or deleted face the designer camera can see shows as a
# hole in game, while Blender's two-sided renders hide it. This renders each exported mesh from six designer-style
# angles with back faces in pure red and prints the red pixel count per view; <name>_<view>.png show where. A clean
# model is near 0 in every view (a few pixels at gun bores and slit edges are fine).
import math
import os
import sys

import addon_utils
import bpy
import numpy as np
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
out_dir, meshes = args[0], args[1:]
os.makedirs(out_dir, exist_ok=True)
addon_utils.enable("io_pdx_mesh")
views = {"fl": (-35, 25), "fr": (35, 25), "rl": (-145, 25), "rr": (145, 25), "top": (-20, 70), "low": (-60, 6)}
for mp in meshes:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable("io_pdx_mesh")
    bpy.ops.io_pdx_mesh.import_mesh(filepath=mp, chk_mesh=True, chk_skel=False, chk_locs=False)
    obs = []
    for o in list(bpy.data.objects):
        if o.type != "MESH": continue
        if any(ms.material and ms.material.get("shader") == "Collision" for ms in o.material_slots):
            o.hide_render = True; continue
        obs.append(o)
    m = bpy.data.materials.new("chk"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    outn = nt.nodes.new("ShaderNodeOutputMaterial"); geo = nt.nodes.new("ShaderNodeNewGeometry")
    dot = nt.nodes.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; dot.inputs[1].default_value = (0.3, -0.5, 0.8)
    nt.links.new(geo.outputs["Normal"], dot.inputs[0])
    ramp = nt.nodes.new("ShaderNodeMapRange"); ramp.inputs[1].default_value = -1; ramp.inputs[2].default_value = 1
    ramp.inputs[3].default_value = 0.25; ramp.inputs[4].default_value = 0.85
    nt.links.new(dot.outputs["Value"], ramp.inputs[0])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    nt.links.new(geo.outputs["Backfacing"], mix.inputs["Factor"])
    comb = nt.nodes.new("ShaderNodeCombineColor")
    for ch in ("Red", "Green", "Blue"): nt.links.new(ramp.outputs[0], comb.inputs[ch])
    nt.links.new(comb.outputs[0], mix.inputs["A"]); mix.inputs["B"].default_value = (1, 0, 0, 1)
    em = nt.nodes.new("ShaderNodeEmission"); nt.links.new(mix.outputs["Result"], em.inputs[0])
    nt.links.new(em.outputs[0], outn.inputs[0])
    for o in obs:
        o.data.materials.clear(); o.data.materials.append(m)
    pts = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    size = (hi - lo).length; tgt = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z + (hi.z - lo.z) * 0.6))
    scn = bpy.context.scene
    scn.render.engine = "BLENDER_EEVEE"; scn.view_settings.view_transform = "Standard"
    scn.render.resolution_x, scn.render.resolution_y = 900, 600
    w = bpy.data.worlds.new("w"); scn.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.1, 0.3, 0.1, 1)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scn.collection.objects.link(cam); scn.camera = cam
    name = os.path.splitext(os.path.basename(mp))[0]
    res = []
    for nm, (az, el) in views.items():
        a, e = math.radians(az), math.radians(el)
        cam.location = tgt + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * size * 0.9
        cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
        f = os.path.join(out_dir, f"{name}_{nm}.png"); scn.render.filepath = f
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(f); px = np.array(img.pixels[:]).reshape(-1, 4)
        red = int(((px[:, 0] > 0.8) & (px[:, 1] < 0.15) & (px[:, 2] < 0.15)).sum())
        res.append(f"{nm}={red}"); bpy.data.images.remove(img)
    print("RED", name, " ".join(res))
