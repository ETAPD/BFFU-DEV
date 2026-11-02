"""Bake-only surface detail for the late Pz IV Ausf. G: hull and turret detail as the Ausf. H (same drawing lines,
from ger_pz4h_detail), stiffening lips along the top of this drawing's hull Schürzen plates."""

from .. import details as dt
from ..details import Frame
from . import ger_pz4h_detail as hd
from .ger_pz4g_late import FENDER_Z, SKIRT_SEAMS, SKIRT_TOP, SKIRT_X_TOP, Y

Z = (0, 0, 1)


def build(v):
    hd.front_and_glacis(v)
    hd.roof_and_deck(v)
    hd.rear(v)
    hd.wheels(v)
    hd.turret(v)
    s = SKIRT_SEAMS
    for side in (1, -1):
        for i in range(5):
            u_a, u_b = s[i] + 0.03, s[i + 1] - 0.02
            if i == 0:
                u_a = 1.10
            if i == 4:
                u_b = 4.70
            x = side * (SKIRT_X_TOP + 0.008 * (i % 2) + 0.007)
            hf = Frame((x, 0, 0.0), (0, side, 0), Z, (side, 0, 0))
            a0, a1 = side * Y(u_a), side * Y(u_b)
            v.detail(f"skirt_lip_{side}_{i}", dt.plate(hf, min(a0, a1), SKIRT_TOP - 0.035, max(a0, a1), SKIRT_TOP - 0.005,
                                                       0.008), "skirt")
        v.detail(f"guard_lip_{side}", hd.geo.box(side * 1.46, Y(2.975), FENDER_Z + 0.012, 0.012, 4.95, 0.02))
