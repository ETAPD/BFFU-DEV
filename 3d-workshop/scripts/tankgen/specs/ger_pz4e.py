"""Panzerkampfwagen IV Ausf. E (Sd.Kfz. 161), September 1940 - April 1941: 7.5 cm KwK 37 L/24.

Traced from the left-hand (Ausf. E) vehicle of MasterJVN's comparison sheet "PzIV-011-EFG.jpg" (Wikimedia Commons,
CC BY 4.0), resampled from ~67 px/m to 175 px/m like ger_pz4f1 (crops in reference/blueprints/ger_pz4e/; the 3 m
line measures 525 px). Datums: side bow x=51, ground y=507.5; top bow x=51, centreline y=271; front centreline
x=291.5, ground y=485; rear centreline x=278, ground y=485.

The Ausf. F model lies on the E's hull, turret, cupola (the E introduced it; red on the sheet), turret side ports and
L/24 gun, so the E calls the shared ger_pz4g/ger_pz4f1 builders. Traced here:
- stepped superstructure front (top view): the driver's half (from 0.2 m right of the centreline to the left side)
  stands 9 cm ahead of the radio operator's half, which carries the smaller Kugelblende 30;
- 20 mm appliqué plates bolted on the superstructure sides, u 1.12-2.23 and 2.23-3.90, z 1.25-1.64 (red on the
  sheet, side view);
- one-piece turret side hatches (the two-leaf hatch came with the F);
- 38 cm Kgs 61/380/120 tracks (the sheet's front view draws them a little narrower still; 380 mm is the documented
  width and the track centre stays where it is).

Coordinates: u = metres back from the bow tip, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from .. import geo
from . import ger_pz4f1 as f1
from . import ger_pz4g as g
from . import pz4_common as c
from .ger_pz4f1 import *  # noqa: F401,F403  (dimensions)
from .ger_pz4f1 import FRONT_U, GLACIS, ROOF_Z, FENDER_Z, SUPER_X, Y  # noqa: F401

NAME = "GER_pz4e"
# paint: from March 1941 the Ausf. E went to Africa with the 5. leichte Division in the first Afrika scheme, RAL 8000
# Gelbbraun with one third RAL 7008 Graugrün; crosses on the superstructure sides; no Zimmerit
CAMO = "afrika_1941"
ZIMMERIT = False
TRACK_W = 0.38
TRACK_X = 1.42 - TRACK_W / 2 + 0.01  # outer edge 1.43 m: the narrower track keeps its centre line
MG_PLATE_SETBACK = 0.086
HULL_MG = {"ball_r": 0.13}
TURRET_SIDE = {"two_leaf": False, "pistol": None}
gun = f1.gun
DRIVER_SPLIT_X = -0.196  # step in the superstructure front (top view)


def wheel_info(scale):
    return c.wheel_info(sys.modules[__name__], scale)


def superstructure(v, S):
    """Stepped front: the radio operator's (right) half set back by MG_PLATE_SETBACK, the driver's half as the F."""
    gz1 = GLACIS[1][1]
    d = MG_PLATE_SETBACK
    sup = [(FRONT_U[0] + d, gz1), (FRONT_U[1] + d, ROOF_Z), (3.95, ROOF_Z), (3.95, FENDER_Z),
           (FRONT_U[0] + d + 0.01, FENDER_Z)]
    v.add("superstructure", geo.prism_x(c.P(S, sup), -SUPER_X, SUPER_X), chamfer=0.025)
    plate = [(FRONT_U[0], gz1), (FRONT_U[1], ROOF_Z), (FRONT_U[1] + d + 0.02, ROOF_Z), (FRONT_U[0] + d + 0.02, gz1)]
    v.add("driver_front_plate", geo.prism_x(c.P(S, plate), DRIVER_SPLIT_X, SUPER_X), chamfer=0.02)
    for side in (1, -1):  # 20 mm appliqué on the superstructure sides
        for k, (u0, u1) in enumerate(((1.12, 2.225), (2.235, 3.90))):
            x = side * (SUPER_X + 0.01)
            v.add(f"side_applique_{side}_{k}", geo.box(x, Y((u0 + u1) / 2), 1.445, 0.02, u1 - u0, 0.39), kind="paint",
                  chamfer=0.006)


def build(v):
    S = sys.modules[__name__]
    g.hull(v, S)
    c.running_gear(v, S)
    g.turret(v, S)
    g.fittings(v, S)
    if DETAIL:
        from . import ger_pz4g_detail

        ger_pz4g_detail.build(v)
    c.rig(v, S)
