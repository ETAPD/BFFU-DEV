"""Panzerkampfwagen IV Ausf. H (Sd.Kfz. 161/2), summer 1943 production.

Traced from MasterJVN's four-view drawing "PzIV-012-H-Variantes.jpg" (Wikimedia Commons, CC BY 4.0), calibrated at
175 px/m (checked against the 7.02 m length with gun, the 3 m scale bar and the 2.88 m track width). The drawing omits
the hull Schürzen; those follow the Ausf. H standard (5 mm plates on a rail, 8 mm turret skirts).

Coordinates: u = metres back from the bow tip, z = metres above ground, x = metres to the vehicle's left.
"""

import math

from .. import geo, parts

NAME = "GER_pz4h"
HULL_L = 5.92
DETAIL = True  # bake-only surface detail (ger_pz4h_detail); switch off while checking shapes against the drawing


def Y(u):
    """Bow-relative distance -> model Y (front is -Y, hull centred on the origin)."""
    return u - HULL_L / 2


# ---- running gear (side + front view) ------------------------------------------------------------------------
TRACK_W = 0.40
TRACK_X = 1.44 - TRACK_W / 2  # track outer edge at 1.44 m
TRACK_T = 0.03
TRACK_PITCH = 0.12  # Kgs 61/400/120
WHEEL_R = 0.235
WHEEL_Z = 0.27
WHEELS_U = [1.10, 1.61, 2.13, 2.62, 3.13, 3.63, 4.14, 4.63]  # 4 leaf-spring bogies, pairs 0.51 m apart
SPROCKET = (0.53, 0.72, 0.34)
SPROCKET_TEETH = 19
IDLER = (5.40, 0.60, 0.30)
ROLLERS_U = [1.51, 2.43, 3.38, 4.38]
ROLLER_Z, ROLLER_R = 0.90, 0.13

# ---- hull ------------------------------------------------------------------------------------------------------
LOWER_X = 0.93  # lower hull between the tracks
SUPER_X = 1.20  # superstructure incl. panniers (front view: 2.40 m)
DECK_X = 1.16  # engine compartment
FENDER_Z = 1.26
ROOF_Z = 1.68
GLACIS = ((0.06, 0.97), (1.05, 1.23))  # 15 deg glacis from the upper nose plate to the superstructure front
FRONT_U = (1.05, 1.10)  # superstructure front plate, bottom and top
REAR_U = 5.42  # hull rear plate
DECK_END_U = 5.30  # engine deck ends, rear plate slopes down

# ---- turret ---------------------------------------------------------------------------------------------------
TURRET_U = 3.03  # turret ring centre
TURRET_X = 0.05  # offset to the vehicle's left (gun bore is 5 cm left of the centreline in the front view)
TURRET_Z = 1.70
TURRET_TOP = 2.31
ROOF_FRONT_Z = 2.25
GUN_Z = 1.97

# Balkenkreuz on the middle hull Schürzen plate, both sides: (side, y, z) in metres
CROSSES = [(1, Y(2.95), 1.10), (-1, Y(2.95), 1.10)]
CROSS_SIZE = 0.52


def wheel_info(scale):
    """{bone: (radius in game units, rotational symmetry step or None)} for the move animation.
    Road wheels carry camo, so they turn whole revolutions; the rest are rotation-neutral."""
    info = {"wheel_01": (SPROCKET[2] * scale, 2 * math.pi / SPROCKET_TEETH),
            "wheel_02": (IDLER[2] * scale, 2 * math.pi / 90)}
    for i in range(len(WHEELS_U)):
        info[f"wheel_{3 + i:02d}"] = (WHEEL_R * scale, None)
    for i in range(len(ROLLERS_U)):
        info[f"wheel_{3 + len(WHEELS_U) + i:02d}"] = (ROLLER_R * scale, 2 * math.pi / 90)
    return info


def build(v):
    hull(v)
    running_gear(v)
    turret(v)
    fittings(v)
    schuerzen(v)
    if DETAIL:
        from . import ger_pz4h_detail  # imported here: it reads this module's dimensions

        ger_pz4h_detail.build(v)
    rig(v)


def P(points):
    return [(Y(u), z) for u, z in points]


