"""Bake-only surface detail for the early Pz IV Ausf. G. The hull is the H's (same drawing lines), so its front,
glacis, roof, deck, rear and wheel detail come from ger_pz4h_detail; the turret detail is traced here: cupola ring
bolts, roof seam bolts, lifting hooks, mantlet bolts, hatch handles."""

import math

from .. import details as dt
from ..details import Frame
from . import ger_pz4h_detail as hd
from .ger_pz4g import CUP_U, CUP_X, FENDER_Z, ROOF_FRONT_Z, TURRET_TOP, TURRET_X, Y

X, Z = (1, 0, 0), (0, 0, 1)


def build(v):
    hd.front_and_glacis(v)
    hd.roof_and_deck(v)
    hd.rear(v)
    hd.wheels(v)
    turret(v)
    for side in (1, -1):
        v.detail(f"guard_lip_{side}", hd.geo.box(side * 1.46, Y(2.975), FENDER_Z + 0.012, 0.012, 4.95, 0.02))


def turret(v):
    tx = TURRET_X
    ring = Frame((CUP_X, Y(CUP_U), TURRET_TOP), X, (0, 1, 0), Z)
    v.detail("cupola_ring_bolts", dt.bolts(ring, dt.circle(0, 0, 0.385, 16), 0.011))
    lid = Frame((CUP_X, Y(CUP_U), 2.60), X, (0, 1, 0), Z)
    for s in (1, -1):
        v.detail(f"cupola_hatch_handle_{s}", dt.handle(lid, 0.0, s * 0.12, 0.14, 0.03))
    slope = math.atan2(TURRET_TOP - ROOF_FRONT_Z, 3.02 - 2.17)
    front_roof = Frame((tx, Y(2.17), ROOF_FRONT_Z), X, (0, math.cos(slope), math.sin(slope)),
                       (0, -math.sin(slope), math.cos(slope)))
    for a in (0.68, -0.68):
        v.detail(f"turret_hook_{a}", dt.lifting_hook(front_roof, a, 0.10))
    roof = Frame((tx, Y(3.02), TURRET_TOP), X, (0, 1, 0), Z)
    v.detail("turret_roof_bolts", dt.bolts(roof, dt.line(-0.60, 0.0, 0.60, 0.0, 11), 0.010))
    gx = 0.056
    mf = Frame((gx, Y(1.627), 1.98), X, Z, (0, -1, 0))
    v.detail("mantlet_bolts", dt.bolts(mf, [(-0.22, 0.068), (0.22, 0.068), (-0.22, -0.068), (0.22, -0.068)], 0.02, 0.014),
             "paint_cast")
