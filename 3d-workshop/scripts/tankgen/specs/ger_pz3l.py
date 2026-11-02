"""Panzerkampfwagen III Ausf. L (Sd.Kfz. 141/1), June - December 1942: 5 cm KwK 39 L/60, spaced armour on the
superstructure front and the mantlet.

Traced from the-blueprints.com four-view "pzkpfw_iii_ausf_l" (commercial drawing, used with the user's agreement as
private tracing reference; kept in the git-ignored reference/blueprints_nonfree/, never committed). No free
four-view of any Panzer III exists (see VARIANTS.md). The sheet has no scale bar and its views differ slightly in
scale, so each view was calibrated on its own against documented Ausf. L dimensions and resampled to 175 px/m:
side 195 px/m (hull 5.45 m to the guard front, height 2.50 m, road wheel pitch 0.572 m = 2.86 m ground contact
over six wheels, all agree), top 192 px/m and front/rear 192 px/m (2.95 m over the tracks). Datums in the resampled
crops: side guard front x=181.3, ground y=477.4; top guard front x=44.7, centreline y=271.2; front centreline
x=290.3, ground y=451.6; rear centreline x=281, ground y=457.1. The drawn road wheels are 0.46 m; the model uses the
documented 520 mm.

Coordinates: u = metres back from the front of the track guards, z = metres above ground, x = to the vehicle's left.
"""

import math
import sys

from .. import geo
from . import pz3_common as p3
from . import pz4_common as c

NAME = "GER_pz3l"
CAMO = "panzergrau"
ZIMMERIT = False
CROSS_KINDS = ("paint",)
DETAIL = True
HULL_L = 5.45


def Y(u):
    return u - HULL_L / 2


CROSSES = [(1, Y(3.0), 1.42), (-1, Y(3.0), 1.42)]  # Balkenkreuz on the superstructure sides
CROSS_SIZE = 0.30

# ---- running gear (side view) ----------------------------------------------------------------------------------
TRACK_W = 0.40
TRACK_X = 1.46 - TRACK_W / 2
TRACK_T = 0.04
TRACK_PITCH = 0.12  # Kgs 61/400/120
WHEEL_R = 0.26
WHEEL_Z = 0.30
WHEELS_U = [1.311, 1.888, 2.455, 3.027, 3.598, 4.168]
SPROCKET = (0.536, 0.715, 0.36)
SPROCKET_TEETH = 21
IDLER = (4.82, 0.756, 0.33)
ROLLERS_U = [1.433, 2.72, 3.765]
ROLLER_Z, ROLLER_R = 0.974, 0.12

# ---- hull ------------------------------------------------------------------------------------------------------
HULL_X = 0.95
LOWER_X = HULL_X
FRONT_U = 1.18  # superstructure front plate
VORPANZER_U = 1.045  # spaced 20 mm plate in front of it
REAR_U = 5.45
ROOF_Z = 1.60
DECK_Z = 1.60
FENDER_Z = 1.245
LOWER_PROFILE = [(0.42, 0.42), (0.12, 0.80), (0.15, 1.10), (FRONT_U, 1.21), (REAR_U, 1.21), (REAR_U, 0.62),
                 (5.20, 0.42)]
SUPER_PROFILE = [(FRONT_U, 1.20), (FRONT_U, ROOF_Z), (5.30, ROOF_Z), (REAR_U, 1.45), (REAR_U, 1.20)]
GUARD_PROFILE = [(0.0, 1.02), (0.28, FENDER_Z - 0.01), (5.20, FENDER_Z - 0.01), (5.47, 1.02), (5.47, 1.04),
                 (5.20, FENDER_Z + 0.01), (0.28, FENDER_Z + 0.01), (0.0, 1.04)]
GUARD_LIP = [(0.28, 1.20), (5.20, 1.20), (5.20, FENDER_Z + 0.01), (0.28, FENDER_Z + 0.01)]

# ---- turret ------------------------------------------------------------------------------------------------------
TURRET_X = 0.0
TURRET_U = 2.75
TURRET_Z = 1.62
TURRET_TOP = 2.17
# turret (side/top/front views): front plate leaning back, sides 0.82 m at the ring and 0.63 m at the roof, roof
# rising from 2.09 m at the front plate to 2.17 m; behind the side hatches the sides converge to the narrow rear
# plate under the overhanging cupola (top view)
TURRET_STATIONS = [(1.70, 0.74, 1.77, 0.60, 2.09), (2.40, 0.82, 2.40, 0.63, 2.165), (3.05, 0.82, 3.05, 0.63, TURRET_TOP),
                   (3.45, 0.50, 3.45, 0.40, TURRET_TOP)]
# stowage bin on the turret rear (side view u 3.36-4.02, bottom 1.73 m; top view rounded, 1.0 m wide)
TURRET_BIN_Z = 1.73
TURRET_BIN = [(3.30, 0.52, 3.30, 0.50, 2.15), (3.90, 0.50, 3.90, 0.48, 2.15), (4.02, 0.32, 4.0, 0.30, 2.14)]
BORE_X = 0.017
GUN_Z = 1.88
CUP_U, CUP_X = 3.10, 0.0


