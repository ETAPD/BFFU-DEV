"""Shared Panzer III construction. Same conventions and helpers as the Panzer IV (pz4_common): every builder takes
the variant's spec module S and reads its dimensions from it, u = metres back from the front of the track guards,
z = up from the ground, x = to the vehicle's left.

A spec provides, besides the running-gear constants pz4_common.running_gear reads (TRACK_*, WHEEL_*, WHEELS_U,
SPROCKET, IDLER, ROLLERS_U, ROLLER_*, LOWER_X):
  HULL_X           half-width of the hull and superstructure
  LOWER_PROFILE    side profile [(u, z), ...] of the lower hull (nose, glacis, belly, rear)
  SUPER_PROFILE    side profile of the superstructure + engine deck (front plate, roof, deck, rear slope)
  GUARD_PROFILE    side profile of the track guards (front and rear mudguards, guard plate)
  TURRET_STATIONS  station list for pz4_common.station_shell; TURRET_BIN (+ TURRET_BIN_Z) for the rear stowage bin
"""

import math

from .. import geo, parts
from . import pz4_common as c


def hull(v, S):
    v.add("hull_lower", geo.prism_x(c.P(S, S.LOWER_PROFILE), -S.HULL_X, S.HULL_X), chamfer=0.02)
    v.add("superstructure", geo.prism_x(c.P(S, S.SUPER_PROFILE), -S.HULL_X, S.HULL_X), chamfer=0.02)
    outer = S.TRACK_X + S.TRACK_W / 2 + 0.02
    v.mirror_x("guard", lambda: geo.prism_x(c.P(S, S.GUARD_PROFILE), S.HULL_X - 0.01, outer), kind="paint")
    v.mirror_x("guard_lip", lambda: geo.prism_x(c.P(S, S.GUARD_LIP), outer - 0.012, outer), kind="paint")


def torsion_suspension(v, S, arm_len=0.30, shocks=(0, 5)):
    """Torsion-bar suspension (Ausf. E on): a trailing arm from each road wheel hub forward to its torsion bar in the
    hull side (the last pair trails backward), bump stops, and shock absorbers on the first and last wheels."""
    for i, u in enumerate(S.WHEELS_U):
        d = -1 if i < len(S.WHEELS_U) // 2 else 1  # front three arms point forward, rear three backward
        d = -1 if getattr(S, "ARMS_FORWARD", True) else d
        for side in (1, -1):
            x = side * (S.HULL_X + 0.05)
            a = (x, S.Y(u), S.WHEEL_Z)
            b = (x, S.Y(u + d * arm_len), S.WHEEL_Z + 0.12)
            v.add(f"arm_{i}_{side}", c.bar(a, b, 0.08, 0.07), kind="paint", chamfer=0.01)
            v.add(f"arm_hub_{i}_{side}", geo.cylinder(0.075, 0.10, 12, axis="X", center=(x, S.Y(u + d * arm_len),
                                                                                       S.WHEEL_Z + 0.12)),
                  kind="paint", chamfer=0.01)
            stop = geo.box(x, S.Y(u - d * 0.02), S.WHEEL_Z + 0.36, 0.08, 0.10, 0.08)
            v.add(f"bump_stop_{i}_{side}", stop, kind="paint", chamfer=0.01)
            if i in shocks:  # vertical shock absorber just ahead of the wheel (side view z 0.55-0.98)
                su = u - 0.175
                v.add(f"shock_{i}_{side}", geo.cylinder(0.045, 0.43, 10, axis="Z",
                                                        center=(x + side * 0.02, S.Y(su), 0.765)),
                      kind="paint", chamfer=0.008)
                v.add(f"shock_mount_{i}_{side}", geo.box(x, S.Y(su), 0.99, 0.10, 0.10, 0.05), kind="paint",
                      chamfer=0.008)


def turret_side_point(S, u, z, side, out=0.0):
    return c.turret_side_point(S, u, z, side, out)


def turret(v, S):
    """Turret shell from the stations on the turret ring, the rear overhang above the engine deck, roof vent."""
    shell = geo.move(c.station_shell(S, S.TURRET_STATIONS, S.TURRET_Z), x=S.TURRET_X)
    v.add("turret", shell, kind="paint", bone="turret", chamfer=0.018)
    if getattr(S, "TURRET_BIN", None):  # stowage bin on the turret rear (Ausf. L on, often retrofitted)
        rear = geo.move(c.station_shell(S, S.TURRET_BIN, S.TURRET_BIN_Z), x=S.TURRET_X)
        v.add("turret_bin", rear, kind="paint", bone="turret", chamfer=0.018)
    v.bone("turret", (S.TURRET_X, S.Y(S.TURRET_U), S.TURRET_Z), "chassie")