def hull(v):
    (gu0, gz0), (gu1, gz1) = GLACIS
    # lower hull: belly, lower nose plate, upper nose plate (80 mm), glacis, then sides up to the track guards,
    # vertical rear plate down to the sloped rear belly
    lower = [(0.42, 0.40), (0.0, 0.73), (gu0, gz0), (gu1, gz1), (REAR_U, gz1), (REAR_U, 0.60), (5.20, 0.40)]
    v.add("hull_lower", geo.prism_x(P(lower), -LOWER_X, LOWER_X), chamfer=0.025)

    # superstructure + engine compartment: one shell at roof height, front plate slightly raked, rear deck sloping
    sup = [(FRONT_U[0], FENDER_Z), (FRONT_U[0], gz1), (FRONT_U[1], ROOF_Z), (3.95, ROOF_Z), (3.95, FENDER_Z)]
    v.add("superstructure", geo.prism_x(P(sup), -SUPER_X, SUPER_X), chamfer=0.025)
    deck = [(3.95, FENDER_Z), (3.95, ROOF_Z), (DECK_END_U, ROOF_Z), (REAR_U, 1.45), (REAR_U, FENDER_Z)]
    v.add("engine_deck", geo.prism_x(P(deck), -DECK_X, DECK_X), chamfer=0.025)

    # track guards: plate at 1.26 m, front mudguard sloping down to the bow and boxed in (front view), rear guard
    # sloping down behind the idler
    guard = [(0.0, 0.90), (0.17, 1.17), (0.50, FENDER_Z - 0.012), (5.55, FENDER_Z - 0.012), (5.95, 1.12),
             (5.95, 1.135), (5.55, FENDER_Z), (0.50, FENDER_Z), (0.17, 1.185), (0.0, 0.915)]
    outer = TRACK_X + TRACK_W / 2 + 0.02
    v.mirror_x("guard", lambda: geo.prism_x(P(guard), SUPER_X - 0.02, outer), kind="paint")
    box = [(0.0, 0.88), (0.0, 0.915), (0.17, 1.185), (0.50, FENDER_Z), (0.50, 0.88)]
    v.mirror_x("guard_box_side", lambda: geo.prism_x(P(box), outer - 0.012, outer), kind="paint")
    v.mirror_x("guard_box_front", lambda: geo.prism_x(P([(0.0, 0.88), (0.012, 0.88), (0.012, 0.915), (0.0, 0.915)]),
                                                       LOWER_X, outer), kind="paint")

    for side in (1, -1):
        v.add(f"tow_front_{side}", geo.move(parts.tow_shackle(), x=side * 0.62, y=Y(0.03), z=0.80), kind="steel")
        v.add(f"tow_rear_{side}", geo.move(parts.tow_shackle(), x=side * 0.62, y=Y(REAR_U + 0.03), z=0.68), kind="steel")


