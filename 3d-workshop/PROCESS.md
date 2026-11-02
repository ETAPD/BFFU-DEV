# Modelling a tank from a scale drawing

The repeatable workflow behind `scripts/tankgen/specs/ger_pz4h.py` (the approved Pz IV Ausf. H). Every new vehicle
goes through the same steps; the checklist at the end lists what review caught on the H, so later vehicles get it
right first time. Commands are in `CLOUD.md` (cloud sessions) and `README.md` (PC).

## 1. Find a drawing

- A **four-view** (side, top, front, rear) line drawing with a **free licence**: Wikimedia Commons CC BY, CC BY-SA,
  CC0 or public domain. MasterJVN's Commons drawings (CC BY 4.0) are the standard; wartime manuals (US/UK, public
  domain) are a fallback for views the main drawing lacks.
- It must be a scale drawing (scale bar or known dimensions), not colour profile art, a sketch or a render.
- One drawing per visually distinct variant. If a variant has no usable drawing, say so; do not invent geometry
  from photos alone. A variant may reuse a sister variant's drawing for the parts they share **only** where
  photos confirm the parts are the same, and the spec docstring must say which parts came from where.
- Download the original, keep it in `reference/blueprints/<vehicle>/`, credit it in README "Drawing credits".
- If no free drawing exists and the project owner agrees to a commercial one (as for the Panzer III), it is private
  tracing reference only: keep the sheet, crops and drawing overlays in the git-ignored
  `reference/blueprints_nonfree/<vehicle>/`, commit only the spec, the model's own outline renders
  (`reference/blueprints/<vehicle>/outline_*.png`) and a README naming the source.
- Commercial sheets usually have no scale bar and differ in scale between views: calibrate every view on its own
  against documented dimensions (and the road wheel pitch for the side view), never assume one scale for a sheet.

## 2. Crop and calibrate

1. Crop each view into `side.png`, `top.png`, `front.png`, `rear.png` (`blueprint.py crop`). Keep the views
   axis-aligned; rotate the sheet first if a view is skewed.
2. Measure **px/m** against at least three known dimensions: overall length (with and without gun), hull width or
   track width (front view), the drawing's scale bar, wheelbase/road-wheel pitch. They must agree within ~1 %;
   if they do not, the drawing is not to scale in that view (note it, and trust the dimensions that agree).
   Rescale all crops to one px/m (the H uses 175 px/m).
3. Set **datums** in pixels for every view and write them in the spec docstring and `CLOUD.md` style:
   side = bow tip x, ground y; top = bow tip x, centreline y; front/rear = centreline x, ground y.
   Ground = bottom of the track in every view.
4. Draw the metric grid (`blueprint.py grid`: 0.1 m blue, 0.5 m red, black datum axes) and zoom into regions
   (`blueprint.py crop ... 3`). One 0.1 m step is `0.1·px/m·zoom` px in the zoom.

## 3. Read coordinates and build

- Coordinates in metres: **u** back from the bow tip, **z** up from the ground, **x** to the vehicle's left.
- Read every plate corner, wheel centre and radius, fitting position off the grid. Put the numbers in the spec as
  named constants or inline with a comment saying which view they came from.
- Build with the shared helpers: `geo.prism_x` for side-profile plates, `station_shell` for armour shells whose
  width and roof change along the length (turrets), `skirt_wall`/`plate`/`bar` for thin plates and arms, `drum()`
  for curved mantlets, `geo.loft` for faceted fittings (visors, mantlets), `geo.lathe` for anything round (cupola,
  wheels, barrel). The Pz IV hull, running gear and turret builders live in `specs/pz4_common.py`; a variant spec
  sets its dimensions and calls them.
- Start with `DETAIL = False` (fast loop); turn it on and add the `_detail` file (bolts, rivets, hinges, grilles)
  once the shapes match.

## 4. Overlay until every red line sits on a drawing line

```
overlay_render.py <spec> <out> <px/m> side=...,<ox>,<oy> top=... front=... rear=...
blueprint.py overlay <view>.png <out>/<view>_render.png <out>/<view>_overlay.png
```

- Overlays are **outlines only** (red part boundaries and creases over the grey drawing). Never fill the model in:
  a filled silhouette hides wrong internal lines.
- Go view by view, part by part: silhouette first, then plate edges, then fittings. A red line with no drawing
  line under it, or a drawing line with no red line, is a mistake until proven otherwise.
- Parts the drawing omits (e.g. Schürzen plates on the H drawing) are hidden with `OVERLAY_HIDE` to check what is
  behind them, and overlaid again with them shown.
