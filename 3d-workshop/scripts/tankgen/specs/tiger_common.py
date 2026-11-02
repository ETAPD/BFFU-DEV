"""Shared Tiger construction: Tiger I (Pz.Kpfw. VI Ausf. E, Sd.Kfz. 181) and Tiger II (Pz.Kpfw. VI Ausf. B,
Sd.Kfz. 182). Same conventions as pz4_common / panther_common: u = metres back from the bow (the front of the hull
side plates / tow eyes), z = metres above ground, x = metres to the vehicle's left; S.Y(u) gives model Y.

Tiger I: the defaults are the early Tiger I as drawn in the School of Tank Technology report on Tiger 131
(Military College of Science, January 1944; public domain, Wikimedia Commons; see ger_tiger1_early.py for the
calibration). A variant spec sets the constants that differ; anything it does not set falls back to TIGER1.

Documented dimensions (Jentz/Doyle, Panzer Tracts 6-1; the drawing's own dimension lines agree): hull 6.316 m,
8.45 m with the gun forward (drawing: 27 ft 9 in = 8.458 m), 3.547 m over the 725 mm combat tracks on 2.82 m
centres (drawing: 2 ft 4.5 in + 6 ft 10 5/8 in + 2 ft 4.5 in), 3.73 m over the mudguards (12 ft 3 in), hull roof
1.78 m (5 ft 10 in), belly 0.43 m (1 ft 5 in), turret roof 2.60 m (8 ft 6.5 in), drum cupola 2.85 m (9 ft 4.25 in).
The 3.0 m height often quoted includes the open cupola hatch / AA mount and is not a drawing line.
"""

import math

from mathutils import Matrix, Vector

from .. import geo, parts
from . import panther_common as pc
from . import pz4_common as c

P = c.P
bar = c.bar

# ---- Tiger I defaults (early, Tiger 131 drawing) ------------------------------------------------------------------
TIGER1 = dict(
    HULL_L=6.316,
    # running gear (side view): 725 mm combat tracks on 2.823 m centres (front view), 800 mm road wheels on eight
    # torsion-bar axles a side; sprocket and idler from the side view
    TRACK_W=0.725, TRACK_X=1.4115, TRACK_T=0.09, TRACK_PITCH=0.13,
    WHEEL_R=0.40, WHEEL_Z=0.50,
    WHEELS_U=[1.237, 1.751, 2.243, 2.771, 3.271, 3.800, 4.300, 4.857],
    SPROCKET=(0.558, 0.728, 0.33), SPROCKET_TEETH=19, IDLER=(5.504, 0.619, 0.30),
    WHEEL_LAYERS=3,  # 3: rubber-tyred wheels in three layers (early/mid); 2: steel-rimmed wheels in two (late)
    WHEEL_STEEL=False,
    # hull (side/front/top views)
    LOWER_X=0.94,  # lower hull between the tracks (front view: nose plate edges at 0.94-0.96)
    SUPER_X=1.565,  # upper hull over the tracks (front/top views)
    FENDER_X=1.86,  # outer edge of the side fenders / front mudguards (top view; 12 ft 3 in overall)
    DECK_Z=1.785, BELLY_Z=0.43,
    FRONT_PLATE=((0.835, 1.36), (0.915, 1.785)),  # driver's front plate, 10 deg (side view; front view z 1.386)
    REAR_PLATE=((5.875, 1.10), (5.94, 1.785)),  # rear plate, leaning in at the bottom (side view)
    SPONSON_Z=(1.36, 1.10),  # lower edge of the upper hull side plate at the front plate / rear plate
    FENDER_A=(1.53, 1.30), FENDER_B=(1.30, 1.08),  # fender strip: inner (bolted) edge and outer edge, front/rear
    NOSE=[(0.0, 0.84), (0.0, 1.21), (0.05, 1.25), (0.835, 1.38)],  # nose front edge and the 80-deg glacis
    NOSE_BELLY_U=0.75, REAR_BELLY_U=5.80,
    # turret (side/top/front views): horseshoe side/rear plate, centre u 3.37 radius 1.12 (top view, fitted), flat
    # front plate; walls vertical from z 1.89, roof 2.60 sloping down to 2.48 at the front plate
    TURRET_U=3.37, TURRET_R=1.12, TURRET_FRONT=(1.80, 1.96, 0.84),  # front plate face u, rear u, half-width
    TURRET_Z=(1.89, 2.48, 2.60, 2.86),  # wall base, roof at the front plate, roof, u where the roof turns flat
    GUN_Z=2.17,
    MANTLET=dict(rc=(2.15, 2.17), r=0.50, z0=1.90, z1=2.45, depth=0.24, half_w=0.80),
    SIGHT=("bino", 0.415),  # binocular (TZF 9b) apertures left of the gun (front view x 0.37 / 0.46)
    COAX=(-0.50, 2.24),
    CUPOLA=("drum", 3.60, 0.53),
    SMOKE=True, S_MINES=True, FEIFEL=True, ESCAPE_HATCH=True, LOADER_PERISCOPE=False, PILZE=False,
    BIN=(4.18, 4.74, 0.68, 1.94, 2.59),  # turret stowage bin: u front/rear, half-width, z bottom/top (side/top)
    MUZZLE_U=-2.10,  # drawing: 27 ft 9 in from the muzzle to the rear
)


def attr(S, name):
    return getattr(S, name) if hasattr(S, name) else TIGER1[name]


def init(S, defaults=TIGER1):
    for k, val in defaults.items():
        if not hasattr(S, k):
            setattr(S, k, val)
    S.ROLLERS_U, S.ROLLER_R, S.ROLLER_Z = [], 0.1, 1.0


