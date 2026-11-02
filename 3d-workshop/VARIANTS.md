# German tank variants (tankgen specs)

Every spec below is traced from a free-licence scale drawing with outline overlays in
`reference/blueprints/<spec>/overlay_{side,top,front,rear}.png`, `DETAIL = True`, and builds clean with
`build_tank.py <spec> /tmp/out /tmp/work --skip-bake` (cloud session, geometry only). Workflow: `PROCESS.md`.
Triangle counts are the build log's `tris` (all parts, before the build culls hidden downward faces).

## Panzer IV

| Spec | Variant | Years | Gun | Paint (`CAMO`, Zimmerit) | Drawing used | Tris |
|---|---|---|---|---|---|---|
| `ger_pz4b` | Ausf. B / C | 1938-39 | 7.5 cm KwK 37 L/24, internal mantlet | `grau_braun_1937`, no | MasterJVN `PzIV-011-BCD.jpg`, C panel (~61 px/m) | 17,080 |
| `ger_pz4d` | Ausf. D | 1939-40 | KwK 37 L/24, external mantlet | `grau_braun_1937`, no | `PzIV-011-BCD.jpg`, D panel | 17,364 |
| `ger_pz4e` | Ausf. E | 1940-41 | KwK 37 L/24 | `afrika_1941`, no | `PzIV-011-EFG.jpg`, E panel (~67 px/m) | 17,556 |
| `ger_pz4f1` | Ausf. F (F1) | 1941-42 | KwK 37 L/24 | `panzergrau`, no | `PzIV-011-EFG.jpg`, F panel | 17,784 |
| `ger_pz4f2` | Ausf. F2 | 1942 | 7.5 cm KwK 40 L/43, ball brake | `afrika_1942`, no | `PzIV-012-G-Variantes.jpg` (basic G; F2 = early G) | 18,236 |
| `ger_pz4g` | Ausf. G, early | 1942 | KwK 40 L/43, ball brake | `panzergrau`, no | `PzIV-012-G-Variantes.jpg`, left vehicle (175 px/m) | 18,236 |
| `ger_pz4g_late` | Ausf. G, late | 1943 | KwK 40 L/48, double brake; Schürzen | `winter_1943` (whitewash), no | `PzIV-012-G-Variantes.jpg`, right vehicle | 18,268 |
| `ger_pz4h` | Ausf. H (approved) | 1943 | KwK 40 L/48; Schürzen | `dunkelgelb_1943`, yes | `PzIV-012-H-Variantes.jpg` (175 px/m) | 18,208 |
| `ger_pz4j` | Ausf. J, spring 1944 | 1944 | KwK 40 L/48; Schürzen | `ambush_1944`, yes | `PzIV-011-HJ.jpg`, J panel (~58 px/m) | 18,164 |

All drawings are by MasterJVN, Wikimedia Commons, CC BY 4.0 (credits in README). The comparison sheets (B/C/D, E/F/G,
H/J) are the same author's drawings at lower resolution, resampled to 175 px/m; their G and H panels lie on the G/H
models traced from the full-size sheets, which confirms their scale and datums. One sheet pixel is 1.5-1.7 cm there,
so parts shared with a full-size drawing come from the full-size trace and only the differences are read off the
small sheet.

What tells the variants apart (all from the drawings):

- **Gun:** L/24 with the thin barrel ending behind the bow (B-F1), L/43 with ball brake and antenna deflector rod
  (F2, early G), L/48 with double brake (late G, H, J).
- **Front plate:** straight with no hull MG and a round vision port (B/C); stepped, MG half set back 9 cm with the
  Kugelblende 30 (D, E); straight 50 mm with the Kugelblende 50 (F1 on).
- **Mantlet:** internal with a thick armoured gun sleeve (B/C); external box mantlet on the curved rotor (D on).
- **Cupola:** tall cylindrical drum (B-D); cast drum with a rounded foot and two-leaf hatch (E-early G); thick cast
  cupola with the vision-block covers (late G-J).
- **Tracks:** 38 cm (B-E), 40 cm (F1 on).
- **Turret sides:** one-piece hatches (B-E), two-leaf (F1-early G), behind turret Schürzen (late G-J). Turret fan from
  the E; loader's front vision port up to the early G; signal port up to the late G.
