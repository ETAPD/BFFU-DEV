"""Panzerkampfwagen IV Ausf. F (later F1, Sd.Kfz. 161), April 1941 - March 1942: 7.5 cm KwK 37 L/24.

Traced from the middle (Ausf. F) vehicle of MasterJVN's comparison sheet "PzIV-011-EFG.jpg" (Wikimedia Commons,
CC BY 4.0). That sheet is the same author's drawings at about 67 px/m (its 1 m black bars are 68 px); the crops in
reference/blueprints/ger_pz4f1/ are resampled by 175/67.3 to 175 px/m (the 3 m scale line then measures 525 px).
Datums: side bow x=47, ground y=513; top bow x=47, centreline y=275; front centreline x=298, ground y=480; rear
centreline x=274.5, ground y=480. At this resolution one pixel of the sheet is 1.5 cm, so small parts were checked
against the Ausf. G sheet (175 px/m), which this sheet's G panel matches.

The F introduced the 50 mm single-plate superstructure front with the Kugelblende 50, the 40 cm tracks with the new
sprocket and idler and the two-leaf turret side hatches, all carried on by the F2 and early G: the overlay of the
early-G model (ger_pz4g) lies on this drawing's hull, running gear, turret shell, cupola, side fittings and vision
ports, so those are ger_pz4g's builders. Traced here: the short L/24 (thin barrel to the muzzle at u 0.85, which
stays behind the bow, thick recoil sleeve, collar) with the bore at 2.01 m, no turret stowage bin (the turret outline
ends at u 3.99 in the side view and the rear view shows the plain turret rear), no antenna deflector.

Coordinates: u = metres back from the bow tip, z = metres above ground, x = metres to the vehicle's left.
"""

from . import ger_pz4g as g
from . import pz4_common as c
from .ger_pz4g import (CROSS_KINDS, CROSS_SIZE, CROSSES, CUP_U, CUP_X, DECK_END_U, DECK_PROFILE, DECK_X,  # noqa
                       FENDER_Z, FRONT_U, GLACIS, GUARD_BOX, GUARD_INNER, GUARD_LIP, GUARD_PROFILE, HULL_L, IDLER,
                       LOWER_PROFILE, LOWER_X, REAR_U, ROLLER_R, ROLLER_Z, ROLLERS_U, ROOF_FRONT_Z, ROOF_Z, SPROCKET,
                       SPROCKET_TEETH, SUPER_X, TRACK_PITCH, TRACK_T, TRACK_W, TRACK_X, TURRET_TOP, TURRET_U,
                       TURRET_X, TURRET_Z, WHEEL_R, WHEEL_Z, WHEELS_U, Y)

NAME = "GER_pz4f1"
# paint: Dunkelgrau (RAL 7021) as delivered for Barbarossa and the winter 1941/42; no Zimmerit
CAMO = "panzergrau"
ZIMMERIT = False
DETAIL = True
GUN_Z = 2.01  # bore axis (side view: barrel and sleeve centred on 2.01-2.02 m)
TURRET_BIN = False
MANTLET = {"collar": (0.112, 1.585, 0.07)}  # mantlet body u 1.62-1.90, collar r 0.11 at u 1.55-1.62


def wheel_info(scale):
    import sys

    return c.wheel_info(sys.modules[__name__], scale)


def build(v):
    import sys

    S = sys.modules[__name__]
    g.hull(v, S)
    c.running_gear(v, S)
    g.turret(v, S)
    g.fittings(v, S)
    if DETAIL:
        from . import ger_pz4g_detail

        ger_pz4g_detail.build(v)
    c.rig(v, S)


def gun(v, S):
    """7.5 cm KwK 37 L/24 (side view): barrel 0.126 m with a chamfered muzzle at u 0.846 back to u 1.05, recoil
    sleeve 0.20 m from u 1.12 to the collar (ring at u 1.35), collar 0.22 m at u 1.47-1.55."""
    gx = c.BORE_X
    face_u = 1.55
    muzzle_u = 0.846
    c.gun(v, S, gx, GUN_Z, face_u,
          [(0.10, face_u), (0.10, 1.37), (0.106, 1.37), (0.106, 1.33), (0.10, 1.33), (0.10, 1.12), (0.066, 1.08),
           (0.063, 1.05), (0.063, 0.87), (0.055, muzzle_u)],
          muzzle_u, None)
    v.add("gun_collar", c.geo.move(c.geo.cylinder(0.111, 0.08, 18, axis="Y"), x=gx, y=Y(1.51), z=GUN_Z),
          kind="steel_paint", bone="barrel_base", chamfer=0.006)
