# Run: blender -b --python roundtrip_test.py -- <in.mesh> <in.anim> <out_dir>
# Imports a vanilla HOI4 mesh + animation, prints what came in, re-exports both,
# then re-imports the exported mesh to confirm nothing was lost.
import os
import sys

import bpy

mesh_in, anim_in, out_dir = sys.argv[sys.argv.index("--") + 1:]
os.makedirs(out_dir, exist_ok=True)
name = os.path.splitext(os.path.basename(mesh_in))[0]


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import addon_utils
    addon_utils.enable("io_pdx_mesh")


def summary(tag):
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    locs = [o for o in bpy.data.objects if o.type == "EMPTY"]
    verts = sum(len(o.data.vertices) for o in meshes)
    tris = sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons)
    bones = sum(len(a.data.bones) for a in arms)
    print(f"[{tag}] meshes={len(meshes)} verts={verts} tris={tris} bones={bones} locators={len(locs)}")
    for o in meshes:
        groups = len(o.vertex_groups)
        for slot in o.material_slots:
            m = slot.material
            shader = m.get("io_pdx_mesh_shader", "?") if m else None
            imgs = [n.image.name for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image] if m and m.use_nodes else []
            print(f"  {o.name}: vgroups={groups} material={m.name if m else None} shader={shader} textures={imgs}")
    for a in arms:
        print("  bones:", [b.name for b in a.data.bones])
    print("  locators:", [l.name for l in locs])
    return verts, tris, bones


clear_scene()
bpy.ops.io_pdx_mesh.import_mesh(filepath=mesh_in, chk_mesh=True, chk_skel=True, chk_locs=True)
before = summary("import")

bpy.ops.io_pdx_mesh.import_anim(filepath=anim_in, int_start=1)
scn = bpy.context.scene
print(f"[anim] frames {scn.frame_start}-{scn.frame_end} fps={scn.render.fps}")

for o in bpy.data.objects:
    o.select_set(True)
mesh_out = os.path.join(out_dir, name + "_rt.mesh")
anim_out = os.path.join(out_dir, os.path.splitext(os.path.basename(anim_in))[0] + "_rt.anim")
bpy.ops.io_pdx_mesh.export_mesh(filepath=mesh_out, chk_mesh=True, chk_skel=True, chk_locs=True, chk_selected=False)
bpy.ops.io_pdx_mesh.export_anim(filepath=anim_out, int_start=scn.frame_start, int_end=scn.frame_end)
print("[export]", mesh_out, os.path.getsize(mesh_out), "|", anim_out, os.path.getsize(anim_out))

clear_scene()
bpy.ops.io_pdx_mesh.import_mesh(filepath=mesh_out, chk_mesh=True, chk_skel=True, chk_locs=True)
after = summary("reimport")
print("[result]", "MATCH" if before == after else f"MISMATCH {before} vs {after}")
