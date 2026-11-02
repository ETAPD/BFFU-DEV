"""Panther II as planned (Pz.Kpfw. V Panther II with the Schmalturm), 1944-45 design: the Panther II hull and
running gear (ger_panther2) with the narrow Schmalturm turret, its conical 'Saukopf' mantlet, stereo rangefinder and
the 7.5 cm L/70 (KwK 44/1) with no muzzle brake, as the sheets draw it. Never built: the one Panther II hull was
captured without a turret.

Drawings: the same the-blueprints.com sheets as ger_panther2 (31013 side, 31012 front/rear, 15894 top; colour
profiles used with the project owner's agreement; same crops and datums, see that docstring). The turret, mantlet
and gun are read off them:
  - turret: front plate leaning back 20 deg from u 2.60 at the roof line to u 2.92 at the roof (z 2.80); front face
    0.92 m wide (front view); sides sloping in, widest at the rear corners; angled rear to u 4.89 (side/top views)
  - Saukopf: cone from the front plate (r 0.34 m) forward to u 2.23 (r 0.17 m); recuperator sleeve to u 1.32,
    barrel to the muzzle at u -2.52 (side view; the drawn barrel, 4.7 m ahead of the mantlet, is an L/70)
  - rangefinder ears either side at the roof front (front view), cupola left rear with the AA ring (side view)

Photos: none exist of a Schmalturm on a Panther II; the hull is checked against the surviving prototype's photos
(ger_panther2). The Schmalturm shape follows the sheets only.

Coordinates: u = metres back from the bow, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import panther_common as pc
from .ger_panther2 import P2_HULL

NAME = "GER_panther2_schmalturm"
HULL_L = 6.87
# paint: late-war Olivgrün base scheme it would have entered service in (1945)
CAMO = "olivgrun_1945"
ZIMMERIT = False
CROSS_KINDS = ("paint",)
DETAIL = True

CROSSES = [(1, 3.55 - HULL_L / 2, 1.66), (-1, 3.55 - HULL_L / 2, 1.66)]
CROSS_SIZE = 0.40

globals().update(P2_HULL)

TURRET_TYPE = "schmalturm"
TURRET_STATIONS = [(2.60, 0.80, 2.92, 0.46, 2.80), (4.40, 1.05, 4.30, 0.75, 2.82), (4.89, 0.72, 4.57, 0.50, 2.82)]
GUN_Z = 2.40
TRUNNION_U = 2.95
SAUKOPF = (2.78, 2.23, 0.34, 0.17)
EARS = (3.05, 2.66)
COAX_X = -0.28
SIGHT = ("mono", 0.26)
MUZZLE_U = -2.52
GUN_SECTIONS = [(0.15, 2.25), (0.15, 1.36), (0.165, 1.36), (0.165, 1.30), (0.10, 1.30), (0.10, 0.32), (0.07, 0.30),
                (0.068, -2.15), (0.075, -2.15), (0.075, -2.52)]
CUPOLA = ("cast", 3.99, 0.37)
AA_RING = True


def Y(u):
    return u - HULL_L / 2


def wheel_info(scale):
    S = sys.modules[__name__]
    pc.init(S)
    return pc.wheel_info(S, scale)


def build(v):
    S = sys.modules[__name__]
    pc.build(v, S)
    if DETAIL:
        from . import ger_panther2_detail

        ger_panther2_detail.build(v, S)