def wheel_info(scale):
    return c.wheel_info(sys.modules[__name__], scale)


def build(v):
    S = sys.modules[__name__]
    p3.hull(v, S)
    c.running_gear(v, S, bogies=False)
    p3.torsion_suspension(v, S)
    turret(v, S)
    fittings(v, S)
    if DETAIL:
        from . import ger_pz3l_detail

        ger_pz3l_detail.build(v, S)
    p3.rig(v, S)


def turret(v, S):
    p3.turret(v, S)
    dz = TURRET_TOP - 2.305  # the Pz IV F/G cupola (same cast cupola), lowered onto this roof
    prof = [(0.0, 2.305), (0.40, 2.305), (0.40, 2.314), (0.378, 2.316), (0.392, 2.335), (0.395, 2.355), (0.395, 2.418),
            (0.386, 2.432), (0.372, 2.432), (0.372, 2.518), (0.36, 2.529), (0.0, 2.529)]
    c.cupola_early(v, S, CUP_X, CUP_U, TURRET_TOP, [(r, z + dz) for r, z in prof], (0.329, 2.529 + dz, 2.60 + dz),
                   slit_z=2.385 + dz)
    c.turret_side_fittings(v, S, visor=getattr(S, "TURRET_SIDE_VISOR", None), hatch=(2.57, 2.88, 2.89, 3.20, 1.74, 2.13),
                           hatch_visor=[(2.66, 2.80, 1.88, 2.00), (2.97, 3.10, 1.88, 2.00)], pistol=None,
                           rear_port=None, hinge_z=(1.85, 1.95, 2.05))
    # mantlet with its 20 mm spaced plate (side view u 1.35-1.72, z 1.64-2.08; front view x -0.20..+0.23)
    S.gun(v, S)


def gun(v, S):
    """5 cm KwK 39 L/60 (side view): mantlet u 1.35-1.75 (z 1.64-2.08, front view x -0.20..+0.23), sleeve r 0.08 m
    to u 0.94, barrel to the muzzle at u -0.95."""
    face = getattr(S, "MANTLET_FACE_U", 1.35)
    p3.mantlet_box(v, S, face, 1.75, -0.20, 0.23, 1.64, 2.08)
    p3.gun(v, S, [(0.08, face), (0.08, 0.94), (0.05, 0.94), (0.05, 0.40), (0.042, 0.40), (0.040, -0.95)], -0.95, face)


def fittings(v, S):
    if getattr(S, "VORPANZER", True):
        vorpanzer(v, S)
    else:
        p3.front_plate_fittings(v, S, FRONT_U, 0.48, -0.64, 1.41)
    hull_fittings(v, S)


def vorpanzer(v, S):
    # spaced armour plate in front of the superstructure front (side view u 1.03-1.06, z 1.18-1.63; front view
    # x +-0.94), with the driver's visor and the hull MG ball mount coming through it
    plate = [(VORPANZER_U - 0.012, 1.18), (VORPANZER_U + 0.012, 1.18), (VORPANZER_U + 0.012, 1.63),
             (VORPANZER_U - 0.012, 1.63)]
    v.add("vorpanzer", geo.prism_x(c.P(S, plate), -0.94, 0.94), chamfer=0.006)
    for side in (1, -1):
        for z in (1.25, 1.55):  # spacer bars to the front plate
            v.add(f"vorpanzer_spacer_{side}_{z}", geo.box(side * 0.80, Y((VORPANZER_U + FRONT_U) / 2), z, 0.05,
                                                          FRONT_U - VORPANZER_U, 0.05), kind="paint")
    p3.front_plate_fittings(v, S, VORPANZER_U - 0.012, 0.48, -0.64, 1.41)


def hull_fittings(v, S):
    # glacis: two brake access hatches
    for side in (1, -1):
        v.add(f"brake_hatch_{side}", geo.box(side * 0.48, Y(0.70), 1.17, 0.50, 0.55, 0.03), kind="paint",
              chamfer=0.01)
    # engine deck (top view): two pairs of access hatches
    p3.deck(v, S, [(3.63, 4.32, -0.85, -0.15), (3.63, 4.32, 0.15, 0.85), (4.66, 5.23, -0.92, -0.21),
                   (4.66, 5.23, 0.17, 0.91)])
    c.headlights(v, S, ((1, 1.32, 1.36), (-1, -1.32, 1.36)), u=0.45)
    c.tow_shackles(v, S, 0.70, 0.62, x=0.55)
    if getattr(S, "DEEP_WADING_MUFFLER", False):
        p3.deep_wading_muffler(v, S)
    else:
        c.rear_mufflers(v, S, main=(0.0, 0.14, 0.82, 0.16, 1.10), aux=None)
    v.locator("left_tracks", (TRACK_X, Y(5.10), 0.0), "tank_base")
    v.locator("right_tracks", (-TRACK_X, Y(5.10), 0.0), "tank_base")
