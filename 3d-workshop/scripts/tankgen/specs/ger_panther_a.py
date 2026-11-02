"""Panzerkampfwagen V Panther Ausf. A (Sd.Kfz. 171), late 1943 - spring 1944 production: cast cupola with
periscopes, Kugelblende in the glacis, monocular sight, Zimmerit, hull Schürzen.

Drawings: the-blueprints.com "Sd.Kfz. 171 Pz.Kpfw.V Ausf.A Panther" sheets 72501 (two sides, front, rear: the late
A with the Kugelblende and Schürzen) and 72503 (the same draughtsman's A four-view, used for the top view only: its
front view still shows the early A's letterbox MG flap). Both are public 500 px previews by Dr Dan Saranga, used
with the project owner's agreement as private tracing reference only (git-ignored
reference/blueprints_nonfree/ger_panther_a/; see reference/blueprints/ger_panther_a/README.md). Calibrated each
view on its own and resampled to 175 px/m:
  side   (72501, left side) 54.0 px/m (hull 6.87 m: bow 114 -> rear 485; 2.96 m to the cupola); the gun is drawn
         2 % long as on the G sheet, the muzzle is placed at the documented 8.66 m; datum bow x=409.4, ground y=582.8
  top    (72503) 52.4 px/m along (6.87 m), 54.3 px/m across (3.27 m); datum bow x=415.7, centreline y=350.2
  front  (72501) 55.8 px/m across (3.27 m over the tracks), 54.0 px/m up; datum x=357.5, ground y=607.1
  rear   (72501) 56.6 px/m across, 54.0 px/m up; datum x=364.6, ground y=607.1
Hull, running gear and turret shell are panther_common's (the A sheets lie on the G/D lines); the differences
read off these sheets are set below.

Photos checked (reference/blueprints/ger_panther_a/photos/, CREDITS.md there):
  - Musée des Blindés Saumur, Panther A "256" (three photos, front and rear left): Kugelblende on the right of the
    glacis and the driver's visor on the left, Zimmerit on all vertical faces, Schürzen in front, the exhausts with
    their cooling pipes and the angled stowage boxes on the rear plate, the cast cupola -> HULL_MG "ball",
    DRIVER_VISOR, ZIMMERIT, SCHUERZEN, EXHAUST "cooled". (Its turret comes from another tank, per the museum.)
  - Deutsches Panzermuseum Munster, Panther A, side: the long straight sponson, the interleaved wheels with the
    front wheel in the inner row, the turret without a cupola bulge -> BULGE False, running gear as the G.
  - Bundesarchiv Bild 101I-476-2051-30A, Italy 1944, Panther A "334": the A in service with its Zimmerit and
    Schürzen.
  No free photos of the Kubinka or Fort Benning Panthers turned up on Commons, so those were not checked.

Coordinates: u = metres back from the bow, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import panther_common as pc

NAME = "GER_panther_a"
HULL_L = 6.87
# paint: winter 1943/44 on the Eastern Front, whitewash over the Dunkelgelb camouflage; Zimmerit (Sept 1943 on)
CAMO = "winter_1943"
ZIMMERIT = True
CROSS_KINDS = ("skirt",)
DETAIL = True

CROSSES = [(1, 3.0 - HULL_L / 2, 1.15), (-1, 3.0 - HULL_L / 2, 1.15)]  # on the Schürzen
CROSS_SIZE = 0.40

HULL_MG = "ball"
DRIVER_VISOR = True
EXHAUST = "cooled"
AA_RING = False
SIGHT = ("mono", 0.31)
CUPOLA = ("cast", 4.15, 0.34)
DECK_X = 1.28  # D/A upper side plates at 40 deg
# Schürzen (side view): six plates from u 0.44 to 6.31, top edge level at 1.42 m, bottom at 0.88 m
SCHUERZEN = True
SKIRT_TOP = 1.42
_SEAMS = [0.44, 1.59, 2.52, 3.40, 4.37, 5.34, 6.31]
SKIRT_PLATES = [(a, b, 0.88) for a, b in zip(_SEAMS, _SEAMS[1:])]


def Y(u):
    return u - HULL_L / 2


def wheel_info(scale):
    S = sys.modules[__name__]
    pc.init(S)
    return pc.wheel_info(S, scale)


def build(v):
    S = sys.modules[__name__]
    pc.build(v, S)
    if DETAIL:
        from . import ger_panther_a_detail

        ger_panther_a_detail.build(v, S)
