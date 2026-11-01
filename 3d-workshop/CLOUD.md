# Working on the 3D models in a cloud (Linux) session

The 3D pipeline is normally run on the Windows PC (GPU bakes, `texconv.exe`). A cloud session can do the
**geometry work** — modelling against the scale drawings and checking with overlays — and commit it; the final
texture bake and DDS conversion are then run on the PC.

## Setup (once per session)

```bash
# Blender 5.2 LTS for Linux (headless use only)
curl -L -o /tmp/blender.tar.xz https://download.blender.org/release/Blender5.2/blender-5.2.3-linux-x64.tar.xz
mkdir -p ~/blender && tar -xf /tmp/blender.tar.xz -C ~/blender --strip-components=1
# the patched PDX add-on is vendored in the repo
mkdir -p ~/.config/blender/5.2/scripts/addons
cp -r 3d-workshop/vendor/io_pdx_mesh ~/.config/blender/5.2/scripts/addons/
~/blender/blender -b --python 3d-workshop/scripts/enable_pdx_addon.py
```

If that exact Blender build isn't on the mirror, use the newest `blender-5.2.*-linux-x64.tar.xz` listed at
https://download.blender.org/release/Blender5.2/ . Headless rendering uses Workbench, so no GPU is needed.

## The drawing-overlay loop

Drawings live in `reference/blueprints/<vehicle>/` (`side.png`, `top.png`, `front.png`, `rear.png`, all at
175 px/m for the Pz IV H). Datums: side view bow x=201 px, ground y=476; top view bow x=27, centreline y=295;
front view centreline x=297.5, ground y=470.

```bash
B=~/blender/blender; D=3d-workshop/reference/blueprints/ger_pz4h; O=/tmp/overlay
$B -b --python 3d-workshop/scripts/overlay_render.py -- ger_pz4h $O 175 \
   side=$D/side.png,201,476 top=$D/top.png,27,295 front=$D/front.png,297.5,470
for v in side top front; do
  $B -b --python 3d-workshop/scripts/blueprint.py -- overlay $D/$v.png $O/${v}_render.png $O/${v}_overlay.png
done
```

`*_overlay.png` shows the model's part outlines in red over the drawing in grey: every red line should sit on a
drawing line. To read exact coordinates, draw a metric grid (0.1 m blue, 0.5 m red, black datum axes) and zoom:

```bash
$B -b --python 3d-workshop/scripts/blueprint.py -- grid $D/side.png /tmp/side_grid.png 175 201 476
$B -b --python 3d-workshop/scripts/blueprint.py -- crop /tmp/side_grid.png /tmp/zoom.png 360 0 1100 220 3
```

In a zoom of factor k, one 0.1 m grid step is 17.5·k px; convert pixel positions back with the datums above.

Geometry lives in `scripts/tankgen/specs/<vehicle>.py` (shapes, in metres: u = back from the bow, z = up from
the ground, x = to the vehicle's left) and `<vehicle>_detail.py` (bake-only bolts/hinges/etc.). Set `DETAIL = False`
in the spec while matching shapes; it speeds the loop up.

Geometry-only export to check it builds: `$B -b --python 3d-workshop/scripts/build_tank.py -- ger_pz4h /tmp/out /tmp/work --skip-bake`
