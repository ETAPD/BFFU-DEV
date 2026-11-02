"""Bake-only surface detail for the Panther (all variants read their own spec S): interlocking plate joints and weld
beads, glacis and deck bolts, hatch hinges and handles, engine-deck wire mesh, wheel hub bolts, turret welds and
lifting eyes. It only lands in the textures, never in the triangle count. Placed from the same drawing readings as
the geometry (ger_panther_g.py and panther_common.py)."""

import math

from .. import details as dt
from ..details import Frame
from . import panther_common as pc

X, Z = (1, 0, 0), (0, 0, 1)


def build(v, S):
    glacis(v, S)
    roof_and_deck(v, S)
    sides(v, S)
    rear(v, S)
    wheels(v, S)
    turret(v, S)


def glacis(v, S):
    (nu, nz), gu = S.NOSE, S.GLACIS_TOP_U
    gl = Frame.from_points((0, S.Y(nu), nz), (1, S.Y(nu), nz), (0, S.Y(gu), S.DECK_Z), (0, -1, 1))
    length = math.hypot(gu - nu, S.DECK_Z - nz)
    # interlocking joint with the lower nose plate and the weld along the roof edge
    v.detail("glacis_nose_weld", dt.weld_bead(gl, [(-S.LOWER_X, 0.02), (S.LOWER_X, 0.02)]))
    v.detail("glacis_roof_weld", dt.weld_bead(gl, [(-S.DECK_X, length - 0.02), (S.DECK_X, length - 0.02)]))
    bf = (pc.sponson_z(S, 0.8) - nz) / math.sin(math.atan2(S.DECK_Z - nz, gu - nu))  # sponson corner up the plate
    for side in (1, -1):  # side-plate joints: nose corner, flaring out to the sponson corner, up to the roof corner
        v.detail(f"glacis_side_weld_{side}", dt.weld_bead(gl, [(side * (S.LOWER_X - 0.02), 0.03),
                                                               (side * (S.SPONSON_X - 0.03), bf),
                                                               (side * (S.DECK_X - 0.02), length - 0.03)]))
    v.detail("glacis_lifting", dt.lifting_hook(gl, 0.0, length - 0.25))
    v.detail("glacis_spare_bolts", dt.bolts(gl, dt.line(-0.9, length * 0.5, 0.9, length * 0.5, 7), 0.016))


def roof_and_deck(v, S):
    roof = Frame((0, S.Y(S.GLACIS_TOP_U), S.DECK_Z), X, (0, 1, 0), Z)
    lid = Frame((0, S.Y(S.GLACIS_TOP_U), S.DECK_Z + 0.05), X, (0, 1, 0), Z)
    b0 = 2.07 - S.GLACIS_TOP_U
    for side in (1, -1):
        a = side * 0.62
        v.detail(f"crew_hinge_{side}", dt.hinge(lid, a + side * 0.20, b0, 0.30, 0.025, along_u=False))
        v.detail(f"crew_handle_{side}", dt.handle(lid, a - side * 0.12, b0, 0.12, 0.035, rot=math.pi / 2))
        v.detail(f"roof_side_weld_{side}", dt.weld_bead(roof, [(side * (S.DECK_X - 0.03), 0.05),
                                                               (side * (S.DECK_X - 0.03), S.DECK_END_U - S.GLACIS_TOP_U - 0.05)]))
        # engine deck: wire mesh over the fans and intake gratings
        deck = Frame((0, S.Y(0.0), S.DECK_Z + 0.06), X, (0, 1, 0), Z)
        v.detail(f"fan_mesh_{side}", dt.mesh_grille(deck, side * 0.90 - 0.26, 5.27, side * 0.90 + 0.26, 5.79, 8, 8,
                                                    0.0, 0.007), "steel")
        for u in (4.82, 6.22):
            g = Frame((0, S.Y(0.0), S.DECK_Z + 0.04), X, (0, 1, 0), Z)
            v.detail(f"grating_mesh_{side}_{u}", dt.mesh_grille(g, side * 1.0 - 0.26, u - 0.15, side * 1.0 + 0.26,
                                                                u + 0.15, 9, 6, 0.0, 0.008), "steel")
    eng = Frame((0, S.Y(0.0), S.DECK_Z + 0.055), X, (0, 1, 0), Z)
    v.detail("engine_hatch_bolts", dt.bolts(eng, dt.rect_border(-0.42, 4.94, 0.42, 5.90, 0.12, 0.03), 0.014))
    v.detail("roof_bolts", dt.bolts(roof, dt.line(-1.1, 2.95 - S.GLACIS_TOP_U, 1.1, 2.95 - S.GLACIS_TOP_U, 14),
                                    0.013))


