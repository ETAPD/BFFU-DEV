"""Panzerkampfwagen VI Tiger Ausf. E (Sd.Kfz. 181), mid production, in winter whitewash, Eastern Front, winter
1943/44: the ger_tiger1_mid vehicle (cast cupola, Zimmerit, no Feifel filters, rubber-tyred wheels in three layers)
under the white winter coat units brushed over the Dunkelgelb, worn through in patches.

Geometry, drawing and photos as ger_tiger1_mid (see there); only the paint differs. Period photos of whitewashed
mid-production Tigers (s.Pz.Abt. 503, 506 and 509, Ukraine, winter 1943/44) show the white over the Zimmerit with
the yellow showing through where it wore off; the crosses stayed clear.

Coordinates: u = metres back from the bow, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import tiger_common as tc

NAME = "GER_tiger1_winter"
HULL_L = 6.316
# paint: whitewash over Dunkelgelb and Zimmerit, winter 1943/44
CAMO = "winter_1943"
ZIMMERIT = True
CROSS_KINDS = ("paint",)
DETAIL = True

CROSSES = [(1, 3.30 - HULL_L / 2, 1.66), (-1, 3.30 - HULL_L / 2, 1.66)]
CROSS_SIZE = 0.36

CUPOLA = ("cast", 3.60, 0.53)
FEIFEL = False
SMOKE = False


def Y(u):
    return u - HULL_L / 2


def wheel_info(scale):
    S = sys.modules[__name__]
    tc.init(S)
    return tc.wheel_info(S, scale)


def build(v):
    S = sys.modules[__name__]
    tc.build_tiger1(v, S)
    if DETAIL:
        from . import tiger1_detail

        tiger1_detail.build(v, S)
