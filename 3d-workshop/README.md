# BFFU 3D workshop

Git-ignored working area for custom HOI4 unit models. Nothing in here ships with the mod; only the final
`.mesh` / `.anim` / `.dds` files copied into `gfx/models/...` and the `.asset` entries do.

```
bin/        texconv.exe (Microsoft DirectXTex, signed, 2026.5.8.1)
scripts/    pipeline scripts (below)
projects/   .blend and .spp source files, one folder per unit
reference/  vanilla imports and test exports
```

## Tools and how they're wired up

| Tool | Version | Setup |
|---|---|---|
| Blender | 5.2.3 LTS | `io_pdx_mesh` add-on, Axis-qc fork `a8ebefb` (upstream ross-g 0.91 adapted for Blender 5.2), plus the BFFU patch in `scripts/io_pdx_mesh_bffu.patch`. Installed in `%APPDATA%\Blender Foundation\Blender\5.2\scripts\addons\io_pdx_mesh`, enabled in preferences. |
| Substance 3D Painter | 12.2.0 | `bffu_hoi4_export.py` in `Documents\Adobe\Adobe Substance 3D Painter\python\startup` (auto-loads). Adds **File > Export HOI4 textures (BFFU)...** |
| JoroDox | 0.8.1 (browser extension) | Load `Documents\GitHub\JoroDox` as an unpacked extension in Edge (no Chrome on this PC). |

### BFFU patch to the add-on

On Blender 5.2 the exporter unwelded nearly every vertex (ENG medium tank: 1,227 → 3,068 verts), because Blender's
stored custom normals drift per-corner by float noise. The patch snaps normals within 0.01 of one already seen
for that vertex, and exports `Collision` meshes position-only like vanilla. After it, ENG and FRA medium tanks
round-trip with identical vertex/triangle/bone/locator counts. If the add-on is ever reinstalled, reapply it
from inside the add-on's `pdx_blender` folder:

```
cd "%APPDATA%\Blender Foundation\Blender\5.2\scripts\addons\io_pdx_mesh\pdx_blender"
git apply "<BFFU-DEV>\3d-workshop\scripts\io_pdx_mesh_bffu.patch"
```

## Texture layout (from `gfx/FX/pdxmesh.shader`, PdxMeshAdvanced)

| File | Format | R | G | B | A |
|---|---|---|---|---|---|
| `*_diffuse.dds` | DXT1 | colour | colour | colour | (none) |
| `*_normal.dds` | DXT5 | normal X (copy) | normal X | glow mask | normal Y |
| `*_spec.dds` | DXT5 | unused | specular level | metalness | glossiness |

The Painter plugin writes exactly this. Painter channels used: Base Color, Metalness, Roughness (inverted to
glossiness), Specular Level (added at 0.5 if missing), Normal (OpenGL). The glow mask is black unless
`EXPORT_EMISSIVE = True` in the plugin, because Painter 12's OpenPBR shader defaults emission colour to white.

**Normal maps are OpenGL (green up).** Derived from the shader: the vertex shader builds `B = cross(N, T) * w`,
the exporter mirrors Blender space (Y/Z swap), and `UnpackRRxGNormal` negates Y. Blender bakes OpenGL natively.
Still to confirm by eye in game on the first unit.

## Scripts

All Blender scripts run headless: `blender.exe -b --python <script> -- <args>`

- `enable_pdx_addon.py` - enable the add-on and save preferences
- `roundtrip_test.py <in.mesh> <in.anim> <out_dir>` - import, re-export, re-import, compare counts
- `dump_mesh.py <file.mesh>...` - shaders, textures, vertex streams and counts per object
- `sp_remote.py <snippet.py>` - run Python inside Painter (needs `launch_painter_remote.bat`). Painter
  executes the snippet with separate globals/locals, so put imports inside a function and call it.
- `bffu_hoi4_export.py` - source copy of the Painter plugin

## Unit workflow (from the kaheti_kartli guide)

1. Model in Blender. One material per texture set, Material type `PdxMeshAdvanced`; tracks use
   `PdxMeshAdvancedAnim` (scrolling UVs).
2. Paint in Painter, export with the BFFU menu entry straight to `gfx/models/units/tanks`.
3. Point the material's textures at the DDS files (PDX material editor in the add-on's sidebar).
4. Bones: import the closest vanilla tank (e.g. `ENG_tank_medium.mesh`, 24 bones: root, tank_base, chassie,
   turret, barrel_base, barrel_tip, wheel_suspention, wheel_01-17), take over its armature, weight-paint vertex
   groups to it, and add an Armature modifier. Move bones to the new wheels/turret, but leave the root
   hierarchy alone or the animations need redoing.
