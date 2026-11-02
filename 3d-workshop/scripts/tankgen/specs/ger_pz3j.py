"""Panzerkampfwagen III Ausf. J (Sd.Kfz. 141), March 1941 - July 1942: 5 cm KwK 38 L/42.

The J introduced the 50 mm one-piece hull front with the Kugelblende 50 and Fahrersehklappe 50 and the hull that
the J1, L and M kept, so hull, running gear and turret are ger_pz3j1's (the L's calibrated geometry without spaced
armour, with the turret side vision ports). Traced from the-blueprints.com side view "pzkpfw_iii_ausf_j" (commercial,
private reference in the git-ignored reference/blueprints_nonfree/ger_pz3j/; 214.5 px/m from the cupola height and
the 0.572 m wheel pitch, resampled to 175 px/m; datum x=7.2 places its road wheels on the L's stations, ground
y=438.1): the short L/42 (muzzle u 0.18, barrel r 0.037 m stepping to 0.045 m at u 0.78, sleeve r 0.08 m with a
collar at u 1.0-1.04) in the mantlet u 1.29-1.75, z 1.75-2.00, bore at 1.87 m, and the turret stowage bin.
"""

import sys

from . import ger_pz3j1 as j1
from . import ger_pz3l as l
from . import pz3_common as p3
from . import pz4_common as c
from .ger_pz3j1 import *  # noqa: F401,F403  (dimensions)
from .ger_pz3l import TURRET_BIN  # noqa: F401  (the drawing shows the bin)

NAME = "GER_pz3j"
# paint: Dunkelgrau (Barbarossa / winter 1941-42); no Zimmerit
CAMO = "panzergrau"
GUN_Z = 1.872


def gun(v, S):
    face = 1.29
    p3.mantlet_box(v, S, face, 1.75, -0.19, 0.22, 1.75, 2.00, round_front=0.07)
    p3.gun(v, S, [(0.08, face), (0.08, 1.04), (0.084, 1.04), (0.084, 1.0), (0.045, 1.0), (0.045, 0.78), (0.037, 0.78),
                  (0.037, 0.182)], 0.182, face)


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
