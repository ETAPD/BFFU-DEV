"""Panzerkampfwagen V Panther Ausf. G (Sd.Kfz. 171), late production, winter 1944/45 - 1945: chin mantlet
(Kinnblende, from September 1944) and flame dampers (Flammvernichter) on the exhausts.

Drawing: the Ausf. G sheet of ger_panther_g (the-blueprints.com ID 72512, private tracing reference, same crops,
calibration and datums; see that spec's docstring). Everything but the mantlet's lower half and the exhausts comes
from it unchanged; the photos below confirm those parts are the same on the late G.
  - Chin: the sheet's 500 px preview does not resolve the mantlet type, but its side view's lower mantlet contour
    runs straight down from the trunnion height to a flat bottom at z 1.98 m, 0.02 m behind the curved face's front
    (u 2.12); that drawn contour is the chin here (ger_panther_g uses the rounded profile instead, per the Saumur
    photos). The chin's width is the mantlet's (front view).
  - Flame dampers: no drawing shows them; size from the Bovington photos against the 0.33 m exhaust spacing
    (rear view): tall cylinders ~0.24 m across and ~0.65 m long, leaning back.

Photos checked (reference/blueprints/ger_panther_g_late/photos/, CREDITS.md there):
  - The Tank Museum, Bovington, Panther G (completed under British control at Hanover in 1945 from late parts), rear left: the
    two flame dampers on the exhausts, the stowage boxes either side of the rear plate, spare track links on the
    rear hull side -> EXHAUST "dampers", rear() boxes and links as on the G.
  - The same tank, front right: the mantlet as wide as the turret front plate with the coaxial MG port right and
    the sight aperture left of the gun, no driver's visor, Kugelblende, curved front mudguards (modelled flat).
    The chin itself is not clear from this angle; see above.
  Plus the Ausf. G photos (ger_panther_g) for everything shared.

Coordinates: u = metres back from the bow, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import panther_common as pc

NAME = "GER_panther_g_late"
HULL_L = 6.87
# paint: late-war factory scheme, Olivgrün base with hard-edged Dunkelgelb and Rotbraun (from the end of 1944);
# no Zimmerit (dropped September 1944)
CAMO = "olivgrun_1945"
ZIMMERIT = False
CROSS_KINDS = ("paint",)
DETAIL = True

CROSSES = [(1, 3.55 - HULL_L / 2, 1.62), (-1, 3.55 - HULL_L / 2, 1.62)]
CROSS_SIZE = 0.40

HULL_MG = "ball"
DRIVER_VISOR = False
EXHAUST = "dampers"
CUPOLA = ("cast", 4.01, 0.31)
MANTLET = dict(pc.DEFAULTS["MANTLET"], chin=(2.12, 1.98))


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
        from . import ger_panther_g_late_detail

        ger_panther_g_late_detail.build(v, S)
