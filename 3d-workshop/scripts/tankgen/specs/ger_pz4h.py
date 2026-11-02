"""Panzerkampfwagen IV Ausf. H (Sd.Kfz. 161/2), summer 1943 production.

Traced from MasterJVN's four-view drawing "PzIV-012-H-Variantes.jpg" (Wikimedia Commons, CC BY 4.0), calibrated at
175 px/m (checked against the 7.02 m length with gun, the 3 m scale bar and the 2.88 m track width). The drawing omits
the hull Schürzen plates (it does show their rail and brackets); the plates follow the Ausf. H standard (5 mm).

Coordinates: u = metres back from the bow tip, z = metres above ground, x = metres to the vehicle's left.
"""

import math

from .. import geo, parts
from . import pz4_common as c

NAME = "GER_pz4h"
HULL_L = 5.92
# paint (see materials.CAMO_SCHEMES): summer/autumn 1943 Dunkelgelb with Olivgrün and Rotbraun, Zimmerit on the
# vertical hull and turret armour (applied from September 1943), Balkenkreuze on the hull Schürzen
CAMO = "dunkelgelb_1943"
ZIMMERIT = True
CROSS_KINDS = ("skirt",)
DETAIL = True  # bake-only surface detail (ger_pz4h_detail); switch off while checking shapes against the drawing


def Y(u):
    """Bow-relative distance -> model Y (front is -Y, hull centred on the origin)."""
    return u - HULL_L / 2


# ---- running gear (side + front view) ------------------------------------------------------------------------
TRACK_W = 0.40
TRACK_X = 1.44 - TRACK_W / 2  # track outer edge at 1.44 m
TRACK_T = 0.03
TRACK_PITCH = 0.12  # Kgs 61/400/120
WHEEL_R = 0.235
WHEEL_Z = 0.27
WHEELS_U = [1.10, 1.61, 2.13, 2.62, 3.13, 3.63, 4.14, 4.63]  # 4 leaf-spring bogies, pairs 0.51 m apart
SPROCKET = (0.53, 0.72, 0.34)
SPROCKET_TEETH = 19
IDLER = (5.40, 0.60, 0.30)
ROLLERS_U = [1.51, 2.43, 3.38, 4.38]
ROLLER_Z, ROLLER_R = 0.90, 0.13

# ---- hull ------------------------------------------------------------------------------------------------------
LOWER_X = 0.93  # lower hull between the tracks
SUPER_X = 1.20  # superstructure incl. panniers (front view: 2.40 m)
DECK_X = 1.16  # engine compartment
FENDER_Z = 1.25
ROOF_Z = 1.68
GLACIS = ((0.06, 0.97), (1.05, 1.23))  # 15 deg glacis from the upper nose plate to the superstructure front
FRONT_U = (1.05, 1.10)  # superstructure front plate, bottom and top
REAR_U = 5.42  # hull rear plate
DECK_END_U = 5.30  # engine deck ends, rear plate slopes down
# lower hull (side view): belly, lower nose plate, upper nose plate (80 mm), glacis, then sides up to the track
# guards, vertical rear plate down to the sloped rear belly
LOWER_PROFILE = [(0.42, 0.40), (0.0, 0.73), GLACIS[0], GLACIS[1], (REAR_U, GLACIS[1][1]), (REAR_U, 0.60), (5.20, 0.40)]
DECK_PROFILE = [(3.95, FENDER_Z), (3.95, ROOF_Z), (DECK_END_U, ROOF_Z), (REAR_U, 1.45), (REAR_U, FENDER_Z)]
# track guards: plate at 1.25 m with a 7 cm outer lip (side view line at 1.18 m), front mudguard sloping down to the
# bow and boxed in (front view), rear mudguard sloping down from u 5.45 to 0.99 m at the tail (side view)
GUARD_PROFILE = [(0.0, 0.90), (0.17, 1.165), (0.50, FENDER_Z - 0.012), (5.45, FENDER_Z - 0.012), (5.95, 0.948),
                 (5.95, 0.993), (5.45, FENDER_Z), (0.50, FENDER_Z), (0.17, 1.18), (0.0, 0.915)]
GUARD_BOX = [(0.0, 0.88), (0.0, 0.915), (0.17, 1.185), (0.50, FENDER_Z), (0.50, 0.88)]
# ahead of the superstructure the guard runs in to the lower hull side (top view: inner edge 0.92 m to u 1.05)
GUARD_INNER = [(0.0, 0.90), (0.17, 1.165), (0.50, FENDER_Z - 0.012), (FRONT_U[0], FENDER_Z - 0.012),
               (FRONT_U[0], FENDER_Z), (0.50, FENDER_Z), (0.17, 1.18), (0.0, 0.915)]
GUARD_LIP = [(0.50, 1.18), (5.45, 1.18), (5.45, FENDER_Z), (0.50, FENDER_Z)]

