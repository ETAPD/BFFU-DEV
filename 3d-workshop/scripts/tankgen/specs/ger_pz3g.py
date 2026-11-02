"""Panzerkampfwagen III Ausf. G (Sd.Kfz. 141), April 1940 - February 1941, in its 5 cm KwK 38 L/42 form (up-gunned
in production from mid-1940 and retrofitted); covers the visually close Ausf. H as well.

Traced from the-blueprints.com four-view "pzkpfw_iii_ausfg" (commercial, private reference in the git-ignored
reference/blueprints_nonfree/ger_pz3g/). Its side view is not to one scale (the 0.572 m wheel pitch gives 117.5 px/m
but the height then comes out 2.60 m), top 119.7, front 116.7, rear 116.5 px/m (2.92-2.95 m); resampled to
175 px/m with datums side x=26.8 (wheels on the L's stations), ground y=476.6; top x=20.5, centreline y=277.0; front
centreline x=297.7, ground y=481.4; rear centreline x=287.7, ground y=551.3. Hull, running gear, turret (side vision
ports, bin), L/42 and mantlet therefore come from ger_pz3j (calibrated on the L/N sheets), and this sheet gives the
G's differences: 36 cm tracks (front view 0.37 m), the hull MG in the smaller Kugelblende 30 with its square plate,
the spare road wheels on the left guard, and the vision ports either side of the mantlet (front view).
"""

import sys

from . import ger_pz3j as j
from . import ger_pz3l as l
from . import pz3_common as p3
from . import pz4_common as c
from .ger_pz3j import *  # noqa: F401,F403  (dimensions)

NAME = "GER_pz3g"
# paint: the Ausf. G (Tropen) of the Afrika Korps in 1941: RAL 8000 Gelbbraun with one third RAL 7008 Graugrün
CAMO = "afrika_1941"
TRACK_W = 0.36
TRACK_X = 1.44 - TRACK_W / 2
MG_BALL_R = 0.12
MG_PLATE = (0.34, 0.30)
TURRET_FRONT_VISORS = (0.46, -0.44)  # front view: gunner's and loader's ports either side of the mantlet
gun = j.gun


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
