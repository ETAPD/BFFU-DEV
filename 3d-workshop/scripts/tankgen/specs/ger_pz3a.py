"""Panzerkampfwagen III Ausf. A (Sd.Kfz. 141), 1937: 3.7 cm KwK 36, five large road wheels on coil springs.

Traced from the-blueprints.com side view "pzkpfw_iii_ausf_a" (commercial, private reference in the git-ignored
reference/blueprints_nonfree/ger_pz3a/; side only, 214 px/m resampled to 175 px/m, datum x=16.4, ground y=413.8).
An overlay of the Ausf. C model lies on the A's hull, turret, cupola, gun, sprocket and idler, so those are
ger_pz3c's. Traced here: five 0.67 m road wheels (u 1.30-4.18, pitch 0.72 m, centre 0.40 m) each on its own arm
with a vertical coil spring, and two return rollers at u 2.42 / 3.88.
"""

import sys

from . import ger_pz3c as cc
from . import pz3_common as p3
from . import pz4_common as c
from .ger_pz3c import *  # noqa: F401,F403  (dimensions)

NAME = "GER_pz3a"
CAMO = "grau_braun_1937"
WHEEL_R = 0.335
WHEEL_Z = 0.40
WHEELS_U = [1.30, 2.01, 2.74, 3.466, 4.18]
ROLLERS_U = [2.42, 3.88]
ROLLER_Z, ROLLER_R = 0.85, 0.12


def wheel_info(scale):
    return c.wheel_info(sys.modules[__name__], scale)


def build(v):
    S = sys.modules[__name__]
    p3.hull(v, S)
    c.running_gear(v, S, bogies=False)
    p3.coil_springs(v, S, top_z=0.74)
    cc.turret(v, S)
    cc.fittings(v, S)
    if DETAIL:
        from . import ger_pz3l_detail

        ger_pz3l_detail.build(v, S)
    p3.rig(v, S)
