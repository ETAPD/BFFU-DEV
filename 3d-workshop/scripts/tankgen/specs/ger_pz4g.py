"""Panzerkampfwagen IV Ausf. G (Sd.Kfz. 161/1), early production, summer 1942: 7.5 cm KwK 40 L/43 with the
single-baffle ball muzzle brake, no Schürzen.

Traced from the left-hand (basic Ausf. G) vehicle of MasterJVN's "PzIV-012-G-Variantes.jpg" (Wikimedia Commons,
CC BY 4.0), which is drawn at 175 px/m like the H sheet (3 m scale bar 525 px, the 1 m black bar 177 px; top view
hull width 2.89 m, front view track span 2.86 m). Crops in reference/blueprints/ger_pz4g/, datums: side bow x=129.5,
ground y=485.5; top bow x=129.5, centreline y=271; front centreline x=370.5, ground y=480; rear centreline x=267,
ground y=480.

The hull, running gear, turret shell and rotor/mantlet lie on the same drawing lines as the Ausf. H model (overlay of
ger_pz4h on this drawing), so they come from ger_pz4h / pz4_common unchanged. What differs and is traced here: the
L/43 gun and ball brake, the antenna deflector rod, the earlier cupola (cast drum, vision slits, two-leaf hatch), a
loader's vision port right of the mantlet, turret side vision ports and two-leaf side hatches (no turret Schürzen),
superstructure side vision ports, the signal port in the turret roof, no hull Schürzen rail, the right headlight.

Coordinates: u = metres back from the bow tip, z = metres above ground, x = metres to the vehicle's left.
"""

import math

from .. import geo, parts
from . import pz4_common as c
from .ger_pz4h import (CROSS_SIZE, DECK_END_U, DECK_PROFILE, DECK_X, FENDER_Z, FRONT_U, GLACIS, GUARD_BOX,  # noqa
                       GUARD_INNER, GUARD_LIP, GUARD_PROFILE, GUN_Z, HULL_L, IDLER, LOWER_PROFILE, LOWER_X, REAR_U,
                       ROLLER_R, ROLLER_Z, ROLLERS_U, ROOF_FRONT_Z, ROOF_Z, SPROCKET, SPROCKET_TEETH, SUPER_X,
                       TRACK_PITCH, TRACK_T, TRACK_W, TRACK_X, TURRET_TOP, TURRET_U, TURRET_X, TURRET_Z, WHEEL_R,
                       WHEEL_Z, WHEELS_U, Y)

NAME = "GER_pz4g"
# paint: factory Dunkelgrau (RAL 7021) over the 1942 summer offensive; plain black-and-white Balkenkreuz on the
# superstructure sides; no Zimmerit (introduced September 1943)
CAMO = "panzergrau"
ZIMMERIT = False
CROSS_KINDS = ("paint",)
CROSSES = [(1, Y(3.05), 1.465), (-1, Y(3.05), 1.465)]
CROSS_SIZE = 0.34
DETAIL = True

CUP_U, CUP_X = 3.618, TURRET_X + 0.008  # early cupola centre (side view u 3.226-4.009, front view x -0.33..+0.45)


def wheel_info(scale):
    import sys

    return c.wheel_info(sys.modules[__name__], scale)


def build(v):
    import sys

    S = sys.modules[__name__]
    hull(v, S)
    c.running_gear(v, S)
    turret(v, S)
    fittings(v, S)
    if DETAIL:
        from . import ger_pz4g_detail

        ger_pz4g_detail.build(v)
    c.rig(v, S)


def hull(v, S):
    c.lower_hull(v, S)
    getattr(S, "superstructure", c.superstructure)(v, S)
    c.engine_deck(v, S)
    c.track_guards(v, S)
    c.tow_shackles(v, S, 0.80, 0.68)