# ---- rig ------------------------------------------------------------------------------------------------------
def wheel_info(S, scale):
    return pc.wheel_info(S, scale)


def rig(v, S):
    pc.rig(v, S)


# ---- running gear ---------------------------------------------------------------------------------------------
def disc(radius, width, face_sign, segments, steel=False, plain=False):
    """One road wheel disc, axle along X: (steel face, rim/tyre ring). face_sign +1/-1: which side the dished steel
    face is on. plain: hidden inner discs get a flat closed face (fewer triangles, still closed from both sides).
    Steel-rimmed wheels (late Tiger I, Tiger II): thick steel rim, rubber ring inside it (not modelled)."""
    w = width / 2
    rim = radius - (0.075 if steel else 0.03)
    if plain:  # square closed section
        ring = geo.lathe([(rim, w), (radius, w), (radius, -w), (rim, -w), (rim, w)], segments)
    else:
        ring = geo.lathe([(rim, w), (radius - 0.01, w), (radius, w - 0.012), (radius, -w + 0.012),
                          (radius - 0.01, -w), (rim, -w), (rim, w)], segments)  # closed section
    s = face_sign
    if plain:
        face = geo.lathe([(0.0, s * (w + 0.01)), (rim, s * w), (rim, -s * w), (0.0, -s * (w - 0.01))], segments)
    else:
        face = geo.lathe([(0.0, s * (w + 0.045)), (0.065, s * (w + 0.04)), (0.10, s * (w + 0.012)),
                          (0.14, s * (w - 0.004)), (radius * 0.70, s * (w - 0.016)), (rim, s * w),
                          (rim, -s * w), (0.0, -s * w)], segments)  # closed: dished face + flat back
    return face, ring


def wheel_spots(S, i):
    """[(dx from the track centre, face visible, segments, plain)] for axle i (0 = front)."""
    if S.WHEEL_LAYERS == 3:  # three layers: odd axles (1st, 3rd...) outermost; the guide horns run between +-0.05
        if i % 2 == 0:
            return ((0.27, True, 18, False), (0.065, True, 10, True), (-0.165, False, 8, True))
        return ((0.165, True, 14, False), (-0.065, False, 8, True), (-0.27, False, 8, True))
    if i % 2 == 0:  # two layers (steel wheels): outer-row axles carry the outer and the innermost disc pair
        return ((0.225, True, 20, False), (-0.225, False, 10, True))
    return ((0.07, True, 16, False), (-0.07, False, 10, True))


def running_gear(v, S, disc_w=0.09):
    """Track belts (the top run rests on the road wheels, no return rollers), sprocket and idler on hub stubs, the
    interleaved road wheels on torsion-bar swing arms. Each axle's bone carries every disc on it, both sides."""
    circles = [(S.Y(S.SPROCKET[0]), S.SPROCKET[1], S.SPROCKET[2] + 0.02), (S.Y(S.IDLER[0]), S.IDLER[1], S.IDLER[2])]
    circles += [(S.Y(u), S.WHEEL_Z, S.WHEEL_R) for u in S.WHEELS_U]
    for side, suffix in ((1, "l"), (-1, "r")):
        v.add(f"track_{suffix}", parts.track_belt(circles, side * S.TRACK_X, S.TRACK_W, S.TRACK_T, 0.15, 0.48,
                                                    drape=True), kind="track", bone="tank_base", smooth_angle=60)

    def sprocket():
        return parts.sprocket(S.SPROCKET[2], S.SPROCKET_TEETH, 0.07, 0.34, 0.17, segments=S.SPROCKET_TEETH + 7)

    def idler():
        return parts.idler(S.IDLER[2], 0.08, 0.32, segments=18)

    for k, (label, (u, z, r), maker) in enumerate((("sprocket", S.SPROCKET, sprocket), ("idler", S.IDLER, idler))):
        bname = f"wheel_{k + 1:02d}"
        v.bone(bname, (0, S.Y(u), z), "wheel_suspention")
        for side in (1, -1):
            bm = maker()
            if side < 0:
                geo.rotate(bm, math.pi, "Z")
            v.add(f"{label}_{side}", geo.move(bm, x=side * S.TRACK_X, y=S.Y(u), z=z), kind="wheel_plain", bone=bname)
            hub_len = S.TRACK_X - S.LOWER_X - 0.17
            stub = geo.cylinder(0.17 if label == "sprocket" else 0.10, hub_len, 12, axis="X",
                                center=(side * (S.LOWER_X + hub_len / 2), S.Y(u), z))
            v.add(f"{label}_hub_{side}", stub, kind="paint", chamfer=0.01)

    rim_kind = "wheel_plain" if S.WHEEL_STEEL else "rubber"
    for i, u in enumerate(S.WHEELS_U):
        bname = f"wheel_{3 + i:02d}"
        v.bone(bname, (0, S.Y(u), S.WHEEL_Z), "wheel_suspention")
        for side in (1, -1):
            for k, (dx, face_out, seg, plain) in enumerate(wheel_spots(S, i)):
                face, ring = disc(S.WHEEL_R, disc_w, 1 if face_out else -1, seg, S.WHEEL_STEEL, plain)
                for label, bm, kind in (("disc", face, "rubber_wheel"), ("tyre", ring, rim_kind)):
                    if side < 0:
                        geo.rotate(bm, math.pi, "Z")
                    v.add(f"roadwheel_{label}_{i}_{k}_{side}",
                          geo.move(bm, x=side * (S.TRACK_X + dx), y=S.Y(u), z=S.WHEEL_Z), kind=kind, bone=bname)
            # torsion-bar swing arm from the hull side to the hub (trailing on the left, leading on the right)
            a = (side * (S.LOWER_X + 0.05), S.Y(u - side * 0.30), S.WHEEL_Z + 0.20)
            b = (side * (S.LOWER_X + 0.05), S.Y(u), S.WHEEL_Z)
            v.add(f"swing_arm_{i}_{side}", bar(a, b, 0.08, 0.10), kind="paint", chamfer=0.01)


