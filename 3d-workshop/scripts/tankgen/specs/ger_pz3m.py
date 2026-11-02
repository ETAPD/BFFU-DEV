"""Panzerkampfwagen III Ausf. M (Sd.Kfz. 141/1), October 1942 - February 1943: 5 cm KwK 39 L/60, Schürzen, deep-wading
exhaust.

The M is the Ausf. L hull and turret with the deep-wading muffler (as the N) and, from 1943, 5 mm hull and turret
Schürzen. Hull, running gear, turret and gun are ger_pz3l's (calibrated on its four-view); the muffler is the N's.
The Schürzen are traced from the-blueprints.com side view "pzkpfw_iii_ausf_m_" (commercial, private reference in
the git-ignored reference/blueprints_nonfree/ger_pz3m/; side only, 184.6 px/m from the 2.47 m cupola height,
resampled to 175 px/m; datum x=183 places its road wheels on the L's stations, ground y=446.5): hull plates z
0.54-1.66 with seams at u 1.75 / 2.70 / 3.67 / 4.63, a leading panel from u 0.26 bent towards the hull and a trailing
plate to u 5.10 with cut corners; turret Schürzen z 1.67-2.15 from u 1.85 round the turret bin to u 4.04. Their
plan positions (no top view of the M) follow the H-style hanging rail just outside the track guards.
"""

import sys

from .. import geo
from . import ger_pz3l as l
from . import pz3_common as p3
from . import pz4_common as c
from .ger_pz3l import *  # noqa: F401,F403  (dimensions)

NAME = "GER_pz3m"
# paint: Dunkelgelb with Olivgrün/Rotbraun (Kursk, summer 1943); Balkenkreuze on the Schürzen; no Zimmerit
CAMO = "dunkelgelb_1943"
CROSS_KINDS = ("skirt",)
CROSSES = [(1, Y(3.2), 1.10), (-1, Y(3.2), 1.10)]
DEEP_WADING_MUFFLER = True
gun = l.gun
SKIRT_X = 1.56
SKIRT_SEAMS = [0.75, 1.754, 2.703, 3.666, 4.634]


def wheel_info(scale):
    return c.wheel_info(sys.modules[__name__], scale)


def schuerzen(v, S):
    s = SKIRT_SEAMS
    top, bot = 1.66, 0.54
    plates = [[(s[i] - 0.01, bot), (s[i + 1] + 0.01, bot), (s[i + 1] + 0.01, top), (s[i] - 0.01, top)] for i in range(4)]
    plates.append([(s[4] - 0.01, bot), (4.82, 0.60), (5.10, 0.80), (5.10, 1.535), (s[4] - 0.01, top)])
    lead = [(0.257, 0.84), (0.45, 0.615), (0.76, 0.615), (0.76, top), (0.52, 1.56), (0.257, 1.40)]
    rail = [(0.30, 1.42), (0.75, 1.68), (4.70, 1.68), (5.10, 1.56)]
    rail = rail + [(u, z - 0.03) for u, z in reversed(rail)]
    for side in (1, -1):
        xr = side * (SKIRT_X - 0.03)
        v.add(f"skirt_rail_{side}", geo.prism_x(c.P(S, rail), xr - 0.015, xr + 0.015), kind="paint", chamfer=0.004)
        for b, u in enumerate((1.30, 2.25, 3.20, 4.15)):  # hanger brackets (the small squares on the side view)
            v.add(f"skirt_bracket_{side}_{b}", geo.box(side * (HULL_X + SKIRT_X - 0.03) / 2, Y(u), 1.63,
                                                       SKIRT_X - 0.03 - HULL_X, 0.05, 0.04), kind="paint", chamfer=0.006)
        for i, pl in enumerate(plates):
            x = side * (SKIRT_X + 0.008 * (i % 2))
            v.add(f"skirt_{side}_{i}", geo.prism_x(c.P(S, pl), x - 0.006, x + 0.006), kind="skirt", smooth_angle=30,
                  chamfer=0.005)
        # leading panel, bent in towards the hull front (plan: from the first plate to 0.25 m further in)
        pts = []
        for u, z in lead:
            t = (0.76 - u) / (0.76 - 0.257)
            pts.append((side * (SKIRT_X - 0.25 * t), Y(u), z))
        v.add(f"skirt_{side}_lead", c.plate(pts, (side * 0.012, 0, 0)), kind="skirt", chamfer=0.004)
    # turret Schürzen: side panels and the wrap round the bin (side view u 1.85-4.04, z 1.67-2.15)
    zb, zt = 1.67, 2.15
    plan = [(0.86, 1.85), (1.05, 2.05), (1.05, 3.45), (0.98, 3.75), (0.80, 3.95), (0.45, 4.04), (0.0, 4.06)]
    for side in (1, -1):
        pts = [(side * x, u) for x, u in plan]
        v.add(f"turret_skirt_{side}", c.skirt_wall(S, pts, zb, lambda u: zt, 0.012, (0.0, 2.9)), kind="skirt",
              bone="turret", smooth_angle=20, chamfer=0.004)
        for u0, u1 in ((2.30, 2.20), (3.10, 3.10)):
            a = (side * 0.62, Y(u0), TURRET_TOP - 0.04)
            b = (side * 1.04, Y(u1), zt - 0.04)
            v.add(f"tskirt_mount_{side}_{u0}", c.bar(a, b, 0.05, 0.03), kind="paint", bone="turret", chamfer=0.006)


def build(v):
    S = sys.modules[__name__]
    p3.hull(v, S)
    c.running_gear(v, S, bogies=False)
    p3.torsion_suspension(v, S)
    l.turret(v, S)
    l.fittings(v, S)
    schuerzen(v, S)
    if DETAIL:
        from . import ger_pz3l_detail

        ger_pz3l_detail.build(v, S)
    p3.rig(v, S)
