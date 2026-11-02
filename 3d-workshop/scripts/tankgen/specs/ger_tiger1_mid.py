"""Panzerkampfwagen VI Tiger Ausf. E (Sd.Kfz. 181), mid production, autumn 1943 - early 1944.

Drawing: the Tiger 131 four-view of ger_tiger1_early (School of Tank Technology, January 1944, public domain; same
crops, calibration and datums, see that spec's docstring). Hull, running gear, turret shell, mantlet and gun are the
same on the mid-production Tiger (photos below), so they come from that drawing unchanged. What changed in production
and is set here from the photos and the documented production changes (Jentz/Doyle, Panzer Tracts 6-1):
  - cast commander's cupola with seven periscopes under an armoured rim and the AA-MG ring (from July 1943),
    replacing the drum cupola; same position (the cupola opening did not move). Its size (0.88 m across at the
    base, 0.20 m high) is read off the photos against the turret roof width;
  - no Feifel air filters (deleted August 1943): the rear plate carries only the two exhaust guards;
  - no NbK 39 smoke dischargers on the turret (deleted June 1943);
  - Zimmerit on the vertical hull and turret armour (from September 1943).
Unchanged: rubber-tyred 800 mm wheels in three layers, binocular sight (two apertures), S-mine dischargers, escape
hatch in the right rear of the turret, KwK 36 L/56 with the double-baffle brake.

Photos checked (reference/blueprints/ger_tiger1_mid/photos/, CREDITS.md there):
  - Tiger I '100', Patriot Museum Kubinka (2017), rear left and left: the low cast cupola; no smoke dischargers on the
    turret front corners; the rear plate with the two tall exhaust guards and no Feifel housings; the three-layer
    rubber-tyred wheels; the side fender strip and turret visor/pistol port as on Tiger 131 -> CUPOLA "cast",
    FEIFEL False, SMOKE False, wheels and hull as the early drawing.
  - Tiger I '221 black', Musée des Blindés Saumur (2022), front left: a late Tiger (steel wheels, see
    ger_tiger1_late), used here only for what the mid shares with it: Zimmerit over the hull front, sides and turret,
    the cast cupola, the front plate with visor and Kugelblende as on Tiger 131 -> ZIMMERIT.
  - Panzermuseum Munster Tiger I (2022): Zimmerit and rubber-tyred wheels (overall shape only).
  - Bundesarchiv Bild 101I-299-1804-04, northern France, 21 March 1944 (Tiger '131' of the LSSAH): a period
    mid-production Tiger with the rubber-tyred wheels and Zimmerit, no Feifel filters.

Coordinates: u = metres back from the bow, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import tiger_common as tc

NAME = "GER_tiger1_mid"
HULL_L = 6.316
# paint: Dunkelgelb with Olivgrün and Rotbraun sprayed by the units (from February 1943), over Zimmerit
CAMO = "dunkelgelb_1943"
ZIMMERIT = True
CROSS_KINDS = ("paint",)
DETAIL = True

CROSSES = [(1, 3.30 - HULL_L / 2, 1.66), (-1, 3.30 - HULL_L / 2, 1.66)]
CROSS_SIZE = 0.36

CUPOLA = ("cast", 3.60, 0.53)
FEIFEL = False
SMOKE = False


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