def running_gear(v):
    circles = [(Y(SPROCKET[0]), SPROCKET[1], SPROCKET[2]), (Y(IDLER[0]), IDLER[1], IDLER[2])]
    circles += [(Y(u), WHEEL_Z, WHEEL_R) for u in WHEELS_U]
    circles += [(Y(u), ROLLER_Z, ROLLER_R) for u in ROLLERS_U]
    for side, suffix in ((1, "l"), (-1, "r")):
        v.add(f"track_{suffix}", parts.track_belt(circles, side * TRACK_X, TRACK_W, TRACK_T, 0.12, 0.48),
              kind="track", bone="tank_base", smooth_angle=60)

    bone_i = 1
    for label, (u, z, r), maker in (("sprocket", SPROCKET, lambda r=SPROCKET[2]: parts.sprocket(r, SPROCKET_TEETH, 0.06, 0.10, 0.11)),
                                    ("idler", IDLER, lambda r=IDLER[2]: parts.idler(r, 0.06, 0.10))):
        bname = f"wheel_{bone_i:02d}"
        v.bone(bname, (0, Y(u), z), "wheel_suspention")
        for side in (1, -1):
            bm = maker()
            if side < 0:
                geo.rotate(bm, math.pi, "Z")
            v.add(f"{label}_{side}", geo.move(bm, x=side * TRACK_X, y=Y(u), z=z), kind="wheel_plain", bone=bname)
            hub_len = TRACK_X - LOWER_X - 0.12
            stub = geo.cylinder(0.14 if label == "sprocket" else 0.08, hub_len, 12, axis="X",
                                center=(side * (LOWER_X + hub_len / 2), Y(u), z))
            v.add(f"{label}_hub_{side}", stub, kind="paint", chamfer=0.01)
        bone_i += 1

    for i, u in enumerate(WHEELS_U):
        bname = f"wheel_{bone_i:02d}"
        v.bone(bname, (0, Y(u), WHEEL_Z), "wheel_suspention")
        for side in (1, -1):
            for label, bm, kind in zip(("disc", "tyre"), parts.double_road_wheel(WHEEL_R, 0.075, 0.07, 0.07, 16),
                                       ("rubber_wheel", "rubber")):
                if side < 0:
                    geo.rotate(bm, math.pi, "Z")
                v.add(f"roadwheel_{label}_{i}_{side}", geo.move(bm, x=side * TRACK_X, y=Y(u), z=WHEEL_Z), kind=kind,
                      bone=bname)
        bone_i += 1

    for i, u in enumerate(ROLLERS_U):
        bname = f"wheel_{bone_i:02d}"
        v.bone(bname, (0, Y(u), ROLLER_Z), "wheel_suspention")
        for side in (1, -1):
            bm = parts.return_roller(ROLLER_R, 0.16, 10)
            if side < 0:
                geo.rotate(bm, math.pi, "Z")
            v.add(f"roller_{i}_{side}", geo.move(bm, x=side * TRACK_X, y=Y(u), z=ROLLER_Z), kind="wheel_plain",
                  bone=bname)
        bone_i += 1

    # leaf-spring bogies: bracket, quarter-elliptic spring housing and the two wheel arms (side view)
    for b in range(4):
        u0, u1 = WHEELS_U[b * 2], WHEELS_U[b * 2 + 1]
        um = (u0 + u1) / 2
        for side in (1, -1):
            x = side * (LOWER_X + 0.08)
            bracket = geo.chamfer(geo.box(x, Y(um), 0.47, 0.14, 0.34, 0.22), 0.02)
            spring = geo.chamfer(geo.box(x, Y(um), 0.62, 0.12, 0.58, 0.08), 0.015)
            arms = geo.box(x + side * 0.03, Y(um), WHEEL_Z + 0.06, 0.07, u1 - u0, 0.07)
            v.add(f"bogie_{b}_{side}", geo.merge(bracket, spring, arms), kind="paint")


