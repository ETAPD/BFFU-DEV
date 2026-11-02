"""Panzerkampfwagen V Panther Ausf. G (Sd.Kfz. 171), 1944 production with the rounded mantlet.

Drawing: the-blueprints.com "Sd.Kfz. 171 Pz.Kpfw.V Ausf.G Panther" (ID 72512, source Dr Dan Saranga), the public
500 px preview, used with the project owner's agreement as private tracing reference only (kept in the git-ignored
reference/blueprints_nonfree/ger_panther_g/, never committed; see reference/blueprints/ger_panther_g/README.md).
No free-licence Panther drawing exists (Commons has only single-profile and turret sketches; see VARIANTS.md).
The preview is ~54 px/m (1.9 cm per sheet pixel) and its views differ slightly in scale, so each was calibrated on
its own and resampled to 175 px/m:
  side   54.0 px/m along (hull 6.87 m: bow 116.7 -> stowage boxes 488), 53.5 px/m up (2.99 m to the AA ring);
         datum bow x=418.2, ground y=642.5
  top    53.9 px/m along, 54.5 px/m across (3.27 m over the tracks); datum bow x=402.7, centreline y=347.9
  front  55.4 px/m across (3.27 m over the tracks), 53.4 px/m up (deck, cupola as the side view); datum x=363.8,
         ground y=715.1
  rear   as the front; datum x=359.7, ground y=715.1
The gun as drawn reaches 8.9 m overall (2 % long); the muzzle is placed at the documented 8.66 m.

Photos checked (PROCESS.md step 5; reference/blueprints/ger_panther_g/photos/, CREDITS.md there):
  - Musée des Blindés Saumur, Panther G "332" (MAN, July 1944), front-left: no driver's visor in the glacis,
    Kugelblende right, headlight on the left glacis corner, front mudguards over the tracks; the rounded mantlet
    (no chin) as one curved face with the gun 'pot' sleeve, as wide as the turret front -> MANTLET half-width 0.60,
    HULL_MG "ball", DRIVER_VISOR False, headlight moved to the glacis corner.
  - Kubinka Panther G (two photos): the first road wheel behind the sprocket is in the inner row, the second in the
    outer row, the rearmost (by the idler) outer; the top run lies on the road wheels (no return rollers); the
    straight one-piece upper side plate with the sponson overhang -> INNER_U / OUTER_U as drawn, no SIDE_STEP.
  - Overloon War Museum Panther G, front: turret front plate with the mantlet and cupola; cast cupola with
    periscope hoods -> CUPOLA "cast".
  - Wartime: the Panther G captured at Pompey, 13 September 1944 (print of 1946): late-1944 G with the rounded
    mantlet.
  Bovington's Panther G (assembled in 1945) is the late G with flame dampers and is used for ger_panther_g_late.
  No free photos of the Munster or Fort Benning Panthers turned up on Commons (Munster has an Ausf. A and an F
  turret; nothing for Fort Benning), so those collections were not checked.
  Not modelled from photos alone: Zimmerit (the Saumur G has it, July 1944) is left off because this spec stands
  for autumn 1944 production in the Hinterhalt scheme, after Zimmerit was dropped in September 1944.

Coordinates: u = metres back from the bow, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import panther_common as pc

NAME = "GER_panther_g"
HULL_L = 6.87
# paint: factory-applied Hinterhalt (ambush) scheme of autumn 1944; Zimmerit was dropped in September 1944
CAMO = "ambush_1944"
ZIMMERIT = False
CROSS_KINDS = ("paint",)
DETAIL = True

CROSSES = [(1, 3.55 - HULL_L / 2, 1.62), (-1, 3.55 - HULL_L / 2, 1.62)]  # on the upper side plates
CROSS_SIZE = 0.40

# Ausf. G: one-piece side plates at 29 deg, no driver's visor, Kugelblende, cooled exhausts, rounded mantlet
HULL_MG = "ball"
DRIVER_VISOR = False
EXHAUST = "cooled"
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
        from . import ger_panther_g_detail

        ger_panther_g_detail.build(v, S)