5. Load the vanilla `*_moving.anim`, re-key (I) where bones moved, export idle/moving/attack/death anims.
6. Export `.mesh`, check it in JoroDox, add the `entity` in `gfx/models/entities/*.asset`, test in game.
7. Entity `scale = 0.8` for tankgen models: meshes are real size at 1.28 units/m (vanilla length), and 0.8 draws
   them at the on-map size GEO uses (~7 units long); vanilla's 0.5 looks too small next to map buildings.

## Drawing credits

- Pz IV Ausf. H four-view drawings (`reference/blueprints/ger_pz4h/`): "PzIV-012-H-Variantes.jpg" by MasterJVN,
  Wikimedia Commons, CC BY 4.0 — https://commons.wikimedia.org/wiki/File:PzIV-012-H-Variantes.jpg
- Pz IV Ausf. G four-view drawings (`reference/blueprints/ger_pz4g/`, early G = left vehicle; `ger_pz4g_late/`,
  late G = right vehicle): "PzIV-012-G-Variantes.jpg" by MasterJVN, Wikimedia Commons, CC BY 4.0 —
  https://commons.wikimedia.org/wiki/File:PzIV-012-G-Variantes.jpg
- Pz IV Ausf. E and F four-view drawings (`reference/blueprints/ger_pz4e/`, `ger_pz4f1/`, resampled to 175 px/m):
  "PzIV-011-EFG.jpg" by MasterJVN, Wikimedia Commons, CC BY 4.0 — https://commons.wikimedia.org/wiki/File:PzIV-011-EFG.jpg
- Pz IV Ausf. B/C and D four-view drawings (`reference/blueprints/ger_pz4b/`, `ger_pz4d/`, resampled to 175 px/m):
  "PzIV-011-BCD.jpg" by MasterJVN, Wikimedia Commons, CC BY 4.0 — https://commons.wikimedia.org/wiki/File:PzIV-011-BCD.jpg
- Pz IV Ausf. J four-view drawings (`reference/blueprints/ger_pz4j/`, resampled to 175 px/m): "PzIV-011-HJ.jpg" by
  MasterJVN, Wikimedia Commons, CC BY 4.0 — https://commons.wikimedia.org/wiki/File:PzIV-011-HJ.jpg
- Tiger I four-view (`reference/blueprints/ger_tiger1_early/`, also the base of `ger_tiger1_mid` and
  `ger_tiger1_late`): the drawings of Tiger 131 in the Military College of Science, School of Tank Technology report
  of January 1944, public domain, Wikimedia Commons: "Tiger Side View Left.png", "Tiger Top View.png",
  "Tiger Front View.png", "Tiger Rear View.png" — https://commons.wikimedia.org/wiki/File:Tiger_Side_View_Left.png
  (and the matching File: pages).

Non-free reference (Panzer III): the Pz III specs are traced from the-blueprints.com drawings, used with the project
owner's agreement as private tracing reference only. They are kept in the git-ignored
`reference/blueprints_nonfree/` and never committed or shipped; each `reference/blueprints/ger_pz3*/README.md` names
its source sheet. See VARIANTS.md.

Non-free reference (Panther): the Panther specs are traced from the-blueprints.com drawings by Dr Dan Saranga (Ausf. D
ID 72504, Ausf. A IDs 72501 and 72503, Ausf. G ID 72512, public 500 px previews), under the same policy: kept in the
git-ignored `reference/blueprints_nonfree/`, never committed or shipped; each `reference/blueprints/ger_panther_*/README.md`
names its source sheet, and the free-licence photos checked are credited in `photos/CREDITS.md` next to it. The
Panther II specs use the same author's Panther II colour profiles (IDs 31013, 31012, 15894), by the owner's agreement.

Non-free reference (Tiger II): the Tiger II specs are traced from the-blueprints.com drawings by Dr Dan Saranga
(Henschel turret ID 63811, Porsche turret ID 14674, public 500 px previews), under the same policy as the Pz III and
Panther: kept in the git-ignored `reference/blueprints_nonfree/`, never committed or shipped; each
`reference/blueprints/ger_tiger2_*/README.md` names its source sheet, and the free-licence photos checked are
credited in `photos/CREDITS.md` next to it (as for every Tiger spec).

Cloud (Linux) sessions: see CLOUD.md.