# ---- Tiger I hull ---------------------------------------------------------------------------------------------
def lin(p0, p1, t):
    return p0 + (p1 - p0) * t


def t1_sponson_z(S, u):
    (u0, _), (u1, _) = S.FRONT_PLATE[0], S.REAR_PLATE[0]
    return lin(S.SPONSON_Z[0], S.SPONSON_Z[1], (u - u0) / (u1 - u0))


def t1_front_u(S, z):
    (u0, z0), (u1, z1) = S.FRONT_PLATE
    return lin(u0, u1, (z - z0) / (z1 - z0))


def t1_rear_u(S, z):
    (u0, z0), (u1, z1) = S.REAR_PLATE
    return lin(u0, u1, (z - z0) / (z1 - z0))


def t1_hull(v, S):
    """Box hull of interlocked plates (side/front/top views; photos of Tiger 131):
      hull_lower: between the tracks: the nose (side-plate horns with the tow eyes), the 80-deg glacis up to the
                  front plate, the lower nose plate down to the belly, the lower rear plate
      hull_upper: the full-width superstructure over the tracks: the 10-deg front plate across the whole width, the
                  vertical side plates down to the sponson floor, the deck, the rear plate leaning in at the bottom.
    Every plate edge is chamfered 3 cm (no razor box corners)."""
    (fu0, fz0), (fu1, fz1) = S.FRONT_PLATE
    (ru0, rz0), (ru1, rz1) = S.REAR_PLATE
    lower = [(S.NOSE_BELLY_U, S.BELLY_Z), (S.REAR_BELLY_U, S.BELLY_Z), (t1_rear_u(S, 1.30) - 0.02, 1.30)]
    lower += [(fu0 + 0.05, 1.30)] + [(u, z) for u, z in reversed(S.NOSE)]
    v.add("hull_lower", geo.prism_x(P(S, lower), -S.LOWER_X, S.LOWER_X), chamfer=0.03)
    # front plate stands 2.5 cm proud of the deck and the side plates run 2 cm past it (interlocked joints)
    upper = [(fu0, S.SPONSON_Z[0]), (ru0, S.SPONSON_Z[1]), (ru1, S.DECK_Z), (fu1, S.DECK_Z)]
    v.add("hull_upper", geo.prism_x(P(S, upper), -S.SUPER_X, S.SUPER_X), chamfer=0.03)
    plate = [(fu0 - 0.005, fz0), (fu0 + 0.075, fz0), (fu1 + 0.075, fz1 + 0.025), (fu1 - 0.005, fz1 + 0.025)]
    v.add("front_plate_lip", geo.prism_x(P(S, plate), -S.SUPER_X + 0.02, S.SUPER_X - 0.02), chamfer=0.012)
    for side in (1, -1):  # side plates' front edges standing past the front plate
        x = side * (S.SUPER_X - 0.04)
        edge = [(fu0 - 0.02, S.SPONSON_Z[0]), (fu0 + 0.06, S.SPONSON_Z[0]), (fu1 + 0.06, fz1 + 0.015),
                (fu1 - 0.02, fz1 + 0.015)]
        v.add(f"side_plate_edge_{side}", geo.prism_x(P(S, edge), x - 0.04, x + 0.04), chamfer=0.012)


def t1_fenders(v, S):
    """Side fenders: a strip sloping out and down from a bolted line on the side plate to the outer edge over the
    track (side view: the two lines falling to the rear; top view: out to 1.86 m); front mudguards ahead of the
    front plate, level with the glacis and turned down at the front; hinged rear mudguards behind the tracks."""
    (fu0, _), (ru0, _) = S.FRONT_PLATE[0], S.REAR_PLATE[0]
    (a0, a1), (b0, b1) = S.FENDER_A, S.FENDER_B
    for side in (1, -1):
        xi, xo = side * S.SUPER_X, side * S.FENDER_X
        pts = [(xi, S.Y(fu0), a0), (xi, S.Y(ru0), a1), (xo, S.Y(ru0), b1), (xo, S.Y(fu0), b0)]
        v.add(f"fender_{side}", c.plate(pts, (0, 0, -0.012)), kind="paint", chamfer=0.004)
        # front mudguard: flat over the track at the glacis height, turned down at its front edge
        x0, x1 = (S.LOWER_X, S.FENDER_X) if side > 0 else (-S.FENDER_X, -S.LOWER_X)
        mg = [(0.10, 1.27), (fu0 + 0.01, 1.385), (fu0 + 0.01, 1.40), (0.10, 1.285), (0.03, 1.20), (0.045, 1.19)]
        v.add(f"mudguard_{side}", geo.prism_x(P(S, mg), x0, x1), kind="paint", chamfer=0.004)
        # rear mudguard flap, hinged at the rear plate and sloping down over the idler (side/rear views, Tiger 131)
        rx0, rx1 = (S.TRACK_X - S.TRACK_W / 2 - 0.02, S.FENDER_X) if side > 0 else (-S.FENDER_X,
                                                                                   -S.TRACK_X + S.TRACK_W / 2 + 0.02)
        flap = [(ru0 - 0.01, 1.10), (ru0 + 0.33, 0.80), (ru0 + 0.345, 0.815), (ru0 + 0.005, 1.12)]
        v.add(f"rear_mudguard_{side}", geo.prism_x(P(S, flap), rx0, rx1), kind="paint", chamfer=0.004)


