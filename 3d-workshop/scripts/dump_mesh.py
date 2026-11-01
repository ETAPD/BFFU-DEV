# Run: blender -b --python dump_mesh.py -- <file.mesh> [more.mesh ...]
# Prints shader, textures, vertex/index counts and bounds for each object in a PDX .mesh.
import sys

from io_pdx_mesh import pdx_data

for path in sys.argv[sys.argv.index("--") + 1:]:
    print("==", path)
    root = pdx_data.read_meshfile(path)
    for shape in root.findall("object/*"):
        for m in shape.findall("mesh"):
            mat = m.find("material")
            p = m.attrib.get("p", [])
            tri = m.attrib.get("tri", [])
            aabb = m.find("aabb")
            print(f"  {shape.tag}: verts={len(p)//3} tris={len(tri)//3} "
                  f"streams={sorted(m.attrib.keys())} "
                  f"shader={mat.attrib.get('shader')} diff={mat.attrib.get('diff')} n={mat.attrib.get('n')} spec={mat.attrib.get('spec')}"
                  + (f" aabb={list(aabb.attrib.get('min'))}..{list(aabb.attrib.get('max'))}" if aabb is not None else ""))
            print("    channels:", [c.tag for c in m])