def sides(v, S):
    for side in (1, -1):
        u0, u1 = 0.85, S.DECK_END_U - 0.1
        zb0, zb1 = pc.sponson_z(S, u0), pc.sponson_z(S, u1)
        if side < 0:  # keep the frame right-handed with its normal outward (Frame.from_points flips v otherwise)
            u0, u1, zb0, zb1 = u1, u0, zb1, zb0
        p0 = (side * S.SPONSON_X, S.Y(u0), zb0)
        p1 = (side * S.SPONSON_X, S.Y(u1), zb1)
        p2 = (side * S.DECK_X, S.Y(u0), S.DECK_Z)
        f = Frame.from_points(p0, p1, p2, (side, 0, 0.3))
        length = math.dist(p0, p1)
        h = math.dist(p0, p2)
        v.detail(f"side_top_weld_{side}", dt.weld_bead(f, [(0.0, h - 0.02), (length, h - 0.02)]))
        # Schürzen hanger brackets / stowage clamps along the side
        v.detail(f"side_clamps_{side}", dt.bolts(f, dt.line(0.5, h * 0.55, length - 0.4, h * 0.55, 9), 0.018, 0.02))


def rear(v, S):
    p0 = (0, S.Y(S.REAR_LOW[0]), S.REAR_LOW[1])
    # u = -X so the normal (u x v) points back and down, out of the leaning rear plate
    f = Frame.from_points(p0, (-1, S.Y(S.REAR_LOW[0]), S.REAR_LOW[1]), (0, S.Y(S.DECK_END_U), S.DECK_Z), (0, 1, -0.5))
    v.detail("rear_bolts", dt.bolts(f, dt.circle(0.0, 0.30, 0.25, 12), 0.016))
    for side in (1, -1):
        v.detail(f"rear_edge_weld_{side}", dt.weld_bead(f, [(side * (S.LOWER_X - 0.02), 0.05),
                                                            (side * (S.DECK_X - 0.05), 1.30)]))


def wheels(v, S):
    for u in S.WHEELS_U:
        outer = u in S.OUTER_U
        if getattr(S, "WHEEL_LAYOUT", "interleaved") == "overlapped":  # Panther II (panther_common.running_gear)
            dx = 0.20 if outer else -0.06
        else:
            dx = 0.235 if outer else 0.075
        for side in (1, -1):
            x = side * (S.TRACK_X + dx + 0.09)
            v.detail(f"hub_bolts_{u}_{side}", dt.wheel_hub_bolts((x, S.Y(u), S.WHEEL_Z), side, 0.09, 8),
                     "rubber_wheel")
            if outer:  # rim bolts round the steel disc
                v.detail(f"rim_bolts_{u}_{side}", dt.wheel_hub_bolts((x - side * 0.03, S.Y(u), S.WHEEL_Z), side,
                                                                     S.WHEEL_R - 0.07, 16, 0.009), "rubber_wheel")


def turret(v, S):
    st = S.TURRET_STATIONS
    (ub, wb, ut, wt, zt), (ub2, wb2, ut2, wt2, zt2) = st[0], st[1]
    roof = Frame((S.TURRET_X, S.Y(ut), zt), X, (0, 1, 0), Z)
    for side in (1, -1):
        # side-to-roof and side-to-front welds
        a = side * wt
        v.detail(f"turret_roof_weld_{side}", dt.weld_bead(roof, [(a - side * 0.02, 0.03), (side * (wt2 - 0.02),
                                                                                            ut2 - ut - 0.05)]))
        p_lo = pc.turret_point(S, ub + 0.04, S.DECK_Z + 0.05, side)
        p_hi = pc.turret_point(S, ut + 0.04, zt - 0.05, side)
        p_back = pc.turret_point(S, ub + side * 1.0, S.DECK_Z + 0.05, side)  # direction only
        f = Frame.from_points(p_lo, p_back, p_hi, (side, 0, 0.3))
        hgt = math.dist(p_lo, p_hi)
        v.detail(f"turret_front_weld_{side}", dt.weld_bead(f, [(0.0, 0.0), (0.0, hgt)]))
        v.detail(f"turret_lift_{side}", dt.lifting_hook(roof, side * (wt - 0.10), 1.2))
    v.detail("turret_roof_bolts", dt.bolts(roof, dt.line(-0.5, 0.25, 0.5, 0.25, 8), 0.012))
