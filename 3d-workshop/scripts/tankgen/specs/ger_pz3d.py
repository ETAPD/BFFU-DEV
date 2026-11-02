"""Panzerkampfwagen III Ausf. D (Sd.Kfz. 141), 1939-40: 3.7 cm KwK 36, eight road wheels on three leaf springs,
the new commander's cupola.

There is no side view of the D among the reference drawings, but the D kept the C's hull, leaf-spring running gear,
turret and gun (the C was the D's direct predecessor; the D's 30 mm armour does not change the outline), so the
geometry is ger_pz3c's. The D's cupola is traced from the-blueprints.com turret comparison "pzkpfw_iii_" (Ausf.
A-C vs D; commercial, private reference in the git-ignored reference/blueprints_nonfree/), scaled against the A-C
cupola drawn beside it (0.66 m): base ring r 0.31 m, band of vision-block covers r 0.34 m at 0.04-0.13 m above the
roof, upper drum r 0.32 m, lid r 0.28 m, 0.29 m tall. Not modelled (no drawing): the angled outer leaf springs of
the D and its modified rear hull.
"""

import sys

from . import ger_pz3c as cc
from . import pz3_common as p3
from . import pz4_common as c
from .ger_pz3c import *  # noqa: F401,F403  (dimensions)
from .ger_pz3c import TURRET_TOP

NAME = "GER_pz3d"
# paint: Dunkelgrau with Dunkelbraun, Poland 1939 / France 1940; no Zimmerit
CAMO = "grau_braun_1937"
t = TURRET_TOP
CUPOLA = {"prof": [(0.0, t), (0.31, t), (0.31, t + 0.04), (0.34, t + 0.05), (0.34, t + 0.13), (0.32, t + 0.14),
                   (0.32, t + 0.25), (0.28, t + 0.27), (0.0, t + 0.27)],
          "hatch_top": (0.27, t + 0.27, t + 0.29), "slit_z": t + 0.09, "slit_r": 0.345, "slits": 6}


def wheel_info(scale):
    return c.wheel_info(sys.modules[__name__], scale)


def build(v):
    S = sys.modules[__name__]
    p3.hull(v, S)
    c.running_gear(v, S, bogies=False)
    p3.leaf_springs(v, S, SPRINGS, cc.bogies())
    cc.turret(v, S)
    cc.fittings(v, S)
    if DETAIL:
        from . import ger_pz3l_detail

        ger_pz3l_detail.build(v, S)
    p3.rig(v, S)