def t1_front(v, S):
    """Front plate fittings: hull MG ball (right, front view x -0.54, z 1.57) and the driver's visor (left, x 0.54,
    z 1.52, 0.63 x 0.32 m); tow shackles on the nose (x 0.92, z 0.72-0.94); tow eyes in the side-plate horns."""
    fu = lambda z: t1_front_u(S, z)
    slope = math.atan2(S.FRONT_PLATE[1][0] - S.FRONT_PLATE[0][0], S.FRONT_PLATE[1][1] - S.FRONT_PLATE[0][1])
    # Kugelblende: armoured ring and ball, MG 34 barrel
    ring = geo.lathe([(0.0, 0.0), (0.185, 0.0), (0.185, -0.04), (0.15, -0.07), (0.10, -0.075), (0.0, -0.075)], 20,
                     axis="Y")
    geo.rotate(ring, -slope, "X")
    v.add("mg_mount", geo.move(ring, x=-0.54, y=S.Y(fu(1.57)), z=1.57), kind="paint_cast", smooth_angle=50)
    ball = geo.lathe([(0.0, -0.12), (0.06, -0.11), (0.09, -0.06), (0.09, -0.03)], 12, axis="Y")
    v.add("mg_ball", geo.move(ball, x=-0.54, y=S.Y(fu(1.57)), z=1.57), kind="paint_cast")
    v.add("hull_mg", geo.move(parts.mg_barrel(0.30), x=-0.54, y=S.Y(fu(1.57) - 0.10), z=1.57), kind="steel")
    # Fahrersehklappe: armoured block with the vision slit, standing proud of the plate
    base_u = fu(1.52)
    vis = [(base_u + 0.02, 1.36), (base_u - 0.10, 1.38), (base_u - 0.12, 1.55), (base_u - 0.08, 1.68),
           (base_u + 0.03, 1.68)]
    v.add("driver_visor", geo.prism_x(P(S, vis), 0.225, 0.855), kind="paint_cast", chamfer=0.015)
    v.add("driver_visor_glass", geo.box(0.54, S.Y(base_u - 0.123), 1.555, 0.40, 0.012, 0.03), kind="glass")
    for side in (1, -1):
        sh = parts.tow_shackle()
        geo.transform(sh, Matrix.Scale(1.3, 4))
        v.add(f"tow_front_{side}", geo.move(sh, x=side * 0.92, y=S.Y(0.04), z=0.82), kind="steel")
        eye = geo.lathe([(0.04, -0.05), (0.075, -0.05), (0.075, 0.05), (0.04, 0.05), (0.04, -0.05)], 12, axis="X")
        v.add(f"tow_eye_{side}", geo.move(eye, x=side * (S.LOWER_X - 0.02), y=S.Y(0.09), z=0.88), kind="paint")


def t1_deck(v, S):
    """Deck fittings (top view): round driver's and radio operator's hatches (u 1.48, x +-0.87, 0.57 m across),
    engine deck with the two radiator gratings a side, fan intake grilles, central engine hatch; S-mine dischargers
    on the front corners (early); antenna base on the right rear (u 4.11, x -1.41)."""
    z = S.DECK_Z
    for side in (1, -1):
        hatch = geo.lathe([(0.0, 0.055), (0.25, 0.055), (0.28, 0.03), (0.285, 0.0), (0.0, 0.0)], 18, axis="Z")
        v.add(f"crew_hatch_{side}", geo.move(hatch, x=side * 0.87, y=S.Y(1.48), z=z), kind="paint", smooth_angle=50)
        for k, u in enumerate((4.227, 4.61)):  # radiator gratings (armoured louvres) over the side radiators
            v.add(f"grating_{side}_{k}", geo.box(side * 1.02, S.Y(u + 0.19), z + 0.025, 0.95, 0.36, 0.05),
                  kind="steel", chamfer=0.008)
        v.add(f"fan_grille_{side}", geo.box(side * 1.03, S.Y(5.68), z + 0.02, 0.95, 0.40, 0.04), kind="steel",
              chamfer=0.008)
        v.add(f"deck_cover_{side}", geo.box(side * 1.05, S.Y(5.22), z + 0.015, 0.35, 0.30, 0.03), kind="paint",
              chamfer=0.006)
    eng = geo.lathe([(0.0, 0.05), (0.24, 0.05), (0.26, 0.02), (0.26, 0.0), (0.0, 0.0)], 18, axis="Z")
    v.add("engine_hatch", geo.move(eng, x=0.0, y=S.Y(5.08), z=z), kind="paint", smooth_angle=50)
    v.add("engine_deck_plate", geo.box(0.0, S.Y(5.10), z + 0.01, 1.00, 1.55, 0.02), kind="paint", chamfer=0.005)
    if S.S_MINES:  # S-Minenwerfer (S-mine dischargers) on the front mudguards by the front plate corners (top view
        # u 0.75, x 1.45; front view: short tubes on the mudguard)
        for side in (1, -1):
            tube = geo.lathe([(0.0, 0.0), (0.045, 0.0), (0.045, 0.13), (0.0, 0.13)], 10, axis="Z")
            geo.rotate(tube, side * math.radians(30), "Y")
            v.add(f"smine_{side}", geo.move(tube, x=side * 1.45, y=S.Y(0.74), z=1.40), kind="steel_paint")
            v.add(f"smine_base_{side}", geo.box(side * 1.45, S.Y(0.74), 1.40, 0.13, 0.13, 0.04), kind="paint",
                  chamfer=0.006)
    v.add("antenna_base", geo.move(geo.cylinder(0.045, 0.10, 8, axis="Z"), x=-1.41, y=S.Y(4.11), z=z + 0.05),
          kind="paint")
    for side in (1, -1):  # tow cable along the top of each side plate (Tiger 131 photos)
        v.add(f"tow_cable_{side}", geo.cylinder(0.022, 3.6, 6, axis="Y", center=(side * (S.SUPER_X + 0.02),
                                                                                  S.Y(3.2), z - 0.08)), kind="steel")
    v.locator("left_tracks", (S.TRACK_X, S.Y(5.6), 0.0), "tank_base")
    v.locator("right_tracks", (-S.TRACK_X, S.Y(5.6), 0.0), "tank_base")


