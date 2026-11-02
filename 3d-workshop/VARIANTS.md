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

**Not modelled: no usable free drawing exists.** Two subagent searches (Commons categories and file search, and
public-domain US/UK wartime manuals on archive.org: TM-E 30-451, Tactical and Technical Trends, Catalog of Enemy
Ordnance Materiel) found no free multi-view or dimensioned drawing of any Pz III Ausf. A-N. What exists:

- `File:Panzer_III_l.svg`: one side profile, no scale, taken from the-blueprints.com (a commercial site); its
  public-domain claim is doubtful and the upload log calls it an Ausf. H while the description says L.
- `File:Panzer_III_LW.svg`: running gear of several versions, no scale, tagged "PD-ineligible" by its author (doubtful
  for a drawing).
- The HWA D 652 manual plates on Commons (Ausf. L, M, N) are photographs, not drawings.

Following PROCESS.md, the Pz III is left out rather than built from photos or a profile of uncertain licence. To go
ahead, the project needs a free-licence four-view drawing (for example, asking MasterJVN to release Pz III sheets
under CC BY like his Pz IV ones), or the user's decision that the Panzer_III_l.svg profile is acceptable for one
variant.

## Wiring the variants into the mod (on the PC)

For each spec, after the bake (`build_tank.py <spec> <out> <work>` without `--skip-bake`, then the DDS conversion as
for the H):

1. Copy `GER_<variant>.mesh`, the three `.anim` files and the textures to `gfx/models/units/tanks/bffu_ger/`.
2. In `gfx/entities/bffu_ger_tanks.gfx`, add a `pdxmesh` named `GER_<variant>_mesh` with its idle/move/attack
   animations, like `GER_pz4h_mesh`.
3. In `gfx/entities/bffu_ger_tanks.asset`, add an entity per variant, copied from `GER_medium_armor_pz4h_entity`:
   name `GER_medium_armor_<variant>_entity` (e.g. `GER_medium_armor_pz4f2_entity`), `pdxmesh = "GER_<variant>_mesh"`,
   **`scale = 0.8`** (README step 7), and `texture_anim_speed` from the build log's track speed as for the H. All Pz IV
   variants use the same road wheels, so the H's value (0.769) applies to each of them; check the log anyway.
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

   Pz III entities, once they exist, go in the same way into `ger_medium_tank_chassis_p3` (A-G/H) and
   `ger_medium_tank_chassis_p3_g` (J-N).

Entity names map to spec names: `ger_pz4g_late` → `GER_pz4g_late` mesh → `GER_medium_armor_pz4g_late_entity`. Each
spec's paint scheme (`CAMO`, `ZIMMERIT`, `CROSS_KINDS`) is applied by the bake automatically.
