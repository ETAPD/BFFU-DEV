"""Panzerkampfwagen III Ausf. C (Sd.Kfz. 141), 1938: 3.7 cm KwK 36 L/46.5, eight small road wheels on three leaf
springs.

Traced from the-blueprints.com side view "pzkpfw_iii_ausf_c" (commercial, private reference in the git-ignored
reference/blueprints_nonfree/ger_pz3c/). Side view only: 211 px/m (its 5.85 m length gives 205, the 2.435 m height
218), resampled to 175 px/m, datum x=23.2 (u 0 = 9 cm behind the front mudguard tip), ground y=454.5. Plan widths
(no top/front view of the A-D) follow the documented 2.82 m width with 36 cm tracks and the 3.7 cm turret of the
Ausf. E/F four-view (ger_pz3f), whose turret is the same.

Coordinates: u = metres back from the datum, z = up from the ground, x = to the vehicle's left.
"""

import sys

from . import pz3_common as p3
from . import pz4_common as c

NAME = "GER_pz3c"
# paint: Dunkelgrau with Dunkelbraun (1937 order), Poland 1939; no Zimmerit
CAMO = "grau_braun_1937"
ZIMMERIT = False
CROSS_KINDS = ("paint",)
DETAIL = True
HULL_L = 5.80


def Y(u):
    return u - HULL_L / 2


CROSSES = [(1, Y(2.6), 1.30), (-1, Y(2.6), 1.30)]
CROSS_SIZE = 0.26

# ---- running gear (side view) ----------------------------------------------------------------------------------
TRACK_W = 0.36
TRACK_X = 1.41 - TRACK_W / 2
TRACK_T = 0.04
TRACK_PITCH = 0.12
WHEEL_R = 0.183
WHEEL_Z = 0.243
WHEELS_U = [1.285, 1.707, 2.141, 2.577, 3.101, 3.525, 3.959, 4.393]
SPROCKET = (0.485, 0.597, 0.40)
SPROCKET_TEETH = 21
IDLER = (5.159, 0.654, 0.354)
ROLLERS_U = [1.467, 2.78, 4.256]
ROLLER_Z, ROLLER_R = 0.883, 0.143
DECK_DETAIL = ((-0.80, -0.05, -0.10, 0.55), (0.10, -0.05, 0.80, 0.55))  # deck hatch rivets, frame at u 4.0
SPRINGS = [(1.08, 1.62, 0.56), (2.40, 3.25, 0.55), (4.05, 4.60, 0.56)]  # leaf springs (u0, u1, top z)

# ---- hull ------------------------------------------------------------------------------------------------------
HULL_X = 0.93
LOWER_X = HULL_X
FRONT_U = 1.37  # superstructure front plate
REAR_U = 5.42
ROOF_Z = 1.489
DECK_Z = ROOF_Z
FENDER_Z = 1.15
LOWER_PROFILE = [(0.55, 0.40), (0.22, 0.62), (0.20, 0.95), (FRONT_U, 1.12), (REAR_U, 1.12), (REAR_U, 0.60),
                 (5.15, 0.40)]
SUPER_PROFILE = [(FRONT_U, 1.12), (FRONT_U, 1.465), (FRONT_U + 0.03, ROOF_Z), (4.78, ROOF_Z), (5.41, 1.34),
                 (REAR_U, 1.12)]
GUARD_PROFILE = [(-0.087, 0.79), (0.245, FENDER_Z - 0.015), (5.19, FENDER_Z + 0.015), (5.765, 0.746), (5.765, 0.776),
                 (5.19, FENDER_Z + 0.04), (0.245, FENDER_Z + 0.01), (-0.087, 0.815)]
GUARD_LIP = [(0.245, FENDER_Z - 0.06), (5.19, FENDER_Z - 0.03), (5.19, FENDER_Z + 0.04), (0.245, FENDER_Z + 0.01)]

