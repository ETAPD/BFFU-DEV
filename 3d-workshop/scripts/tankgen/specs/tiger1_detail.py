"""Bake-only surface detail for the Tiger I (every Tiger I spec reads its own S): interlocked plate joints and weld
beads, the bolted fender line, hatch hinges and handles, engine-deck louvres and wire mesh, wheel hub and rim bolts,
turret welds, mantlet and sleeve bolts. It only lands in the textures, never in the triangle count. Placed from the
same drawing readings as the geometry (ger_tiger1_early.py, tiger_common.py) and the Tiger 131 photos."""

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
    (fu0, fz0), (fu1, fz1) = S.FRONT_PLATE
    (ru0, rz0), (ru1, rz1) = S.REAR_PLATE
    # front plate: welds along the deck and the side-plate joints, bolts of the visor and MG ring
    fp = Frame.from_points((0, S.Y(fu0), fz0), (1, S.Y(fu0), fz0), (0, S.Y(fu1), fz1), (0, -1, 0.1))
    h = math.hypot(fu1 - fu0, fz1 - fz0)
    for side in (1, -1):
        v.detail(f"front_side_weld_{side}", dt.weld_bead(fp, [(side * (S.SUPER_X - 0.10), 0.02),
                                                              (side * (S.SUPER_X - 0.10), h - 0.02)]))
    v.detail("visor_bolts", dt.bolts(fp, dt.rect_border(0.20, 0.0, 0.88, 0.33, 0.11, 0.02), 0.014))
    v.detail("mg_bolts", dt.bolts(fp, dt.circle(-0.54, 1.57 - fz0, 0.21, 10), 0.014))
    # glacis: weld to the front plate and the side horns
    (nu, nz) = S.NOSE[2]
    gl = Frame.from_points((0, S.Y(nu), nz), (1, S.Y(nu), nz), (0, S.Y(fu0), 1.38), (0, 0, 1))
    gl_len = math.hypot(fu0 - nu, 1.38 - nz)
    v.detail("glacis_front_weld", dt.weld_bead(gl, [(-S.LOWER_X + 0.05, gl_len - 0.03), (S.LOWER_X - 0.05,
                                                                                         gl_len - 0.03)]))
    for side in (1, -1):
        v.detail(f"glacis_side_weld_{side}", dt.weld_bead(gl, [(side * (S.LOWER_X - 0.04), 0.02),
                                                               (side * (S.LOWER_X - 0.04), gl_len - 0.02)]))
    v.detail("glacis_hooks", dt.bolts(gl, [(-0.35, 0.40), (0.35, 0.40)], 0.03, 0.03))
    for side in (1, -1):
        # side plate: the bolted line the fender hangs from, and the deck weld
        a0, a1 = S.FENDER_A
        u0, u1 = fu0 + 0.05, ru0 - 0.05
        za0, za1 = a0 + 0.01, a1 + 0.01
        if side < 0:  # keep the frame right-handed with its normal outward
            u0, u1, za0, za1 = u1, u0, za1, za0
        f = Frame.from_points((side * S.SUPER_X, S.Y(u0), za0), (side * S.SUPER_X, S.Y(u1), za1),
                              (side * S.SUPER_X, S.Y(u0), za0 + 0.3), (side, 0, 0))
        length = math.hypot(u1 - u0, za1 - za0)
        v.detail(f"fender_bolts_{side}", dt.bolts(f, dt.line(0.10, 0.015, length - 0.10, 0.015, 18), 0.016))
        top = Frame.from_points((side * S.SUPER_X, S.Y(u0), S.DECK_Z - 0.03),
                                (side * S.SUPER_X, S.Y(u1), S.DECK_Z - 0.03),
                                (side * S.SUPER_X, S.Y(u0), S.DECK_Z), (side, 0, 0))
        v.detail(f"cable_clamps_{side}", dt.bolts(top, dt.line(0.3, -0.05, length - 0.3, -0.05, 7), 0.02, 0.025))
    rp = Frame.from_points((0, S.Y(ru0), rz0), (-1, S.Y(ru0), rz0), (0, S.Y(ru1), rz1), (0, 1, 0))
    rh = math.hypot(ru1 - ru0, rz1 - rz0)
    for side in (1, -1):
        v.detail(f"rear_edge_weld_{side}", dt.weld_bead(rp, [(side * (S.SUPER_X - 0.03), 0.02),
                                                             (side * (S.SUPER_X - 0.03), rh - 0.02)]))
    v.detail("rear_plate_bolts", dt.bolts(rp, dt.line(-0.15, 0.25, 0.15, 0.25, 3) + dt.line(-0.15, 0.45, 0.15, 0.45, 3),
                                          0.016))


