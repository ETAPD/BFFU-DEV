"""Bake-only detail for the late Panther G: as the G (ger_panther_g_detail), plus the three 'Pilze' crane sockets on
the turret roof of the late production."""

import math

from .. import details as dt
from ..details import Frame
from . import ger_panther_g_detail as gd

Z = (0, 0, 1)


def build(v, S):
    gd.build(v, S)
    roof = Frame((S.TURRET_X, S.Y(0.0), S.TURRET_STATIONS[1][4]), (1, 0, 0), (0, 1, 0), Z)
    for k, (x, u) in enumerate(((0.55, 3.20), (-0.55, 3.20), (-0.30, 4.30))):
        v.detail(f"pilz_{k}", dt.bolts(roof, [(x, u)], 0.035, 0.05))
