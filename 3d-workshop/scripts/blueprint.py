# Blueprint tools (run with Blender's Python for numpy + image IO):
#   blender -b --python blueprint.py -- crop <src.jpg> <out.png> x0 y0 x1 y1 [zoom]
#   blender -b --python blueprint.py -- grid <crop.png> <out.png> <px_per_m> <origin_x_px> <origin_y_px>
#   blender -b --python blueprint.py -- overlay <crop.png> <render.png> <out.png>
#
# crop:    cut one view out of a drawing sheet (pixel coords, origin top-left)
# grid:    draw a metric grid over a calibrated view: blue every 0.1 m, red every 0.5 m, black axes at the origin
#          (origin = the drawing's datum: bow tip / ground / centreline), so plate corners can be read in metres
# overlay: the model's part outlines (red) over the drawing (grey)
import os
import sys

import bpy
import numpy as np


def load(path):
    img = bpy.data.images.load(path)
    w, h = img.size
    a = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)[::-1].copy()  # top-left origin


def save(arr, path):
    h, w = arr.shape[:2]
    img = bpy.data.images.new(os.path.basename(path), w, h, alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(arr[::-1], dtype=np.float32).ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()


def crop(src, out, x0, y0, x1, y1, zoom=1):
    a = load(src)[int(y0):int(y1), int(x0):int(x1)]
    z = int(zoom)
    if z > 1:  # nearest-neighbour enlargement keeps grid lines crisp
        a = a.repeat(z, axis=0).repeat(z, axis=1)
    save(a, out)


def grid(src, out, ppm, ox, oy):
    a = load(src)
    h, w = a.shape[:2]
    a[..., :3] = 0.55 + 0.45 * a[..., :3]  # fade the drawing so the grid reads
    step = ppm * 0.1
    for axis, origin, size in ((1, ox, w), (0, oy, h)):
        k0 = int(np.floor(-origin / step)) - 1
        k1 = int(np.ceil((size - origin) / step)) + 1
        for k in range(k0, k1):
            p = int(round(origin + k * step))
            if not 0 <= p < size:
                continue
            if k == 0:
                col, width = (0.0, 0.0, 0.0), 2
            elif k % 5 == 0:
                col, width = (0.9, 0.1, 0.1), 1
            else:
                col, width = (0.35, 0.55, 1.0), 1
            sl = slice(max(0, p - width // 2), p + (width + 1) // 2)
            if axis == 1:
                a[:, sl, :3] = a[:, sl, :3] * 0.4 + np.array(col) * 0.6
            else:
                a[sl, :, :3] = a[sl, :, :3] * 0.4 + np.array(col) * 0.6
    save(a, out)


def overlay(drawing, render, out):
    """Drawing in grey, the model's part outlines in red on top (no fill, so the drawing stays readable)."""
    d = load(drawing)
    r = load(render)
    h = min(d.shape[0], r.shape[0])
    w = min(d.shape[1], r.shape[1])
    d, r = d[:h, :w], r[:h, :w]
    ink = 1.0 - d[..., :3].mean(-1, keepdims=True)
    model = r[..., 3:4] if r.shape[2] == 4 else np.ones((h, w, 1))
    lines = np.clip((1.0 - r[..., :3].mean(-1, keepdims=True)) * 1.5, 0, 1) * model
    outa = np.ones((h, w, 4), np.float32)
    outa[..., :3] = 1.0 - 0.6 * ink
    red = np.array([0.95, 0.05, 0.05])
    outa[..., :3] = outa[..., :3] * (1 - lines) + red * lines
    save(outa, out)


args = sys.argv[sys.argv.index("--") + 1:]
cmd = args[0]
if cmd == "crop":
    crop(args[1], args[2], *map(float, args[3:7]), *(map(float, args[7:8])))
elif cmd == "grid":
    grid(args[1], args[2], *map(float, args[3:6]))
elif cmd == "overlay":
    overlay(args[1], args[2], args[3])
print("DONE", cmd)
