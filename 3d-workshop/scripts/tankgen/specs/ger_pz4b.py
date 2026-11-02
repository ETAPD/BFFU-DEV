"""Panzerkampfwagen IV Ausf. B and C (Sd.Kfz. 161), May 1938 - August 1939: 7.5 cm KwK 37 L/24 in the internal
mantlet, no hull MG.

Traced from the middle (Ausf. C) vehicle of MasterJVN's comparison sheet "PzIV-011-BCD.jpg" (Wikimedia Commons,
CC BY 4.0), ~61 px/m resampled to 175 px/m like ger_pz4d (crops in reference/blueprints/ger_pz4b/). Datums: side bow
x=57, ground y=489.5; top bow x=57, centreline y=286.5; front centreline x=286.5, ground y=504; rear centreline
x=290, ground y=504. The B (42 built) and C (138) differ only in small fittings (the C's armoured coax MG sleeve,
engine), invisible at this scale, so one spec covers both; it follows the C drawing.

The Ausf. D model lies on the C's hull sides, 38 cm running gear, turret, cupola (introduced on the B), turret side
ports and one-piece hatches and the L/24, so the C uses those builders. Traced here:
- straight superstructure front plate across the full width (top view; the D brought back the stepped front);
- no hull MG: a round vision port for the radio operator in its place (front view, 0.6 m right, 1.47 m);
- internal mantlet: no box-shaped external mantlet; the gun comes out of the rotor face in a thick armoured sleeve,
  r 0.14 m from u 2.03 to 1.59 (side view), centred on the bore;
- no superstructure side appliqué.

Coordinates: u = metres back from the bow tip, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from .. import geo
from . import ger_pz4g as g
from . import pz4_common as c
from .ger_pz4d import *  # noqa: F401,F403  (dimensions)
from .ger_pz4d import FRONT_U, Y  # noqa: F401

NAME = "GER_pz4b"
# paint: Dunkelgrau with Dunkelbraun patches (1937 order), as in Poland 1939; no Zimmerit
CAMO = "grau_braun_1937"
ZIMMERIT = False
superstructure = c.superstructure
MG_PLATE_SETBACK = 0.0
HULL_MG = None
MANTLET = {"body": False, "collar": (0.142, 1.81, 0.44)}


def extra_fittings(v, S):
    """Radio operator's round vision port where the later variants have the hull MG (front view)."""
    port = geo.cylinder(0.12, 0.04, 16, axis="Y")
    v.add("radio_port", geo.move(port, x=-0.60, y=Y(FRONT_U[0] + 0.015) - 0.02, z=1.47), kind="paint_cast",
          chamfer=0.008)
    v.add("radio_port_slit", geo.box(-0.60, Y(FRONT_U[0]) - 0.043, 1.47, 0.12, 0.01, 0.014), kind="glass")


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
