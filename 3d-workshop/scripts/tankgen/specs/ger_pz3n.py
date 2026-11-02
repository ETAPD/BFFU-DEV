"""Panzerkampfwagen III Ausf. N (Sd.Kfz. 141/2), June 1942 - August 1943: 7.5 cm KwK 37 L/24 support tank on the
Ausf. L/M chassis.

Traced from the-blueprints.com four-view "pzkpfw_iii_ausf_n" (commercial; private tracing reference in the
git-ignored reference/blueprints_nonfree/ger_pz3n/). Views calibrated separately against documented dimensions and
resampled to 175 px/m: side 196 px/m (height 2.50 m and the 0.572 m wheel pitch agree), top 193 and rear 193 px/m
(2.95 m), front 195.6 px/m. Datums: side x=83 (placed so the road wheels fall on the Ausf. L's stations), ground
y=520.5; top x=85.3, centreline y=267.2; front centreline x=274.2, ground y=482.2; rear centreline x=289.2, ground
y=489.6.

The Ausf. L model lies on this drawing's hull, spaced front plate, running gear, turret, cupola and turret bin, so
the N uses ger_pz3l's builders. Traced here: the L/24 (muzzle u 0.64, barrel r 0.05-0.066 m, sleeve r 0.07 m to
u 0.94) in the N's mantlet (u 1.14-1.58, z 1.75-2.05, front view 0.41 m wide), bore at 1.90 m, and the deep-wading
muffler high on the rear plate with its two pipes (side/rear views).
"""

import sys

from . import ger_pz3l as l
from . import pz3_common as p3
from . import pz4_common as c
from .ger_pz3l import *  # noqa: F401,F403  (dimensions)

NAME = "GER_pz3n"
# paint: from February 1943 the Dunkelgelb base with Olivgrün and Rotbraun; no Zimmerit (Panzer III production ended
# before it was applied in the factory)
CAMO = "dunkelgelb_1943"
GUN_Z = 1.90
DEEP_WADING_MUFFLER = True


def gun(v, S):
    face = 1.14
    p3.mantlet_box(v, S, face, 1.70, -0.20, 0.21, 1.75, 2.05, round_front=0.08)
    p3.gun(v, S, [(0.072, face), (0.072, 0.94), (0.066, 0.92), (0.060, 0.86), (0.055, 0.76), (0.052, 0.64)], 0.64,
           face)


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
