"""Bake-only surface detail for the Tiger II (both turrets read their own S): interlocked plate joints and weld beads
on the glacis, sides and rear, deck bolts and gratings, hatch hinges, wheel hub and rim bolts, turret welds. It only
lands in the textures, never in the triangle count (Munster and Bovington photos: dovetailed, welded plate joints)."""

import math

from .. import details as dt
from ..details import Frame
from . import tiger_common as tc

X, Z = (1, 0, 0), (0, 0, 1)


def build(v, S):
    hull(v, S)
    deck(v, S)
    wheels(v, S)
    turret(v, S)


def hull(v, S):
    (nu, nz), gu = S.NOSE, S.GLACIS_TOP_U
    gl = Frame.from_points((0, S.Y(nu), nz), (1, S.Y(nu), nz), (0, S.Y(gu), S.DECK_Z), (0, -1, 1))
    length = math.hypot(gu - nu, S.DECK_Z - nz)
    v.detail("glacis_nose_weld", dt.weld_bead(gl, [(-S.LOWER_X, 0.03), (S.LOWER_X, 0.03)]))
    v.detail("glacis_roof_weld", dt.weld_bead(gl, [(-S.DECK_X, length - 0.02), (S.DECK_X, length - 0.02)]))
    bf = (S.SPONSON_Z - nz) / math.sin(math.atan2(S.DECK_Z - nz, gu - nu))
    for side in (1, -1):  # dovetailed side-plate joints up the glacis edges
        v.detail(f"glacis_side_weld_{side}", dt.weld_bead(gl, [(side * (S.LOWER_X - 0.02), 0.04),
                                                               (side * (S.LOWER_X - 0.02), bf),
                                                               (side * (S.SPONSON_X - 0.03), bf),
                                                               (side * (S.DECK_X - 0.02), length - 0.03)]))
        v.detail(f"glacis_dovetails_{side}", dt.plate(gl, side * (S.SPONSON_X - 0.10) - 0.04, bf + 0.12,
                                                      side * (S.SPONSON_X - 0.10) + 0.04, bf + 0.30, 0.012))
    v.detail("glacis_hooks", dt.bolts(gl, [(-0.45, length - 0.35), (0.45, length - 0.35)], 0.03, 0.03))
    for side in (1, -1):
        u0, u1 = tc.t2_glacis_u(S, S.SPONSON_Z) + 0.1, S.DECK_END_U - 0.05
        if side < 0:
            u0, u1 = u1, u0
        p0 = (side * S.SPONSON_X, S.Y(u0), S.SPONSON_Z)
        p1 = (side * S.SPONSON_X, S.Y(u1), S.SPONSON_Z)
        p2 = (side * S.DECK_X, S.Y(u0), S.DECK_Z)
        f = Frame.from_points(p0, p1, p2, (side, 0, 0.4))
        ln, h = math.dist(p0, p1), math.dist(p0, p2)
        v.detail(f"side_top_weld_{side}", dt.weld_bead(f, [(0.0, h - 0.02), (ln, h - 0.02)]))
        v.detail(f"side_clamps_{side}", dt.bolts(f, dt.line(0.4, h * 0.45, ln - 0.4, h * 0.45, 10), 0.018, 0.02))
    zr = (S.DECK_Z + S.REAR_BEAK[1]) / 2
    rp = Frame.from_points((0, S.Y(tc.t2_rear_u(S, S.REAR_BEAK[1])), S.REAR_BEAK[1]),
                           (-1, S.Y(tc.t2_rear_u(S, S.REAR_BEAK[1])), S.REAR_BEAK[1]),
                           (0, S.Y(S.DECK_END_U), S.DECK_Z), (0, 1, 0.3))
    for side in (1, -1):
        v.detail(f"rear_edge_weld_{side}", dt.weld_bead(rp, [(side * (S.SPONSON_X - 0.05), 0.03),
                                                             (side * (S.DECK_X - 0.03), S.DECK_Z - zr)]))