def deck(v, S):
    z = S.DECK_Z
    lid = Frame((0, S.Y(0.0), z + 0.055), X, (0, 1, 0), Z)
    for side in (1, -1):
        x = side * 0.87
        v.detail(f"crew_hinge_{side}", dt.hinge(lid, x + side * 0.20, 1.48, 0.26, 0.025, along_u=False))
        v.detail(f"crew_handle_{side}", dt.handle(lid, x - side * 0.10, 1.48, 0.12, 0.035, rot=math.pi / 2))
        # radiator gratings (armoured louvres) and the fan grilles: slats and wire mesh
        for k, u in enumerate((4.227, 4.61)):
            g = Frame((0, S.Y(0.0), z + 0.05), X, (0, 1, 0), Z)
            v.detail(f"grating_slats_{side}_{k}", dt.grille(g, side * 1.02 - 0.45, u + 0.03, side * 1.02 + 0.45,
                                                            u + 0.35, 7, 0.02, 30.0), "steel")
        g = Frame((0, S.Y(0.0), z + 0.04), X, (0, 1, 0), Z)
        v.detail(f"fan_mesh_{side}", dt.mesh_grille(g, side * 1.03 - 0.45, 5.50, side * 1.03 + 0.45, 5.86, 12, 6,
                                                    0.0, 0.008), "steel")
        v.detail(f"filler_cap_{side}", dt.bolts(Frame((0, S.Y(0.0), z + 0.03), X, (0, 1, 0), Z),
                                                [(side * 1.05, 5.22)], 0.07, 0.02))
        # deck edge welds (interlocked side plates)
        roof = Frame((0, S.Y(0.0), z), X, (0, 1, 0), Z)
        v.detail(f"deck_side_weld_{side}", dt.weld_bead(roof, [(side * (S.SUPER_X - 0.03), 1.0),
                                                               (side * (S.SUPER_X - 0.03), 5.85)]))
    eng = Frame((0, S.Y(0.0), z + 0.06), X, (0, 1, 0), Z)
    v.detail("engine_hatch_bolts", dt.bolts(eng, dt.circle(0.0, 5.08, 0.21, 12), 0.013))
    v.detail("engine_plate_bolts", dt.bolts(Frame((0, S.Y(0.0), z + 0.02), X, (0, 1, 0), Z),
                                            dt.rect_border(-0.47, 4.36, 0.47, 5.84, 0.18, 0.03), 0.013))
    v.detail("deck_front_weld", dt.weld_bead(Frame((0, S.Y(0.0), z), X, (0, 1, 0), Z),
                                             [(-S.SUPER_X + 0.05, S.FRONT_PLATE[1][0] + 0.10),
                                              (S.SUPER_X - 0.05, S.FRONT_PLATE[1][0] + 0.10)]))


def wheels(v, S):
    for i, u in enumerate(S.WHEELS_U):
        dx, face_out, _, plain = tc.wheel_spots(S, i)[0]
        for side in (1, -1):
            x = side * (S.TRACK_X + dx + 0.045)
            v.detail(f"hub_bolts_{i}_{side}", dt.wheel_hub_bolts((x + side * 0.04, S.Y(u), S.WHEEL_Z), side, 0.075, 8),
                     "rubber_wheel")
            v.detail(f"rim_bolts_{i}_{side}", dt.wheel_hub_bolts((x - side * 0.01, S.Y(u), S.WHEEL_Z), side,
                                                                 S.WHEEL_R - 0.07, 12, 0.010), "rubber_wheel")
        if S.WHEEL_LAYERS == 3:  # second layer face
            dx2 = tc.wheel_spots(S, i)[1][0] if i % 2 == 0 else None
            if dx2 is not None:
                for side in (1, -1):
                    x = side * (S.TRACK_X + dx2 + 0.045)
                    v.detail(f"hub2_bolts_{i}_{side}", dt.wheel_hub_bolts((x + side * 0.012, S.Y(u), S.WHEEL_Z), side,
                                                                          0.075, 8), "rubber_wheel")


def turret(v, S):
    z0, zf, zr, ur = S.TURRET_Z
    roof = Frame((0, S.Y(0.0), zr), X, (0, 1, 0), Z)
    # roof plate welds along the horseshoe edge
    pts = [(x * 0.97, S.TURRET_U + (u - S.TURRET_U) * 0.97) for x, u in tc.t1_turret_plan(S)
           if u >= ur]
    if len(pts) > 2:
        v.detail("turret_roof_weld", dt.weld_bead(roof, pts))
    v.detail("roof_bolts", dt.bolts(roof, dt.line(-0.5, ur + 0.05, 0.5, ur + 0.05, 8), 0.012))
    v.detail("loader_hatch_hinge", dt.hinge(Frame((0, S.Y(0.0), zr + 0.055), X, (0, 1, 0), Z), -0.65, 3.02, 0.40,
                                            0.022))
    # front plate: weld where the horseshoe meets it, bolts of the mantlet trunnion housings
    fu0, fu1, hw = S.TURRET_FRONT
    fr = Frame.from_points((0, S.Y(fu0 + 0.05), z0 + 0.05), (1, S.Y(fu0 + 0.05), z0 + 0.05),
                           (0, S.Y(fu0 + 0.09), zf - 0.05), (0, -1, 0))
    for side in (1, -1):
        v.detail(f"turret_front_weld_{side}", dt.weld_bead(fr, [(side * (hw - 0.03), 0.0),
                                                                (side * (hw - 0.03), zf - z0 - 0.12)]))
    # mantlet: bolt ring of the sleeve collar and the trunnion bolts on the ends
    m = S.MANTLET
    rc_u, rc_z = m["rc"]
    face_u = rc_u - m["r"]
    mf = Frame((0, S.Y(face_u - 0.12), S.GUN_Z), X, (0, 0, 1), (0, -1, 0))
    v.detail("collar_bolts", dt.bolts(mf, dt.circle(0.0, 0.0, 0.17, 8, math.pi / 8), 0.02, 0.02))
    for side in (1, -1):
        v.detail(f"mantlet_end_bolts_{side}", dt.bolts(Frame((0, S.Y(face_u + 0.02), 0.0), X, (0, 0, 1), (0, -1, 0)),
                                                       dt.line(side * 0.74, S.GUN_Z - 0.18, side * 0.74,
                                                               S.GUN_Z + 0.18, 3), 0.018))