def t1_rear(v, S):
    """Rear plate (rear view, Tiger 131 photos): two tall exhaust mufflers in sheet-metal guards (x +-0.36, z 0.82-
    1.97); Feifel air filters (early): on each upper corner a housing with two upright filter cans (x 1.10 and
    1.41) over conical dust hoppers, a pipe into the hull and ducts over the engine deck; tow shackles, jack."""
    for side in (1, -1):
        x = side * 0.363
        base_u = t1_rear_u(S, 1.4)
        guard = geo.lathe([(0.0, 0.0), (0.20, 0.0), (0.215, 0.03), (0.215, 1.09), (0.19, 1.15), (0.0, 1.15)], 16,
                          axis="Z")
        geo.transform(guard, Matrix.Scale(0.62, 4, (0, 1, 0)))
        v.add(f"exhaust_guard_{side}", geo.move(guard, x=x, y=S.Y(base_u + 0.10), z=0.82), kind="exhaust")
        v.locator("left_exhaust" if side > 0 else "right_exhaust", (x, S.Y(base_u + 0.10), 2.02), "chassie")
        sh = parts.tow_shackle()
        geo.transform(sh, Matrix.Scale(1.3, 4))
        v.add(f"tow_rear_{side}", geo.move(sh, x=side * 0.95, y=S.Y(t1_rear_u(S, 0.85) + 0.05), z=0.85),
              kind="steel")
        if S.FEIFEL:
            hu = t1_rear_u(S, 1.75) + 0.20
            v.add(f"feifel_box_{side}", geo.box(side * 1.255, S.Y(hu), 1.78, 0.66, 0.34, 0.20), kind="paint",
                  chamfer=0.02)
            for k, fx in enumerate((1.10, 1.41)):
                can = geo.lathe([(0.0, 0.0), (0.06, 0.0), (0.15, 0.13), (0.15, 0.47), (0.14, 0.50), (0.0, 0.50)],
                                14, axis="Z")
                v.add(f"feifel_can_{side}_{k}", geo.move(can, x=side * fx, y=S.Y(hu + 0.02), z=1.45), kind="paint",
                      smooth_angle=50)
            pipe = geo.cylinder(0.065, 0.30, 10, axis="X", center=(side * 0.88, S.Y(hu - 0.05), 1.82))
            v.add(f"feifel_pipe_{side}", pipe, kind="paint")
            v.add(f"feifel_bracket_{side}", geo.box(side * 1.255, S.Y(hu - 0.06), 1.40, 0.50, 0.20, 0.04),
                  kind="paint", chamfer=0.008)
            # duct over the deck from the filter to the engine intake by the turret (top view diagonals)
            a = Vector((side * 0.98, S.Y(5.90), S.DECK_Z + 0.10))
            b = Vector((side * 0.32, S.Y(4.95), S.DECK_Z + 0.08))
            d = b - a
            duct = geo.cylinder(0.065, d.length, 10, axis="Y")
            geo.transform(duct, d.to_track_quat("Y", "Z").to_matrix().to_4x4())
            v.add(f"feifel_duct_{side}", geo.move(duct, *((a + b) / 2)), kind="paint")
    v.add("jack", geo.box(0.0, S.Y(t1_rear_u(S, 0.62) + 0.10), 0.62, 0.40, 0.14, 0.14), kind="paint",
          chamfer=0.015)
    v.add("rear_hatch", geo.move(geo.lathe([(0.0, 0.03), (0.14, 0.03), (0.16, 0.0), (0.0, 0.0)], 14, axis="Y"),
                                 x=0.0, y=S.Y(t1_rear_u(S, 0.74) + 0.01), z=0.74), kind="paint")


# ---- Tiger I turret -------------------------------------------------------------------------------------------
def t1_turret_plan(S, n_arc=22):
    """Horseshoe plan [(x, u)], counter-clockwise from the front left corner: the straight side from the front
    plate's corner tangent onto the circle, round the rear, and back up the right side."""
    cu, r = S.TURRET_U, S.TURRET_R
    fu1, hw = S.TURRET_FRONT[1], S.TURRET_FRONT[2]
    # angles about the turret centre, 0 = straight back: x = r sin(a), u = cu + r cos(a)
    a0 = math.atan2(hw, fu1 - cu)  # the front corner
    d = math.hypot(hw, fu1 - cu)
    ang_left = a0 - math.acos(r / d)  # tangent point of the straight side
    pts = [(hw, fu1)]
    for k in range(n_arc + 1):  # round the rear from the left tangent point to the right one
        a = ang_left - 2 * ang_left * k / n_arc
        pts.append((r * math.sin(a), cu + r * math.cos(a)))
    pts.append((-hw, fu1))
    return pts