def turret(v):
    tx, ty = TURRET_X, Y(TURRET_U)
    # turret shell (side/top/front views): narrow front plate, cheeks angled back to the 25-deg sides, angled rear
    # corners, roof sloping down to the front plate
    base = [(-0.56, -1.00), (0.56, -1.00), (0.92, -0.55), (0.92, 0.72), (0.70, 0.97), (-0.70, 0.97), (-0.92, 0.72),
            (-0.92, -0.55)]
    top = [(-0.48, -0.95, ROOF_FRONT_Z), (0.48, -0.95, ROOF_FRONT_Z), (0.64, -0.45, TURRET_TOP), (0.62, 0.70, TURRET_TOP),
           (0.52, 0.92, TURRET_TOP), (-0.52, 0.92, TURRET_TOP), (-0.62, 0.70, TURRET_TOP), (-0.64, -0.45, TURRET_TOP)]
    shell = geo.loft([(x + tx, y + ty, TURRET_Z) for x, y in base], [(x + tx, y + ty, z) for x, y, z in top])
    v.add("turret", shell, kind="paint", bone="turret", chamfer=0.025)

    # rear stowage bin inside the skirt wrap
    v.add("turret_bin", geo.box(tx, ty + 1.20, 2.03, 1.10, 0.46, 0.36), kind="paint", bone="turret", chamfer=0.03)
    # cupola (drum 0.74 m, top at 2.63 m) on the rear of the roof, ventilator and signal port ahead of it
    v.add("cupola", geo.move(parts.cupola(0.37, 0.30, 5), x=tx, y=Y(3.56), z=TURRET_TOP - 0.01), kind="paint_cast",
          bone="turret")
    v.add("vent", geo.move(geo.lathe([(0.0, 0.07), (0.12, 0.06), (0.15, 0.0)], 12, axis="Z"),
                           x=tx - 0.05, y=Y(2.95), z=TURRET_TOP), kind="paint", bone="turret")
    v.add("signal_port", geo.move(geo.cylinder(0.06, 0.05, 10, axis="Z"), x=tx + 0.35, y=Y(2.85),
                                  z=TURRET_TOP + 0.02), kind="paint", bone="turret")

    # external mantlet (0.79 x 0.43 m, front view) tapering forward, recoil sleeve 0.30 m across, L/48 barrel,
    # double-baffle brake; muzzle 1.07 m ahead of the bow
    back = [(-0.40, -0.215), (0.40, -0.215), (0.40, 0.215), (-0.40, 0.215)]
    front = [(-0.33, -0.17), (0.33, -0.17), (0.33, 0.17), (-0.33, 0.17)]
    mantlet = geo.loft([(tx + x, Y(2.03), GUN_Z + z) for x, z in back], [(tx + x, Y(1.82), GUN_Z + z) for x, z in front])
    v.add("mantlet", mantlet, kind="paint_cast", bone="turret", chamfer=0.03)
    v.add("coax_port", geo.move(geo.cylinder(0.03, 0.05, 8, axis="Y"), x=tx - 0.22, y=Y(1.81), z=GUN_Z + 0.02),
          kind="steel", bone="turret")
    v.add("sight_port", geo.move(geo.cylinder(0.035, 0.05, 8, axis="Y"), x=tx + 0.24, y=Y(1.81), z=GUN_Z + 0.05),
          kind="steel", bone="turret")
    face = Y(1.82)
    muzzle = Y(-1.07)
    length = face - muzzle
    barrel = parts.gun_barrel([(0.15, 0.0), (0.15, 0.21), (0.12, 0.23), (0.070, 0.30), (0.062, length - 0.27),
                               (0.062, length - 0.25)], 16)
    geo.move(barrel, x=tx, y=face, z=GUN_Z)
    brake = geo.move(parts.muzzle_brake_double(0.10, 0.27, 16), x=tx, y=muzzle + 0.27, z=GUN_Z)
    v.add("gun", geo.merge(barrel, brake), kind="steel_paint", bone="barrel_base")
    v.locator("barrel", (tx, muzzle, GUN_Z), "barrel_tip")
    v.bone("barrel_base", (tx, Y(2.0), GUN_Z), "turret")
    v.bone("barrel_tip", (tx, muzzle, GUN_Z), "barrel_base")
    v.bone("turret", (tx, ty, TURRET_Z), "chassie")

    # turret Schürzen (8 mm): side panels at 1.20 m, rear wrap round the bin to u = 4.82, and front panels that are
    # tilted planes from the side panel's top-front corner down-inwards to the turret cheek (the front-view "X")
    zb, zt = 1.70, TURRET_TOP
    side_top = [(1.05, 2.36), (1.20, 2.62), (1.20, 4.20), (0.98, 4.60), (0.55, 4.79), (0.0, 4.82)]
    side_bot = [(1.20, 2.75), (1.20, 2.80), (1.20, 4.20), (0.98, 4.60), (0.55, 4.79), (0.0, 4.82)]
    for side in (1, -1):
        top = [(side * x + tx - TURRET_X, Y(u)) for x, u in side_top]
        bot = [(side * x + tx - TURRET_X, Y(u)) for x, u in side_bot]
        v.add(f"turret_skirt_{side}", geo.wall_loft(bot, top, zb, zt, -0.014 * side), kind="skirt", bone="turret",
              smooth_angle=20, chamfer=0.004)
        # tilted front panel
        quad = [(side * 1.20 + tx - TURRET_X, Y(2.75), zb), (side * 1.05 + tx - TURRET_X, Y(2.36), zt),
                (side * 0.66 + tx - TURRET_X, Y(2.06), zt), (side * 0.58 + tx - TURRET_X, Y(2.12), zb)]
        v.add(f"turret_skirt_front_{side}", panel(quad, 0.014), kind="skirt", bone="turret", chamfer=0.004)
        # mounting arms from the turret sides out to the skirt
        for u in (2.80, 3.55):
            v.add(f"skirt_mount_{side}_{u}", geo.box(tx + side * 1.06, Y(u), zt - 0.06, 0.30, 0.05, 0.04), kind="paint",
                  bone="turret", chamfer=0.008)
        # two-piece doors over the turret side hatches
        v.add(f"skirt_door_{side}", geo.box(tx + side * 1.215, Y(3.05), 2.00, 0.012, 0.55, 0.42), kind="skirt",
              bone="turret", chamfer=0.004)


