# Run: blender -b --python preview_final.py -- <file.mesh> <out_dir>
# Renders an exported PDX mesh with its DDS textures decoded the way HOI4's PdxMeshAdvanced shader reads them:
# diffuse RGB, normal X = G / Y = A (OpenGL), spec G = specular, B = metalness, A = glossiness.
import math
import os
import sys

import addon_utils
import bpy
from mathutils import Vector

mesh_path, out_dir = sys.argv[sys.argv.index("--") + 1:]
os.makedirs(out_dir, exist_ok=True)
tex_dir = os.path.dirname(mesh_path)
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable("io_pdx_mesh")
bpy.ops.io_pdx_mesh.import_mesh(filepath=mesh_path, chk_mesh=True, chk_skel=True, chk_locs=False)


def load(name):
    img = bpy.data.images.load(os.path.join(tex_dir, name), check_existing=True)
    return img


def hoi4_material(mat):
    """Rebuild the material from the PDX texture names stored on the imported material."""
    names = [n.image.name for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image]
    diff = next((n for n in names if "diffuse" in n.lower()), None)
    spec_name = next((n for n in names if "spec" in n.lower()), None)
    nrm_name = next((n for n in names if "normal" in n.lower()), None)
    if diff is None:
        return
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    d = nt.nodes.new("ShaderNodeTexImage"); d.image = load(diff)
    nt.links.new(d.outputs["Color"], bsdf.inputs["Base Color"])
    s = nt.nodes.new("ShaderNodeTexImage"); s.image = load(spec_name)
    s.image.colorspace_settings.name = "Non-Color"
    sep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(s.outputs["Color"], sep.inputs[0])
    nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])
    rough = nt.nodes.new("ShaderNodeMath"); rough.operation = "SUBTRACT"; rough.inputs[0].default_value = 1.0
    nt.links.new(s.outputs["Alpha"], rough.inputs[1]); nt.links.new(rough.outputs[0], bsdf.inputs["Roughness"])
    n = nt.nodes.new("ShaderNodeTexImage"); n.image = load(nrm_name)
    n.image.colorspace_settings.name = "Non-Color"
    nsep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(n.outputs["Color"], nsep.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineColor")
    nt.links.new(nsep.outputs["Green"], comb.inputs["Red"])
    nt.links.new(n.outputs["Alpha"], comb.inputs["Green"])
    comb.inputs["Blue"].default_value = 1.0
    nmap = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(comb.outputs[0], nmap.inputs["Color"])
    nt.links.new(nmap.outputs[0], bsdf.inputs["Normal"])


for m in bpy.data.materials:
    if m.node_tree:
        hoi4_material(m)
for o in bpy.data.objects:
    if o.type == "MESH" and any(ms.material and ms.material.get("shader") == "Collision" for ms in o.material_slots):
        o.hide_render = True

scn = bpy.context.scene
scn.render.engine = "BLENDER_EEVEE"
scn.render.resolution_x, scn.render.resolution_y = 1400, 900
scn.view_settings.view_transform = "AgX"
world = bpy.data.worlds.new("w"); scn.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.45, 0.5, 0.55, 1); bg.inputs[1].default_value = 0.8
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 3.5; sun.rotation_euler = (math.radians(50), 0, math.radians(35))
scn.collection.objects.link(sun)
ground = bpy.data.meshes.new("g"); ground.from_pydata([(-30, -30, 0), (30, -30, 0), (30, 30, 0), (-30, 30, 0)], [], [(0, 1, 2, 3)])
gobj = bpy.data.objects.new("ground", ground); scn.collection.objects.link(gobj)
gm = bpy.data.materials.new("ground"); gm.diffuse_color = (0.25, 0.23, 0.18, 1)
gm.use_nodes = True; gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.22, 0.2, 0.15, 1)
ground.materials.append(gm)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scn.collection.objects.link(cam); scn.camera = cam
cam.data.lens = 70
target = Vector((0, -0.3, 1.2))
for name, pos in {"front34": (-9.5, -12.0, 5.5), "side": (-16.0, 0.0, 2.0), "hoi4": (-8.0, -8.0, 14.0),
                  "rear34": (9.5, 11.5, 5.0), "closeup": (-5.0, -6.5, 3.6)}.items():
    cam.location = pos
    t = target if name != "closeup" else Vector((0.0, -1.5, 1.6))
    cam.rotation_euler = (t - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = os.path.join(out_dir, name + ".png")
    bpy.ops.render.render(write_still=True)
print("RENDERED", out_dir)