def t1_roof_z(S, u):
    z0, zf, zr, ur = S.TURRET_Z
    fu1 = S.TURRET_FRONT[1]
    return zf + (zr - zf) * min(1.0, max(0.0, (u - fu1) / (ur - fu1)))


def t1_wall_x(S, u):
    """Half-width of the horseshoe at u (plan)."""
    pts = t1_turret_plan(S)
    best = 0.0
    for (x0, u0), (x1, u1) in zip(pts, pts[1:]):
        if x0 >= 0 and x1 >= 0 and min(u0, u1) <= u <= max(u0, u1) and u0 != u1:
            best = max(best, x0 + (x1 - x0) * (u - u0) / (u1 - u0))
    return best


def t1_turret_shell(v, S):
    """Turret: ONE horseshoe side-and-rear plate bent round (vertical walls), the flat 100 mm front plate across
    its open front, the roof sloping down to the front plate; turret ring collar under it."""
    z0 = S.TURRET_Z[0]
    plan = t1_turret_plan(S)
    bot = [(x, S.Y(u), z0) for x, u in plan]
    top = [(x, S.Y(u), t1_roof_z(S, u)) for x, u in plan]
    v.add("turret", geo.loft(bot, top), kind="paint", bone="turret", chamfer=0.03, smooth_angle=30)
    fu0, fu1, hw = S.TURRET_FRONT
    zf = S.TURRET_Z[1]
    front = [(fu0 + 0.04, z0), (fu1 + 0.02, z0), (fu1 + 0.02, zf + 0.005), (fu0 + 0.10, zf + 0.005)]
    v.add("turret_front", geo.prism_x(P(S, front), -hw - 0.01, hw + 0.01), kind="paint", bone="turret",
          chamfer=0.03)
    collar = geo.cylinder(0.98, z0 - S.DECK_Z + 0.02, 40, axis="Z",
                          center=(0, S.Y(S.TURRET_U), (z0 + S.DECK_Z) / 2))
    v.add("turret_collar", collar, kind="paint", bone="turret")


def t1_mantlet(v, S):
    """Gun mantlet (side/front views, Tiger 131 photos): a thick plate as wide as the turret front, curved about the
    trunnion axis (one smooth face, side view: front at u 1.66 at the gun, 1.70 at the top and bottom edges), its
    ends turned back; the bolted collar of the gun sleeve; coaxial MG port right, sight apertures left."""
    m = S.MANTLET
    (rc_u, rc_z), rr = m["rc"], m["r"]
    prof = c.drum_profile(S, rc_u, rc_z, rr, m["z0"], m["z1"], rr, m["depth"], 14)
    hw = m["half_w"]
    v.add("mantlet", geo.prism_x(prof, -hw + 0.07, hw - 0.07), kind="paint_cast", bone="turret", chamfer=0.02,
          smooth_angle=55)
    for side in (1, -1):  # ends turned back towards the front plate (front view: framed bands at the ends)
        prof_e = c.drum_profile(S, rc_u + 0.04, rc_z, rr - 0.01, m["z0"] + 0.02, m["z1"] - 0.02, rr - 0.01,
                                m["depth"] - 0.03, 10)
        x0, x1 = (hw - 0.08, hw) if side > 0 else (-hw, -hw + 0.08)
        v.add(f"mantlet_end_{side}", geo.prism_x(prof_e, x0, x1), kind="paint_cast", bone="turret", chamfer=0.025,
              smooth_angle=55)
    face_u = lambda z: rc_u - math.sqrt(max(rr * rr - (z - rc_z) ** 2, 0.0))
    # gun sleeve: big boss on the mantlet with the bolted collar (side view: r 0.20 at u 1.51-1.63)
    fu = face_u(S.GUN_Z)
    boss = geo.lathe([(0.0, 0.0), (0.31, 0.0), (0.29, -0.03), (0.21, -0.05), (0.0, -0.05)], 24, axis="Y")
    v.add("mantlet_boss", geo.move(boss, x=0.0, y=S.Y(fu + 0.02), z=S.GUN_Z), kind="paint_cast", bone="turret",
          smooth_angle=50)
    collar = geo.lathe([(0.0, 0.0), (0.20, 0.0), (0.20, -0.12), (0.185, -0.14), (0.0, -0.14)], 20, axis="Y")
    v.add("gun_collar", geo.move(collar, x=0.0, y=S.Y(fu - 0.02), z=S.GUN_Z), kind="paint_cast", bone="turret")
    cx, cz = S.COAX
    v.add("coax_port", geo.move(geo.cylinder(0.035, 0.05, 10, axis="Y"), x=cx, y=S.Y(face_u(cz) - 0.015), z=cz),
          kind="glass", bone="turret")
    kind_, sx = S.SIGHT
    holes = (sx - 0.045, sx + 0.045) if kind_ == "bino" else (sx,)
    for k, x in enumerate(holes):
        v.add(f"sight_{k}", geo.move(geo.cylinder(0.028, 0.05, 10, axis="Y"), x=x, y=S.Y(face_u(2.24) - 0.015),
                                     z=2.24), kind="glass", bone="turret")


