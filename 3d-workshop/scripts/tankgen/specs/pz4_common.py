"""Shared Panzer IV construction, factored out of the approved Ausf. H (ger_pz4h).

Every builder takes the variant's spec module `S` and reads its dimensions from it, so the *method* is shared while
the *numbers* stay per drawing: a variant only lands here where its geometry is built the same way. Coordinates as
in the specs: u = metres back from the bow tip, z = metres above ground, x = metres to the vehicle's left;
S.Y(u) turns u into model Y.

Constants a spec provides (see ger_pz4h.py for the documented values):
  running gear: TRACK_W, TRACK_X, TRACK_T, TRACK_PITCH, WHEEL_R, WHEEL_Z, WHEELS_U, SPROCKET, SPROCKET_TEETH, IDLER,
                ROLLERS_U, ROLLER_Z, ROLLER_R, LOWER_X
  hull:         SUPER_X, DECK_X, FENDER_Z, ROOF_Z, GLACIS, FRONT_U, REAR_U, DECK_END_U, LOWER_PROFILE, DECK_PROFILE,
                GUARD_PROFILE, GUARD_BOX, GUARD_INNER, GUARD_LIP
"""

import math

from .. import geo, parts


# ---- small geometry helpers (thin plates, shells, arms) -------------------------------------------------------
def P(S, points):
    """[(u, z), ...] -> side-profile [(Y, z), ...] for geo.prism_x."""
    return [(S.Y(u), z) for u, z in points]


