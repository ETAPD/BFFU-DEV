"""Panzerkampfwagen IV Ausf. G (Sd.Kfz. 161/1), late production, spring 1943: 7.5 cm KwK 40 L/48 with the
double-baffle brake, hull and turret Schürzen, the thicker cast cupola of the Ausf. H.

Traced from the right-hand (late) vehicle of MasterJVN's "PzIV-012-G-Variantes.jpg" (Wikimedia Commons, CC BY 4.0),
175 px/m (3 m scale bar 525 px). Crops in reference/blueprints/ger_pz4g_late/, datums: side bow x=218, ground
y=474.5; top bow x=218, centreline y=311; front centreline x=314.5, ground y=488; rear centreline x=300, ground y=488.

An overlay of the Ausf. H model on this drawing lies on the same hull, running gear, turret, turret Schürzen, gun,
Schürzen rail and brackets, so those are ger_pz4h's builders, unchanged. Unlike the H sheet this drawing shows the
hull Schürzen plates, and they differ from the H model's: traced here (5 plates, u 0.51-5.59, top 1.73 m, bottom
0.43 m, cut lower corners, hanging slightly out at the top in the front view). The turret roof still has the signal
port (deleted on the H).

Coordinates: u = metres back from the bow tip, z = metres above ground, x = metres to the vehicle's left.
"""

from .. import geo
from . import ger_pz4h as h
from . import pz4_common as c
from .ger_pz4h import (CROSS_SIZE, DECK_END_U, DECK_PROFILE, DECK_X, FENDER_Z, FRONT_U, GLACIS, GUARD_BOX,  # noqa
                       GUARD_INNER, GUARD_LIP, GUARD_PROFILE, GUN_Z, HULL_L, IDLER, LOWER_PROFILE, LOWER_X, REAR_U,
                       ROLLER_R, ROLLER_Z, ROLLERS_U, ROOF_FRONT_Z, ROOF_Z, SPROCKET, SPROCKET_TEETH, SUPER_X,
                       TRACK_PITCH, TRACK_T, TRACK_W, TRACK_X, TURRET_TOP, TURRET_U, TURRET_X, TURRET_Z, WHEEL_R,
                       WHEEL_Z, WHEELS_U, Y)

NAME = "GER_pz4g_late"
# paint: Dunkelgelb factory base from February 1943 with Olivgrün and Rotbraun sprayed in the field; no Zimmerit
# (late G production ended June 1943, Zimmerit came in September); Balkenkreuze on the middle hull Schürzen plate
CAMO = "dunkelgelb_1943"
ZIMMERIT = False
CROSS_KINDS = ("skirt",)
CROSSES = [(1, Y(3.18), 1.12), (-1, Y(3.18), 1.12)]
DETAIL = True

# hull Schürzen (side view): plate seams, top and bottom edges
SKIRT_SEAMS = [0.506, 1.58, 2.677, 3.694, 4.643, 5.592]
SKIRT_TOP, SKIRT_BOTTOM = 1.73, 0.432
SKIRT_X_TOP, SKIRT_X_BOTTOM = 1.64, 1.57  # front view: plates hang out at the top


def wheel_info(scale):
    import sys

    return c.wheel_info(sys.modules[__name__], scale)


def build(v):
    import sys

    S = sys.modules[__name__]
    h.hull(v, S)
    c.running_gear(v, S)
    h.turret(v, S)
    # signal port lid in the flat turret roof, left of the cupola (top view u 3.13, 0.54 m left)
    lid = geo.lathe([(0.0, 0.0), (0.075, 0.0), (0.075, 0.022), (0.065, 0.032), (0.0, 0.032)], 14, axis="Z")
    v.add("signal_port", geo.move(lid, x=0.537, y=Y(3.126), z=TURRET_TOP), kind="paint_cast", bone="turret",
          smooth_angle=50)
    h.fittings(v, S)
    schuerzen(v, S)
    if DETAIL:
        from . import ger_pz4g_late_detail

        ger_pz4g_late_detail.build(v)
    c.rig(v, S)


def schuerzen(v, S):
    """Rail and brackets as the H (top view), plates traced from this drawing (side view): leading plate with its
    top edge rising from 1.58 m at the front to 1.73 m and its lower front corner cut from 0.70 m at u 0.51 to the
    bottom at u 1.55; trailing plate with the top falling from u 4.70 to 1.53 m and the lower rear corner cut up to
    0.66 m. Plates overlap 1 cm at the seams, alternately in front."""
    import math

    s = SKIRT_SEAMS
    top, bot = SKIRT_TOP, SKIRT_BOTTOM
    plates = [[(s[0], 0.695), (1.55, bot), (s[1] + 0.01, bot), (s[1] + 0.01, top), (s[0], 1.583)]]
    for i in (1, 2, 3):
        plates.append([(s[i] - 0.01, bot), (s[i + 1] + 0.01, bot), (s[i + 1] + 0.01, top), (s[i] - 0.01, top)])
    plates.append([(s[4] - 0.01, bot), (4.66, bot), (s[5], 0.655), (s[5], 1.531), (4.70, top), (s[4] - 0.01, top)])
    tilt = math.atan2(SKIRT_X_TOP - SKIRT_X_BOTTOM, top - bot)
    rail_top = [(0.50, 1.69), (1.08, 1.745), (4.70, 1.745), (5.61, 1.545)]
    rail = rail_top + [(u, z - 0.034) for u, z in reversed(rail_top)]
    for side in (1, -1):
        xr = side * (SKIRT_X_TOP - 0.04)
        v.add(f"skirt_rail_{side}", geo.prism_x(c.P(S, rail), xr - 0.02, xr + 0.02), kind="paint", chamfer=0.004)
        for b, u in enumerate((1.35, 2.44, 3.76, 4.91)):
            v.add(f"skirt_bracket_{side}_{b}", geo.box(side * (SUPER_X + SKIRT_X_TOP - 0.04) / 2, Y(u), 1.70,
                                                       SKIRT_X_TOP - 0.04 - SUPER_X, 0.05, 0.04), kind="paint",
                  chamfer=0.006)
        for i, pl in enumerate(plates):
            x = SKIRT_X_TOP + 0.008 * (i % 2)
            bm = geo.prism_x(c.P(S, pl), -0.006, 0.006)
            geo.rotate(bm, side * tilt, "Y", origin=(0, 0, top))  # bottom swings in towards the hull
            v.add(f"skirt_{side}_{i}", geo.move(bm, x=side * x), kind="skirt", smooth_angle=30, chamfer=0.005)