def deck(v, S):
    z = S.DECK_Z
    lid = Frame((0, S.Y(0.0), z + 0.05), X, (0, 1, 0), Z)
    for side in (1, -1):
        v.detail(f"crew_hinge_{side}", dt.hinge(lid, side * 0.575, 1.47, 0.40, 0.025))
        v.detail(f"crew_handle_{side}", dt.handle(lid, side * 0.575, 1.80, 0.14, 0.035))
        g = Frame((0, S.Y(0.0), z + 0.05), X, (0, 1, 0), Z)
        for k, (u, du) in enumerate(((5.28, 0.55), (6.69, 0.40))):
            v.detail(f"grating_mesh_{side}_{k}", dt.mesh_grille(g, side * 1.10 - 0.17, u - du / 2 + 0.02,
                                                                side * 1.10 + 0.17, u + du / 2 - 0.02, 5, 8, 0.0,
                                                                0.008), "steel")
        fan = Frame((0, S.Y(0.0), z + 0.075), X, (0, 1, 0), Z)
        v.detail(f"fan_mesh_{side}", dt.mesh_grille(fan, side * 0.91 - 0.22, 5.75, side * 0.91 + 0.22, 6.19, 8, 8,
                                                    0.0, 0.007), "steel")
        roof = Frame((0, S.Y(0.0), z), X, (0, 1, 0), Z)
        v.detail(f"deck_side_weld_{side}", dt.weld_bead(roof, [(side * (S.DECK_X - 0.03), S.GLACIS_TOP_U + 0.05),
                                                               (side * (S.DECK_X - 0.03), S.DECK_END_U - 0.05)]))
    eng = Frame((0, S.Y(0.0), z + 0.04), X, (0, 1, 0), Z)
    v.detail("engine_hatch_bolts", dt.bolts(eng, dt.rect_border(-0.50, 5.53, 0.50, 6.93, 0.14, 0.03), 0.014))
    v.detail("roof_bolts", dt.bolts(Frame((0, S.Y(0.0), z), X, (0, 1, 0), Z),
                                    dt.line(-1.1, 4.95, 1.1, 4.95, 14), 0.013))


def wheels(v, S):
    for i, u in enumerate(S.WHEELS_U):
        dx = tc.wheel_spots(S, i)[0][0]
        for side in (1, -1):
            x = side * (S.TRACK_X + dx + 0.045)
            v.detail(f"hub_bolts_{i}_{side}", dt.wheel_hub_bolts((x + side * 0.05, S.Y(u), S.WHEEL_Z), side, 0.075, 8),
                     "rubber_wheel")
            v.detail(f"rim_bolts_{i}_{side}", dt.wheel_hub_bolts((x + side * 0.008, S.Y(u), S.WHEEL_Z), side,
                                                                 S.WHEEL_R - 0.11, 16, 0.011), "rubber_wheel")


def turret(v, S):
    z = S.CUPOLA_Z
    roof = Frame((0, S.Y(0.0), z), X, (0, 1, 0), Z)
    cu = S.CUPOLA[1]
    v.detail("turret_roof_bolts", dt.bolts(roof, dt.line(-0.55, cu - 0.75, 0.55, cu - 0.75, 9) +
                                           dt.line(-0.5, cu + 1.25, 0.5, cu + 1.25, 8), 0.012))
    v.detail("loader_hatch_hinge", dt.hinge(Frame((0, S.Y(0.0), z + 0.05), X, (0, 1, 0), Z), -0.52, cu - 0.05,
                                            0.40, 0.022))
    v.detail("turret_lift", dt.lifting_hook(roof, 0.0, cu - 1.0))
    if S.TURRET_TYPE == "henschel":
        (ub, wb, ut, wt, zt) = S.T2_STATIONS[0]
        fr = Frame.from_points((0, S.Y(ub), S.TURRET_BASE_Z), (1, S.Y(ub), S.TURRET_BASE_Z), (0, S.Y(ut), zt),
                               (0, -1, 0.1))
        h = math.hypot(ut - ub, zt - S.TURRET_BASE_Z)
        for side in (1, -1):  # interlocked front plate / side plate joints
            v.detail(f"turret_front_weld_{side}", dt.weld_bead(fr, [(side * (wb - 0.05), 0.05),
                                                                    (side * (wt - 0.03), h - 0.05)]))
        mf = Frame((0, S.Y(S.SAUKOPF[0] - 0.01), S.GUN_Z), X, (0, 0, 1), (0, -1, 0))
        v.detail("saukopf_bolts", dt.bolts(mf, dt.circle(0.0, 0.0, 0.36, 10, 0.3), 0.018, 0.015))
