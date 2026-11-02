"""Bake-only surface detail for the Pz III Ausf. L: bolts on the spaced armour and the front plate, deck hatch
rivets and handles, turret roof bolts, cupola ring bolts, wheel hub bolts."""

import math

from .. import details as dt
from ..details import Frame
from .ger_pz3l import (CUP_U, CUP_X, DECK_Z, IDLER, SPROCKET, TRACK_X, TURRET_TOP, VORPANZER_U, WHEEL_Z, WHEELS_U,
                       Y)

X, Z = (1, 0, 0), (0, 0, 1)


def build(v, S=None):
    front = Frame((0, Y(VORPANZER_U - 0.012), 1.18), (1, 0, 0), Z, (0, -1, 0))
    v.detail("vorpanzer_bolts", dt.bolts(front, dt.line(-0.88, 0.40, 0.88, 0.40, 13) + dt.line(-0.88, 0.05, 0.88, 0.05, 13),
                                         0.013))
    deck = Frame((0, Y(4.0), DECK_Z + 0.03), X, (0, 1, 0), Z)
    for k, (a0, b0, a1, b1) in enumerate(((-0.85, -0.37, -0.15, 0.32), (0.15, -0.37, 0.85, 0.32), (-0.92, 0.66, -0.21, 1.23),
                                          (0.17, 0.66, 0.91, 1.23))):
        v.detail(f"deck_rivets_{k}", dt.rivets(deck, dt.rect_border(a0, b0, a1, b1, 0.08, 0.02), 0.009))
        v.detail(f"deck_handle_{k}", dt.handle(deck, (a0 + a1) / 2, (b0 + b1) / 2, 0.14, 0.035))
    roof = Frame((0, Y(2.4), TURRET_TOP), X, (0, 1, 0), Z)
    v.detail("turret_roof_bolts", dt.bolts(roof, dt.line(-0.55, 0.0, 0.55, 0.0, 9), 0.010))
    ring = Frame((CUP_X, Y(CUP_U), TURRET_TOP), X, (0, 1, 0), Z)
    v.detail("cupola_ring_bolts", dt.bolts(ring, dt.circle(0, 0, 0.385, 16), 0.011))
    for u in WHEELS_U:
        for side in (1, -1):
            c = (side * TRACK_X, Y(u), WHEEL_Z)
            v.detail(f"hub_bolts_{u}_{side}", dt.wheel_hub_bolts(c, side, 0.06, 8, 0.011, 0.008, side * 0.128),
                     "rubber_wheel")
    for label, (u, z, r), n in (("sprocket", SPROCKET, 10), ("idler", IDLER, 8)):
        for side in (1, -1):
            c = (side * TRACK_X, Y(u), z)
            v.detail(f"{label}_bolts_{side}", dt.wheel_hub_bolts(c, side, r * 0.38, n, 0.013, 0.01, side * 0.16),
                     "wheel_plain")
