"""Bake-only surface detail for the Pz IV Ausf. H, placed from the same drawing as the geometry: bolts, rivets,
hinges, handles, grilles, vision blocks and welds. It only lands in the textures, never in the triangle count.
"""

import math

from .. import details as dt
from .. import geo
from ..details import Frame
from .ger_pz4h import (FENDER_Z, FRONT_U, GLACIS, GUN_Z, IDLER, REAR_U, ROOF_FRONT_Z, ROOF_Z, SPROCKET, SUPER_X,
                       TRACK_X, TURRET_TOP, TURRET_X, WHEEL_Z, WHEELS_U, Y)

X, Z = (1, 0, 0), (0, 0, 1)


def build(v):
    front_and_glacis(v)
    roof_and_deck(v)
    rear(v)
    wheels(v)
    turret(v)
    skirts_and_guards(v)


def front_and_glacis(v):
    (gu0, gz0), (gu1, gz1) = GLACIS
    front = Frame.from_points((0, Y(FRONT_U[0]), gz1), (1, Y(FRONT_U[0]), gz1), (0, Y(FRONT_U[1]), ROOF_Z), (0, -1, 0))
    v.detail("visor_bolts", dt.bolts(front, [(0.12, 0.07), (0.60, 0.07), (0.12, 0.24), (0.60, 0.24)], 0.014, 0.06))
    v.detail("ball_bolts", dt.bolts(front, dt.circle(-0.61, 0.18, 0.19, 10), 0.013))
    edge = dt.line(-1.14, 0.42, 1.14, 0.42, 17) + dt.line(-1.14, 0.04, -1.14, 0.38, 4) + dt.line(1.14, 0.04, 1.14, 0.38, 4)
    v.detail("front_edge_bolts", dt.bolts(front, edge, 0.012))
    v.detail("front_weld", dt.weld_bead(front, [(-1.18, 0.0), (1.18, 0.0)]))

    gl = Frame.from_points((0, Y(gu0), gz0), (1, Y(gu0), gz0), (0, Y(gu1), gz1), (0, -1, 1))
    lid = Frame(gl.point(0, 0, 0.035), gl.u, gl.v, gl.n)
    v.detail("inspection_rivets", dt.rivets(lid, dt.rect_border(-0.35, 0.21, 0.35, 0.91, 0.07, 0.02), 0.010))
    for side in (1, -1):
        a = side * 0.67
        v.detail(f"brake_rivets_{side}", dt.rivets(lid, dt.rect_border(a - 0.17, 0.19, a + 0.17, 0.82, 0.07, 0.02), 0.009))
        for b in (0.30, 0.70):
            v.detail(f"brake_hinge_{side}_{b}", dt.hinge(lid, a + side * 0.17, b, 0.10, 0.018, along_u=False))
        v.detail(f"brake_handle_{side}", dt.handle(lid, a - side * 0.10, 0.50, 0.12, 0.035, rot=math.pi / 2))
    v.detail("glacis_weld", dt.weld_bead(gl, [(-0.92, 0.02), (0.92, 0.02)]))
    nose = Frame.from_points((0, Y(0.0), 0.73), (1, Y(0.0), 0.73), (0, Y(gu0), gz0), (0, -1, 0))
    v.detail("nose_bolts", dt.bolts(nose, dt.line(-0.86, 0.20, 0.86, 0.20, 12), 0.012))


def roof_and_deck(v):
    roof = Frame((0, Y(FRONT_U[1]), ROOF_Z), X, (0, 1, 0), Z)
    lid = Frame((0, Y(FRONT_U[1]), ROOF_Z + 0.04), X, (0, 1, 0), Z)
    b0 = 1.395 - FRONT_U[1]
    for side in (1, -1):
        a = side * 0.69
        v.detail(f"crew_rivets_{side}", dt.rivets(lid, dt.rect_border(a - 0.26, b0, a + 0.26, b0 + 0.50, 0.07, 0.02), 0.009))
        v.detail(f"crew_hinge_{side}", dt.hinge(lid, side * 0.96, b0 + 0.25, 0.32, 0.022, along_u=False))
        v.detail(f"crew_handle_{side}", dt.handle(lid, side * 0.50, b0 + 0.25, 0.12, 0.035, rot=math.pi / 2))
        v.detail(f"roof_side_weld_{side}", dt.weld_bead(roof, [(side * (SUPER_X - 0.03), 0.05), (side * (SUPER_X - 0.03), 4.1)]))
    v.detail("roof_front_weld", dt.weld_bead(roof, [(-1.16, 0.02), (1.16, 0.02)]))
    v.detail("roof_bolts", dt.bolts(roof, dt.line(-1.12, 0.88, 1.12, 0.88, 17) + dt.line(-1.12, 2.80, 1.12, 2.80, 17), 0.012))

    hatch = Frame((0, Y(4.60), ROOF_Z + 0.037), X, (0, 1, 0), Z)
    louvre = Frame((0, Y(4.56), ROOF_Z + 0.03), X, (0, 1, 0), Z)
    for side in (1, -1):
        a = side * 0.36
        v.detail(f"engine_rivets_{side}", dt.rivets(hatch, dt.rect_border(a - 0.33, -0.62, a + 0.33, 0.62, 0.08, 0.02), 0.009))
        for b in (-0.35, 0.35):
            v.detail(f"engine_hinge_{side}_{b}", dt.hinge(hatch, side * 0.04, b, 0.14, 0.02, along_u=False))
        v.detail(f"engine_handle_{side}", dt.handle(hatch, side * 0.58, 0.0, 0.14, 0.035, rot=math.pi / 2))
        v.detail(f"louvre_slats_{side}", dt.grille(louvre, side * 0.66 - 0.19, -0.22, side * 0.66 + 0.19, 0.22, 7, 0.025))


