"""Panzerkampfwagen IV Ausf. H (Sd.Kfz. 161/2), summer 1943 production.

Traced from MasterJVN's four-view drawing "PzIV-012-H-Variantes.jpg" (Wikimedia Commons, CC BY 4.0), calibrated at
175 px/m (checked against the 7.02 m length with gun, the 3 m scale bar and the 2.88 m track width). The drawing omits
the hull Schürzen plates (it does show their rail and brackets); the plates follow the Ausf. H standard (5 mm).

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
FENDER_Z = 1.25
ROOF_Z = 1.68
GLACIS = ((0.06, 0.97), (1.05, 1.23))  # 15 deg glacis from the upper nose plate to the superstructure front
FRONT_U = (1.05, 1.10)  # superstructure front plate, bottom and top
REAR_U = 5.42  # hull rear plate
DECK_END_U = 5.30  # engine deck ends, rear plate slopes down

# ---- turret ---------------------------------------------------------------------------------------------------
TURRET_U = 3.03  # turret ring centre
TURRET_X = 0.05  # offset to the vehicle's left (gun bore is 5 cm left of the centreline in the front view)
TURRET_Z = 1.70
TURRET_TOP = 2.305  # flat rear roof (side view)
ROOF_FRONT_Z = 2.21  # top of the front plate; the roof plate slopes up to TURRET_TOP at u 3.02
GUN_Z = 1.98  # bore axis (side view)

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
    sup = [(FRONT_U[0], gz1), (FRONT_U[1], ROOF_Z), (3.95, ROOF_Z), (3.95, FENDER_Z), (FRONT_U[0] + 0.01, FENDER_Z)]
    v.add("superstructure", geo.prism_x(P(sup), -SUPER_X, SUPER_X), chamfer=0.025)
    deck = [(3.95, FENDER_Z), (3.95, ROOF_Z), (DECK_END_U, ROOF_Z), (REAR_U, 1.45), (REAR_U, FENDER_Z)]
    v.add("engine_deck", geo.prism_x(P(deck), -DECK_X, DECK_X), chamfer=0.025)

    # track guards: plate at 1.25 m with a 7 cm outer lip (side view line at 1.18 m), front mudguard sloping down to
    # the bow and boxed in (front view), rear mudguard sloping down from u 5.45 to 0.99 m at the tail (side view)
    guard = [(0.0, 0.90), (0.17, 1.165), (0.50, FENDER_Z - 0.012), (5.45, FENDER_Z - 0.012), (5.95, 0.948),
             (5.95, 0.993), (5.45, FENDER_Z), (0.50, FENDER_Z), (0.17, 1.18), (0.0, 0.915)]
    outer = TRACK_X + TRACK_W / 2 + 0.02
    v.mirror_x("guard", lambda: geo.prism_x(P(guard), SUPER_X - 0.02, outer), kind="paint")
    box = [(0.0, 0.88), (0.0, 0.915), (0.17, 1.185), (0.50, FENDER_Z), (0.50, 0.88)]
    # ahead of the superstructure the guard runs in to the lower hull side (top view: inner edge 0.92 m to u 1.05)
    inner = [(0.0, 0.90), (0.17, 1.165), (0.50, FENDER_Z - 0.012), (FRONT_U[0], FENDER_Z - 0.012),
             (FRONT_U[0], FENDER_Z), (0.50, FENDER_Z), (0.17, 1.18), (0.0, 0.915)]
    v.mirror_x("guard_inner", lambda: geo.prism_x(P(inner), LOWER_X, SUPER_X - 0.02), kind="paint")
    v.mirror_x("guard_lip", lambda: geo.prism_x(P([(0.50, 1.18), (5.45, 1.18), (5.45, FENDER_Z), (0.50, FENDER_Z)]),
                                                 outer - 0.012, outer), kind="paint")
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


def station_shell(stations, z0):
    """Armour shell from fore-aft stations [(u_base, half_w_base, u_top, half_w_top, z_top), ...] about x = 0:
    planar-ish side walls between stations, a roof that can bend at any station, flat floor at z0."""
    import bmesh

    bm = bmesh.new()
    rows = []
    for ub, wb, ut, wt, zt in stations:
        rows.append([bm.verts.new((-wb, Y(ub), z0)), bm.verts.new((wb, Y(ub), z0)),
                     bm.verts.new((wt, Y(ut), zt)), bm.verts.new((-wt, Y(ut), zt))])
    for r0, r1 in zip(rows, rows[1:]):
        for k in range(4):
            k2 = (k + 1) % 4
            bm.faces.new((r0[k], r0[k2], r1[k2], r1[k]))
    bm.faces.new(rows[0])
    bm.faces.new(list(reversed(rows[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def turret(v):
    tx, ty = TURRET_X, Y(TURRET_U)

    def roof_z(u):  # roof: front plate top at u 2.17 / 2.21 m, sloping up to the flat rear roof at u 3.02
        return ROOF_FRONT_Z + (TURRET_TOP - ROOF_FRONT_Z) * min(1.0, max(0.0, (u - 2.17) / (3.02 - 2.17)))

    # turret shell (hidden behind the Schürzen in the side view; top view: roof 1.38 m wide, sides 25 deg)
    # front plate leaning back 10 deg, cheeks to the full-width sides, angled rear corners
    stations = [(2.10, 0.80, 2.17, 0.69, roof_z(2.17)), (2.60, 0.97, 2.60, 0.69, roof_z(2.60)),
                (3.02, 0.97, 3.02, 0.69, TURRET_TOP), (3.75, 0.97, 3.80, 0.69, TURRET_TOP),
                (4.00, 0.70, 4.00, 0.50, TURRET_TOP)]
    shell = geo.move(station_shell(stations, TURRET_Z), x=tx)
    v.add("turret", shell, kind="paint", bone="turret", chamfer=0.02)

    # rear stowage bin inside the skirt wrap: D-shaped in plan (top view u 3.83-4.81, 1.13 m wide), lid flat behind
    # the roof, then sloping down to 2.26 m at the back (side view)
    plan = [(-0.566, 3.834), (0.566, 3.834), (0.566, 4.28)]
    plan += [(0.566 * math.cos(a), 4.28 + 0.526 * math.sin(a))
             for a in (math.radians(d) for d in range(20, 161, 20))]
    plan += [(-0.566, 4.28)]
    lid = lambda u: TURRET_TOP - 0.01 - 0.037 * max(0.0, u - 4.0) / (4.806 - 4.0)
    v.add("turret_bin", geo.loft([(tx + x, Y(u), 1.86) for x, u in plan], [(tx + x, Y(u), lid(u)) for x, u in plan]),
          kind="paint", bone="turret", chamfer=0.02)

    # commander's cupola (side/front view): base ring 0.95 m, armoured drum flaring 0.83 -> 0.88 m with the
    # vision-block covers, chamfered top and the hatch, top at 2.62 m
    cz = TURRET_TOP
    cup_u, cup_x = 3.574, tx + 0.005
    prof = [(0.0, cz), (0.472, cz), (0.472, 2.364), (0.416, 2.364), (0.438, 2.459), (0.444, 2.462),
            (0.444, 2.47), (0.438, 2.47), (0.438, 2.524), (0.38, 2.554), (0.0, 2.554)]
    v.add("cupola", geo.move(geo.lathe([(r, z - cz) for r, z in prof], 24, axis="Z"), x=cup_x, y=Y(cup_u), z=cz),
          kind="paint_cast", bone="turret", smooth_angle=50)
    hatch = geo.lathe([(0.0, 2.554), (0.388, 2.554), (0.388, 2.605), (0.372, 2.619), (0.0, 2.619)], 24, axis="Z")
    v.add("cupola_hatch", geo.move(hatch, x=cup_x, y=Y(cup_u)), kind="paint_cast", bone="turret", smooth_angle=50)
    for k in range(6):  # vision-block covers, one per segment of the drum
        a = 2 * math.pi * (k + 0.5) / 6 + math.pi / 2
        cover = geo.box(0, 0, 0, 0.016, 0.22, 0.05)
        geo.move(cover, x=0.44, z=2.497)
        geo.rotate(cover, a, "Z")
        v.add(f"cupola_block_{k}", geo.move(cover, x=cup_x, y=Y(cup_u)), kind="paint_cast", bone="turret",
              chamfer=0.006)

    # fan ventilator cover on the sloping roof plate, right of the gun (top view u 2.61-2.86, 0.26 m right of the
    # centreline; side view top 2.35 m)
    slope = math.atan2(TURRET_TOP - ROOF_FRONT_Z, 3.02 - 2.17)
    vent = geo.lathe([(0.0, -0.02), (0.125, -0.02), (0.125, 0.055), (0.11, 0.075), (0.0, 0.075)], 16, axis="Z")
    geo.rotate(vent, slope, "X")
    v.add("vent", geo.move(vent, x=-0.257, y=Y(2.737), z=roof_z(2.737)), kind="paint", bone="turret",
          smooth_angle=50)

    # gun (side/top/front views): curved inner (rotor) mantlet in the turret front, mantlet body 0.51 x 0.29 m with
    # chamfered edges and a round front collar, barrel jacket 0.23 m from u 1.58 to 1.03, L/48 barrel, double-baffle
    # brake; muzzle 1.07 m ahead of the bow
    # rotor: one smooth drum face, 0.78 m wide, 0.76 m radius, running from 2.165 m at u 2.08 down to 1.73 m at u 1.99
    # (front/side views) and leaning back with the turret front; its ends show as the arcs either side of it in the
    # front view (out to 0.445 m, z 1.85-2.09)
    rc_u, rc_z, rr = 2.741, 1.80, 0.758

    def rotor_u(z):  # front face of the rotor at height z
        return rc_u - math.sqrt(rr * rr - (z - rc_z) ** 2)

    def drum(z0, z1, r_front, depth, steps):
        t0, t1 = math.asin((z0 - rc_z) / rr), math.asin((z1 - rc_z) / rr)
        ts = [t1 + (t0 - t1) * k / steps for k in range(steps + 1)]
        front = [(rc_u - r_front * math.cos(t), rc_z + rr * math.sin(t)) for t in ts]
        back = [(rc_u - (r_front - depth) * math.cos(t), rc_z + rr * math.sin(t)) for t in reversed(ts)]
        return P(front + back)

    v.add("mantlet_rotor", geo.prism_x(drum(1.73, 2.165, rr, 0.12, 12), -0.39, 0.39), kind="paint_cast",
          bone="turret", chamfer=0.012)
    for side in (1, -1):
        end = geo.prism_x(drum(1.85, 2.09, rr - 0.006, 0.10, 6), 0.0, 0.06)
        v.add(f"mantlet_rotor_end_{side}", geo.move(end, x=side * 0.385 - (0.06 if side < 0 else 0.0)),
              kind="paint_cast", bone="turret", chamfer=0.02)

    def plate_u(z):  # turret front plate face, leaning back from u 2.10 at the turret ring to u 2.17 at the roof
        return 2.10 + 0.07 * (z - TURRET_Z) / (ROOF_FRONT_Z - TURRET_Z)

    # gunner's vision port, left of the mantlet (front view: faceted octagon centred 0.61 m left at 2.00 m; side view:
    # sticks out to u ~2.03), and the sight aperture between it and the mantlet (dark ellipse at 0.47 m, 1.99 m)
    octa = [(-1.0, -0.45), (-0.62, -1.0), (0.62, -1.0), (1.0, -0.45), (1.0, 0.45), (0.62, 1.0), (-0.62, 1.0),
            (-1.0, 0.45)]
    base = [(0.61 + 0.08 * a, plate_u(2.0 + 0.09 * b) + 0.01, 2.0 + 0.09 * b) for a, b in octa]
    face = [(0.61 + 0.05 * a, plate_u(2.0 + 0.055 * b) - 0.10, 2.0 + 0.055 * b) for a, b in octa]
    v.add("gunner_visor", geo.loft([(x, Y(u), z) for x, u, z in base], [(x, Y(u), z) for x, u, z in face]),
          kind="paint_cast", bone="turret", chamfer=0.006)
    v.add("gunner_visor_slit", geo.box(0.61, Y(plate_u(2.0) - 0.105), 2.0, 0.07, 0.012, 0.014), kind="glass",
          bone="turret")
    from mathutils import Matrix

    sight = geo.cylinder(0.026, 0.05, 12, axis="Y")
    geo.transform(sight, Matrix.Scale(1.4, 4, (0, 0, 1)))
    v.add("sight_port", geo.move(sight, x=0.471, y=Y(plate_u(1.99) - 0.012), z=1.99), kind="glass", bone="turret")
    x0, x1, z0, z1 = -0.20, 0.31, GUN_Z - 0.143, GUN_Z + 0.143
    octo = [(x0, z0 + 0.06), (x0 + 0.10, z0), (x1 - 0.09, z0), (x1, z0 + 0.06), (x1, z1 - 0.06), (x1 - 0.09, z1),
            (x0 + 0.10, z1), (x0, z1 - 0.06)]
    body = geo.loft([(x, Y(2.04), z) for x, z in octo], [(x, Y(1.627), z) for x, z in octo])
    v.add("mantlet", body, kind="paint_cast", bone="turret", chamfer=0.01)
    gx = 0.056  # bore: 5.6 cm left of the centreline (front view)
    v.add("mantlet_collar", geo.move(geo.cylinder(0.143, 0.06, 20, axis="Y"), x=gx, y=Y(1.605), z=GUN_Z),
          kind="paint_cast", bone="turret", chamfer=0.008)
    # coaxial MG port in the rotor, right of the gun (front view: dark round at 0.27 m right, 1.97 m)
    v.add("coax_collar", geo.move(geo.cylinder(0.05, 0.04, 12, axis="Y"), x=-0.27, y=Y(rotor_u(1.97) - 0.01),
                                  z=1.97), kind="paint_cast", bone="turret", chamfer=0.006)
    v.add("coax_port", geo.move(geo.cylinder(0.028, 0.035, 10, axis="Y"), x=-0.27, y=Y(rotor_u(1.97) - 0.03),
                                z=1.97), kind="steel", bone="turret")
    face_u = 1.60
    muzzle_u = -1.074
    brake_l = 0.278
    d = lambda u: face_u - u  # distance forward of the face
    barrel = parts.gun_barrel([(0.1145, 0.0), (0.1145, d(1.069)), (0.118, d(1.069)), (0.118, d(1.028)),
                               (0.0655, d(1.028)), (0.0655, d(0.10)), (0.061, d(0.10)), (0.061, d(-0.65)),
                               (0.072, d(-0.65)), (0.072, d(-0.73)), (0.061, d(-0.73)),
                               (0.061, d(muzzle_u + brake_l))], 16)
    geo.move(barrel, x=gx, y=Y(face_u), z=GUN_Z)
    brake = geo.move(parts.muzzle_brake_double(0.112, brake_l, 16), x=gx, y=Y(muzzle_u + brake_l), z=GUN_Z)
    v.add("gun", geo.merge(barrel, brake), kind="steel_paint", bone="barrel_base")
    v.locator("barrel", (gx, Y(muzzle_u), GUN_Z), "barrel_tip")
    v.bone("barrel_base", (gx, Y(2.0), GUN_Z), "turret")
    v.bone("barrel_tip", (gx, Y(muzzle_u), GUN_Z), "barrel_base")
    v.bone("turret", (tx, ty, TURRET_Z), "chassie")

    # turret Schürzen (8 mm), centred on the turret: side panels from u 2.07 (flaring out to 1.21 m by u 2.8),
    # top edge 2.23 m, falling to 2.15 m over the front metre (side view), bottom at 1.73 m; rear wrap curving in
    # from u 3.9 round the bin to u 4.85 (top view); bent front panels between the side panel and the mantlet
    # (the front-view "X" is the fold from the outer top corner to the inner bottom corner)
    zb = 1.73
    skirt_top = lambda u: 2.152 + 0.08 * min(1.0, (u - 2.07) / 0.98)
    plan = [(1.02, 2.07), (1.06, 2.32), (1.19, 2.68), (1.21, 2.80), (1.207, 3.90), (1.08, 4.24), (0.885, 4.49),
            (0.67, 4.67), (0.386, 4.79), (0.0, 4.845)]
    for side in (1, -1):
        pts = [(tx + side * x, u) for x, u in plan]
        v.add(f"turret_skirt_{side}", skirt_wall(pts, zb, skirt_top, 0.014, (tx, 3.4)), kind="skirt", bone="turret",
              smooth_angle=20, chamfer=0.004)
        front = [(1.02, 2.075, skirt_top(2.07)), (0.69, 2.095, 2.20), (0.66, 1.985, 2.03), (0.64, 1.982, zb),
                 (1.02, 2.07, zb)]
        v.add(f"turret_skirt_front_{side}", plate([(tx + side * x, Y(u), z) for x, u, z in front], (0, 0.014, 0)),
              kind="skirt", bone="turret", chamfer=0.003)
        # mounting arms from the turret roof edge out to the top of the skirt (top view)
        for u0, u1 in ((2.47, 2.33), (3.02, 2.78), (3.86, 4.05)):
            a = (tx + side * 0.69, Y(u0), roof_z(u0) - 0.03)
            b = (tx + side * 1.20, Y(u1), skirt_top(u1) - 0.03)
            v.add(f"skirt_mount_{side}_{u0}", bar(a, b, 0.05, 0.03), kind="paint", bone="turret", chamfer=0.006)
        # two-leaf door over the turret side hatch (side view u 3.13-3.83, full skirt height)
        for k, (u0, u1) in enumerate(((3.13, 3.475), (3.485, 3.83))):
            zt = skirt_top((u0 + u1) / 2) - 0.012
            v.add(f"skirt_door_{side}_{k}", geo.box(tx + side * 1.223, Y((u0 + u1) / 2), (zb + zt) / 2 + 0.006,
                                                    0.012, u1 - u0, zt - zb - 0.012),
                  kind="skirt", bone="turret", chamfer=0.003)


def skirt_wall(plan, z0, ztop, thickness, centre):
    """Thin wall along a plan polyline [(x, u), ...] with its top edge at z = ztop(u); the thickness grows away
    from the plan point centre (x, u) (the turret)."""
    import bmesh
    from mathutils import Vector

    pts = [Vector((x, Y(u))) for x, u in plan]
    c = Vector((centre[0], Y(centre[1])))
    n = len(pts)
    bm = bmesh.new()
    rows = []
    for i, p in enumerate(pts):
        d0 = (pts[i] - pts[i - 1]) if i > 0 else (pts[1] - pts[0])
        d1 = (pts[i + 1] - pts[i]) if i < n - 1 else d0
        d = (d0.normalized() + d1.normalized()).normalized()
        nrm = Vector((d.y, -d.x))
        if nrm.dot(p - c) < 0:
            nrm = -nrm
        o = p + nrm * thickness
        zt = ztop(plan[i][1])
        rows.append([bm.verts.new((p.x, p.y, z0)), bm.verts.new((p.x, p.y, zt)), bm.verts.new((o.x, o.y, zt)),
                     bm.verts.new((o.x, o.y, z0))])
    for r0, r1 in zip(rows, rows[1:]):
        for k in range(4):
            k2 = (k + 1) % 4
            bm.faces.new((r0[k], r1[k], r1[k2], r0[k2]))
    bm.faces.new(rows[0])
    bm.faces.new(list(reversed(rows[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def plate(points, offset):
    """Thin plate from a 3D polygon (fan-triangulated from its first vertex, so it may be bent) pushed by offset."""
    import bmesh
    from mathutils import Vector

    off = Vector(offset)
    bm = bmesh.new()
    a = [bm.verts.new(Vector(p)) for p in points]
    b = [bm.verts.new(Vector(p) + off) for p in points]
    n = len(points)
    for i in range(1, n - 1):
        bm.faces.new((a[0], a[i], a[i + 1]))
        bm.faces.new((b[0], b[i + 1], b[i]))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], b[i], b[j], a[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bar(a, b, width, height):
    """Rectangular bar from point a to point b (mounting arms)."""
    from mathutils import Vector

    a, b = Vector(a), Vector(b)
    d = b - a
    bm = geo.box(0, 0, 0, width, d.length, height)
    geo.transform(bm, d.to_track_quat("Y", "Z").to_matrix().to_4x4())
    return geo.move(bm, *((a + b) / 2))


def fittings(v):
    front = Y(FRONT_U[0])
    # driver's visor (Fahrersehklappe 80) on the left, MG ball mount on the right (front view)
    # visor (front view): base plate 0.54 x 0.22 m, then an armoured hood over a 3.6 cm vision slit and a lower lip,
    # both 0.42 m wide and standing 10 cm proud; the hood's front face slopes back (side view)
    v.add("driver_visor", geo.box(0.36, front - 0.015, 1.38, 0.54, 0.03, 0.22), kind="paint_cast", chamfer=0.02)
    hood = [(0.95, 1.389), (FRONT_U[0], 1.389), (FRONT_U[0], 1.475), (1.00, 1.475)]
    v.add("driver_visor_hood", geo.prism_x(P(hood), 0.15, 0.57), kind="paint_cast", chamfer=0.01)
    v.add("driver_visor_lip", geo.box(0.36, Y(1.0), 1.319, 0.42, 0.10, 0.068), kind="paint_cast", chamfer=0.01)
    v.add("driver_visor_glass", geo.box(0.36, Y(1.015), 1.371, 0.37, 0.01, 0.036), kind="glass")
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

    # headlights on the front guards, behind the mudguards (front view: left one 1.06 m out at 1.40 m, right one
    # 1.35 m out at 1.37 m; top view u 0.46-0.62), each on a short post
    for side, x, z in ((1, 1.06, 1.40), (-1, -1.35, 1.37)):
        lamp = geo.merge(parts.headlight(0.085, 0.12), geo.cylinder(0.018, z - FENDER_Z, 6, axis="Z",
                                                                     center=(0, 0.07, -(z - FENDER_Z) / 2)))
        v.add(f"headlight_{side}", geo.move(lamp, x=x, y=Y(0.60), z=z), kind="paint_cast")

    # engine deck: two access hatches, cooling louvres either side (top view u 4.33-4.79, 0.46-0.86 m out)
    for side in (1, -1):
        v.add(f"engine_hatch_{side}", geo.box(side * 0.36, Y(4.60), ROOF_Z + 0.02, 0.66, 1.25, 0.035), kind="paint",
              chamfer=0.01)
        v.add(f"louvre_{side}", geo.box(side * 0.66, Y(4.56), ROOF_Z + 0.015, 0.40, 0.46, 0.03), kind="paint",
              chamfer=0.008)

    # rear: main muffler across the rear plate, offset to the right (rear view x -0.80..+0.31, z 0.95-1.27; top
    # view u 5.45-5.71), short tail pipe on top angled to the left, auxiliary (generator) muffler under its left end
    v.add("muffler", geo.move(parts.muffler(0.159, 1.07), x=-0.243, y=Y(REAR_U + 0.16), z=1.106), kind="exhaust")
    tail = geo.cylinder(0.04, 0.14, 8, axis="Z")
    geo.rotate(tail, math.radians(-35), "Y")
    v.add("tailpipe", geo.move(tail, x=-0.13, y=Y(REAR_U + 0.16), z=1.30), kind="exhaust")
    v.add("aux_muffler", geo.chamfer(geo.box(0.495, Y(REAR_U + 0.12), 1.02, 0.30, 0.18, 0.29), 0.06), kind="exhaust")
    v.locator("right_exhaust", (-0.10, Y(REAR_U + 0.16), 1.40), "chassie")
    v.locator("left_exhaust", (0.495, Y(REAR_U + 0.12), 1.20), "chassie")

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
    """Hull Schürzen (5 mm). The drawing shows the hanger rail and its brackets but not the plates: rail 1.59 m out
    (top view, u 0.58-5.50), 1.54-1.57 m high, sloping down at both ends (side view); 5 plates per side hang on it."""
    rail_top = [(0.58, 1.525), (1.08, 1.571), (5.05, 1.571), (5.50, 1.505)]
    rail = rail_top + [(u, z - 0.034) for u, z in reversed(rail_top)]
    for side in (1, -1):
        xr = side * 1.59
        v.add(f"skirt_rail_{side}", geo.prism_x(P(rail), xr - 0.02, xr + 0.02), kind="paint", chamfer=0.004)
        # brackets from the superstructure side out to the rail (top view u 1.35, 2.44, 3.76, 4.91)
        for b, u in enumerate((1.35, 2.44, 3.76, 4.91)):
            v.add(f"skirt_bracket_{side}_{b}", geo.box(side * (SUPER_X + 1.59) / 2, Y(u), 1.52, 1.59 - SUPER_X, 0.05,
                                                       0.04), kind="paint", chamfer=0.006)
        x = side * 1.625  # plates hang just outside the rail
        top = 1.575
        for i in range(5):
            u0 = 0.62 + i * 0.97
            plate = [(Y(u0), top), (Y(u0), 0.62), (Y(u0 + 1.02), 0.62), (Y(u0 + 1.02), top)]
            if i == 0:  # leading plate: top edge follows the rail down to its front end, long diagonal to the bottom
                plate = [(Y(0.58), 1.53), (Y(0.58), 1.40), (Y(1.04), 0.62), (Y(u0 + 1.02), 0.62),
                         (Y(u0 + 1.02), top), (Y(1.08), top)]
            elif i == 4:  # trailing plate: top edge follows the rail down, rear corner cut towards the idler
                plate = [(Y(u0), top), (Y(u0), 0.62), (Y(u0 + 0.86), 0.62), (Y(u0 + 0.98), 0.78),
                         (Y(u0 + 0.98), 1.505), (Y(5.05), top)]
            off = 0.008 * (i % 2)
            v.add(f"skirt_{side}_{i}", geo.prism_x(plate, x - 0.006 + side * off, x + 0.006 + side * off),
                  kind="skirt", smooth_angle=30, chamfer=0.005)


def rig(v):
    v.bone("root", (0, 0, 0))
    v.bone("tank_base", (0, 0, 0), "root")
    v.bone("chassie", (0, 0, 0.9), "tank_base")
    v.bone("wheel_suspention", (0, 0, WHEEL_Z), "tank_base")
