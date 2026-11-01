# Run: blender -b --python enhance_geo.py -- <geo .mesh> <name> <out_dir> <work_dir> <real length with gun, m>
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tankgen import geo_enhance

geo_mesh, name, out_dir, work_dir, length = sys.argv[sys.argv.index("--") + 1:]
print("[geo_enhance] DONE", geo_enhance.run(geo_mesh, name, out_dir, work_dir, float(length)))