def panel(quad, thickness):
    """Thin plate from a 3D quad (front panels of the turret Schürzen)."""
    import bmesh
    from mathutils import Vector

    pts = [Vector(p) for p in quad]
    n = (pts[1] - pts[0]).cross(pts[3] - pts[0]).normalized()
    bm = bmesh.new()
    a = [bm.verts.new(p) for p in pts]
    b = [bm.verts.new(p + n * thickness) for p in pts]
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((a[i], b[i], b[j], a[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def fittings(v):
    front = Y(FRONT_U[0])
    # driver's visor (Fahrersehklappe 80) on the left, MG ball mount on the right (front view)
    v.add("driver_visor", geo.box(0.36, front - 0.03, 1.36, 0.54, 0.07, 0.22), kind="paint_cast", chamfer=0.02)
    v.add("ball_mount", geo.move(parts.ball_mount(0.16), x=-0.61, y=front - 0.01, z=1.41), kind="paint_cast")
    v.add("hull_mg", geo.move(parts.mg_barrel(0.36), x=-0.61, y=front - 0.12, z=1.41), kind="steel")

    # glacis: central transmission inspection plate and two brake access hatches (top view)
    (gu0, gz0), (gu1, gz1) = GLACIS
    slope = math.atan2(gz1 - gz0, gu1 - gu0)

    def on_glacis(u):
        return gz0 + (u - gu0) * math.tan(slope)

    for name, x, w, u0, u1 in (("inspection", 0.0, 0.70, 0.27, 0.96), ("brake_l", 0.67, 0.34, 0.25, 0.87),
                               ("brake_r", -0.67, 0.34, 0.25, 0.87)):
        um = (u0 + u1) / 2
        h = geo.box(0, 0, 0, w, (u1 - u0) / math.cos(slope), 0.035)
        geo.rotate(h, slope, "X")
        geo.move(h, x=x, y=Y(um), z=on_glacis(um) + 0.015)
        v.add(f"glacis_{name}", h, kind="paint", chamfer=0.01)

    # crew hatches on the superstructure roof, either side (top view: u 1.39-1.90, centres 0.69 m out)
    for side in (1, -1):
        v.add(f"crew_hatch_{side}", geo.box(side * 0.69, Y(1.645), ROOF_Z + 0.02, 0.52, 0.50, 0.04), kind="paint",
              chamfer=0.012)

    # spare track links across the upper nose plate
    for col in range(4):
        link = geo.chamfer(geo.box(0, 0, 0, 0.38, 0.03, 0.115), 0.008)
        geo.rotate(link, -math.atan2(0.06, 0.24), "X")
        geo.move(link, x=-0.63 + col * 0.42, y=Y(0.03) - 0.025, z=0.85)
        v.add(f"spare_link_{col}", link, kind="track_steel")

    # headlights on the front guards
    for side in (1, -1):
        v.add(f"headlight_{side}", geo.move(parts.headlight(0.075), x=side * 1.30, y=Y(0.25), z=FENDER_Z + 0.06),
              kind="paint_cast")

    # engine deck: two access hatches, cooling louvres either side (top view u 4.33-4.79, 0.46-0.86 m out)
    for side in (1, -1):
        v.add(f"engine_hatch_{side}", geo.box(side * 0.36, Y(4.60), ROOF_Z + 0.02, 0.66, 1.25, 0.035), kind="paint",
              chamfer=0.01)
        v.add(f"louvre_{side}", geo.box(side * 0.66, Y(4.56), ROOF_Z + 0.015, 0.40, 0.46, 0.03), kind="paint",
              chamfer=0.008)

    # rear: main muffler across the rear plate (top view u 5.42-5.73), tail pipe, auxiliary muffler
    v.add("muffler", geo.move(parts.muffler(0.155, 1.06), x=0.24, y=Y(REAR_U + 0.16), z=1.20), kind="exhaust")
    v.add("tailpipe", geo.move(geo.cylinder(0.045, 0.22, 8, axis="Z"), x=-0.22, y=Y(REAR_U + 0.16), z=1.42),
          kind="exhaust")
    v.add("aux_muffler", geo.move(parts.muffler(0.07, 0.34), x=-0.70, y=Y(REAR_U + 0.10), z=1.10), kind="exhaust")
    v.locator("right_exhaust", (-0.22, Y(REAR_U + 0.16), 1.55), "chassie")
    v.locator("left_exhaust", (0.60, Y(REAR_U + 0.16), 1.25), "chassie")

    # tools: shovel and jack on the guards, tow cables, antenna base
    v.add("shovel", geo.move(parts.shovel(1.05), x=1.32, y=Y(1.6), z=FENDER_Z + 0.03), kind="wood")
    v.add("jack", geo.box(-1.30, Y(5.10), FENDER_Z + 0.11, 0.18, 0.28, 0.22), kind="paint", chamfer=0.015)
    for k, x in enumerate((1.28, 1.32)):
        v.add(f"tow_cable_{k}", geo.move(parts.tool(2.4, 0.022, 6), x=x, y=Y(3.6), z=FENDER_Z + 0.03), kind="steel")
    v.add("antenna_base", geo.move(geo.cylinder(0.04, 0.10, 8, axis="Z"), x=-1.08, y=Y(4.05), z=ROOF_Z + 0.05),
          kind="paint")
    v.locator("left_tracks", (TRACK_X, Y(5.70), 0.0), "tank_base")
    v.locator("right_tracks", (-TRACK_X, Y(5.70), 0.0), "tank_base")


def schuerzen(v):
    """Hull Schürzen (5 mm, not in the drawing): rail on brackets along the superstructure, 5 plates per side."""
    for side in (1, -1):
        x = side * (TRACK_X + TRACK_W / 2 + 0.07)
        v.add(f"skirt_rail_{side}", geo.box(x - side * 0.02, Y(3.0), 1.56, 0.03, 4.6, 0.035), kind="paint")
        for b, u in enumerate((1.2, 2.2, 3.2, 4.2, 5.1)):
            v.add(f"skirt_bracket_{side}_{b}", geo.box(side * (SUPER_X + 0.15), Y(u), 1.54, 0.30, 0.05, 0.04),
                  kind="paint")
        for i in range(5):
            u0 = 0.62 + i * 0.97
            plate = [(Y(u0), 1.62), (Y(u0), 0.62), (Y(u0 + 1.02), 0.62), (Y(u0 + 1.02), 1.62)]
            if i == 0:  # leading plate: long diagonal from the top (over the sprocket) back to the bottom
                plate = [(Y(u0 - 0.10), 1.62), (Y(u0 - 0.10), 1.48), (Y(u0 + 0.42), 0.62), (Y(u0 + 1.02), 0.62),
                         (Y(u0 + 1.02), 1.62)]
            elif i == 4:  # trailing plate: rear corner cut down towards the idler
                plate = [(Y(u0), 1.62), (Y(u0), 0.62), (Y(u0 + 0.86), 0.62), (Y(u0 + 0.98), 0.78),
                         (Y(u0 + 0.98), 1.38), (Y(u0 + 0.80), 1.62)]
            off = 0.008 * (i % 2)
            v.add(f"skirt_{side}_{i}", geo.prism_x(plate, x - 0.006 + side * off, x + 0.006 + side * off),
                  kind="skirt", smooth_angle=30, chamfer=0.005)


def rig(v):
    v.bone("root", (0, 0, 0))
    v.bone("tank_base", (0, 0, 0), "root")
    v.bone("chassie", (0, 0, 0.9), "tank_base")
    v.bone("wheel_suspention", (0, 0, WHEEL_Z), "tank_base")