def t1_gun(v, S):
    """8.8 cm KwK 36 L/56 (side view): recoil sleeve r 0.171 from the collar to u 0.86, barrel jacket r 0.119 to the
    bow, barrel tapering 0.093 -> 0.073, double-baffle brake 0.49 m long, 0.26 m across; muzzle at u -2.10."""
    brake_l = 0.49
    m0 = S.MUZZLE_U + brake_l
    sections = [(0.171, 1.51), (0.171, 0.86), (0.13, 0.84), (0.119, 0.80), (0.119, 0.0), (0.095, -0.03),
                (0.093, -0.06), (0.073, m0 + 0.10), (0.078, m0 + 0.06), (0.078, m0)]

    def brake():
        bm = parts.muzzle_brake_double(0.131, brake_l, 18)
        geo.transform(bm, Matrix.Scale(0.80, 4, (1, 0, 0)))  # flattened sides (front view)
        return bm

    c.gun(v, S, 0.0, S.GUN_Z, 1.51, sections, S.MUZZLE_U, (brake, brake_l), segments=18, base_u=2.05)


def t1_cupola(v, S):
    """Commander's cupola, left rear of the roof (top view centre u 3.60, x 0.53; 0.88 m across).
    drum (early): tall cylindrical drum with five vision slits under brows, hatch hinged up (rear view 2.85 m);
    cast (mid/late): low cast cupola with seven periscopes under an armoured rim, flat hatch, AA ring."""
    kind_, cu, cx = S.CUPOLA
    x, y = cx, S.Y(cu)
    z = S.TURRET_Z[2]
    if kind_ == "drum":
        prof = [(0.0, -0.02), (0.44, -0.02), (0.44, 0.04), (0.405, 0.05), (0.405, 0.22), (0.385, 0.25), (0.0, 0.25)]
        v.add("cupola", geo.move(geo.lathe(prof, 28, axis="Z"), x=x, y=y, z=z), kind="paint_cast", bone="turret",
              smooth_angle=50)
        hatch = geo.lathe([(0.0, 0.035), (0.34, 0.035), (0.36, 0.0), (0.0, 0.0)], 20, axis="Z")
        v.add("cupola_hatch", geo.move(hatch, x=x, y=y, z=z + 0.25), kind="paint_cast", bone="turret",
              smooth_angle=50)
        for k in range(5):
            a = math.pi + 2 * math.pi * k / 5
            g = geo.box(0.40, 0, 0, 0.02, 0.15, 0.03)
            geo.rotate(g, a, "Z")
            v.add(f"cupola_slit_{k}", geo.move(g, x=x, y=y, z=z + 0.13), kind="glass", bone="turret")
            brow = geo.box(0.415, 0, 0, 0.03, 0.20, 0.025)
            geo.rotate(brow, a, "Z")
            v.add(f"cupola_brow_{k}", geo.move(brow, x=x, y=y, z=z + 0.165), kind="paint_cast", bone="turret",
                  chamfer=0.006)
        return
    # cast cupola (from July 1943): low dome, periscopes under the overhanging rim, pivoting flat hatch
    prof = [(0.0, -0.02), (0.44, -0.02), (0.44, 0.03), (0.40, 0.05), (0.38, 0.13), (0.41, 0.14), (0.41, 0.17),
            (0.33, 0.20), (0.0, 0.20)]
    v.add("cupola", geo.move(geo.lathe(prof, 28, axis="Z"), x=x, y=y, z=z), kind="paint_cast", bone="turret",
          smooth_angle=50)
    v.add("cupola_hatch", geo.move(geo.lathe([(0.0, 0.04), (0.29, 0.035), (0.31, 0.0), (0.0, 0.0)], 20, axis="Z"),
                                   x=x, y=y, z=z + 0.20), kind="paint_cast", bone="turret", smooth_angle=50)
    for k in range(7):
        a = 2 * math.pi * (k + 0.5) / 7
        glass = geo.box(0.39, 0, 0, 0.012, 0.11, 0.035)
        geo.rotate(glass, a, "Z")
        v.add(f"cupola_glass_{k}", geo.move(glass, x=x, y=y, z=z + 0.10), kind="glass", bone="turret")
    ring = geo.lathe([(0.40, 0.0), (0.43, 0.0), (0.43, 0.03), (0.40, 0.03), (0.40, 0.0)], 28, axis="Z")
    v.add("aa_ring", geo.move(ring, x=x, y=y, z=z + 0.19), kind="steel_paint", bone="turret")


