"""Shared Panther (Pz.Kpfw. V, Sd.Kfz. 171) construction: hull, interleaved running gear, turret, mantlet, gun,
cupolas and rear fittings. Same conventions as pz4_common / pz3_common: u = metres back from the bow (front of the
hull nose / tow brackets), z = metres above ground, x = metres to the vehicle's left; S.Y(u) gives model Y.

The default numbers are the Ausf. G as traced on the-blueprints.com sheet 72512 (calibrated at ~54 px/m, resampled
to 175 px/m; see ger_panther_g.py). A variant spec sets the constants that differ on its own sheet; anything it does
not set falls back to these. Builders read the spec module S through attr(), so a spec only lists its differences.

Documented dimensions every view was calibrated against (Jentz/Doyle, Panzer Tracts 5): hull 6.87 m long, 8.66 m
with the gun forward, 3.27 m over the tracks (3.42 m over the Schürzen), 2.99 m high; 660 mm tracks on 2.61 m
centres; 860 mm road wheels on eight torsion-bar axles per side, interleaved (Schachtellaufwerk).
"""

import math

from .. import geo, parts
from . import pz4_common as c

P = c.P

# ---- defaults (Ausf. G, sheet 72512) ---------------------------------------------------------------------------
DEFAULTS = dict(
    HULL_L=6.87,
    # running gear (side view; track width/centres documented)
    TRACK_W=0.66, TRACK_X=1.305, TRACK_T=0.07, TRACK_PITCH=0.153,
    WHEEL_R=0.43, WHEEL_Z=0.505,
    # interleaved road wheels: the drawing shows the rearmost wheel in the outer row and the frontmost in the inner
    INNER_U=[1.23, 2.31, 3.43, 4.57], OUTER_U=[1.79, 2.88, 4.00, 5.10],
    SPROCKET=(0.455, 0.86, 0.37), SPROCKET_TEETH=17, IDLER=(5.82, 0.735, 0.33),
    # hull: lower hull between the tracks, upper hull (sponsons) over them
    LOWER_X=0.92, BELLY_Z=0.56, NOSE=(0.0, 0.90), NOSE_BELLY_U=0.52,
    DECK_Z=1.87, GLACIS_TOP_U=1.37,  # upper glacis 80 mm at 55 deg from vertical
    SPONSON_Z=(1.50, 1.27),  # sponson floor (lower edge of the upper side plate) at the front and rear (side view)
    SPONSON_X=1.585,  # lower edge of the upper side plate (top view outer edge)
    DECK_X=1.33,  # roof edge: G side plates 50 mm at 29 deg (front view)
    DECK_END_U=6.62, REAR_LOW=(5.97, 0.62),  # rear plate at 30 deg from the deck edge down to the belly
    SIDE_STEP=None,  # D/A: the upper side plate's lower rear corner cut up diagonally (u0, u1, z1); G: one piece
    # turret (side/top/front views)
    TURRET_U=3.72, TURRET_X=0.0,
    TURRET_STATIONS=[(2.55, 0.98, 2.71, 0.76, 2.60), (4.50, 1.17, 4.40, 0.80, 2.67), (4.93, 0.76, 4.58, 0.56, 2.67)],
    GUN_Z=2.30, TRUNNION_U=2.50,
    MANTLET=dict(rc=(2.50, 2.30), r=0.40, z0=2.00, z1=2.62, depth=0.48, half_w=0.60, chin=None),
    SLEEVE=(2.12, 1.98, 0.165),  # gun sleeve ("pot") in front of the mantlet: u back, u front, radius
    MUZZLE_U=-1.79,  # 8.66 m with the gun forward
    COAX_X=-0.45, SIGHT=("mono", 0.31),
    CUPOLA=("cast", 4.01, 0.31), BULGE=False,
    EXHAUST="cooled", SMOKE=False, HULL_MG="ball", DRIVER_VISOR=False, AA_RING=True,
    SCHUERZEN=False,
    # Panther II: overlapped (not interleaved) all-steel wheels, headlight on the left front mudguard, Schmalturm
    WHEEL_LAYOUT="interleaved", WHEEL_STEEL=False, HEADLIGHT=(1.12, None, 1.70), TURRET_TYPE="panther",
)


def attr(S, name):
    return getattr(S, name) if hasattr(S, name) else DEFAULTS[name]


def init(S):
    """Copy the defaults the spec does not override onto it (running_gear and the helpers read plain attributes)."""
    for k, val in DEFAULTS.items():
        if not hasattr(S, k):
            setattr(S, k, val)
    S.WHEELS_U = sorted(S.INNER_U + S.OUTER_U)
    S.ROLLERS_U = []
    S.ROLLER_R = 0.1
    S.ROLLER_Z = 1.0


# ---- rig -------------------------------------------------------------------------------------------------------
N_WHEEL_BONES = 17


def wheel_info(S, scale):
    """Vanilla 24-bone rig: wheel_01 sprocket, wheel_02 idler, wheel_03.. the road-wheel axles front to rear (eight on
    the Panther, seven on the Panther II; each bone carries every disc on that axle, both sides). The remaining bones
    up to wheel_17 exist so the rig keeps the vanilla bone set; they carry no geometry and turn with the road wheels."""
    info = {"wheel_01": (S.SPROCKET[2] * scale, 2 * math.pi / S.SPROCKET_TEETH),
            "wheel_02": (S.IDLER[2] * scale, 2 * math.pi / 90)}
    for i in range(3, N_WHEEL_BONES + 1):
        info[f"wheel_{i:02d}"] = (S.WHEEL_R * scale, None)
    return info


