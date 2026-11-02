"""Panzerkampfwagen Tiger Ausf. B (Tiger II, Sd.Kfz. 182) with the production (Henschel) turret, 1944-45.

Drawing: the-blueprints.com "Sd.Kfz. 182 Pz.Kpfw.VI Ausf.B King Tiger (Henschel Turret)" (ID 63811, source Dr Dan
Saranga, the same series as the Panther sheets), the public 500 px preview, used with the project owner's agreement as
private tracing reference only (git-ignored reference/blueprints_nonfree/ger_tiger2_henschel/; see
reference/blueprints/ger_tiger2_henschel/README.md). No free-licence Tiger II drawing exists: Commons has only a small
single side profile (Panzer_VI_B.svg, 500 x 200 px) and "King Tiger Blueprint.jpg", which is labelled CC BY 4.0 but is
a scan of page 17 of the copyrighted magazine Bronekollektsiya 2/2001 (re-uploaded from drawingdatabase.com), so it
was not used. The preview is ~47 px/m (2.1 cm per sheet pixel); each view was calibrated on its own and resampled to
175 px/m:
  side   46.3 px/m along (hull 7.38 m: bow 138 -> rear plate 480; muzzle to rear 10.29 m: 46.2), 46.9 up (as the
         front view); datum bow x=521.6, ground y=695.0
  top    46.3 along, 47.3 across (3.755 m over the fenders); datum bow x=529.2, centreline y=351.5
  front  47.0 px/m (3.755 m over the fenders: 47.1; 3.09 m to the cupola: 46.8); datum x=411.1, ground y=682.3
  rear   47.0 px/m (fenders 47.3, height 46.3); datum x=516.6, ground y=676.7
The gun as drawn reaches 10.20 m overall; the muzzle is placed at the documented 10.286 m.

Read off the sheet: nine axles (0.52-0.54 m pitch) of 800 mm wheels, the outer row on the odd axles; sprocket at u
0.65 (18 teeth), idler 0.66 m at u 6.27; the glacis from the nose (z 1.0) to the roof at u 1.15 (50 deg), deck 1.93,
sponson floor 1.50, side plates from 1.49 m out at the floor to 1.34 at the deck (front view); the upper rear plate
leaning forward from the deck edge (u 7.00) to the beak (u 7.28, z 1.45). Henschel turret: flat front plate (base
u 2.06, 0.86 m half-width; top u 2.20, 0.60 m, z 2.63), widest 1.32 m at u 3.46, rear plate from u 5.77 up to 5.49,
roof 2.85; the Saukopf mantlet 0.84 m across at the plate; cupola at u 3.83, x 0.43.

Photos checked (reference/blueprints/ger_tiger2_henschel/photos/, CREDITS.md there):
  - Tiger II '104', The Tank Museum Bovington (2017), front left: the flat-faced turret front with the Saukopf
    mantlet, the narrow front plate and the side plates widening behind it; the one-piece glacis with the
    Kugelblende right and no driver's visor; curved front mudguards; the overlapping (not interleaved) steel wheels in
    two rows -> T2_STATIONS, SAUKOPF, WHEEL_LAYERS "overlap", t2_fenders mudguards.
  - Tiger II '104', rear right: the side plates running past the rear plate as horns with tow eyes; the exhausts low
    on the rear plate in cast guards, curving down; the upper rear plate leaning forward; tow cable looped on the
    hull side; spare track links on the turret side; the turret rear hatch; Zimmerit (this tank, 1944) ->
    t2_hull rear_horn, t2_rear, tow_cable, t2_track_links.
  - Tiger II '104', running gear: steel wheels with flat bolted faces, the sprocket and idler.
  - Tiger II '233 red', Musée des Blindés Saumur (2022): the production turret and hull from the left, the Pilze on
    the roof, the cupola with its periscopes.
  - Tiger II at the Deutsches Panzermuseum Munster (2023), the interlocked and welded plate joints at the rear (the
    side plate dovetailed into the rear plate) -> chamfered plate edges, tiger2_detail welds.
  - Bundesarchiv Bild 101I-680-8282A-32A, Budapest, October 1944: a production Tiger II in service.
  - Bundesarchiv Bild 101I-721-0398-21A, France, June 1944: a Henschel-turret Tiger II being sprayed; the Saukopf
    mantlet from the side, the sloping turret side with track-link hooks, the overlapping wheels, Zimmerit (1944
    vehicles; this spec stands for the 1945 production without it).
  On the PC review the owner found the turret wrong and a line across the middle of the glacis. The line was the
  joint between the lower and upper hull parts at the sponson floor height, chamfered on both: the hull is now built
  as the Panther's, the glacis ONE flat plate from the nose edge to the roof. Against the Bovington and Saumur photos
  the Saukopf as first traced was a flat lid 0.25 m deep; the real cast bell stands out about 0.46 m to its nose, and
  the front plate reaches 2.70 m with a gentler roof slope behind it (T2_STATIONS, SAUKOPF in tiger_common).

Coordinates: u = metres back from the bow, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import tiger_common as tc

NAME = "GER_tiger2_henschel"
HULL_L = 7.38
# paint: factory Olivgrün base with hard-edged Dunkelgelb and Rotbraun (orders of late 1944, spring 1945 production);
# Zimmerit was dropped in September 1944
CAMO = "olivgrun_1945"
ZIMMERIT = False
CROSS_KINDS = ("paint",)
DETAIL = True

CROSSES = [(1, 3.6 - HULL_L / 2, 1.74), (-1, 3.6 - HULL_L / 2, 1.74)]
CROSS_SIZE = 0.36
TURRET_TYPE = "henschel"


def Y(u):
    return u - HULL_L / 2


def wheel_info(scale):
    S = sys.modules[__name__]
    tc.init2(S)
    return tc.wheel_info(S, scale)


def build(v):
    S = sys.modules[__name__]
    tc.build_tiger2(v, S)
    if DETAIL:
        from . import tiger2_detail

        tiger2_detail.build(v, S)