def mantlet_box(v, S, u_front, u_back, x0, x1, z0, z1, round_front=0.06, name="mantlet"):
    """External mantlet (Walzenblende) seen in the side view as a block with a rounded front: octagonal section
    lofted from the turret front to its face."""
    r = round_front
    octo = [(x0, z0 + r), (x0 + r, z0), (x1 - r, z0), (x1, z0 + r), (x1, z1 - r), (x1 - r, z1), (x0 + r, z1),
            (x0, z1 - r)]
    body = geo.loft([(x, S.Y(u_back), z) for x, z in octo], [(x, S.Y(u_front), z) for x, z in octo])
    v.add(name, body, kind="paint_cast", bone="turret", chamfer=0.012)


def gun(v, S, sections, muzzle_u, face_u, brake=None):
    c.gun(v, S, S.BORE_X, S.GUN_Z, face_u, sections, muzzle_u, brake)


def front_plate_fittings(v, S, plate_u, visor_x, mg_x, z, mg_ball_r=0.15):
    """Fahrersehklappe 50 (left) and Kugelblende 50 (right) on the superstructure front plate."""
    c.driver_visor(v, S, visor_x, z, plate_u, plate_w=0.42, plate_h=0.20, hood_w=0.32, depth=0.08)
    c.hull_mg(v, S, mg_x, z, plate_u, ball_r=mg_ball_r)


def deck(v, S, hatches, louvres=()):
    """Engine deck hatches [(u0, u1, x0, x1), ...] and louvres, lying on the deck at DECK_Z."""
    for k, (u0, u1, x0, x1) in enumerate(hatches):
        v.add(f"deck_hatch_{k}", geo.box((x0 + x1) / 2, S.Y((u0 + u1) / 2), S.DECK_Z + 0.015, x1 - x0, u1 - u0, 0.03),
              kind="paint", chamfer=0.01)
    for k, (u0, u1, x0, x1) in enumerate(louvres):
        v.add(f"louvre_{k}", geo.box((x0 + x1) / 2, S.Y((u0 + u1) / 2), S.DECK_Z + 0.012, x1 - x0, u1 - u0, 0.024),
              kind="paint", chamfer=0.006)


def rig(v, S):
    c.rig(v, S)


def deep_wading_muffler(v, S, z=1.42, r=0.12, length=1.0, du=0.12):
    """Ausf. M/N exhaust for deep wading (side/rear views): the muffler mounted high across the rear plate, two
    pipes from the engine coming up to it."""
    v.add("muffler", geo.move(parts.muffler(r, length), y=S.Y(S.REAR_U + du), z=z), kind="exhaust")
    for k, x in enumerate((-0.12, 0.12)):
        v.add(f"exhaust_pipe_{k}", geo.cylinder(0.045, z - 0.85, 8, axis="Z",
                                                center=(x, S.Y(S.REAR_U + 0.07), (z + 0.85) / 2)), kind="exhaust")
    v.locator("right_exhaust", (-0.40, S.Y(S.REAR_U + du), z + 0.1), "chassie")
    v.locator("left_exhaust", (0.40, S.Y(S.REAR_U + du), z + 0.1), "chassie")


def spare_wheels(v, S, stations=(1.75, 4.72), x=1.25, count=2, z0=1.43):
    """Spare road wheels carried lying flat in racks above the left track guard (top view circles, side view stacks
    at z 1.41-1.58), with the rack post down to the guard."""
    for k, u in enumerate(stations):
        for n in range(count):
            for label, bm, kind in zip(("disc", "tyre"), parts.double_road_wheel(S.WHEEL_R, 0.075, 0.0, 0.07, 16),
                                       ("rubber_wheel", "rubber")):
                geo.rotate(bm, math.pi / 2, "Y")
                z = z0 + n * 0.085
                v.add(f"spare_wheel_{label}_{k}_{n}", geo.move(bm, x=x, y=S.Y(u), z=z), kind=kind)
        v.add(f"spare_wheel_rack_{k}", geo.cylinder(0.03, z0 - S.FENDER_Z, 8, axis="Z",
                                                    center=(x, S.Y(u), (z0 + S.FENDER_Z) / 2)), kind="paint")


# ---- early Panzer III (Ausf. A-F): 3.7 cm KwK 36 in the internal mantlet, leaf / coil spring running gear --------
# The 3.7 cm turret front as traced on the Ausf. C side view (turret front plate base at u 1.80, z 1.49): curved
# internal mantlet shield centred on the bore, twin-MG cap and recoil sleeve, L/46.5 barrel to u 0.68.
C_FRONT_U, C_BASE_Z, C_BORE_Z = 1.80, 1.489, 1.774


