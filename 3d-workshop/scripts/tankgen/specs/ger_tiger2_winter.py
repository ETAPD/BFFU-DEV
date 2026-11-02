"""Panzerkampfwagen Tiger Ausf. B (Tiger II, Sd.Kfz. 182) with the Henschel turret in winter whitewash, winter
1944/45 (Ardennes, Hungary): the ger_tiger2_henschel vehicle under the white winter coat brushed over the factory
paint, worn through to the green and brown patches underneath.

Geometry, drawing and photos as ger_tiger2_henschel (see there); only the paint differs. Period photos of
whitewashed Tiger IIs (s.Pz.Abt. 503 in Hungary, January-March 1945; s.SS-Pz.Abt. 501, Ardennes) show the white
coat over the late camouflage, rubbed off on the plate edges and the hull front; the crosses stayed clear.

Coordinates: u = metres back from the bow, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import tiger_common as tc

NAME = "GER_tiger2_winter"
HULL_L = 7.38
# paint: whitewash over the late-1944 factory camouflage, no Zimmerit (dropped in September 1944)
CAMO = "winter_1945"
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