- Save the final `overlay_{side,top,front,rear}.png` next to the drawing.

## 5. Check against photos (required, every vehicle)

**Never skip this step and never show previews before it is done.** The owner caught the same errors on the Pz IV
and again on the Pz III because the drawings were followed without photos: boxy turrets, the wrong cheek shape,
missing curved mantlets. Study museum and period photos of that exact variant alongside the drawing, and in the
spec docstring name the photos checked and what they changed. The drawing is the dimensional reference, but it
flattens curved parts and hides fittings. Download a handful of
free-licence museum photos (Commons) into `reference/blueprints/<vehicle>/photos/` with a `CREDITS.md`
(file, vehicle, author, licence, source) and check: curved and cast parts (mantlet, cupola, sprocket, idler),
vision ports and visors, hatches, exhaust, tools, appliqué. Restored museum vehicles carry later modifications;
trust the drawing for dimensions.

## 5b. Check for holes (required, every vehicle)

HOI4 culls back faces and Blender's renders do not, so an inside-out face, an open surface (a ring lathe without its
inner wall, a loose wheel with one steel face) or a face the bake deleted shows as a hole only in game. The owner
found such holes on the Pz III turret cheeks, cupola rings and spare wheels in the designer. After the build run
`blender -b --python check_backfaces.py -- <out_dir> <file.mesh>`: it renders the exported mesh from six
designer-style angles with back faces in red. Every view must be near 0 red (gun bores and slit edges excepted);
look at the `<name>_<view>.png` renders for anything else and fix the geometry, not the check.

## 6. Done, per vehicle

- spec + `_detail` file, `DETAIL = True`;
- `overlay_{side,top,front,rear}.png` saved next to the drawing, red outlines on the drawing lines;
- `build_tank.py <spec> /tmp/out /tmp/work --skip-bake` runs clean; note the triangle count;
- committed and pushed (one commit per vehicle); the PC bakes it and wires it into the mod.

## Checklist: mistakes caught on the Pz IV H

Go through this before calling a vehicle done.

- [ ] **Not blocky.** Real armour has angles and cuts: raked plates, chamfered corners, sloped glacis, bevelled
      turret sides. No plain boxes where the drawing shows a slope or a cut corner.
- [ ] **Identity right.** The first H attempt looked like a Pz III/IV blend. Check the features that identify the
      variant (wheel count and suspension, superstructure front, turret shape, cupola, gun, hull MG) against the
      drawing and photos of *that* variant, not a sister model.
- [ ] **Overlays are outlines only**, never filled: filling hid errors on the H.
- [ ] **Gun proportions**: mantlet size, barrel jacket length and diameter, barrel steps, muzzle brake length and
      diameter, muzzle position all read off the drawing. Calibre length (L/24, L/43, L/48, L/42, L/60) must give
      the right barrel length.
- [ ] **Turret front not flat**: front plate leans back, cheeks angle out, roof front slopes; the overlay of the
      side and top views shows it.
- [ ] **Curved mantlets curve**: the Pz IV inner (rotor) mantlet is ONE smooth curved face (`drum()`), not a flat
      plate with a bend. The Pz III 5 cm / 7.5 cm guns sit in a roller (Walzenblende) that shows beside and around
      the mantlet block (`pz3_common.mantlet_box`).
- [ ] **Turret cheeks as on the photos**: Pz IV and Pz III turrets have a front plate narrow at the ring that widens
      to the side walls at a mid-height apex, with long triangular cheeks cutting the lower front corners back
      under the side hatch (`pz4_common.turret_shell`, `pz3_common.cheek_shell`). A short cheek up to the roof, or a
      tapered trapezoid front, is wrong.
- [ ] **Photos checked** (step 5) and named in the spec docstring.
- [ ] **Vision ports and visors have a visible glass slit**: a `kind="glass"` box recessed between a hood and a lip,
      or set into a faceted (`geo.loft`) port.
- [ ] **Cupola profile stepped** (base ring, drum, vision-block covers, chamfer, hatch) as a `geo.lathe` traced from
      the side and front views. Different variants carry different cupolas.
- [ ] **Roof fittings present**: periscopes, vents, signal ports where the drawing has them, and none where it has
      not.
- [ ] **Bow track guards and Schürzen rail slope** down at their ends as drawn, not flat boxes.
- [ ] Hidden parts checked with `OVERLAY_HIDE` (Schürzen, bins).
- [ ] **No holes** (step 5b): `check_backfaces.py` near 0 red in every view. Ring-shaped lathes (tyres, rims, rings)
  get a closed section; loose wheels a steel face on both sides.
- [ ] Overlays saved, build clean, triangle count noted.
