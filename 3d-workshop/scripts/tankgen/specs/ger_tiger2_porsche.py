"""Panzerkampfwagen Tiger Ausf. B (Tiger II, Sd.Kfz. 182) with the early (Porsche) turret, 1944.

Drawings: the hull and running gear are the Henschel-turret sheet's (ger_tiger2_henschel, the-blueprints.com ID
63811; the hull did not change with the turret), checked against the-blueprints.com "Sd.Kfz. 182 Tiger II Pz.Kpfw. VI
King Tiger Ausf.B" (ID 14674, source Dr Dan Saranga, public 500 px preview), which draws the Tiger II with the
Porsche turret and is the source of the turret here. Both are used with the project owner's agreement as private
tracing reference only (git-ignored reference/blueprints_nonfree/ger_tiger2_porsche/; see
reference/blueprints/ger_tiger2_porsche/README.md). Sheet 14674 is ~38-40 px/m (2.5 cm per sheet pixel) and its
views differ in scale, so each was calibrated on its own and resampled to 175 px/m:
  side   37.9 px/m along (hull 7.38 m: bow 118.75 -> rear 398.5), 39.9 up (3.09 m to the cupola); datum bow x=548.3,
         ground y=699.6
  top    37.9 along, 39.3 across (3.755 m over the fenders); datum bow x=554.1, centreline y=361.8
  front  39.5 px/m (3.755 m over the fenders), 39.6 up; datum x=478.0, ground y=729.2
  rear   as the front; datum x=480.7, ground y=729.2
Its hull lines lie on the Henschel sheet's within a sheet pixel (overlays), which confirms the shared hull.

Porsche turret, read off sheet 14674 (side/top/front views): the front is ONE curved surface, rolling round from the
roof (u 2.75 at z 2.82) down past the gun (u 2.27 at z 2.35) and back to the turret base (u 2.42 at z 1.99); in plan
the nose is rounded into the side plates; the side plates slope in steeply to a narrow roof (1.36 m), flat on top
(z 2.95) from u 3.4 to 4.6, then falling to the rear plate (u 5.44 at z 2.82, 5.75 at the base); the bulge in the left
side plate under the cupola (u 3.85, x 0.55); the small bell-shaped mantlet (Topfblende) on a flat plate round the
gun (z 2.33).

Photos checked (reference/blueprints/ger_tiger2_porsche/photos/, CREDITS.md there):
  - The Tank Museum Bovington, Tiger II with the Porsche turret (pre-production hull V2), front left and rear left
    (2017): the rounded turret nose rolling from the roof down to the base with the bell mantlet in it; the cupola
    bulge in the left side plate; the steep sides and narrow roof; the hull, wheels and rear as the production tank
    -> t2_turret_porsche (ring stack with the rounded nose, bulge, bell mantlet), hull shared with the Henschel.
  - The same tank (Toshonenov, 2017), front left: confirms the curved nose and the roof line.
  No free wartime photo of a Porsche-turret Tiger II turned up; the paint (Dunkelgelb three-colour over Zimmerit) is
  the documented finish of s.Pz.Abt. 503's Porsche-turret tanks in Normandy, July 1944 (the Bovington turret is
  unpainted primer with no Zimmerit, as a pre-production vehicle).
  Pilze crane sockets came in June 1944, after most Porsche turrets were built; none on the Bovington turret, so
  none here.

Coordinates: u = metres back from the bow, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import tiger_common as tc

NAME = "GER_tiger2_porsche"
HULL_L = 7.38
# paint: Dunkelgelb with Olivgrün and Rotbraun over Zimmerit, as s.Pz.Abt. 503 in Normandy, summer 1944
CAMO = "dunkelgelb_1943"
ZIMMERIT = True
CROSS_KINDS = ("paint",)
DETAIL = True

CROSSES = [(1, 3.6 - HULL_L / 2, 1.74), (-1, 3.6 - HULL_L / 2, 1.74)]
CROSS_SIZE = 0.36

TURRET_TYPE = "porsche"
# (z, nose u at the centreline, half-width, rear plate u)
P_RINGS = [(1.99, 2.42, 1.22, 5.75), (2.15, 2.31, 1.17, 5.70), (2.35, 2.27, 1.10, 5.63), (2.55, 2.31, 1.02, 5.55),
           (2.70, 2.42, 0.88, 5.48), (2.82, 2.75, 0.72, 5.44), (2.95, 3.40, 0.68, 4.60)]
GUN_Z = 2.33
SLEEVE = (2.0, 1.45, 0.15)
CUPOLA = ("cast", 3.85, 0.55)
CUPOLA_Z = 2.93
PILZE = False


def Y(u):
    return u - HULL_L / 2


def wheel_info(scale):
    S = sys.modules[__name__]
    tc.init2(S)
    return tc.wheel_info(S, scale)


def build(v):
    S = sys.modules[__name__]
    tc.build_tiger2(v, S)
    if DETAIL:
        from . import tiger2_detail

        tiger2_detail.build(v, S)