- **Hull:** bolted 20 mm superstructure side appliqué (late D, E); hull Schürzen on late G, H, J (the late G's plates
  are drawn on its sheet and differ from the H's); no auxiliary muffler on the J.

### Unresolved

- **Ausf. A:** no free drawing exists (Commons has photos only), so it is not modelled.
- **Ausf. F2** has no drawing of its own; it is the early-G geometry (same vehicle, renamed July 1942) in Afrika paint.
  Its render is identical to `ger_pz4g` apart from the paint.
- **Ausf. J, three return rollers:** the drawn J (spring 1944) has four, like the real early J. The late J's
  three-roller running gear (from about December 1944), wire-mesh Schürzen and vertical exhausts have no free
  drawing and are not modelled.
- **B vs C:** one spec; they differ only in small fittings below the comparison sheet's resolution.
- The comparison-sheet variants (B/C, D, E, F1, J) are traced at 1.5-1.7 cm per sheet pixel; the E's track width
  uses the documented 380 mm (the sheet draws them a little narrower).
- Step 5 of PROCESS.md (checking curved parts and fittings against museum photos) was done for the H only. Commons
  rate-limits downloads from cloud sessions, so photo sets for the other variants are still to collect.
- Balkenkreuze use the black cross with white outline everywhere; the plain white crosses of Poland 1939 (B/C, D) are
  not a bake option yet.

## Panzer III

No free-licence drawing of any Panzer III exists (Commons, archive.org wartime manuals and the HWA D 652 plates were
searched; see git history of this file). With the project owner's agreement the Pz III is traced from the commercial
drawings of the-blueprints.com, used **only as private tracing reference**: the drawings, crops and drawing overlays
stay in the git-ignored `reference/blueprints_nonfree/<spec>/`, and the repository gets the geometry, the model's own
outline renders (`reference/blueprints/<spec>/outline_*.png`) and a README naming the source sheet. None of these
sheets has a scale bar, and most are not to one scale between views (or even within one view), so every view was
calibrated against documented dimensions (length, width, height, the 0.572 m road wheel pitch) and resampled to
175 px/m; the side datum is placed so the road wheels fall on the same stations.

| Spec | Variant | Years | Gun | Paint (`CAMO`) | Drawing used (the-blueprints.com) | Tris | Track speed / `texture_anim_speed` |
|---|---|---|---|---|---|---|---|
| `ger_pz3a` | Ausf. A | 1937 | 3.7 cm KwK 36, internal mantlet | `grau_braun_1937` | A side view (side only) | 17,556 | 1.347 / 1.096 |
| `ger_pz3b` | Ausf. B | 1937-38 | 3.7 cm KwK 36 | `grau_braun_1937` | B side view (side only) | 16,232 | 0.804 / 0.654 |
| `ger_pz3c` | Ausf. C | 1938 | 3.7 cm KwK 36 | `grau_braun_1937` | C side view (side only) | 16,760 | 0.736 / 0.599 |
| `ger_pz3d` | Ausf. D | 1939-40 | 3.7 cm KwK 36 | `grau_braun_1937` | C side view + A-C/D turret comparison | 16,696 | 0.736 / 0.599 |
| `ger_pz3f` | Ausf. E/F | 1938-40 | 3.7 cm KwK 36 | `grau_braun_1937` | F four-view (shows the 5 cm; 3.7 cm from the C) | 16,604 | 1.046 / 0.851 |
| `ger_pz3g` | Ausf. G/H | 1940-41 | 5 cm KwK 38 L/42 | `afrika_1941` | G four-view (differences) | 18,076 | 1.046 / 0.851 |
| `ger_pz3j` | Ausf. J | 1941-42 | 5 cm KwK 38 L/42 | `panzergrau` | J side view | 17,848 | 1.046 / 0.851 |
| `ger_pz3j1` | Ausf. J (J1) | 1941-42 | 5 cm KwK 39 L/60 | `panzergrau` | J four-view (differences) | 17,716 | 1.046 / 0.851 |
| `ger_pz3l` | Ausf. L | 1942 | 5 cm KwK 39 L/60, spaced armour | `panzergrau` | L four-view (main calibration) | 17,748 | 1.046 / 0.851 |
| `ger_pz3m` | Ausf. M | 1942-43 | 5 cm KwK 39 L/60, Schürzen | `dunkelgelb_1943` | M side view (Schürzen) + L four-view | 19,308 | 1.046 / 0.851 |
| `ger_pz3n` | Ausf. N | 1942-43 | 7.5 cm KwK 37 L/24 | `dunkelgelb_1943` | N four-view | 17,788 | 1.046 / 0.851 |

Built from `specs/pz3_common.py` (hull from side profiles, torsion bars, leaf springs, coil springs, 3.7 cm internal
mantlet, mantlets, deep-wading muffler, spare wheels) and the shared Pz IV helpers. The L is the calibrated core:
its four-view agrees with the N, J and G sheets; the A-D share the C's hull and turret.

What tells them apart:

- **Running gear:** five large wheels on coil springs (A); eight small wheels in four bogies on two long leaf springs
  (B) or three leaf springs (C, D); six road wheels on torsion bars, 36 cm tracks (E-H), 40 cm (J on).
- **Gun:** 3.7 cm in the internal mantlet with twin coaxial MGs (A-F); 5 cm L/42 in the external mantlet (G, H, J);
  5 cm L/60 (J1, L, M); 7.5 cm L/24 (N).
- **Front:** Kugelblende 30 in its square plate (A-H); 50 mm plate with Kugelblende 50 (J on); spaced 20 mm plate
  ahead of it and on the mantlet (L, M, N).
- **Turret:** drum cupola (A-C); stepped cupola (D on); turret bin (G on, not E/F/J1 as drawn); side vision ports
  ahead of the hatch (up to J1); spare road wheels on the left guard (G on).
- **Rear:** deep-wading muffler high on the rear plate (M, N); Schürzen (M).

### Unresolved (Pz III)

- **Licence:** the source drawings are commercial; only geometry derived from them is in the repo. If the mod needs a
  clean-room provenance, these specs should be re-checked against a free drawing if one is ever published.
- **A, B, C, D are traced from side views only.** Plan widths and front/rear shapes follow the documented 2.82 m
  width and the E/F turret (same 3.7 cm turret), not a drawing.
- **D:** no D side view; it is the C with the D cupola. The D's angled outer springs and rear hull are not modelled.
- **E vs F, G vs H:** one spec each (differences below drawing resolution or not drawn); the H's 40 cm tracks and
  new sprocket/idler are not separated from the G.
- **M Schürzen plan position** (no top view of the M) follows the H-style rail just outside the guards.
- Photo checks (PROCESS.md step 5) were not done for the Pz III by the cloud session. Review on the PC (from a
  Pz III L/M picture and the Pz IV lessons) added the long lower turret cheeks with their apex at mid-height, the
  roller behind the 5 cm / 7.5 cm mantlets and 3 cm turret chamfers; a full photo pass per variant is still open.

## Panther

No free-licence drawing of any Panther exists: Wikimedia Commons has only a single side profile
(`Panzer_V_panther.svg`, itself traced from the-blueprints.com), small turret strips and armour schemes, and MasterJVN
has drawn no Panther. As for the Panzer III, the Panther is traced from the-blueprints.com drawings (all by Dr Dan
Saranga, one consistent series) **as private tracing reference only**, from the public 500 px previews (the full-size
sheets need a login): sheets, crops and drawing overlays stay in the git-ignored `reference/blueprints_nonfree/<spec>/`;
the repository gets the geometry, the model's own outline renders (`reference/blueprints/<spec>/outline_*.png`), a
README naming the sheet and the free-licence photos checked (`photos/` with `CREDITS.md`). The previews are ~54 px/m
(about 1.9 cm per sheet pixel) and their views differ slightly in scale, so every view was calibrated on its own
against the documented hull length 6.87 m, 8.66 m with the gun, 3.27 m over the tracks and 2.99 m height (and the
860 mm road wheels), and resampled to 175 px/m.

| Spec | Variant | Years | Gun | Paint (`CAMO`, Zimmerit) | Drawing used (the-blueprints.com) | Tris | Track speed / `texture_anim_speed` |
|---|---|---|---|---|---|---|---|
| `ger_panther_d` | Ausf. D (Kursk) | 1943 | 7.5 cm KwK 42 L/70, binocular sight | `dunkelgelb_1943`, no | Ausf. D four-view, ID 72504 (running gear from the G sheet) | 18,180 | 1.729 / 1.407 |
| `ger_panther_a` | Ausf. A | 1943-44 | KwK 42 L/70, monocular sight | `winter_1943` (whitewash), yes | Ausf. A sheet 72501 (side, front, rear) + 72503 (top) | 18,860 | 1.729 / 1.407 |
| `ger_panther_g` | Ausf. G | 1944 | KwK 42 L/70, rounded mantlet | `ambush_1944`, no | Ausf. G four-view, ID 72512 | 18,368 | 1.729 / 1.407 |
| `ger_panther_g_late` | Ausf. G, late | 1944-45 | KwK 42 L/70, chin mantlet | `olivgrun_1945` (new), no | Ausf. G four-view, ID 72512 | 18,420 | 1.729 / 1.407 |

Built from `specs/panther_common.py` (lower hull and sponsons cut by the glacis and rear plate, eight-axle
interleaved running gear, turret shell, curved mantlet with optional chin, gun, drum and cast cupolas, rear fittings,
Schürzen) on the `pz4_common` helpers (`station_shell`, `drum_profile`, `bar`, `gun`). The G sheet is the calibrated
core; the D and A sheets lie on its hull, turret and running-gear lines, so each spec only sets its differences.
All four share the documented 860 mm road wheels, so the track speed is the same: 1.729 game units/s,
`texture_anim_speed` = 1.729 / 1.28 / 0.48 / 2 = 1.407.

Rig: the vanilla 24 bones. `wheel_01` sprocket, `wheel_02` idler, `wheel_03`-`wheel_10` the eight road-wheel axles
front to rear (each bone carries every disc on its axle, both sides: outer-row axles an outer and an innermost disc,
inner-row axles a disc pair either side of the guide teeth), `wheel_11`-`wheel_17` kept on the first seven axles
without geometry so the rig has the vanilla bone set. No return rollers (the top run lies on the wheels).

What tells the variants apart:

- **Cupola:** tall drum with six vision slits and a turret-side bulge under it (D); low cast cupola with seven
  periscope hoods, no bulge (A, G), with the AA-MG ring on the G.
- **Glacis:** letterbox MG flap and driver's visor (D); Kugelblende and driver's visor (A); Kugelblende, no visor (G).
- **Mantlet:** binocular sight holes (D), monocular (A, G); rounded lower half (D, A, G), chin (late G).
- **Hull side:** upper side plates at 40 deg, roof edge 1.28 m out (D, A); one-piece 29 deg plates, roof edge 1.33 m
  out (G).
- **Turret:** three smoke dischargers a side (D only).
- **Rear:** plain exhausts (D); exhausts with cooling pipes (A, G); flame dampers (late G).
- **Schürzen:** fitted on the A (drawn on its sheet); the D and G sheets show none.

### Unresolved (Panther)

- **Licence:** the source drawings are commercial; only geometry derived from them is in the repo (as the Pz III).
- **Resolution:** traced from 500 px previews at ~1.9 cm per sheet pixel, so small fittings (hinges, periscopes,
  tools) are placed from photos and documented sizes within that tolerance.
- **Chin mantlet:** the 500 px G sheet does not resolve the mantlet type. Its drawn lower contour runs straight down
  to a flat bottom, which is used as the late G's chin; the G uses the rounded profile the Saumur photos show. A
  side photo of a chin-mantlet G would settle the chin's exact depth.
- **D running gear:** the D sheet draws the road wheels 1.0 m across (documented 0.86 m) and the wheel set 0.13 m
  further back; the D uses the G sheet's running gear, which matches the documented wheels and the photos.
- **Kursk Schürzen:** many Ausf. D at Kursk carried Schürzen; the D sheet shows none, so none are modelled.
- **Photos:** Commons has free photos of the Saumur A and G, Munster A, Kubinka G, Bovington late G, Overloon G and
  the Breda D, plus Bundesarchiv wartime photos; none of the Munster G, Kubinka D or Fort Benning Panthers turned up,
  so those were not checked. The D's drum cupola and smoke dischargers rest on its drawing.
- **D/A hull side:** the D/A upper side plate is modelled with its 40 deg slope; any difference in its lower rear
  edge from the G's one-piece plate is below the sheets' resolution and is not modelled.
- **Turret offset:** the G top view draws the turret and gun 6 cm right of the hull centreline; the model keeps them
  on the centreline.

## Wiring the variants into the mod (on the PC)

For each spec, after the bake (`build_tank.py <spec> <out> <work>` without `--skip-bake`, then the DDS conversion as
for the H):

1. Copy `GER_<variant>.mesh`, the three `.anim` files and the textures to `gfx/models/units/tanks/bffu_ger/`.
2. In `gfx/entities/bffu_ger_tanks.gfx`, add a `pdxmesh` named `GER_<variant>_mesh` with its idle/move/attack
   animations, like `GER_pz4h_mesh`.
3. In `gfx/entities/bffu_ger_tanks.asset`, add an entity per variant, copied from `GER_medium_armor_pz4h_entity`:
   name `GER_medium_armor_<variant>_entity` (e.g. `GER_medium_armor_pz4f2_entity`), `pdxmesh = "GER_<variant>_mesh"`,
   **`scale = 0.8`** (README step 7), and `texture_anim_speed` from the build log's track speed as for the H
   (track speed / 1.28 / 0.48 / 2). All Pz IV variants use the same road wheels, so the H's value (0.769) applies to
   each of them; check the log anyway.
4. In `gfx/interface/equipmentdesigner/graphic_db/00_tank_icons.txt`, add every Pz IV entity to the models pool of
   `ger_medium_tank_chassis_p4` next to `GER_medium_armor_pz4h_entity`, so players pick the variant from the
   designer's model dropdown:

   ```
   ger_medium_tank_chassis_p4 = {
       ...
       pool = {
           weight = 0.01
           models = {
               GER_medium_armor_pz4b_entity        # Ausf. B/C
               GER_medium_armor_pz4d_entity        # Ausf. D
               GER_medium_armor_pz4e_entity        # Ausf. E
               GER_medium_armor_pz4f1_entity       # Ausf. F1
               GER_medium_armor_pz4f2_entity       # Ausf. F2
               GER_medium_armor_pz4g_entity        # Ausf. G (early)
               GER_medium_armor_pz4g_late_entity   # Ausf. G (late)
               GER_medium_armor_pz4h_entity        # Ausf. H
               GER_medium_armor_pz4j_entity        # Ausf. J
           }
       }
   }
   ```

   The Pz III entities go the same way into the Pz III chassis pools: `ger_medium_tank_chassis_p3` gets
   `GER_medium_armor_pz3a/b/c/d/f/g_entity` (Ausf. A-H) and `ger_medium_tank_chassis_p3_g` gets
   `GER_medium_armor_pz3j/j1/l/m/n_entity` (Ausf. J-N). Pz III `texture_anim_speed` values are in the table above
   (speed / 1.28 m / 0.48 m tile / 2).

   The Panther entities go the same way into the Panther chassis pool: `GER_medium_armor_panther_d_entity`,
   `GER_medium_armor_panther_a_entity`, `GER_medium_armor_panther_g_entity` and `GER_medium_armor_panther_g_late_entity`
   (mesh `GER_panther_<x>_mesh`) go into the models pool of `ger_medium_tank_chassis_p5`, **replacing**
   `GER_medium_armor_2_alt_0_entity` there. Their `texture_anim_speed` is 1.407 (track speed 1.729 / 1.28 m /
   0.48 m tile / 2).

Entity names map to spec names: `ger_pz4g_late` → `GER_pz4g_late` mesh → `GER_medium_armor_pz4g_late_entity`. Each
spec's paint scheme (`CAMO`, `ZIMMERIT`, `CROSS_KINDS`) is applied by the bake automatically.