# ---- turret ---------------------------------------------------------------------------------------------------
TURRET_U = 3.03  # turret ring centre
TURRET_X = 0.05  # offset to the vehicle's left (gun bore is 5 cm left of the centreline in the front view)
TURRET_Z = 1.70
TURRET_TOP = 2.305  # flat rear roof (side view)
ROOF_FRONT_Z = 2.21  # top of the front plate; the roof plate slopes up to TURRET_TOP at u 3.02
GUN_Z = 1.98  # bore axis (side view)

# Balkenkreuz on the middle hull Schürzen plate, both sides: (side, y, z) in metres
CROSSES = [(1, Y(2.95), 1.10), (-1, Y(2.95), 1.10)]
CROSS_SIZE = 0.52


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
    schuerzen(v, S)
    if DETAIL:
        from . import ger_pz4h_detail  # imported here: it reads this module's dimensions

        ger_pz4h_detail.build(v)
    c.rig(v, S)


def hull(v, S):
    c.lower_hull(v, S)
    c.superstructure(v, S)
    c.engine_deck(v, S)
    c.track_guards(v, S)
    c.tow_shackles(v, S, 0.80, 0.68)


def turret(v, S):
    tx, ty = TURRET_X, Y(TURRET_U)

    def roof_z(u):
        return c.roof_z(S, u)

    c.turret_shell(v, S)

    # rear stowage bin inside the skirt wrap: D-shaped in plan (top view u 3.83-4.81, 1.13 m wide), lid flat behind
    # the roof, then sloping down to 2.26 m at the back (side view)
    c.turret_bin(v, S, tx, 3.834, 4.28, 4.806, 0.566, 1.86, TURRET_TOP - 0.01, TURRET_TOP - 0.01 - 0.037, 4.0)

    # commander's cupola (side/front view): base ring 0.95 m, armoured drum flaring 0.83 -> 0.88 m with the
    # vision-block covers, chamfered top and the hatch, top at 2.62 m
    cz = TURRET_TOP
    cup_u, cup_x = 3.574, tx + 0.005
    prof = [(0.0, cz), (0.472, cz), (0.472, 2.364), (0.416, 2.364), (0.438, 2.459), (0.444, 2.462),
            (0.444, 2.47), (0.438, 2.47), (0.438, 2.524), (0.38, 2.554), (0.0, 2.554)]
    c.cupola_late(v, S, cup_x, cup_u, cz, prof,
                  [(0.0, 2.554), (0.388, 2.554), (0.388, 2.605), (0.372, 2.619), (0.0, 2.619)])

    # fan ventilator cover on the sloping roof plate, right of the gun (top view u 2.61-2.86, 0.26 m right of the
    # centreline; side view top 2.35 m)
    slope = math.atan2(TURRET_TOP - ROOF_FRONT_Z, 3.02 - 2.17)
    c.roof_vent(v, S, -0.257, 2.737, roof_z(2.737), slope)

    # gun (side/top/front views): rotor and mantlet as pz4_common.turret_front, L/48 barrel, double-baffle brake;
    # muzzle 1.07 m ahead of the bow. Gunner's vision port left of the mantlet.
    gx = c.BORE_X
    c.turret_front(v, S, ports=(("gunner_visor", 0.61),))
    face_u = 1.60
    muzzle_u = -1.074
    brake_l = 0.278
    c.gun(v, S, gx, GUN_Z, face_u,
          [(0.1145, face_u), (0.1145, 1.069), (0.118, 1.069), (0.118, 1.028), (0.0655, 1.028), (0.0655, 0.10),
           (0.061, 0.10), (0.061, -0.65), (0.072, -0.65), (0.072, -0.73), (0.061, -0.73), (0.061, muzzle_u + brake_l)],
          muzzle_u, (lambda: parts.muzzle_brake_double(0.112, brake_l, 16), brake_l))
    v.bone("turret", (tx, ty, TURRET_Z), "chassie")

    # turret Schürzen (8 mm), centred on the turret: side panels from u 2.07 (flaring out to 1.21 m by u 2.8),
    # top edge 2.23 m, falling to 2.15 m over the front metre (side view), bottom at 1.73 m; rear wrap curving in
    # from u 3.9 round the bin to u 4.85 (top view); bent front panels between the side panel and the mantlet
    # (the front-view "X" is the fold from the outer top corner to the inner bottom corner)
    zb = 1.73
    skirt_top = lambda u: 2.152 + 0.08 * min(1.0, (u - 2.07) / 0.98)
    plan = [(1.02, 2.07), (1.06, 2.32), (1.19, 2.68), (1.21, 2.80), (1.207, 3.90), (1.08, 4.24), (0.885, 4.49),
            (0.67, 4.67), (0.386, 4.79), (0.0, 4.845)]
    for side in (1, -1):
        pts = [(tx + side * x, u) for x, u in plan]
        v.add(f"turret_skirt_{side}", c.skirt_wall(S, pts, zb, skirt_top, 0.014, (tx, 3.4)), kind="skirt", bone="turret",
              smooth_angle=20, chamfer=0.004)
        front = [(1.02, 2.075, skirt_top(2.07)), (0.69, 2.095, 2.20), (0.66, 1.985, 2.03), (0.64, 1.982, zb),
                 (1.02, 2.07, zb)]
        v.add(f"turret_skirt_front_{side}", c.plate([(tx + side * x, Y(u), z) for x, u, z in front], (0, 0.014, 0)),
              kind="skirt", bone="turret", chamfer=0.003)
        # mounting arms from the turret roof edge out to the top of the skirt (top view)
        for u0, u1 in ((2.47, 2.33), (3.02, 2.78), (3.86, 4.05)):
            a = (tx + side * 0.69, Y(u0), roof_z(u0) - 0.03)
            b = (tx + side * 1.20, Y(u1), skirt_top(u1) - 0.03)
            v.add(f"skirt_mount_{side}_{u0}", c.bar(a, b, 0.05, 0.03), kind="paint", bone="turret", chamfer=0.006)
        # two-leaf door over the turret side hatch (side view u 3.13-3.83, full skirt height)
        for k, (u0, u1) in enumerate(((3.13, 3.475), (3.485, 3.83))):
            zt = skirt_top((u0 + u1) / 2) - 0.012
            v.add(f"skirt_door_{side}_{k}", geo.box(tx + side * 1.223, Y((u0 + u1) / 2), (zb + zt) / 2 + 0.006,
                                                    0.012, u1 - u0, zt - zb - 0.012),
                  kind="skirt", bone="turret", chamfer=0.003)


