"""Panzerkampfwagen IV Ausf. J (Sd.Kfz. 161/2), spring 1944 production: 7.5 cm KwK 40 L/48, no auxiliary engine.

Traced from the right-hand (Ausf. J, "Prod. Spring 1944") vehicle of MasterJVN's comparison sheet "PzIV-011-HJ.jpg"
(Wikimedia Commons, CC BY 4.0), drawn at ~58 px/m (1 m black bars 59 px) and resampled by 175/58.3 to 175 px/m (top
view hull width then 504 px = 2.88 m). Crops in reference/blueprints/ger_pz4j/, datums: side bow x=210, ground
y=468; top bow x=210, centreline y=282; front centreline x=286, ground y=494; rear centreline x=270.5, ground y=494.
Like the H sheet, it draws the Schürzen rail but not the plates.

The Ausf. H model lies on the J's hull, running gear, turret with its Schürzen, cupola and gun, so the J is built from
ger_pz4h. Traced here: no auxiliary (turret traverse generator) muffler at the rear (marked deleted on the sheet's
rear view; the J traversed by hand). This spring-1944 J still has four return rollers on the drawing: the three-roller
running gear came with the late J (from about December 1944), for which no free drawing exists, so it is not modelled.

Coordinates: u = metres back from the bow tip, z = metres above ground, x = metres to the vehicle's left.
"""

import sys

from . import ger_pz4h as h
from . import pz4_common as c
from .ger_pz4h import *  # noqa: F401,F403  (dimensions)

NAME = "GER_pz4j"
# paint: late summer 1944 factory ambush (Hinterhalt) pattern, hard-edged Olivgrün and Rotbraun over Dunkelgelb with
# contrasting dots, factory Zimmerit (applied until September 1944), Balkenkreuze on the Schürzen
CAMO = "ambush_1944"
ZIMMERIT = True
CROSS_KINDS = ("skirt",)
AUX_MUFFLER = None


def wheel_info(scale):
    return c.wheel_info(sys.modules[__name__], scale)


def build(v):
    S = sys.modules[__name__]
    h.hull(v, S)
    c.running_gear(v, S)
    h.turret(v, S)
    h.fittings(v, S)
    h.schuerzen(v, S)
    if h.DETAIL:
        from . import ger_pz4h_detail

        ger_pz4h_detail.build(v)
    c.rig(v, S)
