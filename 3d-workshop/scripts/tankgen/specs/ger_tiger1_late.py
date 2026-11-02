"""Panzerkampfwagen VI Tiger Ausf. E (Sd.Kfz. 181), late production, 1944 (Normandy, East Prussia).

Drawing: the Tiger 131 four-view of ger_tiger1_early (School of Tank Technology, January 1944, public domain; same
crops, calibration and datums, see that spec's docstring) for the parts the late Tiger shares: hull, wheel stations,
sprocket and idler positions, turret shell, mantlet and gun (photos below). The late production changes are set from
the photos and the documented production changes (Jentz/Doyle, Panzer Tracts 6-1):
  - steel-rimmed, internally sprung 800 mm road wheels (from February 1944) in TWO layers: the outer-row axles
    carry the outer and the innermost disc, the inner-row axles a pair either side of the guide horns; same eight
    axle stations as the drawing;
  - monocular TZF 9c sight: one aperture left of the gun instead of two (from April 1944);
  - the loader's fixed periscope in the roof front right (from March 1944);
  - three 'Pilze' sockets for the 2-ton jib crane on the roof (from June 1944), replacing the lifting eyes;
  - cast cupola and AA ring (as the mid), no Feifel filters, no smoke dischargers, Zimmerit (to September 1944).

Photos checked (reference/blueprints/ger_tiger1_late/photos/, CREDITS.md there):
  - The Vimoutiers Tiger (s.SS-Pz.Abt. 102, abandoned August 1944; four photos, 2001): the steel wheels with flat
    faces and the outer bolt ring in two layers (left side and front views) -> WHEEL_LAYERS 2, WHEEL_STEEL; ONE sight
    hole left of the gun, the coaxial MG port right -> SIGHT "mono"; the cast cupola; the rear plate with the two
    exhausts and no Feifel filters; the front plate with the visor block and Kugelblende as on Tiger 131. Its side
    fenders, mudguards and Zimmerit are gone (restored monument), so those follow the drawing and the documented
    production standard.
  - Tiger I '221 black', Musée des Blindés Saumur (2022), rear left: the steel-rimmed wheels with bolted faces,
    Zimmerit on the hull and turret sides, the exhausts in their lower guards, the cast cupola, the escape hatch.

Coordinates: u = metres back from the bow, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import tiger_common as tc

NAME = "GER_tiger1_late"
HULL_L = 6.316
# paint: factory Hinterhalt (ambush) scheme of August 1944 over Zimmerit (applied until September 1944)
CAMO = "ambush_1944"
ZIMMERIT = True
CROSS_KINDS = ("paint",)
DETAIL = True

CROSSES = [(1, 3.30 - HULL_L / 2, 1.66), (-1, 3.30 - HULL_L / 2, 1.66)]
CROSS_SIZE = 0.36

CUPOLA = ("cast", 3.60, 0.53)
FEIFEL = False
SMOKE = False
WHEEL_LAYERS = 2
WHEEL_STEEL = True
SIGHT = ("mono", 0.415)
LOADER_PERISCOPE = True
PILZE = True


def Y(u):
    return u - HULL_L / 2


def wheel_info(scale):
    S = sys.modules[__name__]
    tc.init(S)
    return tc.wheel_info(S, scale)


def build(v):
    S = sys.modules[__name__]
    tc.build_tiger1(v, S)
    if DETAIL:
        from . import tiger1_detail

        tiger1_detail.build(v, S)
