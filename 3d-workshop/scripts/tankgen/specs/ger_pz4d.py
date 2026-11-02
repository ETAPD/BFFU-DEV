"""Panzerkampfwagen IV Ausf. D (Sd.Kfz. 161), October 1939 - October 1940: 7.5 cm KwK 37 L/24 in the external
mantlet that the D introduced.

Traced from the right-hand (Ausf. D) vehicle of MasterJVN's comparison sheet "PzIV-011-BCD.jpg" (Wikimedia Commons,
CC BY 4.0), drawn at ~61 px/m (its 1 m black bars are 62 px) and resampled by 175/61.3 to 175 px/m (the 3 m line then
measures 525-529 px). Crops in reference/blueprints/ger_pz4d/, datums: side bow x=60, ground y=489.5; top bow x=60,
centreline y=288; front centreline x=289.5, ground y=504; rear centreline x=293.5, ground y=504. One sheet pixel is
1.6 cm here.

The Ausf. E model lies on the D's hull with its stepped front (the D brought back the hull MG in the set-back right
half), the 38 cm running gear, the turret with one-piece side hatches and side ports, the external mantlet and the
L/24, and the bolted side appliqué that the drawing shows (fitted to late D production from mid-1940), so the D uses
ger_pz4e's builders. Traced here: the older commander's cupola (side view: base ring r 0.385 m to 2.50 m, then the
cylindrical drum r 0.335 m with the vision slits up to the flat two-leaf hatch at 2.65 m, centred at u 3.625), and no
turret fan (it came with the E).

Coordinates: u = metres back from the bow tip, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import ger_pz4e as e
from . import ger_pz4g as g
from . import pz4_common as c
from .ger_pz4e import *  # noqa: F401,F403  (dimensions)
from .ger_pz4e import TURRET_TOP, TURRET_X, Y  # noqa: F401

NAME = "GER_pz4d"
# paint: Dunkelgrau with one third Dunkelbraun patches, the order of July 1937 still in force for Poland and France;
# crosses on the superstructure sides; no Zimmerit
CAMO = "grau_braun_1937"
ZIMMERIT = False
CROSS_KINDS = ("paint",)
CROSSES = [(1, Y(3.05), 1.465), (-1, Y(3.05), 1.465)]
ROOF_VENT = False
CUP_U, CUP_X = 3.625, TURRET_X + 0.008
CUPOLA = {"prof": [(0.0, TURRET_TOP), (0.40, TURRET_TOP), (0.40, 2.315), (0.385, 2.322), (0.385, 2.49),
                   (0.36, 2.505), (0.335, 2.512), (0.335, 2.638), (0.325, 2.648), (0.0, 2.648)],
          "hatch_top": (0.31, 2.648, 2.668), "slit_z": 2.575, "slit_r": 0.337, "slits": 5}
superstructure = e.superstructure
gun = e.gun


def wheel_info(scale):
    return c.wheel_info(sys.modules[__name__], scale)


def build(v):
    S = sys.modules[__name__]
    g.hull(v, S)
    c.running_gear(v, S)
    g.turret(v, S)
    g.fittings(v, S)
    if DETAIL:
        from . import ger_pz4g_detail

        ger_pz4g_detail.build(v, S)
    c.rig(v, S)
