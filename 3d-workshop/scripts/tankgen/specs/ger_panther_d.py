"""Panzerkampfwagen V Panther Ausf. D (Sd.Kfz. 171), as at Kursk (Operation Zitadelle), July 1943.

Drawing: the-blueprints.com "Sd.Kfz. 171 Pz.Kpfw.V Ausf.D Panther" (ID 72504, source Dr Dan Saranga), the public
500 px preview, used with the project owner's agreement as private tracing reference only (git-ignored
reference/blueprints_nonfree/ger_panther_d/; see reference/blueprints/ger_panther_d/README.md). It is the same
draughtsman's series as the G sheet (72512) and lies on the same hull, running gear and turret lines wherever the
two variants share parts, so the shared construction is panther_common's and only the differences are set here.
Calibration, each view on its own, resampled to 175 px/m:
  side   54.2 px/m (hull 6.87 m: bow 112.5 -> rear 485; 8.66 m to the muzzle and 2.97 m to the cupola agree);
         datum bow x=403.2, ground y=750.3
  top    53.5 px/m along, 54.3 px/m across (3.27 m); datum bow x=391.6, centreline y=350.2
  front  55.8 px/m across (3.27 m over the tracks), 54.2 px/m up; datum x=365.4, ground y=742.3
  rear   55.5 px/m across, 54.2 px/m up; datum x=365.6, ground y=742.3

What the D sheet shows that differs from the G (and is modelled here): the drum cupola with six vision slits,
further forward; the letterbox MG flap (front view x -0.47 m) and the driver's visor (x +0.47 m) on the glacis;
two binocular sight holes left of the gun; smoke dischargers (three a side) at the front of the turret sides; the
bulge in the left turret side under the cupola (top view); the upper hull side plates at 40 deg (roof edge 1.28 m
out); plain exhausts without cooling pipes; no AA ring.

Running gear: this sheet draws the road wheels 1.0 m across (documented 860 mm) and the wheel set 0.13 m further
back than the G sheet, with the sprocket and idler on the same stations. The D and G running gear are the same on
the real vehicles (photos: Breda D, Kubinka G), so the D uses the G sheet's running gear (panther_common defaults).

Photos checked (reference/blueprints/ger_panther_d/photos/, CREDITS.md there):
  - Panther D memorial, Wilhelminapark Breda (the D hull of the Polish 1st Armoured Division memorial), front
    left: the glacis with the driver's visor and the MG flap position, the sloping upper side plates, front
    mudguards, the rounded mantlet with its two sight holes, the interleaved wheels (front wheel inner row)
    -> DRIVER_VISOR, HULL_MG "flap", SIGHT "bino".
  - Bundesarchiv Bild 101III-Merz-023-22, Waffen-SS "Das Reich" Panthers during Zitadelle, July 1943: the
    Kursk-period vehicle in the field (low resolution: confirms the overall shape and the drum-cupola turret
    outline only).
  No free photos of the Kubinka, Munster or Fort Benning D-type Panthers turned up on Commons, so those were not
  checked; the drum cupola and smoke dischargers rest on the drawing (which shows both) and the documented
  production standard (dischargers deleted from June 1943, but the Kursk vehicles were May-June builds).

Coordinates: u = metres back from the bow, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import panther_common as pc

NAME = "GER_panther_d"
HULL_L = 6.87
# paint: Dunkelgelb with Olivgrün/Rotbraun sprayed in the field (Kursk, July 1943); no Zimmerit yet
CAMO = "dunkelgelb_1943"
ZIMMERIT = False
CROSS_KINDS = ("paint",)
DETAIL = True

CROSSES = [(1, 3.55 - HULL_L / 2, 1.62), (-1, 3.55 - HULL_L / 2, 1.62)]
CROSS_SIZE = 0.40

HULL_MG = "flap"
DRIVER_VISOR = True
EXHAUST = "plain"
SMOKE = True
AA_RING = False
SIGHT = ("bino", 0.47)
CUPOLA = ("drum", 4.07, 0.30)
BULGE = True
DECK_X = 1.28  # D/A upper side plates at 40 deg: roof edge 1.28 m out (front view)


def Y(u):
    return u - HULL_L / 2


def wheel_info(scale):
    S = sys.modules[__name__]
    pc.init(S)
    return pc.wheel_info(S, scale)


def build(v):
    S = sys.modules[__name__]
    pc.build(v, S)
    if DETAIL:
        from . import ger_panther_d_detail

        ger_panther_d_detail.build(v, S)
