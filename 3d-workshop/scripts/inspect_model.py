# Run: blender -b --python inspect_model.py -- <file.mesh> [more.mesh ...]
# Prints size, triangle count per material, textures, bones and locators of PDX meshes.
import sys

import addon_utils
import bpy

for path in sys.argv[sys.argv.index("--") + 1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable("io_pdx_mesh")
    bpy.ops.io_pdx_mesh.import_mesh(filepath=path, chk_mesh=True, chk_skel=True, chk_locs=True)
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    lo = [min(v[i] for o in meshes for v in [o.matrix_world @ c.co for c in o.data.vertices]) for i in range(3)]
    hi = [max(v[i] for o in meshes for v in [o.matrix_world @ c.co for c in o.data.vertices]) for i in range(3)]
    print(f"== {path.split('/')[-1]}  size x={hi[0]-lo[0]:.2f} y={hi[1]-lo[1]:.2f} z={hi[2]-lo[2]:.2f}")
    for o in meshes:
        for i, slot in enumerate(o.material_slots):
            tris = sum(len(p.vertices) - 2 for p in o.data.polygons if p.material_index == i)
            m = slot.material
            imgs = [f"{n.image.name}({n.image.size[0]}x{n.image.size[1]})" for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image] if m else []
            print(f"  {o.name}[{i}] tris={tris} shader={m.get('io_pdx_mesh_shader', m.get('PDX_SHADER')) if m else None} {imgs}")
    for a in [o for o in bpy.data.objects if o.type == "ARMATURE"]:
        print("  bones:", [(b.name, b.parent.name if b.parent else None) for b in a.data.bones])
    print("  locators:", [(l.name, tuple(round(c, 2) for c in l.matrix_world.translation)) for l in bpy.data.objects if l.type == "EMPTY"])