def t1_turret_fittings(v, S):
    """Turret side and roof fittings: round visors at the front of both sides (left: side view u 2.60, z 2.25);
    pistol port (left rear, u 3.94, z 2.19) or the escape hatch (right rear, Tiger 131 photos); NbK 39 smoke
    dischargers, three on each front corner (early); stowage bin on the rear; roof vent, loader's hatch, and the
    loader's periscope and Pilze crane sockets (late); lifting eyes."""
    def wall_point(u, z, side, out=0.0):
        xw = t1_wall_x(S, u)
        # normal of the wall in plan at u
        e = 0.02
        dxdu = (t1_wall_x(S, u + e) - t1_wall_x(S, u - e)) / (2 * e)
        n = Vector((1.0, -dxdu)).normalized()
        return Vector((side * (xw + out * n.x), S.Y(u + out * n.y), z)), Vector((side * n.x, n.y, 0.0))

    def on_wall(name, bm, u, z, side, out, kind="paint_cast"):
        p, n = wall_point(u, z, side, out)
        # local +Z = outward wall normal, +X = up the wall... right-handed on both sides
        zax = Vector((n.x, n.y, 0)).normalized()
        yax = Vector((0, 0, 1))
        xax = yax.cross(zax).normalized()
        rot = Matrix((xax, yax, zax)).transposed().to_4x4()
        geo.transform(bm, rot)
        v.add(name, geo.move(bm, *p), kind=kind, bone="turret", smooth_angle=50)

    for side in (1, -1):
        visor = geo.lathe([(0.0, 0.06), (0.09, 0.06), (0.11, 0.03), (0.115, 0.0), (0.0, 0.0)], 16, axis="Z")
        on_wall(f"turret_visor_{side}", visor, 2.60, 2.25, side, 0.0)
        slit = geo.box(0, 0, 0.061, 0.10, 0.018, 0.004)
        on_wall(f"turret_visor_slit_{side}", slit, 2.60, 2.25, side, 0.0, kind="glass")
        if S.SMOKE:
            # NbK 39: three cups on a bracket at the front corner, fanned out and up (side view u 2.34-2.57,
            # z 2.26-2.60; front view x 1.20-1.31)
            for k in range(3):
                tube = geo.lathe([(0.0, 0.0), (0.045, 0.0), (0.045, 0.17), (0.0, 0.17)], 10, axis="Z")
                geo.rotate(tube, math.radians(-50), "X")  # leaning forward
                geo.rotate(tube, side * math.radians(25 + 25 * (k - 1)), "Y")  # fanned out sideways
                p, _ = wall_point(2.47, 2.30 + 0.085 * k, side, 0.09)
                v.add(f"smoke_{side}_{k}", geo.move(tube, *p), kind="steel_paint", bone="turret")
            p, _ = wall_point(2.47, 2.38, side, 0.03)
            v.add(f"smoke_mount_{side}", geo.move(geo.box(0, 0, 0, 0.06, 0.10, 0.22), *p), kind="paint",
                  bone="turret", chamfer=0.006)
    plug = geo.lathe([(0.0, 0.05), (0.11, 0.05), (0.13, 0.02), (0.135, 0.0), (0.0, 0.0)], 16, axis="Z")
    on_wall("turret_pistol_port", plug, 3.94, 2.19, 1, 0.0)
    if S.ESCAPE_HATCH:  # Notausstieg: large round hatch in the right rear of the horseshoe (from December 1942)
        esc = geo.lathe([(0.0, 0.05), (0.25, 0.05), (0.27, 0.02), (0.275, 0.0), (0.0, 0.0)], 22, axis="Z")
        on_wall("turret_escape_hatch", esc, 4.02, 2.22, -1, 0.0)
    else:
        plug_r = geo.lathe([(0.0, 0.05), (0.11, 0.05), (0.13, 0.02), (0.135, 0.0), (0.0, 0.0)], 16, axis="Z")
        on_wall("turret_pistol_port_r", plug_r, 3.94, 2.19, -1, 0.0)
    # stowage bin (Gepäckkasten) on the rear: box with rounded rear corners (side/top views)
    u0, u1, hw, zb, zt = S.BIN
    plan = [(-hw, u0), (hw, u0), (hw, u1 - 0.10), (hw - 0.04, u1 - 0.02), (hw - 0.12, u1), (-hw + 0.12, u1),
            (-hw + 0.04, u1 - 0.02), (-hw, u1 - 0.10)]
    v.add("turret_bin", geo.loft([(x, S.Y(u), zb) for x, u in plan], [(x, S.Y(u), zt) for x, u in plan]),
          kind="paint", bone="turret", chamfer=0.02)
    roof = S.TURRET_Z[2]
    # loader's hatch (right of the roof, top view u 3.00-3.55, x -0.34 to -0.97) and the domed ventilator behind it
    v.add("loader_hatch", geo.box(-0.65, S.Y(3.27), roof + 0.03, 0.62, 0.55, 0.05), kind="paint", bone="turret",
          chamfer=0.02)
    vent = geo.lathe([(0.0, 0.10), (0.10, 0.09), (0.15, 0.04), (0.16, 0.0), (0.0, 0.0)], 14, axis="Z")
    v.add("vent", geo.move(vent, x=-0.59, y=S.Y(3.92), z=roof), kind="paint_cast", bone="turret")
    if S.LOADER_PERISCOPE:  # fixed periscope for the loader, roof front right (from the late Tiger I)
        v.add("loader_periscope", geo.box(-0.40, S.Y(3.0), roof + 0.05, 0.14, 0.20, 0.10), kind="paint_cast",
              bone="turret", chamfer=0.015)
    if S.PILZE:  # three 'Pilze' sockets for the 2-ton jib crane (late, from June 1944)
        for k, (px, pu) in enumerate(((0.62, 3.10), (-0.62, 3.10), (0.0, 4.15))):
            pil = geo.lathe([(0.0, 0.06), (0.06, 0.06), (0.07, 0.04), (0.035, 0.03), (0.035, 0.0), (0.0, 0.0)], 10,
                            axis="Z")
            v.add(f"pilz_{k}", geo.move(pil, x=px, y=S.Y(pu), z=roof), kind="paint", bone="turret")
    else:
        for k, (px, pu) in enumerate(((0.80, 2.55), (-0.80, 2.55), (0.75, 4.05), (-0.75, 4.05))):
            v.add(f"lift_eye_{k}", geo.box(px, S.Y(pu), t1_roof_z(S, pu) + 0.035, 0.03, 0.12, 0.08), kind="paint",
                  bone="turret", chamfer=0.008)


def t1_turret(v, S):
    t1_turret_shell(v, S)
    t1_mantlet(v, S)
    t1_gun(v, S)
    t1_cupola(v, S)
    t1_turret_fittings(v, S)
    v.bone("turret", (0, S.Y(S.TURRET_U), S.DECK_Z), "chassie")


def build_tiger1(v, S):
    init(S)
    t1_hull(v, S)
    t1_fenders(v, S)
    t1_front(v, S)
    t1_deck(v, S)
    t1_rear(v, S)
    running_gear(v, S)
    t1_turret(v, S)
    rig(v, S)
