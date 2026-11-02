"""Panzerkampfwagen III Ausf. B (Sd.Kfz. 141), 1937-38: 3.7 cm KwK 36, eight evenly spaced road wheels in four
bogies on two long leaf springs.

Traced from the-blueprints.com side view "pzkpfw_iii_ausf_b" (commercial, private reference in the git-ignored
reference/blueprints_nonfree/ger_pz3b/; side only, 212 px/m resampled to 175 px/m, datum x=15.7, ground y=443.3).
An overlay of the Ausf. C model lies on the B's hull, turret, cupola, gun, sprocket and idler, so those are
ger_pz3c's. Traced here: road wheels at u 1.37-4.49 (pitch 0.446 m, r 0.20 m), the two leaf springs (u 1.60-2.45 and
3.35-4.20 at 0.66 m) each carrying two bogies, return rollers at u 1.51 / 2.85 / 4.31.
"""

import sys

from . import ger_pz3c as cc
from . import pz3_common as p3
from . import pz4_common as c
from .ger_pz3c import *  # noqa: F401,F403  (dimensions)

NAME = "GER_pz3b"
CAMO = "grau_braun_1937"
WHEEL_R = 0.20
WHEEL_Z = 0.247
WHEELS_U = [1.367, 1.813, 2.264, 2.71, 3.156, 3.596, 4.047, 4.487]
ROLLERS_U = [1.51, 2.85, 4.31]
ROLLER_Z = 0.905
SPRINGS = [(1.60, 2.45, 0.66), (3.35, 4.20, 0.66)]


def wheel_info(scale):
    return c.wheel_info(sys.modules[__name__], scale)


def build(v):
    S = sys.modules[__name__]
    p3.hull(v, S)
    c.running_gear(v, S, bogies=False)
    w = WHEELS_U
    p3.leaf_springs(v, S, SPRINGS, [(w[i], w[i + 1]) for i in range(0, 8, 2)])
    cc.turret(v, S)
    cc.fittings(v, S)
    if DETAIL:
        from . import ger_pz3l_detail

        ger_pz3l_detail.build(v, S)
    p3.rig(v, S)
