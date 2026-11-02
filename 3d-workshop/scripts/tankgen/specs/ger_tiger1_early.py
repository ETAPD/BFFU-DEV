"""Panzerkampfwagen VI Tiger Ausf. E (Sd.Kfz. 181), early production, 1942-43 (Leningrad front, Tunisia).

Drawing: the four-view of Tiger 131 (Henschel, February 1943, captured in Tunisia April 1943) in the Military College
of Science, School of Tank Technology report of January 1944, public domain (Wikimedia Commons "Tiger Side View
Left.png", "Tiger Top View.png", "Tiger Front View.png", "Tiger Rear View.png"; credits in README). A period line
drawing measured from the vehicle, with its own dimension lines, which every view was calibrated against and
resampled to 175 px/m (reference/blueprints/ger_tiger1_early/side.png etc.; the originals are kept as src_*.png):
  side   276 px/m (27 ft 9 in = 8.458 m muzzle to rear: 275.5; ground contact 11 ft 10 1/8 in = 3.610 m between the
         first and last axle: 276.7); datum bow (front of the side-plate horns) x=394.4, ground y=682.2
  top    280 px/m along (bow to rear as the side view), 284 across (3.73 m over the mudguards); datum bow x=408.8,
         centreline y=374.3 (gun axis)
  front  280.2 px/m across (track 2 ft 4.5 in = 0.724 m: 280.2; between the tracks 6 ft 10 5/8 in: 280.3;
         overall 12 ft 3 in: 279.2), 281.8 up (hull roof 5 ft 10 in); datum x=408.7, ground y=700.8
  rear   280 across (tracks), 281 up (turret roof 8 ft 6.5 in: 279.6, cupola 9 ft 4.25 in: 282.4); datum x=340.9,
         ground y=702.5
The drawing shows exactly this variant: the drum cupola with vision slits, Feifel air filters on the rear, three
NbK 39 smoke dischargers on each turret front corner, S-mine dischargers on the front deck corners, rubber-tyred
800 mm wheels interleaved in three layers, the binocular sight's two apertures in the mantlet, the 8.8 cm KwK 36
L/56 with its double-baffle brake.

Photos checked (reference/blueprints/ger_tiger1_early/photos/, CREDITS.md there):
  - Tiger 131, The Tank Museum Bovington (2017), left side: the hull side is ONE flat vertical plate from the deck to
    the sponson; the two lines the drawing shows falling to the rear are a fender strip sloping out and down from a
    bolted line (not the sponson floor) -> t1_fenders; tow cable along the top of the side plate -> tow_cable; the
    turret's one-piece horseshoe side with the round visor ahead and the pistol port behind, the bin on the rear.
  - Tiger 131, front left: the full-width 10-deg front plate with the Kugelblende right and the visor block left;
    the near-flat glacis between the side-plate horns, which run past the nose with the tow eyes; the shackles on
    the nose plate; front mudguards level with the glacis; the mantlet as wide as the turret front, its face curved
    and its ends turned back, the two binocular sight holes left of the gun, the big bolted sleeve collar
    -> t1_mantlet (curved face about the trunnion, ends, boss, collar), SIGHT "bino"; three smoke-discharger tubes
    fanned out on each turret front corner -> SMOKE.
  - Tiger 131, rear right: two tall sheet-metal exhaust guards; Feifel filter housings on the upper rear corners
    with two cans over conical hoppers and a pipe into the hull; hinged rear mudguard flaps sloping over the
    idlers; the large round escape hatch in the right rear of the turret -> t1_rear, rear_mudguard,
    ESCAPE_HATCH. (The track links on the nose and turret sides are field stowage and are not modelled.)
  - Tiger 131 (Tank Museum photo), front: confirms the front plate, mantlet and cupola; wheels in three layers
    (track view: the outer wheels on the odd axles, the second layer between, the third behind).
  - Bundesarchiv Bild 101I-698-0038-04, Russland-Nord, June 1943 (Tiger "231" of s.Pz.Abt. 502, Leningrad front):
    period early Tiger with the drum cupola, Feifel filters and smoke dischargers in Dunkelgrau.

Coordinates: u = metres back from the bow, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import tiger_common as tc

NAME = "GER_tiger1_early"
HULL_L = 6.316
# paint: Braun 8020 with Grau 7027 patches, as Tiger 131 in Tunisia (s.Pz.Abt. 504, spring 1943); no Zimmerit yet
CAMO = "afrika_1942"
ZIMMERIT = False
CROSS_KINDS = ("paint",)
DETAIL = True

CROSSES = [(1, 3.30 - HULL_L / 2, 1.66), (-1, 3.30 - HULL_L / 2, 1.66)]  # on the hull side plates (photo)
CROSS_SIZE = 0.36


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
