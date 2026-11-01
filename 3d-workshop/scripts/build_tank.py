# Run: blender -b --python build_tank.py -- <spec module> <out_dir> <work_dir> [--skip-bake]
# Builds, bakes, rigs, animates and exports one vehicle from scripts/tankgen/specs/<spec>.py.
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tankgen import build

args = sys.argv[sys.argv.index("--") + 1:]
spec_name, out_dir, work_dir = args[:3]
spec = importlib.import_module("tankgen.specs." + spec_name)
result = build.run(spec, out_dir, work_dir, skip_bake="--skip-bake" in args)
print("[tankgen] DONE", result)