def station_shell(S, stations, z0):
    """Armour shell from fore-aft stations [(u_base, half_w_base, u_top, half_w_top, z_top), ...] about x = 0:
    planar-ish side walls between stations, a roof that can bend at any station, flat floor at z0."""
    import bmesh

    bm = bmesh.new()
    rows = []
    for ub, wb, ut, wt, zt in stations:
        rows.append([bm.verts.new((-wb, S.Y(ub), z0)), bm.verts.new((wb, S.Y(ub), z0)),
                     bm.verts.new((wt, S.Y(ut), zt)), bm.verts.new((-wt, S.Y(ut), zt))])
    for r0, r1 in zip(rows, rows[1:]):
        for k in range(4):
            k2 = (k + 1) % 4
            bm.faces.new((r0[k], r0[k2], r1[k2], r1[k]))
    bm.faces.new(rows[0])
    bm.faces.new(list(reversed(rows[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def skirt_wall(S, plan, z0, ztop, thickness, centre):
    """Thin wall along a plan polyline [(x, u), ...] with its top edge at z = ztop(u); the thickness grows away
    from the plan point centre (x, u) (the turret)."""
    import bmesh
    from mathutils import Vector

    pts = [Vector((x, S.Y(u))) for x, u in plan]
    c = Vector((centre[0], S.Y(centre[1])))
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


def drum_profile(S, rc_u, rc_z, rr, z0, z1, r_front, depth, steps):
    """Side profile of a curved (cylindrical, axis along x) mantlet face: centre (rc_u, rc_z), radius rr, between
    heights z0 and z1, `depth` thick. One smooth curved face, never a bent flat plate."""
    t0, t1 = math.asin((z0 - rc_z) / rr), math.asin((z1 - rc_z) / rr)
    ts = [t1 + (t0 - t1) * k / steps for k in range(steps + 1)]
    front = [(rc_u - r_front * math.cos(t), rc_z + rr * math.sin(t)) for t in ts]
    back = [(rc_u - (r_front - depth) * math.cos(t), rc_z + rr * math.sin(t)) for t in reversed(ts)]
    return P(S, front + back)


# ---- rig / animation ------------------------------------------------------------------------------------------
def wheel_info(S, scale):
    """{bone: (radius in game units, rotational symmetry step or None)} for the move animation.
    Road wheels carry camo, so they turn whole revolutions; the rest are rotation-neutral."""
    info = {"wheel_01": (S.SPROCKET[2] * scale, 2 * math.pi / S.SPROCKET_TEETH),
            "wheel_02": (S.IDLER[2] * scale, 2 * math.pi / 90)}
    for i in range(len(S.WHEELS_U)):
        info[f"wheel_{3 + i:02d}"] = (S.WHEEL_R * scale, None)
    for i in range(len(S.ROLLERS_U)):
        info[f"wheel_{3 + len(S.WHEELS_U) + i:02d}"] = (S.ROLLER_R * scale, 2 * math.pi / 90)
    return info


def rig(v, S):
    v.bone("root", (0, 0, 0))
    v.bone("tank_base", (0, 0, 0), "root")
    v.bone("chassie", (0, 0, 0.9), "tank_base")
    v.bone("wheel_suspention", (0, 0, S.WHEEL_Z), "tank_base")


# ---- hull -----------------------------------------------------------------------------------------------------
def lower_hull(v, S):
    """Lower hull between the tracks from its side profile (belly, nose plates, glacis, sides, rear plate)."""
    v.add("hull_lower", geo.prism_x(P(S, S.LOWER_PROFILE), -S.LOWER_X, S.LOWER_X), chamfer=0.025)


def engine_deck(v, S):
    v.add("engine_deck", geo.prism_x(P(S, S.DECK_PROFILE), -S.DECK_X, S.DECK_X), chamfer=0.025)


def track_guards(v, S):
    """Track guards: plate at fender height with an outer lip, front mudguard sloping down to the bow and boxed in,
    rear mudguard sloping down to the tail; ahead of the superstructure the guard runs in to the lower hull."""
    outer = S.TRACK_X + S.TRACK_W / 2 + 0.02
    v.mirror_x("guard", lambda: geo.prism_x(P(S, S.GUARD_PROFILE), S.SUPER_X - 0.02, outer), kind="paint")
    v.mirror_x("guard_inner", lambda: geo.prism_x(P(S, S.GUARD_INNER), S.LOWER_X, S.SUPER_X - 0.02), kind="paint")
    v.mirror_x("guard_lip", lambda: geo.prism_x(P(S, S.GUARD_LIP), outer - 0.012, outer), kind="paint")
    v.mirror_x("guard_box_side", lambda: geo.prism_x(P(S, S.GUARD_BOX), outer - 0.012, outer), kind="paint")
    z0, z1 = S.GUARD_BOX[0][1], S.GUARD_BOX[1][1]
    v.mirror_x("guard_box_front", lambda: geo.prism_x(P(S, [(0.0, z0), (0.012, z0), (0.012, z1), (0.0, z1)]),
                                                       S.LOWER_X, outer), kind="paint")


def tow_shackles(v, S, front_z, rear_z, x=0.62):
    for side in (1, -1):
        v.add(f"tow_front_{side}", geo.move(parts.tow_shackle(), x=side * x, y=S.Y(0.03), z=front_z), kind="steel")
        v.add(f"tow_rear_{side}", geo.move(parts.tow_shackle(), x=side * x, y=S.Y(S.REAR_U + 0.03), z=rear_z),
              kind="steel")


def glacis_hatches(v, S, hatches):
    """Hatches lying on the glacis: [(name, x, width, u0, u1), ...] (top view)."""
    (gu0, gz0), (gu1, gz1) = S.GLACIS
    slope = math.atan2(gz1 - gz0, gu1 - gu0)
    for name, x, w, u0, u1 in hatches:
        um = (u0 + u1) / 2
        h = geo.box(0, 0, 0, w, (u1 - u0) / math.cos(slope), 0.035)
        geo.rotate(h, slope, "X")
        geo.move(h, x=x, y=S.Y(um), z=gz0 + (um - gu0) * math.tan(slope) + 0.015)
        v.add(f"glacis_{name}", h, kind="paint", chamfer=0.01)


def driver_visor(v, S, x, z, front_u, plate_w=0.54, plate_h=0.22, hood_w=0.42, depth=0.10, slit_h=0.036,
                 hood_top=None, lip_h=0.068):
    """Fahrersehklappe: base plate on the superstructure front, an armoured hood over the glass vision slit and a
    lower lip, both standing `depth` proud; the hood's front face slopes back (side view)."""
    front = S.Y(front_u)
    v.add("driver_visor", geo.box(x, front - 0.015, z, plate_w, 0.03, plate_h), kind="paint_cast", chamfer=0.02)
    slit_z = z - 0.009
    zt = hood_top if hood_top is not None else z + 0.095
    hood = [(front_u - depth, slit_z + slit_h / 2), (front_u, slit_z + slit_h / 2), (front_u, zt),
            (front_u - depth + 0.05, zt)]
    v.add("driver_visor_hood", geo.prism_x(P(S, hood), x - hood_w / 2, x + hood_w / 2), kind="paint_cast",
          chamfer=0.01)
    v.add("driver_visor_lip", geo.box(x, S.Y(front_u - depth + 0.05), slit_z - slit_h / 2 - lip_h / 2, hood_w,
                                      depth, lip_h), kind="paint_cast", chamfer=0.01)
    v.add("driver_visor_glass", geo.box(x, S.Y(front_u - depth + 0.065), slit_z, hood_w - 0.05, 0.01, slit_h),
          kind="glass")


def hull_mg(v, S, x, z, front_u, ball_r=0.16, mg_len=0.36):
    """Kugelblende: ball mount with the MG 34 barrel jacket."""
    front = S.Y(front_u)
    v.add("ball_mount", geo.move(parts.ball_mount(ball_r), x=x, y=front - 0.01, z=z), kind="paint_cast")
    v.add("hull_mg", geo.move(parts.mg_barrel(mg_len), x=x, y=front - 0.12, z=z), kind="steel")


def headlights(v, S, lamps, u=0.60):
    """Headlights on posts on the front guards: [(side, x, z), ...]."""
    for side, x, z in lamps:
        lamp = geo.merge(parts.headlight(0.085, 0.12), geo.cylinder(0.018, z - S.FENDER_Z, 6, axis="Z",
                                                                     center=(0, 0.07, -(z - S.FENDER_Z) / 2)))
        v.add(f"headlight_{side}", geo.move(lamp, x=x, y=S.Y(u), z=z), kind="paint_cast")


def deck_hatches(v, S, crew_u=1.645, engine_u=4.60, louvre_u=4.56):
    """Crew hatches on the superstructure roof either side, engine access hatches and cooling louvres."""
    for side in (1, -1):
        v.add(f"crew_hatch_{side}", geo.box(side * 0.69, S.Y(crew_u), S.ROOF_Z + 0.02, 0.52, 0.50, 0.04),
              kind="paint", chamfer=0.012)
    for side in (1, -1):
        v.add(f"engine_hatch_{side}", geo.box(side * 0.36, S.Y(engine_u), S.ROOF_Z + 0.02, 0.66, 1.25, 0.035),
              kind="paint", chamfer=0.01)
        v.add(f"louvre_{side}", geo.box(side * 0.66, S.Y(louvre_u), S.ROOF_Z + 0.015, 0.40, 0.46, 0.03),
              kind="paint", chamfer=0.008)


def rear_mufflers(v, S, main=(-0.243, 0.16, 1.106, 0.159, 1.07), aux=(0.495, 0.12, 1.02)):
    """Main muffler across the rear plate (x, du behind the rear plate, z, radius, length) with a short tail pipe
    angled to the left, and the auxiliary (turret traverse generator) muffler under its left end."""
    mx, mdu, mz, mr, ml = main
    v.add("muffler", geo.move(parts.muffler(mr, ml), x=mx, y=S.Y(S.REAR_U + mdu), z=mz), kind="exhaust")
    tail = geo.cylinder(0.04, 0.14, 8, axis="Z")
    geo.rotate(tail, math.radians(-35), "Y")
    v.add("tailpipe", geo.move(tail, x=mx + 0.113, y=S.Y(S.REAR_U + mdu), z=mz + 0.194), kind="exhaust")
    v.locator("right_exhaust", (mx + 0.143, S.Y(S.REAR_U + mdu), mz + 0.294), "chassie")
    if aux:
        ax, adu, az = aux
        v.add("aux_muffler", geo.chamfer(geo.box(ax, S.Y(S.REAR_U + adu), az, 0.30, 0.18, 0.29), 0.06),
              kind="exhaust")
        v.locator("left_exhaust", (ax, S.Y(S.REAR_U + adu), az + 0.18), "chassie")
    else:
        v.locator("left_exhaust", (-mx, S.Y(S.REAR_U + mdu), mz + 0.294), "chassie")


def tools_and_locators(v, S, shovel_u=1.6, jack_u=5.10, antenna=(-1.08, 4.05)):
    v.add("shovel", geo.move(parts.shovel(1.05), x=1.32, y=S.Y(shovel_u), z=S.FENDER_Z + 0.03), kind="wood")
    v.add("jack", geo.box(-1.30, S.Y(jack_u), S.FENDER_Z + 0.11, 0.18, 0.28, 0.22), kind="paint", chamfer=0.015)
    for k, x in enumerate((1.28, 1.32)):
        v.add(f"tow_cable_{k}", geo.move(parts.tool(2.4, 0.022, 6), x=x, y=S.Y(3.6), z=S.FENDER_Z + 0.03),
              kind="steel")
    v.add("antenna_base", geo.move(geo.cylinder(0.04, 0.10, 8, axis="Z"), x=antenna[0], y=S.Y(antenna[1]),
                                   z=S.ROOF_Z + 0.05), kind="paint")
    v.locator("left_tracks", (S.TRACK_X, S.Y(5.70), 0.0), "tank_base")
    v.locator("right_tracks", (-S.TRACK_X, S.Y(5.70), 0.0), "tank_base")


# ---- running gear ---------------------------------------------------------------------------------------------
def running_gear(v, S, sprocket_maker=None, idler_maker=None):
    circles = [(S.Y(S.SPROCKET[0]), S.SPROCKET[1], S.SPROCKET[2]), (S.Y(S.IDLER[0]), S.IDLER[1], S.IDLER[2])]
    circles += [(S.Y(u), S.WHEEL_Z, S.WHEEL_R) for u in S.WHEELS_U]
    circles += [(S.Y(u), S.ROLLER_Z, S.ROLLER_R) for u in S.ROLLERS_U]
    for side, suffix in ((1, "l"), (-1, "r")):
        v.add(f"track_{suffix}", parts.track_belt(circles, side * S.TRACK_X, S.TRACK_W, S.TRACK_T, 0.12, 0.48),
              kind="track", bone="tank_base", smooth_angle=60)

    sprocket_maker = sprocket_maker or (lambda: parts.sprocket(S.SPROCKET[2], S.SPROCKET_TEETH, 0.06, 0.10, 0.11))
    idler_maker = idler_maker or (lambda: parts.idler(S.IDLER[2], 0.06, 0.10))
    bone_i = 1
    for label, (u, z, r), maker in (("sprocket", S.SPROCKET, sprocket_maker), ("idler", S.IDLER, idler_maker)):
        bname = f"wheel_{bone_i:02d}"
        v.bone(bname, (0, S.Y(u), z), "wheel_suspention")
        for side in (1, -1):
            bm = maker()
            if side < 0:
                geo.rotate(bm, math.pi, "Z")
            v.add(f"{label}_{side}", geo.move(bm, x=side * S.TRACK_X, y=S.Y(u), z=z), kind="wheel_plain", bone=bname)
            hub_len = S.TRACK_X - S.LOWER_X - 0.12
            stub = geo.cylinder(0.14 if label == "sprocket" else 0.08, hub_len, 12, axis="X",
                                center=(side * (S.LOWER_X + hub_len / 2), S.Y(u), z))
            v.add(f"{label}_hub_{side}", stub, kind="paint", chamfer=0.01)
        bone_i += 1

    for i, u in enumerate(S.WHEELS_U):
        bname = f"wheel_{bone_i:02d}"
        v.bone(bname, (0, S.Y(u), S.WHEEL_Z), "wheel_suspention")
        for side in (1, -1):
            for label, bm, kind in zip(("disc", "tyre"), parts.double_road_wheel(S.WHEEL_R, 0.075, 0.07, 0.07, 16),
                                       ("rubber_wheel", "rubber")):
                if side < 0:
                    geo.rotate(bm, math.pi, "Z")
                v.add(f"roadwheel_{label}_{i}_{side}", geo.move(bm, x=side * S.TRACK_X, y=S.Y(u), z=S.WHEEL_Z),
                      kind=kind, bone=bname)
        bone_i += 1

    for i, u in enumerate(S.ROLLERS_U):
        bname = f"wheel_{bone_i:02d}"
        v.bone(bname, (0, S.Y(u), S.ROLLER_Z), "wheel_suspention")
        for side in (1, -1):
            bm = parts.return_roller(S.ROLLER_R, 0.16, 10)
            if side < 0:
                geo.rotate(bm, math.pi, "Z")
            v.add(f"roller_{i}_{side}", geo.move(bm, x=side * S.TRACK_X, y=S.Y(u), z=S.ROLLER_Z), kind="wheel_plain",
                  bone=bname)
        bone_i += 1

    # leaf-spring bogies: bracket, quarter-elliptic spring housing and the two wheel arms (side view)
    for b in range(4):
        u0, u1 = S.WHEELS_U[b * 2], S.WHEELS_U[b * 2 + 1]
        um = (u0 + u1) / 2
        for side in (1, -1):
            x = side * (S.LOWER_X + 0.08)
            bracket = geo.chamfer(geo.box(x, S.Y(um), 0.47, 0.14, 0.34, 0.22), 0.02)
            spring = geo.chamfer(geo.box(x, S.Y(um), 0.62, 0.12, 0.58, 0.08), 0.015)
            arms = geo.box(x + side * 0.03, S.Y(um), S.WHEEL_Z + 0.06, 0.07, u1 - u0, 0.07)
            v.add(f"bogie_{b}_{side}", geo.merge(bracket, spring, arms), kind="paint")


# ---- turret ---------------------------------------------------------------------------------------------------
def cupola_late(v, S, cup_x, cup_u, cz, prof, hatch_prof, cover_r=0.44, cover_z=2.497):
    """Cast commander's cupola (Ausf. F2 late / G / H / J): stepped lathe profile [(r, z), ...] traced from the
    side and front views, a domed hatch and six vision-block covers on the drum."""
    v.add("cupola", geo.move(geo.lathe([(r, z - cz) for r, z in prof], 24, axis="Z"), x=cup_x, y=S.Y(cup_u), z=cz),
          kind="paint_cast", bone="turret", smooth_angle=50)
    hatch = geo.lathe(hatch_prof, 24, axis="Z")
    v.add("cupola_hatch", geo.move(hatch, x=cup_x, y=S.Y(cup_u)), kind="paint_cast", bone="turret", smooth_angle=50)
    for k in range(6):  # vision-block covers, one per segment of the drum
        a = 2 * math.pi * (k + 0.5) / 6 + math.pi / 2
        cover = geo.box(0, 0, 0, 0.016, 0.22, 0.05)
        geo.move(cover, x=cover_r, z=cover_z)
        geo.rotate(cover, a, "Z")
        v.add(f"cupola_block_{k}", geo.move(cover, x=cup_x, y=S.Y(cup_u)), kind="paint_cast", bone="turret",
              chamfer=0.006)


def roof_vent(v, S, x, u, z, slope):
    """Fan ventilator cover on the (sloping) turret roof plate."""
    vent = geo.lathe([(0.0, -0.02), (0.125, -0.02), (0.125, 0.055), (0.11, 0.075), (0.0, 0.075)], 16, axis="Z")
    geo.rotate(vent, slope, "X")
    v.add("vent", geo.move(vent, x=x, y=S.Y(u), z=z), kind="paint", bone="turret", smooth_angle=50)


def faceted_port(v, S, name, x, z, plate_u, half_w, half_h, depth, slit_w, slit_h=0.014, face_k=0.6,
                 glass_name=None):
    """Faceted (octagonal) vision port standing proud of a front plate, with a glass slit in its face.
    plate_u(z) gives the plate face at height z."""
    octa = [(-1.0, -0.45), (-0.62, -1.0), (0.62, -1.0), (1.0, -0.45), (1.0, 0.45), (0.62, 1.0), (-0.62, 1.0),
            (-1.0, 0.45)]
    base = [(x + half_w * a, plate_u(z + half_h * b) + 0.01, z + half_h * b) for a, b in octa]
    fw, fh = half_w * 0.625, half_h * face_k
    face = [(x + fw * a, plate_u(z + fh * b) - depth, z + fh * b) for a, b in octa]
    v.add(name, geo.loft([(px, S.Y(u), pz) for px, u, pz in base], [(px, S.Y(u), pz) for px, u, pz in face]),
          kind="paint_cast", bone="turret", chamfer=0.006)
    v.add(glass_name or name + "_slit", geo.box(x, S.Y(plate_u(z) - depth - 0.005), z, slit_w, 0.012, slit_h),
          kind="glass", bone="turret")


def gun(v, S, gx, gz, face_u, sections, muzzle_u, brake, segments=16, base_u=2.0):
    """Gun barrel lathed from [(radius, u), ...] going forward from the mantlet face at face_u, with a muzzle brake
    maker(brake) -> bmesh (pivot at its rear end) or None; rigged to barrel_base/barrel_tip."""
    d = lambda u: face_u - u  # distance forward of the face
    barrel = parts.gun_barrel([(r, d(u)) for r, u in sections], segments)
    geo.move(barrel, x=gx, y=S.Y(face_u), z=gz)
    pieces = [barrel]
    if brake:
        maker, brake_l = brake
        pieces.append(geo.move(maker(), x=gx, y=S.Y(muzzle_u + brake_l), z=gz))
    v.add("gun", geo.merge(*pieces), kind="steel_paint", bone="barrel_base")
    v.locator("barrel", (gx, S.Y(muzzle_u), gz), "barrel_tip")
    v.bone("barrel_base", (gx, S.Y(base_u), gz), "turret")
    v.bone("barrel_tip", (gx, S.Y(muzzle_u), gz), "barrel_base")


def turret_bin(v, S, tx, u0, u_mid, u1, half_w, z0, lid_front, lid_back, flat_u):
    """Rear stowage bin (Gepäckkasten): D-shaped in plan, lid flat then sloping down at the back."""
    r = u1 - u_mid
    plan = [(-half_w, u0), (half_w, u0), (half_w, u_mid)]
    plan += [(half_w * math.cos(a), u_mid + r * math.sin(a)) for a in (math.radians(d) for d in range(20, 161, 20))]
    plan += [(-half_w, u_mid)]
    lid = lambda u: lid_front - (lid_front - lid_back) * max(0.0, u - flat_u) / max(1e-6, u1 - flat_u)
    v.add("turret_bin", geo.loft([(tx + x, S.Y(u), z0) for x, u in plan],
                                 [(tx + x, S.Y(u), lid(u)) for x, u in plan]),
          kind="paint", bone="turret", chamfer=0.02)


def hull_schuerzen(v, S, rail_top, brackets_u, plates, x_rail=1.59, x_plate=1.625):
    """Hull Schürzen (5 mm): a hanger rail sloping down at both ends, brackets from the superstructure side out to
    it, and plates hanging just outside the rail. plates: one side-profile polygon [(u, z), ...] per plate."""
    rail = rail_top + [(u, z - 0.034) for u, z in reversed(rail_top)]
    for side in (1, -1):
        xr = side * x_rail
        v.add(f"skirt_rail_{side}", geo.prism_x(P(S, rail), xr - 0.02, xr + 0.02), kind="paint", chamfer=0.004)
        for b, u in enumerate(brackets_u):
            v.add(f"skirt_bracket_{side}_{b}", geo.box(side * (S.SUPER_X + x_rail) / 2, S.Y(u), 1.52,
                                                       x_rail - S.SUPER_X, 0.05, 0.04), kind="paint", chamfer=0.006)
        x = side * x_plate
        for i, pl in enumerate(plates):
            off = 0.008 * (i % 2)
            v.add(f"skirt_{side}_{i}", geo.prism_x(P(S, pl), x - 0.006 + side * off, x + 0.006 + side * off),
                  kind="skirt", smooth_angle=30, chamfer=0.005)
