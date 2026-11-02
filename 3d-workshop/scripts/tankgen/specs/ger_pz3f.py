"""Panzerkampfwagen III Ausf. E/F (Sd.Kfz. 141), 1938-40: 3.7 cm KwK 36 in the internal mantlet, torsion bars.

Traced from the-blueprints.com four-view "pzkpfw_iii_ausf_f_mit_5_cm_kwk_38" (commercial, private reference in the
git-ignored reference/blueprints_nonfree/ger_pz3f/), an Ausf. F. Side 200 px/m (fitted on the 0.572 m road wheel
pitch), top 199.7, front 197.6, rear 199 px/m (2.91 m width), resampled to 175 px/m; datums side x=81 (wheels on the
L's stations), ground y=537.3; top x=81.5, centreline y=264.6; front centreline x=275.9, ground y=455.2; rear
centreline x=291.5, ground y=452.0. The Ausf. G model (ger_pz3g) lies on this drawing's hull, 36 cm torsion-bar
running gear, Kugelblende 30, turret and turret front ports, so the E/F uses those builders. Traced here: the return
rollers at u 1.62 / 2.72 / 3.79, no turret bin. That drawing shows an F re-armed with the 5 cm gun; the E/F as built
carried the 3.7 cm KwK 36 in the internal mantlet, which is taken from the Ausf. C side view (ger_pz3c, same turret)
and placed on this turret front.
"""

import sys

from . import ger_pz3l as l
from . import pz3_common as p3
from . import pz4_common as c
from .ger_pz3g import *  # noqa: F401,F403  (dimensions)

NAME = "GER_pz3f"
# paint: Dunkelgrau with Dunkelbraun, France 1940; no Zimmerit
CAMO = "grau_braun_1937"
ROLLERS_U = [1.62, 2.72, 3.79]
TURRET_BIN = None
SPARE_WHEELS = False
GUN_Z = p3.C_BORE_Z + (1.62 - p3.C_BASE_Z)


def gun(v, S):
    p3.gun_37(v, S, du=-0.10)


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