def rig(v, S):
    c.rig(v, S)
    n = len(S.WHEELS_U)
    for i in range(N_WHEEL_BONES - 2 - n):  # spare vanilla wheel bones, on the road-wheel axles in turn
        u = S.WHEELS_U[i % n]
        v.bone(f"wheel_{3 + n + i:02d}", (0, S.Y(u), S.WHEEL_Z), "wheel_suspention")


# ---- hull ------------------------------------------------------------------------------------------------------
def glacis_u(S, z):
    """Upper glacis: from the nose up to the roof edge."""
    (u0, z0), u1 = S.NOSE, S.GLACIS_TOP_U
    return u0 + (u1 - u0) * (z - z0) / (S.DECK_Z - z0)


def rear_u(S, z):
    """Rear plate, leaning forward towards the bottom."""
    (u0, z0), u1 = S.REAR_LOW, S.DECK_END_U
    return u0 + (u1 - u0) * (z - z0) / (S.DECK_Z - z0)


def sponson_z(S, u):
    zf, zr = S.SPONSON_Z
    return zf + (zr - zf) * u / S.DECK_END_U


def hull(v, S):
    """The hull front is two plates meeting at one straight nose edge (photos: Fort Benning, Saumur): the lower nose
    plate from the belly up to the nose, and the upper glacis, ONE flat face from the nose to the roof edge, as wide as
    the lower hull up to the sponson floor and the full width of the sponsons above it. The sponson floors are flat
    back from the glacis (no sloped underside), and the upper side plates slope in to the roof; the rear plate
    closes it behind.
      hull_lower: belly, lower nose plate and the lower rear, up to the nose height
      hull_upper: everything above the nose height, from the glacis back to the rear plate (8-point sections:
                  lower-hull sides, sponson floors, side plates, roof)"""
    import bmesh

    nu, nz = S.NOSE
    lower = [(S.NOSE_BELLY_U, S.BELLY_Z), (nu, nz), (rear_u(S, nz), nz), S.REAR_LOW,
             (S.REAR_LOW[0] - 0.30, S.BELLY_Z)]
    v.add("hull_lower", geo.prism_x(P(S, lower), -S.LOWER_X, S.LOWER_X), chamfer=0.025)

    bm = bmesh.new()
    rows = []
    lx, wb, wt = S.LOWER_X, S.SPONSON_X, S.DECK_X

    def ring(u_of_z, zb, u_top):
        """[(x, z)] round the section, with u for each point from u_of_z (glacis / rear plate / station)."""
        pts = [(-lx, nz), (-lx, zb), (-wb, zb), (-wt, S.DECK_Z), (wt, S.DECK_Z), (wb, zb), (lx, zb), (lx, nz)]
        return [bm.verts.new((x, S.Y(u_top if z == S.DECK_Z else u_of_z(z)), z)) for x, z in pts]

    zf = sponson_z(S, glacis_u(S, sponson_z(S, 0.8)))
    rows.append(ring(lambda z: glacis_u(S, z), zf, S.GLACIS_TOP_U))  # the glacis: all on its plane
    for u in (1.6, 3.0, 4.5, 5.6):
        rows.append(ring(lambda z, u=u: u, sponson_z(S, u), u))
    zr = sponson_z(S, rear_u(S, sponson_z(S, 6.3)))
    rows.append(ring(lambda z: rear_u(S, z), zr, S.DECK_END_U))  # the rear plate
    n = len(rows[0])
    for r0, r1 in zip(rows, rows[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    # caps (glacis in front, rear plate behind) are T-shaped, so not convex: build each from two convex pieces on
    # its plane (lower-hull part + sponson-width part), or the triangulation folds at the inner corners
    for ring_, flip in ((rows[0], False), (rows[-1], True)):
        for idx in ((0, 1, 6, 7), (1, 2, 3, 4, 5, 6)):
            vs = [ring_[i] for i in idx]
            bm.faces.new(list(reversed(vs)) if flip else vs)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) == 4 and not _planar(f)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    v.add("hull_upper", bm, chamfer=0.028)
    if S.SIDE_STEP:  # D/A: the lower rear corner of the upper side plate is cut away; fill plate inside it
        u0, u1, z1 = S.SIDE_STEP
        for side in (1, -1):
            x = side * (S.SPONSON_X - 0.03)
            v.add(f"side_step_{side}", geo.box(x, S.Y((u0 + u1) / 2), (z1 + sponson_z(S, u0)) / 2, 0.02,
                                               u1 - u0, z1 - sponson_z(S, u0)), kind="paint")


def _planar(f, tol=0.004):
    """True when a face's corners lie within tol of its plane (non-planar quads get triangulated)."""
    f.normal_update()
    c = f.calc_center_median()
    return all(abs((v.co - c).dot(f.normal)) < tol for v in f.verts)


def deck(v, S):
    """Roof and engine deck fittings (top view): driver's and radio operator's hatches, engine access hatch, the two
    fan grilles and four air-intake gratings."""
    z = S.DECK_Z
    for side in (1, -1):
        hatch = geo.lathe([(0.0, 0.05), (0.27, 0.05), (0.30, 0.02), (0.30, 0.0)], 14, axis="Z")
        from mathutils import Matrix

        geo.transform(hatch, Matrix.Scale(1.25, 4, (0, 1, 0)))
        v.add(f"crew_hatch_{side}", geo.move(hatch, x=side * 0.62, y=S.Y(2.07), z=z), kind="paint")
        v.add(f"periscope_{side}", geo.box(side * 0.62, S.Y(1.64), z + 0.04, 0.16, 0.10, 0.08), kind="paint",
              chamfer=0.012)
        fan = geo.lathe([(0.0, 0.06), (0.24, 0.06), (0.30, 0.03), (0.30, 0.0)], 18, axis="Z")
        v.add(f"fan_{side}", geo.move(fan, x=side * 0.90, y=S.Y(5.53), z=z), kind="paint", smooth_angle=50)
        for u in (4.82, 6.22):
            v.add(f"grating_{side}_{u}", geo.box(side * 1.00, S.Y(u), z + 0.02, 0.55, 0.32, 0.04), kind="steel",
                  chamfer=0.006)
    v.add("engine_hatch", geo.box(0, S.Y(5.42), z + 0.03, 0.88, 1.00, 0.05), kind="paint", chamfer=0.012)
    for k, u in enumerate((5.15, 5.65)):  # filler caps on the engine hatch
        v.add(f"filler_{k}", geo.move(geo.cylinder(0.12, 0.04, 12, axis="Z"), x=0.0, y=S.Y(u), z=z + 0.07),
              kind="paint")


def front(v, S):
    """Glacis fittings: hull MG (ball mount or letterbox flap), driver's visor (D/A), headlight, tow brackets."""
    gz = 1.62
    gu = glacis_u(S, gz)
    slope = math.atan2(S.DECK_Z - S.NOSE[1], S.GLACIS_TOP_U - S.NOSE[0])
    if S.HULL_MG == "ball":  # Kugelblende 100 (Ausf. A late, G): the ball sits in the plate behind a thin, nearly
        # flush armour ring (photos), no raised boss: the glacis stays one slope
        ring = geo.lathe([(0.12, -0.01), (0.20, -0.01), (0.20, 0.008), (0.17, 0.015), (0.12, 0.012)], 18, axis="Z",
                         close_axis=False)
        from mathutils import Matrix

        geo.transform(ring, Matrix.Scale(1.15, 4, (1, 0, 0)))
        geo.rotate(ring, slope, "X")  # ring axis along the glacis' outward normal
        v.add("mg_mount", geo.move(ring, x=-0.52, y=S.Y(gu), z=gz), kind="paint_cast", smooth_angle=50)
        ball = geo.move(geo.lathe([(0.0, -0.075), (0.07, -0.05), (0.10, 0.0), (0.0, 0.03)], 12, axis="Y"),
                        x=-0.52, y=S.Y(gu - 0.01), z=gz)
        v.add("mg_ball", ball, kind="paint_cast")
        v.add("hull_mg", geo.move(parts.mg_barrel(0.30), x=-0.52, y=S.Y(gu - 0.07), z=gz), kind="steel")
    else:  # letterbox flap (Ausf. D, early A): MG port with an armoured flap on the glacis
        flap = geo.box(0, 0, 0, 0.12, 0.30, 0.04)
        geo.rotate(flap, slope, "X")
        v.add("mg_flap", geo.move(flap, x=-0.52, y=S.Y(gu), z=gz + 0.02), kind="paint", chamfer=0.01)
        slot = geo.box(0, 0, 0, 0.05, 0.16, 0.02)
        geo.rotate(slot, slope, "X")
        v.add("mg_slot", geo.move(slot, x=-0.52, y=S.Y(gu - 0.01), z=gz + 0.005), kind="glass")
    if S.DRIVER_VISOR:  # Fahrersehklappe on the glacis (D/A)
        dz = 1.66
        du = glacis_u(S, dz)
        hood = geo.box(0, 0, 0, 0.36, 0.20, 0.06)
        geo.rotate(hood, slope, "X")
        v.add("driver_visor", geo.move(hood, x=0.55, y=S.Y(du), z=dz + 0.035), kind="paint_cast", chamfer=0.015)
        glass = geo.box(0, 0, 0, 0.26, 0.012, 0.03)
        v.add("driver_visor_glass", geo.move(glass, x=0.55, y=S.Y(du - 0.07), z=dz + 0.02), kind="glass")
    # headlight on the left of the glacis (front view), tow brackets as extensions of the side plates
    lamp = geo.merge(parts.headlight(0.085, 0.12), geo.cylinder(0.02, 0.10, 6, axis="Z", center=(0, 0.06, -0.06)))
    hx, hu, hz = S.HEADLIGHT  # on the glacis corner (Panther), or on the left front mudguard (Panther II)
    hu = glacis_u(S, hz - 0.06) - 0.08 if hu is None else hu
    v.add("headlight", geo.move(lamp, x=hx, y=S.Y(hu), z=hz), kind="paint_cast")
    for side in (1, -1):
        prof = [(-0.02, 0.70), (0.25, 0.70), (0.50, 1.05), (0.30, 1.15), (-0.02, 0.95)]
        v.add(f"tow_bracket_{side}", geo.prism_x(P(S, prof), side * S.LOWER_X - 0.04, side * S.LOWER_X + 0.04),
              kind="paint", chamfer=0.01)
        v.add(f"tow_pin_{side}", geo.cylinder(0.035, 0.16, 8, axis="X", center=(side * S.LOWER_X, S.Y(0.08), 0.82)),
              kind="steel")
        # front mudguard over the track (front view: plate at the sponson floor, sloping down to the bow)
        zf = sponson_z(S, glacis_u(S, sponson_z(S, 0.8)))
        ue = glacis_u(S, zf) - 0.005  # back edge meets the glacis at the sponson corner, clear of the plate in front
        mg = [(0.10, zf - 0.18), (ue, zf - 0.01), (ue, zf + 0.01), (0.10, zf - 0.16)]
        x0, x1 = (0.97, 1.64) if side > 0 else (-1.64, -0.97)
        v.add(f"mudguard_{side}", geo.prism_x(P(S, mg), x0, x1), kind="paint")


def rear(v, S):
    """Rear plate: two exhausts (with cooling pipes, flame dampers or plain), stowage boxes either side, central
    access hatch, jack; tow shackles."""
    for side in (1, -1):
        x = side * 0.33
        base_z = 1.22
        u = rear_u(S, base_z) + 0.10
        pipe = geo.cylinder(0.075, 0.82, 12, axis="Z", center=(x, S.Y(u + 0.06), base_z + 0.41))
        v.add(f"exhaust_{side}", pipe, kind="exhaust")
        v.add(f"exhaust_guard_{side}", geo.box(x, S.Y(u), base_z - 0.02, 0.26, 0.22, 0.30), kind="paint",
              chamfer=0.02)
        top = base_z + 0.82
        if S.EXHAUST == "cooled":  # two cooling pipes beside the exhaust (G; late A), sheet-metal guard over the base
            for k, dx in enumerate((-0.12, 0.12)):
                cp = geo.cylinder(0.045, 0.62, 10, axis="Z", center=(x + dx, S.Y(u + 0.06), base_z + 0.25))
                v.add(f"cooling_pipe_{side}_{k}", cp, kind="exhaust")
        elif S.EXHAUST == "dampers":  # Flammvernichter: cylindrical pots on the exhausts (late 1944 / 1945)
            # Bovington's late G: tall sheet-metal cylinders, ~0.65 m long and ~0.24 m across, leaning back
            pot = geo.lathe([(0.0, 0.0), (0.09, 0.0), (0.12, 0.06), (0.12, 0.62), (0.11, 0.66), (0.0, 0.66)], 14,
                            axis="Z")
            geo.rotate(pot, math.radians(-14), "X")
            v.add(f"flame_damper_{side}", geo.move(pot, x=x, y=S.Y(u + 0.06), z=top - 0.12), kind="exhaust")
            top += 0.52
        v.locator("left_exhaust" if side > 0 else "right_exhaust", (x, S.Y(u + 0.06), top + 0.05), "chassie")
        # stowage box (Gepäckkasten) on each side of the rear plate (rear view x 0.55-1.27, z 1.18-1.78)
        zc = 1.48
        uc = rear_u(S, zc) + 0.17
        box = geo.box(side * 0.92, S.Y(uc), zc, 0.70, 0.34, 0.58)
        slope = math.atan2(S.DECK_END_U - S.REAR_LOW[0], S.DECK_Z - S.REAR_LOW[1])
        geo.rotate(box, -slope, "X", origin=(0, S.Y(uc), zc))
        v.add(f"rear_box_{side}", box, kind="paint", chamfer=0.02)
        v.add(f"tow_rear_{side}", geo.move(parts.tow_shackle(), x=side * 0.62, y=S.Y(rear_u(S, 0.80) + 0.04), z=0.80),
              kind="steel")
    hatch = geo.lathe([(0.0, 0.04), (0.20, 0.04), (0.22, 0.0)], 14, axis="Y")
    rz = 0.88
    v.add("rear_hatch", geo.move(hatch, x=0.0, y=S.Y(rear_u(S, rz) + 0.03), z=rz), kind="paint")
    v.add("jack", geo.box(0.0, S.Y(rear_u(S, 1.50) + 0.12), 1.50, 0.18, 0.18, 0.40), kind="paint", chamfer=0.015)


def tools(v, S):
    """Tools and cleaning rods on the hull side (side view), spare track links, antenna base, locators."""
    for side in (1, -1):
        x = side * (S.SPONSON_X - 0.09)
        z = sponson_z(S, 3.5) + 0.25
        v.add(f"rods_{side}", geo.cylinder(0.045, 2.0, 8, axis="Y", center=(x, S.Y(3.45), z)), kind="paint")
        v.add(f"bar_{side}", geo.cylinder(0.025, 1.6, 6, axis="Y", center=(x, S.Y(3.4), z + 0.12)), kind="wood")
    for k in range(6):  # spare track links on the rear hull sides (side view u 4.6-5.9)
        for side in (1, -1):
            u = 4.65 + k * 0.24
            z = sponson_z(S, u) + 0.30
            link = parts.track_link_spare(0.22, 0.24, 0.05)
            geo.rotate(link, math.pi / 2, "Y")
            v.add(f"spare_link_{side}_{k}", geo.move(link, x=side * (S.SPONSON_X - 0.10), y=S.Y(u), z=z),
                  kind="track_steel")
    v.add("antenna_base", geo.move(geo.cylinder(0.04, 0.10, 8, axis="Z"), x=-0.90, y=S.Y(4.55), z=S.DECK_Z + 0.05),
          kind="paint")
    v.locator("left_tracks", (S.TRACK_X, S.Y(6.0), 0.0), "tank_base")
    v.locator("right_tracks", (-S.TRACK_X, S.Y(6.0), 0.0), "tank_base")


def schuerzen(v, S):
    """Hull Schürzen (5 mm): plates hanging from a rail along the sponson edge (A sheet 72501)."""
    plates = getattr(S, "SKIRT_PLATES", [])
    for side in (1, -1):
        x = side * (S.SPONSON_X + 0.035)
        top = getattr(S, "SKIRT_TOP", None)
        u_a, u_b = plates[0][0], plates[-1][1]
        rail_z = top + 0.02 if top else sponson_z(S, 3.6) + 0.01
        v.add(f"skirt_rail_{side}", geo.box(x, S.Y((u_a + u_b) / 2), rail_z, 0.04, u_b - u_a, 0.04), kind="paint",
              chamfer=0.005)
        for i, (u0, u1, zb) in enumerate(plates):
            zt = top if top else sponson_z(S, (u0 + u1) / 2) + 0.02
            off = 0.008 * (i % 2)
            v.add(f"skirt_{side}_{i}", geo.box(x + side * (0.015 + off), S.Y((u0 + u1) / 2), (zt + zb) / 2, 0.008,
                                               u1 - u0, zt - zb), kind="skirt", smooth_angle=30, chamfer=0.003)


# ---- running gear ----------------------------------------------------------------------------------------------
def disc(radius, width, outer_face, segments, steel=False):
    """One road wheel: steel disc with a rubber tyre (Panther 860 mm), or the all-steel, internally sprung wheel
    (Panther II / Tiger II 800 mm) with a thick steel rim and no tyre: returns (disc, rim)."""
    w = width / 2
    rim = radius - (0.07 if steel else 0.045)
    tyre = geo.lathe([(rim, w), (radius - 0.01, w), (radius, w - 0.015), (radius, -w + 0.015),
                      (radius - 0.01, -w), (rim, -w)], segments)
    s = 1 if outer_face else -1
    face = geo.lathe([(0.0, s * (w + 0.04)), (0.07, s * (w + 0.035)), (0.11, s * (w + 0.01)), (0.13, s * (w - 0.005)),
                      (radius * 0.72, s * (w - 0.02)), (rim, s * w)], segments)
    return face, tyre


def running_gear(v, S):
    """Track belts round sprocket, idler and road wheels (the top run rests on the road wheels: no return rollers);
    sprocket and idler on hub stubs; eight axles of interleaved 860 mm wheels per side. Outer-row axles carry an
    outer and an inner disc, inner-row axles a pair of discs straddling the track's guide teeth between them.
    Torsion-bar swing arms from the hull side to each hub."""
    circles = [(S.Y(S.SPROCKET[0]), S.SPROCKET[1], S.SPROCKET[2] + 0.02), (S.Y(S.IDLER[0]), S.IDLER[1], S.IDLER[2])]
    circles += [(S.Y(u), S.WHEEL_Z, S.WHEEL_R) for u in S.WHEELS_U]
    for side, suffix in ((1, "l"), (-1, "r")):
        v.add(f"track_{suffix}", parts.track_belt(circles, side * S.TRACK_X, S.TRACK_W, S.TRACK_T, 0.15, 0.48,
                                                    drape=True),
              kind="track", bone="tank_base", smooth_angle=60)

    def sprocket():
        return parts.sprocket(S.SPROCKET[2], S.SPROCKET_TEETH, 0.07, 0.30, 0.16, segments=34)

    def idler():
        return parts.idler(S.IDLER[2], 0.07, 0.30, segments=20)

    for k, (label, (u, z, r), maker) in enumerate((("sprocket", S.SPROCKET, sprocket), ("idler", S.IDLER, idler))):
        bname = f"wheel_{k + 1:02d}"
        v.bone(bname, (0, S.Y(u), z), "wheel_suspention")
        for side in (1, -1):
            bm = maker()
            if side < 0:
                geo.rotate(bm, math.pi, "Z")
            v.add(f"{label}_{side}", geo.move(bm, x=side * S.TRACK_X, y=S.Y(u), z=z), kind="wheel_plain", bone=bname)
            hub_len = S.TRACK_X - S.LOWER_X - 0.15
            stub = geo.cylinder(0.16 if label == "sprocket" else 0.09, hub_len, 12, axis="X",
                                center=(side * (S.LOWER_X + hub_len / 2), S.Y(u), z))
            v.add(f"{label}_hub_{side}", stub, kind="paint", chamfer=0.01)

    outer = set(S.OUTER_U)
    overlapped = S.WHEEL_LAYOUT == "overlapped"
    for i, u in enumerate(S.WHEELS_U):
        bname = f"wheel_{3 + i:02d}"
        v.bone(bname, (0, S.Y(u), S.WHEEL_Z), "wheel_suspention")
        for side in (1, -1):
            if overlapped:  # Panther II: outer-row pairs outboard, inner-row pairs inboard; they overlap only
                spots = ((0.20, True, 18), (0.08, False, 10)) if u in outer else ((-0.06, True, 16), (-0.18, False, 10))
            elif u in outer:  # outer row: visible outer disc and the innermost disc
                spots = ((0.235, True, 18), (-0.235, False, 10))
            else:  # inner row: a pair of discs either side of the guide teeth, between the outer-row discs
                spots = ((0.075, True, 14), (-0.075, False, 10))
            rim_kind = "wheel_plain" if S.WHEEL_STEEL else "rubber"
            for k, (dx, face_out, seg) in enumerate(spots):
                face, tyre = disc(S.WHEEL_R, 0.10, face_out, seg, S.WHEEL_STEEL)
                for label, bm, kind in (("disc", face, "rubber_wheel"), ("tyre", tyre, rim_kind)):
                    if side < 0:
                        geo.rotate(bm, math.pi, "Z")
                    v.add(f"roadwheel_{label}_{i}_{k}_{side}",
                          geo.move(bm, x=side * (S.TRACK_X + dx), y=S.Y(u), z=S.WHEEL_Z), kind=kind, bone=bname)
            # swing arm from the hull side (torsion bar) to the hub, trailing; the arms on the right side lead
            # (opposed bars), which only shows from below
            a = (side * (S.LOWER_X + 0.05), S.Y(u - 0.30), S.WHEEL_Z + 0.22)
            b = (side * (S.LOWER_X + 0.05), S.Y(u), S.WHEEL_Z)
            v.add(f"swing_arm_{i}_{side}", c.bar(a, b, 0.08, 0.10), kind="paint", chamfer=0.01)


# ---- turret ----------------------------------------------------------------------------------------------------
def turret_shell(v, S):
    """Turret (side/top/front views): front plate leaning back 12 deg, side plates sloping in 25 deg and narrowing
    to the front in plan, roof rising slightly to the rear, rear corners angled in plan to the rear plate."""
    shell = c.station_shell(S, S.TURRET_STATIONS, S.DECK_Z - 0.01)
    v.add("turret", geo.move(shell, x=S.TURRET_X), kind="paint", bone="turret", chamfer=0.028)
    if S.BULGE:  # bulge in the left side plate under the cupola (top view)
        cu, cx = S.CUPOLA[1], S.CUPOLA[2]
        st = S.TURRET_STATIONS
        z0, z1 = st[1][4] - 0.45, st[1][4] - 0.02
        ring = [(math.cos(a) * 0.30, math.sin(a) * 0.36) for a in (math.radians(d) for d in range(-90, 91, 30))]
        bot = [(S.TURRET_X + cx + 0.35 + px, S.Y(cu + py), z0) for px, py in ring]
        top = [(S.TURRET_X + cx + 0.20 + px * 0.9, S.Y(cu + py * 0.9), z1) for px, py in ring]
        v.add("turret_bulge", geo.loft(bot, top), kind="paint_cast", bone="turret", chamfer=0.02)


def turret_point(S, u, z, side, out=0.0):
    """Point on the sloping side plate between the first two stations."""
    (ub, wb, ut, wt, zt), (ub2, wb2, ut2, wt2, zt2) = S.TURRET_STATIONS[0], S.TURRET_STATIONS[1]
    f = (u - ub) / (ub2 - ub)
    wbase = wb + (wb2 - wb) * f
    wtop = wt + (wt2 - wt) * f
    ztop = zt + (zt2 - zt) * f
    z0 = S.DECK_Z
    k = (wbase - wtop) / (ztop - z0)
    x = wbase - k * (z - z0)
    n = 1 / math.sqrt(1 + k * k)
    return (S.TURRET_X + side * (x + out * n), S.Y(u), z + out * k * n)


def mantlet(v, S):
    """Curved cast mantlet (Topfblende): ONE smooth curved face about the trunnion axis (side view), its ends cut
    square, in front of the turret front plate; gun sleeve ('pot') in front. The late G's chin: the lower half of
    the face runs straight down to a flat bottom ledge (side view), deflecting hits away from the hull roof."""
    m = S.MANTLET
    (rc_u, rc_z), rr = m["rc"], m["r"]
    prof = c.drum_profile(S, rc_u, rc_z, rr, m["z0"] if not m["chin"] else rc_z, m["z1"], rr, m["depth"], 16)
    if m["chin"]:  # chin: face drops straight down from the trunnion height to the ledge, then back to the plate
        cu, cz = m["chin"]
        front_u = rc_u - rr
        top = c.drum_profile(S, rc_u, rc_z, rr, rc_z, m["z1"], rr, m["depth"], 12)
        # drum_profile = front points top->down, then back points; rebuild with the chin below
        n = len(top) // 2
        front = top[:n]
        back = top[n:]
        chin = [(S.Y(front_u), rc_z - 0.10), (S.Y(cu), cz + 0.03), (S.Y(cu + 0.03), cz), (S.Y(rc_u - rr + m["depth"]
                                                                                            + 0.08), cz)]
        prof = front + chin + [(S.Y(rc_u - rr + m["depth"]), rc_z)] + back
    hw = m["half_w"]
    v.add("mantlet", geo.prism_x(prof, -hw, hw), kind="paint_cast", bone="turret", chamfer=0.02, smooth_angle=55)
    su0, su1, sr = S.SLEEVE
    sleeve = geo.lathe([(0.0, 0.0), (sr, 0.0), (sr, -(su0 - su1) + 0.03), (sr - 0.03, -(su0 - su1)),
                        (0.0, -(su0 - su1))], 20, axis="Y")
    v.add("gun_sleeve", geo.move(sleeve, x=S.TURRET_X, y=S.Y(su0), z=S.GUN_Z), kind="paint_cast", bone="turret",
          smooth_angle=55)
    # coaxial MG port right of the gun, gunner's sight aperture(s) left of it (front view)
    face_u = lambda z: rc_u - math.sqrt(max(rr * rr - (z - rc_z) ** 2, 0.0))
    v.add("coax_port", geo.move(geo.cylinder(0.035, 0.05, 10, axis="Y"), x=S.TURRET_X + S.COAX_X,
                                y=S.Y(face_u(S.GUN_Z + 0.02) - 0.01), z=S.GUN_Z + 0.02), kind="glass", bone="turret")
    kind_, sx = S.SIGHT
    holes = (sx - 0.05, sx + 0.05) if kind_ == "bino" else (sx,)
    for k, x in enumerate(holes):
        v.add(f"sight_{k}", geo.move(geo.cylinder(0.03, 0.05, 10, axis="Y"), x=S.TURRET_X + x,
                                     y=S.Y(face_u(S.GUN_Z + 0.06) - 0.01), z=S.GUN_Z + 0.06), kind="glass",
              bone="turret")


def gun(v, S):
    """7.5 cm KwK 42 L/70: tapering barrel from the sleeve to the double-baffle brake; muzzle 8.66 m from the hull
    rear (documented), brake 0.50 m long and 0.24 m across (drawing)."""
    su1 = S.SLEEVE[1]
    brake_l = 0.50
    m0 = S.MUZZLE_U + brake_l
    sections = [(0.095, su1 + 0.02), (0.095, su1 - 0.30), (0.085, su1 - 0.32), (0.080, su1 - 1.6),
                (0.068, m0 + 0.6), (0.064, m0)]
    brake = (lambda: parts.muzzle_brake_double(0.12, brake_l, 16), brake_l)
    c.gun(v, S, S.TURRET_X, S.GUN_Z, su1 + 0.02, sections, S.MUZZLE_U, brake, segments=16, base_u=S.TRUNNION_U)


def cupola(v, S):
    """Commander's cupola, left rear of the roof: drum cupola with six vision slits (D) or the cast cupola with seven
    periscopes and the AA-MG ring (A, G)."""
    kind_, cu, cx = S.CUPOLA
    x, y = S.TURRET_X + cx, S.Y(cu)
    z = S.TURRET_STATIONS[1][4]
    if kind_ == "drum":  # Ausf. D: tall drum, six vision slits, hatch hinged up then swung aside
        prof = [(0.0, 0.0), (0.42, 0.0), (0.42, 0.05), (0.36, 0.06), (0.36, 0.30), (0.33, 0.33), (0.0, 0.33)]
        v.add("cupola", geo.move(geo.lathe(prof, 24, axis="Z"), x=x, y=y, z=z - 0.02), kind="paint_cast",
              bone="turret", smooth_angle=50)
        v.add("cupola_hatch", geo.move(geo.lathe([(0.0, 0.05), (0.30, 0.05), (0.32, 0.0)], 20, axis="Z"), x=x, y=y,
                                       z=z + 0.31), kind="paint_cast", bone="turret", smooth_angle=50)
        for k in range(6):
            a = 2 * math.pi * k / 6 + math.pi
            g = geo.box(0.36, 0, 0, 0.02, 0.15, 0.035)
            geo.rotate(g, a, "Z")
            v.add(f"cupola_slit_{k}", geo.move(g, x=x, y=y, z=z + 0.18), kind="glass", bone="turret")
            brow = geo.box(0.37, 0, 0, 0.03, 0.20, 0.025)
            geo.rotate(brow, a, "Z")
            v.add(f"cupola_brow_{k}", geo.move(brow, x=x, y=y, z=z + 0.215), kind="paint_cast", bone="turret",
                  chamfer=0.006)
        return
    # cast cupola (Ausf. A, G): low dome, seven periscope housings, pivoting hatch, AA ring on top
    prof = [(0.0, 0.0), (0.43, 0.0), (0.43, 0.04), (0.40, 0.06), (0.37, 0.17), (0.31, 0.21), (0.0, 0.21)]
    v.add("cupola", geo.move(geo.lathe(prof, 28, axis="Z"), x=x, y=y, z=z - 0.02), kind="paint_cast", bone="turret",
          smooth_angle=50)
    v.add("cupola_hatch", geo.move(geo.lathe([(0.0, 0.05), (0.27, 0.04), (0.29, 0.0)], 20, axis="Z"), x=x, y=y,
                                   z=z + 0.19), kind="paint_cast", bone="turret", smooth_angle=50)
    for k in range(7):
        a = 2 * math.pi * (k + 0.5) / 7
        hood = geo.box(0.38, 0, 0, 0.08, 0.13, 0.07)
        geo.rotate(hood, a, "Z")
        v.add(f"cupola_periscope_{k}", geo.move(hood, x=x, y=y, z=z + 0.11), kind="paint_cast", bone="turret",
              chamfer=0.01)
        glass = geo.box(0.425, 0, 0, 0.01, 0.10, 0.025)
        geo.rotate(glass, a, "Z")
        v.add(f"cupola_glass_{k}", geo.move(glass, x=x, y=y, z=z + 0.10), kind="glass", bone="turret")
    if S.AA_RING:  # Fliegerbeschussgerät: ring rail over the cupola
        ring = geo.lathe([(0.39, 0.0), (0.42, 0.0), (0.42, 0.025), (0.39, 0.025)], 24, axis="Z")
        v.add("aa_ring", geo.move(ring, x=x, y=y, z=z + 0.24), kind="steel_paint", bone="turret")
        for k in range(3):
            a = 2 * math.pi * k / 3 + 0.4
            post = geo.box(0.405, 0, 0, 0.025, 0.025, 0.06)
            geo.rotate(post, a, "Z")
            v.add(f"aa_post_{k}", geo.move(post, x=x, y=y, z=z + 0.20), kind="steel_paint", bone="turret")


def turret_fittings(v, S):
    """Rear hatch (round, in the rear plate), pistol port / vision slot, roof vent and periscope, smoke dischargers
    (D: three Nebelwurfgeräte each side at the front of the side plates), stowage on the side plates."""
    st = S.TURRET_STATIONS
    (ub, wb, ut, wt, zt) = st[-1]
    zc = S.DECK_Z + 0.44  # rear view: round hatch 0.49 m across, right of the centreline, centre at 2.31 m
    f = (zc - S.DECK_Z) / (zt - S.DECK_Z)
    u_r = ub + (ut - ub) * f
    slope = math.atan2(ub - ut, zt - S.DECK_Z)
    hatch = geo.lathe([(0.0, 0.05), (0.24, 0.05), (0.27, 0.0)], 20, axis="Y")
    geo.rotate(hatch, -slope, "X")
    v.add("turret_rear_hatch", geo.move(hatch, x=S.TURRET_X - 0.21, y=S.Y(u_r - 0.02), z=zc), kind="paint_cast",
          bone="turret", smooth_angle=50)
    # vent and loader's periscope on the roof (top view)
    roof = st[1][4]
    v.add("vent", geo.move(geo.lathe([(0.0, 0.06), (0.11, 0.06), (0.13, 0.0)], 14, axis="Z"), x=S.TURRET_X - 0.55,
                           y=S.Y(4.10), z=roof), kind="paint", bone="turret")
    v.add("loader_periscope", geo.box(S.TURRET_X - 0.45, S.Y(3.15), roof + 0.04, 0.14, 0.18, 0.08), kind="paint",
          bone="turret", chamfer=0.012)
    v.add("roof_dome", geo.move(geo.lathe([(0.0, 0.07), (0.15, 0.05), (0.20, 0.0)], 16, axis="Z"),
                                x=S.TURRET_X - 0.10, y=S.Y(3.35), z=roof - 0.005), kind="paint_cast", bone="turret")
    # pistol port / vision flap on each side plate
    for side in (1, -1):
        p = turret_point(S, 4.15, 2.30, side, 0.02)
        plug = geo.cylinder(0.07, 0.04, 12, axis="X", center=(0, 0, 0))
        v.add(f"pistol_port_{side}", geo.move(plug, *p), kind="paint_cast", bone="turret")
        if S.SMOKE:  # three smoke dischargers per side, fanned out at the front of the side plate
            for k in range(3):
                q = turret_point(S, 2.85, 2.12 + k * 0.13, side, 0.06)
                tube = geo.cylinder(0.045, 0.22, 10, axis="Z")
                geo.rotate(tube, side * math.radians(35), "Y")
                geo.rotate(tube, math.radians(-30), "X")
                v.add(f"smoke_{side}_{k}", geo.move(tube, *q), kind="steel_paint", bone="turret")
    # spare track links / hooks on the turret side are field fit; lifting hooks on the roof
    for k, (hx, hu) in enumerate(((0.62, 2.95), (-0.62, 2.95), (0.55, 4.35), (-0.55, 4.35))):
        hook = geo.box(S.TURRET_X + hx, S.Y(hu), roof + 0.04, 0.03, 0.10, 0.08)
        v.add(f"lift_hook_{k}", hook, kind="paint", bone="turret", chamfer=0.008)


def schmalturm(v, S):
    """Schmalturm (planned for the Panther II and the Panther Ausf. F): narrow front plate leaning back 20 deg, the
    conical 'Saukopf' mantlet round the gun, the stereo rangefinder's armoured 'ears' either side of the roof front,
    and the 7.5 cm L/70 with its long recuperator sleeve, no muzzle brake drawn (side/front views)."""
    st = S.TURRET_STATIONS
    gz = S.GUN_Z
    (ub, wb, ut, wt, zt) = st[0]
    face = ub + (ut - ub) * (gz - S.DECK_Z) / (zt - S.DECK_Z)  # front plate at gun height
    c0, c1, cr0, cr1 = S.SAUKOPF  # cone from the plate (u, radius) forward to its nose
    cone = geo.lathe([(0.0, 0.0), (cr0, 0.0), (cr0 * 0.92, -(face - c0) * 0.25), (cr1, -(face - c1)),
                      (0.0, -(face - c1))], 24, axis="Y")
    v.add("mantlet", geo.move(cone, x=S.TURRET_X, y=S.Y(face + 0.02), z=gz), kind="paint_cast", bone="turret",
          smooth_angle=60)
    for side in (1, -1):  # rangefinder ears (front view: bumps at the roof front corners)
        p = turret_point(S, S.EARS[0], S.EARS[1], side, 0.0)
        ear = geo.lathe([(0.0, 0.0), (0.11, 0.0), (0.11, 0.10), (0.07, 0.15), (0.0, 0.15)], 14, axis="X")
        if side < 0:
            geo.rotate(ear, math.pi, "Z")
        v.add(f"rangefinder_ear_{side}", geo.move(ear, *p), kind="paint_cast", bone="turret", smooth_angle=50)
    v.add("coax_port", geo.move(geo.cylinder(0.03, 0.05, 10, axis="Y"), x=S.TURRET_X + S.COAX_X,
                                y=S.Y(face - 0.01), z=gz - 0.05), kind="glass", bone="turret")
    v.add("sight_0", geo.move(geo.cylinder(0.03, 0.05, 10, axis="Y"), x=S.TURRET_X + S.SIGHT[1],
                              y=S.Y(face - 0.01), z=gz + 0.10), kind="glass", bone="turret")
    sections = S.GUN_SECTIONS
    c.gun(v, S, S.TURRET_X, gz, c1, sections, S.MUZZLE_U, None, segments=16, base_u=S.TRUNNION_U)


def turret(v, S):
    turret_shell(v, S)
    if S.TURRET_TYPE == "schmalturm":
        schmalturm(v, S)
    else:
        mantlet(v, S)
        gun(v, S)
    cupola(v, S)
    turret_fittings(v, S)
    v.bone("turret", (S.TURRET_X, S.Y(S.TURRET_U), S.DECK_Z), "chassie")


def build(v, S):
    init(S)
    hull(v, S)
    deck(v, S)
    front(v, S)
    rear(v, S)
    tools(v, S)
    if S.SCHUERZEN:
        schuerzen(v, S)
    running_gear(v, S)
    turret(v, S)
    rig(v, S)
