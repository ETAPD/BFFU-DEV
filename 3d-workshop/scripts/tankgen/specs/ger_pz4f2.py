"""Panzerkampfwagen IV Ausf. F2 (Sd.Kfz. 161/1), March - July 1942: 7.5 cm KwK 40 L/43 with the ball brake.

No separate free drawing exists. The F2 and the early Ausf. G are the same vehicle: production carried straight on
and the type was renamed Ausf. G in July 1942 (the sheet "PzIV-011-EFG.jpg" captions the F panel "F1: Abr-41,
F2: Mar-42" and draws the G panel as the same vehicle). So this spec is ger_pz4g's geometry, traced from MasterJVN's
"PzIV-012-G-Variantes.jpg" (basic G = the F2 standard), with its own name and paint. Changes made during G
production (loader's and turret side ports deleted, smoke dischargers) are not on the drawn basic G either.

Paint: the F2 is the "Mark IV Special" of the summer 1942 desert battles, so it takes the March 1942 Afrika scheme
(RAL 8020 Braun with one third RAL 7027 Grau); ger_pz4g carries the Dunkelgrau of the Eastern Front.
"""

import sys

from . import ger_pz4g as g
from . import pz4_common as c
from .ger_pz4g import *  # noqa: F401,F403  (dimensions)
from .ger_pz4g import CUP_U, CUP_X, Y  # noqa: F401

NAME = "GER_pz4f2"
CAMO = "afrika_1942"
ZIMMERIT = False
CROSS_KINDS = ("paint",)
CROSSES = [(1, Y(3.05), 1.465), (-1, Y(3.05), 1.465)]
gun = g.gun


def wheel_info(scale):
    return c.wheel_info(sys.modules[__name__], scale)


def build(v):
    S = sys.modules[__name__]
    g.hull(v, S)
    c.running_gear(v, S)
    g.turret(v, S)
    g.fittings(v, S)
    if g.DETAIL:
        from . import ger_pz4g_detail

        ger_pz4g_detail.build(v, S)
    c.rig(v, S)
