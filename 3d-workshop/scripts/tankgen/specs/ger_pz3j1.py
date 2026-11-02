"""Panzerkampfwagen III Ausf. J with the 5 cm KwK 39 L/60 ("J1", Sd.Kfz. 141/1), December 1941 - June 1942.

The J1 is the Ausf. L without the spaced armour: same hull (50 mm one-piece front with the Kugelblende 50 and the
Fahrersehklappe 50), running gear, turret and gun, and the L was the J1's direct production continuation. So the
geometry is ger_pz3l's (calibrated on its four-view) minus the 20 mm spaced plate in front of the superstructure and
the spaced plate on the mantlet, plus the turret side vision ports ahead of the side hatches (deleted on the L).
Those differences are read off the-blueprints.com four-view "sd_kfz_141_pzkpfwiii_ausfj" (commercial, private
tracing reference in the git-ignored reference/blueprints_nonfree/ger_pz3j1/). That sheet's views are not to one
scale (height says ~157 px/m, length and wheel pitch ~150), so it is fitted at 150 px/m on its running gear and
used for the differences only. Resampled datums: side guard front x=157.4, ground y=492; top x=137.5, centreline
y=281.2; front centreline x=275.9, ground y=492.2; rear centreline x=286.7, ground y=701.2.
"""

import sys

from . import ger_pz3l as l
from . import pz3_common as p3
from . import pz4_common as c
from .ger_pz3l import *  # noqa: F401,F403  (dimensions)

NAME = "GER_pz3j1"
# paint: Dunkelgrau, the 1942 summer offensive in the East; no Zimmerit
CAMO = "panzergrau"
VORPANZER = False
TURRET_BIN = None  # the J1 sheet shows the plain turret rear
MANTLET_FACE_U = 1.45  # mantlet without its spaced front plate
TURRET_SIDE_VISOR = (2.10, 2.36, 1.86, 2.02)  # side view, ahead of the hatch


def wheel_info(scale):
    return c.wheel_info(sys.modules[__name__], scale)


def build(v):
    S = sys.modules[__name__]
    p3.hull(v, S)
    c.running_gear(v, S, bogies=False)
    p3.torsion_suspension(v, S)
    l.turret(v, S)
    l.fittings(v, S)
    if DETAIL:
        from . import ger_pz3l_detail

        ger_pz3l_detail.build(v, S)
    p3.rig(v, S)