def turret(v, S):
    tx = TURRET_X
    c.turret_shell(v, S)
    # rear stowage bin (side view u 3.90-4.77, top view D-shaped as on the H; rear view bottom 1.77 m)
    if getattr(S, "TURRET_BIN", True):
        c.turret_bin(v, S, tx, 3.834, 4.28, 4.806, 0.566, 1.77, TURRET_TOP - 0.01, TURRET_TOP - 0.01 - 0.037, 4.0)

    # early cupola (side view u 3.226-4.009, front view): base flange, lower drum 0.79 m with a rounded foot and the
    # vision slits (2.31-2.43 m), upper ring 0.74 m (to 2.52 m), two-leaf hatch 0.66 m, top 2.60 m
    cz = TURRET_TOP
    prof = [(0.0, cz), (0.40, cz), (0.40, 2.314), (0.378, 2.316), (0.392, 2.335), (0.395, 2.355), (0.395, 2.418),
            (0.386, 2.432), (0.372, 2.432), (0.372, 2.518), (0.36, 2.529), (0.0, 2.529)]
    c.cupola_early(v, S, CUP_X, CUP_U, cz, prof, (0.329, 2.529, 2.60))

    # fan ventilator cover on the sloping roof plate (front/top view, as on the H)
    slope = math.atan2(TURRET_TOP - ROOF_FRONT_Z, 3.02 - 2.17)
    c.roof_vent(v, S, -0.257, 2.737, c.roof_z(S, 2.737), slope)
    # signal port lid in the flat roof, left of the cupola (top view u 3.16, 0.49 m left)
    lid = geo.lathe([(0.0, 0.0), (0.075, 0.0), (0.075, 0.022), (0.065, 0.032), (0.0, 0.032)], 14, axis="Z")
    v.add("signal_port", geo.move(lid, x=0.49, y=Y(3.164), z=TURRET_TOP), kind="paint_cast", bone="turret",
          smooth_angle=50)

    # front: rotor and mantlet as the H; gunner's port 0.61 m left and loader's port 0.54 m right of the centreline
    # (front view octagons at 2.00 m), sight aperture
    c.turret_front(v, S, ports=(("gunner_visor", 0.61), ("loader_visor", -0.537)), **getattr(S, "MANTLET", {}))
    # side vision ports, two-leaf side hatches, pistol ports (side view)
    c.turret_side_fittings(v, S, **getattr(S, "TURRET_SIDE", {}))

    S.gun(v, S)
    v.bone("turret", (tx, Y(TURRET_U), TURRET_Z), "chassie")


def gun(v, S):
    # 7.5 cm KwK 40 L/43 (side/top views): jacket 0.19 m from the mantlet collar to u 1.05 with clamp rings at
    # u 1.43-1.47 and 1.095-1.13, barrel 0.12 m, ball brake u -0.296 to the muzzle at u -0.606
    gx = c.BORE_X
    face_u = 1.60
    muzzle_u = -0.606
    brake_l = 0.31
    c.gun(v, S, gx, GUN_Z, face_u,
          [(0.097, face_u), (0.097, 1.47), (0.112, 1.47), (0.112, 1.43), (0.097, 1.43), (0.097, 1.13),
           (0.112, 1.13), (0.112, 1.095), (0.097, 1.095), (0.097, 1.05), (0.062, 1.05), (0.062, 0.10), (0.060, 0.10),
           (0.060, muzzle_u + brake_l)],
          muzzle_u, (lambda: c.ball_brake(brake_l), brake_l))
    # antenna deflector rod along the lower left of the barrel, from the jacket's front ring (u 1.0, z 1.94) sloping
    # down to its tip at u -0.05, z 1.885 (side view); 0.14 m left of the centreline (top view)
    c.antenna_deflector(v, S, (gx + 0.075, 1.0, 1.935), (gx + 0.085, -0.054, 1.886))


def hull_side_point(u, z, side, out=0.0):
    return (side * (SUPER_X + out), Y(u), z)


def fittings(v, S):
    c.driver_visor(v, S, 0.36, 1.38, FRONT_U[0])
    c.hull_mg(v, S, -0.61, 1.41, FRONT_U[0] + getattr(S, "MG_PLATE_SETBACK", 0.0), **getattr(S, "HULL_MG", {}))
    c.glacis_hatches(v, S, (("inspection", 0.0, 0.70, 0.27, 0.96), ("brake_l", 0.67, 0.34, 0.25, 0.87),
                            ("brake_r", -0.67, 0.34, 0.25, 0.87)))
    # headlights (front view: 1.05 m left and 1.07 m right, both at 1.40 m)
    c.headlights(v, S, ((1, 1.05, 1.40), (-1, -1.07, 1.40)))
    c.deck_hatches(v, S)
    c.rear_mufflers(v, S)
    c.tools_and_locators(v, S)
    # superstructure side vision ports, driver (left) and radio operator (right): side view u 1.36-1.66,
    # z 1.33-1.50, faceted with the slit along the ridge
    for side in (1, -1):
        c.side_port(v, S, f"hull_side_visor_{side}", side, 1.359, 1.664, 1.33, 1.498, (0.08, 0.015), 0.06,
                    hull_side_point, bone="chassie")