def gun_37(v, S, du=0.0, dz=None):
    """3.7 cm KwK 36 L/46.5 in the internal mantlet (Innenblende). du shifts the C's numbers fore-aft, dz up (default
    keeps the bore at the same height above the turret base as on the C)."""
    if dz is None:
        dz = S.TURRET_Z - C_BASE_Z
    gz = C_BORE_Z + dz
    # curved shield: an arc of radius 0.21 m about (u 1.91, bore), from 1.61 to 1.96 m on the C, 0.46 m wide
    prof = c.drum_profile(S, 1.91 + du, gz, 0.21, gz - 0.16, gz + 0.19, 0.21, 0.06, 10)
    v.add("mantlet_inner", geo.prism_x(prof, S.BORE_X - 0.23, S.BORE_X + 0.23), kind="paint_cast", bone="turret",
          chamfer=0.01)
    face = 1.60 + du
    secs = [(0.10, face), (0.10, 1.51 + du), (0.069, 1.51 + du), (0.069, 1.28 + du), (0.041, 1.22 + du),
            (0.041, 0.99 + du), (0.027, 0.99 + du), (0.027, 0.68 + du)]
    c.gun(v, S, S.BORE_X, gz, face, secs, 0.68 + du, None)
    for k, x in enumerate((0.12, 0.22)):  # twin coaxial MGs beside the gun (right of it, front view)
        v.add(f"coax_{k}", geo.move(parts.mg_barrel(0.12), x=S.BORE_X - x, y=S.Y(1.62 + du), z=gz - 0.02),
              kind="steel", bone="turret")


def leaf_springs(v, S, springs, bogies):
    """Leaf-spring running gear (Ausf. B-D): springs [(u0, u1, z), ...] lying along the hull side, bogie beams
    [(u_a, u_b), ...] linking each wheel pair, hangers from the bogie up to the spring ends."""
    for side in (1, -1):
        x = side * (S.HULL_X + 0.06)
        for k, (u0, u1, z) in enumerate(springs):
            um = (u0 + u1) / 2
            leaves = [((u0 + u1) / 2, u1 - u0, 0.02)]
            for n in range(1, 5):  # leaf stack, shorter downwards
                leaves.append((um, (u1 - u0) * (1 - 0.17 * n), 0.02))
            bm = None
            for n, (u, length, t) in enumerate(leaves):
                b = geo.box(x, S.Y(u), z - n * 0.022, 0.09, length, t)
                bm = b if bm is None else geo.merge(bm, b)
            v.add(f"leaf_spring_{k}_{side}", bm, kind="paint", chamfer=0.004)
            v.add(f"spring_clamp_{k}_{side}", geo.box(x, S.Y(um), z - 0.05, 0.11, 0.08, 0.14), kind="paint",
                  chamfer=0.008)
        for k, (ua, ub) in enumerate(bogies):
            um = (ua + ub) / 2
            beam = geo.box(x + side * 0.02, S.Y(um), S.WHEEL_Z + 0.04, 0.07, ub - ua, 0.07)
            post = geo.box(x, S.Y(um), (S.WHEEL_Z + 0.04 + springs[0][2]) / 2, 0.08, 0.08,
                           springs[0][2] - S.WHEEL_Z - 0.04)
            v.add(f"bogie_{k}_{side}", geo.merge(beam, post), kind="paint", chamfer=0.008)


def coil_springs(v, S, top_z=0.78, r=0.07):
    """Ausf. A: each large road wheel on its own arm with a vertical coil spring above the hub."""
    for i, u in enumerate(S.WHEELS_U):
        for side in (1, -1):
            x = side * (S.HULL_X + 0.07)
            prof = []
            n = 7
            z0 = S.WHEEL_Z + S.WHEEL_R * 0.55
            for k in range(n + 1):
                z = z0 + (top_z - z0) * k / n
                prof += [(r, z - 0.012), (r + 0.015, z), (r, z + 0.012)]
            spring = geo.lathe([(0.0, z0)] + prof + [(0.0, top_z + 0.012)], 10, axis="Z")
            v.add(f"coil_{i}_{side}", geo.move(spring, x=x, y=S.Y(u)), kind="paint", smooth_angle=60)
            v.add(f"coil_arm_{i}_{side}", c.bar((x, S.Y(u), S.WHEEL_Z), (x, S.Y(u - 0.30), S.WHEEL_Z + 0.20), 0.07,
                                                0.07), kind="paint", chamfer=0.008)