def rear(v):
    plate = Frame((0, Y(REAR_U), 0.62), (-1, 0, 0), Z, (0, 1, 0))
    v.detail("rear_bolts", dt.bolts(plate, dt.line(-0.85, 0.20, 0.85, 0.20, 12) + dt.line(-0.85, 0.75, 0.85, 0.75, 12), 0.012))
    v.add("rear_light", geo.box(-0.80, Y(REAR_U + 0.02), 1.22, 0.10, 0.05, 0.07), kind="paint_cast", chamfer=0.01)
    v.add("tow_pintle", geo.box(0.0, Y(REAR_U + 0.05), 0.70, 0.16, 0.12, 0.12), kind="steel", chamfer=0.015)
    for k in (-1, 1):
        strap = geo.lathe([(0.157, -0.02), (0.169, -0.015), (0.169, 0.015), (0.157, 0.02)], 16, close_axis=False)
        v.detail(f"muffler_strap_{k}", geo.move(strap, x=-0.365 + k * 0.345, y=Y(REAR_U + 0.16), z=1.106), "steel")


def wheels(v):
    for u in WHEELS_U:
        for side in (1, -1):
            c = (side * TRACK_X, Y(u), WHEEL_Z)
            v.detail(f"hub_bolts_{u}_{side}", dt.wheel_hub_bolts(c, side, 0.052, 8, 0.011, 0.008, side * 0.128), "rubber_wheel")
    for label, (u, z, r), n in (("sprocket", SPROCKET, 10), ("idler", IDLER, 8)):
        for side in (1, -1):
            c = (side * TRACK_X, Y(u), z)
            v.detail(f"{label}_bolts_{side}", dt.wheel_hub_bolts(c, side, r * 0.38, n, 0.013, 0.01, side * 0.16), "wheel_plain")


def turret(v):
    tx = TURRET_X
    cup_u, cup_x = 3.574, tx + 0.005  # matches ger_pz4h.turret
    ring = Frame((cup_x, Y(cup_u), 2.364), X, (0, 1, 0), Z)
    v.detail("cupola_ring_bolts", dt.bolts(ring, dt.circle(0, 0, 0.445, 18), 0.012))
    # sloping front roof plate (u 2.17 -> 3.02): lifting hooks at its front corners (top view), seam bolts at u 3.02
    slope = math.atan2(TURRET_TOP - ROOF_FRONT_Z, 3.02 - 2.17)
    front_roof = Frame((tx, Y(2.17), ROOF_FRONT_Z), X, (0, math.cos(slope), math.sin(slope)), (0, -math.sin(slope), math.cos(slope)))
    for a in (0.68, -0.68):
        v.detail(f"turret_hook_{a}", dt.lifting_hook(front_roof, a, 0.10))
    roof = Frame((tx, Y(3.02), TURRET_TOP), X, (0, 1, 0), Z)
    v.detail("turret_roof_bolts", dt.bolts(roof, dt.line(-0.60, 0.0, 0.60, 0.0, 11), 0.010))
    for k in range(6):  # glass under each of the drum's vision-block covers
        ang = 2 * math.pi * (k + 0.5) / 6 + math.pi / 2
        c, s = math.cos(ang), math.sin(ang)
        f = Frame((cup_x + 0.43 * c, Y(cup_u) + 0.43 * s, 2.44), (-s, c, 0), Z, (c, s, 0))
        v.detail(f"cupola_glass_{k}", dt.vision_block(f, 0, 0, 0.12, 0.035, 0.015), "glass")
    gx = 0.056
    mf = Frame((gx, Y(1.627), GUN_Z), X, Z, (0, -1, 0))
    v.detail("mantlet_bolts", dt.bolts(mf, [(-0.22, 0.068), (0.22, 0.068), (-0.22, -0.068), (0.22, -0.068)], 0.02, 0.014),
             "paint_cast")
    for side in (1, -1):  # door hinges and handle on the turret Schürzen (side view u 3.13 / 3.83, z 1.84 / 2.15)
        sf = Frame((tx + side * 1.229, Y(3.05), 1.70), (0, side, 0), Z, (side, 0, 0))
        for a in (0.08, 0.78):
            for b in (0.14, 0.45):
                v.detail(f"tskirt_hinge_{side}_{a}_{b}", dt.hinge(sf, side * a, b, 0.08, 0.016, along_u=False), "skirt")
        v.detail(f"tskirt_handle_{side}", dt.handle(sf, side * 0.36, 0.30, 0.10, 0.03, rot=math.pi / 2), "skirt")


def skirts_and_guards(v):
    for side in (1, -1):
        for i in range(5):  # stiffening lip along the top of each hull Schürzen plate (plates as in ger_pz4h.schuerzen)
            u0 = 0.62 + i * 0.97
            u_a, u_b = (1.10, u0 + 1.0) if i == 0 else (u0 + 0.02, 5.03) if i == 4 else (u0 + 0.02, u0 + 1.0)
            x = side * (1.631 + 0.008 * (i % 2))
            hf = Frame((x, 0, 0.62), (0, side, 0), Z, (side, 0, 0))
            a0, a1 = side * Y(u_a), side * Y(u_b)
            v.detail(f"skirt_lip_{side}_{i}", dt.plate(hf, min(a0, a1), 0.92, max(a0, a1), 0.95, 0.008), "skirt")
        v.detail(f"guard_lip_{side}", geo.box(side * 1.46, Y(2.975), FENDER_Z + 0.012, 0.012, 4.95, 0.02))