# ---- turret (side view; plan widths as the E/F turret) ------------------------------------------------------------
TURRET_X = 0.0
TURRET_U = 2.70
TURRET_Z = ROOF_Z
TURRET_TOP = 2.12
TURRET_STATIONS = [(1.80, 0.74, 1.925, 0.60, 1.99), (2.62, 0.82, 2.62, 0.63, 2.094), (3.30, 0.82, 3.30, 0.63, TURRET_TOP),
                   (3.616, 0.50, 3.50, 0.40, TURRET_TOP)]
BORE_X = 0.0
GUN_Z = p3.C_BORE_Z
CUP_U, CUP_X = 3.18, 0.0
# drum cupola of the Ausf. A-C (side view u 2.86-3.50, base 2.10, top 2.38): cylinder with vision slits, flat lid
CUPOLA = {"prof": [(0.0, TURRET_TOP), (0.33, TURRET_TOP), (0.33, 2.14), (0.32, 2.15), (0.32, 2.34), (0.33, 2.35),
                   (0.33, 2.37), (0.0, 2.37)], "hatch_top": (0.30, 2.37, 2.385), "slit_z": 2.25, "slit_r": 0.322,
          "slits": 8}
TURRET_SIDE = {"visor": (2.27, 2.59, 1.81, 1.97), "hatch": (2.69, 2.96, 2.96, 3.24, 1.65, 2.07), "two_leaf": False,
               "hatch_visor": (2.90, 3.06, 1.82, 1.92), "pistol": None, "rear_port": None,
               "hinge_z": (1.75, 1.86, 1.97)}


def wheel_info(scale):
    return c.wheel_info(sys.modules[__name__], scale)


def bogies():
    w = WHEELS_U
    return [(w[i], w[i + 1]) for i in range(0, 8, 2)]


def build(v):
    S = sys.modules[__name__]
    p3.hull(v, S)
    c.running_gear(v, S, bogies=False)
    p3.leaf_springs(v, S, SPRINGS, bogies())
    turret(v, S)
    fittings(v, S)
    if DETAIL:
        from . import ger_pz3l_detail

        ger_pz3l_detail.build(v, S)
    p3.rig(v, S)


def turret(v, S):
    p3.turret(v, S)
    cup = S.CUPOLA
    c.cupola_early(v, S, S.CUP_X, S.CUP_U, S.TURRET_TOP, **cup)
    c.turret_side_fittings(v, S, **S.TURRET_SIDE)
    p3.gun_37(v, S)
    # signal port / periscope housing ahead of the cupola (side view u 2.62-2.74, up to 2.31 m)
    v.add("turret_periscope", c.geo.box(0.25, Y(2.68), TURRET_TOP + 0.09, 0.12, 0.12, 0.20), kind="paint_cast",
          bone="turret", chamfer=0.03)


def fittings(v, S):
    # Kugelblende 30 (right) and driver's visor (left) on the superstructure front (side view MG at 1.32 m)
    p3.front_plate_fittings(v, S, FRONT_U, 0.45, -0.55, 1.32, mg_ball_r=0.11)
    # driver's side vision port (side view u 1.51-1.81, z 1.27-1.44)
    pt = lambda u, z, side, out=0.0: (side * (HULL_X + out), Y(u), z)
    for side in (1, -1):
        c.side_port(v, S, f"hull_side_visor_{side}", side, 1.51, 1.81, 1.27, 1.44, (0.09, 0.02), 0.05, pt,
                    bone="chassie")
    p3.deck(v, S, [(3.95, 4.55, -0.80, -0.10), (3.95, 4.55, 0.10, 0.80)])
    c.headlights(v, S, ((1, 1.20, 1.25), (-1, -1.20, 1.25)), u=0.55)
    c.tow_shackles(v, S, 0.60, 0.60, x=0.55)
    c.rear_mufflers(v, S, main=(0.0, 0.12, 0.95, 0.13, 1.0), aux=None)
    v.locator("left_tracks", (TRACK_X, Y(5.10), 0.0), "tank_base")
    v.locator("right_tracks", (-TRACK_X, Y(5.10), 0.0), "tank_base")
