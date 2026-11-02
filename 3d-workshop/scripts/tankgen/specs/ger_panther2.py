"""Panther II prototype (Pz.Kpfw. V Panther II), 1945: the one completed Panther II hull, with the Panther Ausf. G
turret it carries today (the US Army fitted it after the war as a placeholder; the hull was captured turretless).

Drawings: the-blueprints.com "Sd.Kfz. 171 Pz.Kpfw. V Panther II" sheets by Dr Dan Saranga, public 500 px previews,
used with the project owner's agreement as private tracing reference only (git-ignored
reference/blueprints_nonfree/ger_panther2/; see reference/blueprints/ger_panther2/README.md):
  side   ID 31013 (side profile), 50.6 px/m (hull 6.87 m as the Panther: bow 130 -> rear 477.5; 2.99 m to the
         cupola agrees); datum bow x=489.6, ground y=624.5
  front  ID 31012 (side, front, rear), 52.0 px/m across (3.27 m over the tracks), 48.5 px/m up (cupola at 2.99 m as
         the side view); datum x=359.7, ground y=599.3
  rear   ID 31012, as the front; datum x=351.3, ground y=599.3
  top    ID 15894 (four-view, ~37 px/m: 36.8 along, 38.2 across); datum bow x=491.8, centreline y=360.7
The project owner agreed to use them although they are shaded colour profiles (PROCESS.md asks for line drawings):
their outlines are clear, but the camouflage hides internal lines, and the top view is small (2.7 cm per sheet
pixel). No line drawing of the Panther II exists on Commons or elsewhere. These sheets show the PLANNED Panther II
with the Schmalturm (ger_panther2_schmalturm); this spec takes the hull and running gear from them and the turret
from ger_panther_g (the photos show the surviving hull with exactly that turret).

Documented: all-steel 800 mm road wheels shared with the Tiger II, overlapping but not interleaved; seven per
side (four outer, three inner); overall size very close to the Panther G. Track width taken as the Panther's 660 mm.

Photos checked (reference/blueprints/ger_panther2/photos/, CREDITS.md there):
  - The surviving Panther II, US Army Armor & Cavalry Collection, Fort Benning (2023), front left: the Panther
    glacis with the Kugelblende and no driver's visor, the headlight on the left front mudguard (not on the glacis),
    curved front mudguards, the Tiger II-style all-steel overlapping wheels and track, the Ausf. G turret with the
    rounded mantlet and KwK 42 -> HULL_MG, DRIVER_VISOR False, HEADLIGHT, WHEEL_STEEL / overlapped, G turret.
  - The same tank at the Patton Museum, Fort Knox (2007), front right: confirms the hull front and the G turret.
  No free rear or side photo turned up, so the rear (plain exhausts, stowage boxes) follows the 31012 rear view.

Coordinates: u = metres back from the bow, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import panther_common as pc

NAME = "GER_panther2"
HULL_L = 6.87
# paint: red-oxide primer overall, as a 1945 factory prototype; its wartime finish is not documented
CAMO = "primer_1945"
ZIMMERIT = False
CROSS_KINDS = ("paint",)
DETAIL = True

CROSSES = []

# Panther II hull and running gear (side/front/top views of the sheets), shared with ger_panther2_schmalturm
P2_HULL = dict(
    DECK_Z=1.90, GLACIS_TOP_U=1.43, SPONSON_Z=(1.46, 1.31), DECK_END_U=6.70,
    WHEEL_R=0.40, WHEEL_Z=0.48, WHEEL_LAYOUT="overlapped", WHEEL_STEEL=True,
    OUTER_U=[1.27, 2.60, 3.92, 5.25], INNER_U=[1.93, 3.26, 4.59],  # 0.663 m pitch, frontmost in the outer row
    SPROCKET=(0.46, 0.84, 0.38), SPROCKET_TEETH=17, IDLER=(6.05, 0.65, 0.33),
    HULL_MG="ball", DRIVER_VISOR=False, HEADLIGHT=(1.32, 0.55, 1.74), EXHAUST="plain",
)
globals().update(P2_HULL)

# Ausf. G turret (ger_panther_g / panther_common defaults), raised with the 3 cm higher roof
_dz = DECK_Z - 1.87
TURRET_STATIONS = [(ub, wb, ut, wt, z + _dz) for ub, wb, ut, wt, z in pc.DEFAULTS["TURRET_STATIONS"]]
GUN_Z = pc.DEFAULTS["GUN_Z"] + _dz
_m = pc.DEFAULTS["MANTLET"]
MANTLET = dict(_m, rc=(_m["rc"][0], _m["rc"][1] + _dz), z0=_m["z0"] + _dz, z1=_m["z1"] + _dz)
CUPOLA = ("cast", 4.01, 0.31)


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
        from . import ger_panther2_detail

        ger_panther2_detail.build(v, S)