def fittings(v, S):
    # driver's visor (Fahrersehklappe 80) on the left, MG ball mount on the right (front view)
    # visor (front view): base plate 0.54 x 0.22 m, then an armoured hood over a 3.6 cm vision slit and a lower lip,
    # both 0.42 m wide and standing 10 cm proud; the hood's front face slopes back (side view)
    c.driver_visor(v, S, 0.36, 1.38, FRONT_U[0])
    c.hull_mg(v, S, -0.61, 1.41, FRONT_U[0])
    # glacis: central transmission inspection plate and two brake access hatches (top view)
    c.glacis_hatches(v, S, (("inspection", 0.0, 0.70, 0.27, 0.96), ("brake_l", 0.67, 0.34, 0.25, 0.87),
                            ("brake_r", -0.67, 0.34, 0.25, 0.87)))
    # headlights on the front guards, behind the mudguards (front view: left one 1.06 m out at 1.40 m, right one
    # 1.35 m out at 1.37 m; top view u 0.46-0.62), each on a short post
    c.headlights(v, S, ((1, 1.06, 1.40), (-1, -1.35, 1.37)))
    # crew hatches on the superstructure roof (top view: u 1.39-1.90, centres 0.69 m out); engine deck: two access
    # hatches, cooling louvres either side (top view u 4.33-4.79, 0.46-0.86 m out)
    c.deck_hatches(v, S)
    # rear: main muffler across the rear plate, offset to the right (rear view x -0.80..+0.31, z 0.95-1.27; top
    # view u 5.45-5.71), short tail pipe on top angled to the left, auxiliary (generator) muffler under its left end
    c.rear_mufflers(v, S, aux=getattr(S, "AUX_MUFFLER", (0.495, 0.12, 1.02)))
    # tools: shovel and jack on the guards, tow cables, antenna base
    c.tools_and_locators(v, S)


def schuerzen(v, S):
    """Hull Schürzen (5 mm). The drawing shows the hanger rail and its brackets but not the plates: rail 1.59 m out
    (top view, u 0.58-5.50), 1.54-1.57 m high, sloping down at both ends (side view); 5 plates per side hang on it."""
    top = 1.575
    plates = []
    for i in range(5):
        u0 = 0.62 + i * 0.97
        pl = [(u0, top), (u0, 0.62), (u0 + 1.02, 0.62), (u0 + 1.02, top)]
        if i == 0:  # leading plate: top edge follows the rail down to its front end, long diagonal to the bottom
            pl = [(0.58, 1.53), (0.58, 1.40), (1.04, 0.62), (u0 + 1.02, 0.62), (u0 + 1.02, top), (1.08, top)]
        elif i == 4:  # trailing plate: top edge follows the rail down, rear corner cut towards the idler
            pl = [(u0, top), (u0, 0.62), (u0 + 0.86, 0.62), (u0 + 0.98, 0.78), (u0 + 0.98, 1.505), (5.05, top)]
        plates.append(pl)
    # rail (top view u 0.58-5.50) with brackets from the superstructure side (top view u 1.35, 2.44, 3.76, 4.91)
    c.hull_schuerzen(v, S, [(0.58, 1.525), (1.08, 1.571), (5.05, 1.571), (5.50, 1.505)], (1.35, 2.44, 3.76, 4.91),
                     plates)
