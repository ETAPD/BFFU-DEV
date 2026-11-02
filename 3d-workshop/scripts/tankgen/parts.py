"""Reusable tank parts. All functions return bmesh objects centred on their own pivot (wheels on their axle)."""

import math

import bmesh
from mathutils import Matrix

from . import geo


def road_wheel_disc(radius, width, hub_r, segments, outer=True):
    """One rubber-tyred steel disc, axle along X, outward face towards +X. Returns (steel, tyre) bmeshes;
    the inner disc of a pair has no visible steel face, so its steel part is None."""
    w = width / 2
    rim = radius - 0.03
    # closed ring (inner wall at the rim included): an open tyre showed its inside, which the game culls to a hole
    tyre = geo.lathe([(rim, w + 0.004), (radius - 0.008, w), (radius, w - 0.012), (radius, -w + 0.012),
                      (radius - 0.008, -w), (rim, -w), (rim, w + 0.004)], segments)
    if not outer:
        return None, tyre
    face = geo.lathe([(0.0, w + 0.03), (hub_r, w + 0.018), (radius * 0.78, w - 0.006), (rim, w + 0.004)], segments)
    return face, tyre


def flat_road_wheel(radius, width, hub_r, segments):
    """Road wheel lying loose (spare wheel racks): steel face on both sides, so a stack is closed top and bottom.
    Returns (steel, tyre)."""
    face, tyre = road_wheel_disc(radius, width, hub_r, segments, outer=True)
    back = face.copy()
    geo.transform(back, Matrix.Scale(-1, 4, (1, 0, 0)))
    bmesh.ops.reverse_faces(back, faces=back.faces)
    return geo.merge(face, back), tyre


def double_road_wheel(radius, disc_width, gap, hub_r, segments):
    """Returns (steel, rubber) bmeshes for a pair of discs straddling the track guide horns."""
    off = (disc_width + gap) / 2
    face, tyre_o = road_wheel_disc(radius, disc_width, hub_r, segments, outer=True)
    _, tyre_i = road_wheel_disc(radius, disc_width, hub_r, segments, outer=False)
    geo.move(face, x=off)
    geo.move(tyre_o, x=off)
    geo.move(tyre_i, x=-off)
    return face, geo.merge(tyre_o, tyre_i)


def sprocket(radius, teeth, ring_width, gap, hub_r, segments=None):
    """Two toothed rings with a dished hub. Teeth are flat trapezoids around the ring."""
    seg = segments or teeth * 2
    off = (ring_width + gap) / 2
    parts = []
    for side in (1, -1):
        prof = [(radius * 0.86, ring_width / 2), (radius * 0.92, ring_width / 2),
                (radius * 0.92, -ring_width / 2), (radius * 0.86, -ring_width / 2), (radius * 0.86, ring_width / 2)]
        ring = geo.lathe(prof, seg)  # closed ring section: an open ring shows its culled inside
        geo.move(ring, x=side * off)
        parts.append(ring)
        for t in range(teeth):
            a = 2 * math.pi * t / teeth
            tooth = geo.loft_z([(-ring_width / 2, -0.035), (ring_width / 2, -0.035),
                                (ring_width / 2, 0.035), (-ring_width / 2, 0.035)], radius * 0.9,
                               [(-ring_width / 2, -0.014), (ring_width / 2, -0.014),
                                (ring_width / 2, 0.014), (-ring_width / 2, 0.014)], radius, cap=True)
            geo.rotate(tooth, a, "X")
            geo.move(tooth, x=side * off)
            parts.append(tooth)
    hub = geo.lathe([(0.0, off + ring_width / 2 + 0.07), (hub_r * 0.7, off + ring_width / 2 + 0.065),
                     (hub_r, off + ring_width / 2 + 0.03), (radius * 0.86, off - 0.01),
                     (radius * 0.86, -off + 0.01), (hub_r, -off - 0.03), (0.0, -off - 0.04)], 16)
    parts.append(hub)
    return geo.merge(*parts)


def idler(radius, width, gap, segments=18, spokes=0):
    """Rear idler: two steel rims on a hub (tubular welded idler on Pz IV H is approximated by a dished disc)."""
    off = (width + gap) / 2
    parts = []
    for side in (1, -1):
        rim = geo.lathe([(radius * 0.82, width / 2), (radius, width / 2 - 0.005), (radius, -width / 2 + 0.005),
                         (radius * 0.82, -width / 2), (radius * 0.82, width / 2)], segments)  # closed ring section
        geo.move(rim, x=side * off)
        parts.append(rim)
    disc = geo.lathe([(0.0, off + 0.08), (radius * 0.18, off + 0.075), (radius * 0.25, off + 0.04),
                      (radius * 0.82, off + width / 2 - 0.005), (radius * 0.82, -off - width / 2 + 0.005),
                      (radius * 0.25, -off - 0.03), (0.0, -off - 0.035)], segments)
    parts.append(disc)
    return geo.merge(*parts)


def return_roller(radius, width, segments=12):
    prof = [(0.0, width / 2 + 0.025), (radius * 0.5, width / 2 + 0.02), (radius, width / 2 - 0.008),
            (radius, -width / 2 + 0.008), (radius * 0.35, -width / 2 - 0.12)]
    return geo.lathe(prof, segments)


def _circle_pts(circles):
    pts = []
    for y, z, r in circles:
        for k in range(48):
            a = 2 * math.pi * k / 48
            pts.append((y + r * math.cos(a), z + r * math.sin(a)))
    return pts


def _upper_z(hull, y):
    """Highest z of a closed convex polygon at y (None outside it)."""
    best = None
    for i in range(len(hull)):
        (y0, z0), (y1, z1) = hull[i - 1], hull[i]
        if min(y0, y1) <= y <= max(y0, y1) and y0 != y1:
            z = z0 + (z1 - z0) * (y - y0) / (y1 - y0)
            best = z if best is None else max(best, z)
    return best


def _drape(loop, circles):
    """Lower the top run onto the road wheels (no return rollers): circles[0] and [1] are the sprocket and idler,
    circles[2:] the road wheels. The belt runs straight from each end wheel down to the nearest road wheel, then
    across the road-wheel tops, sagging a little between them."""
    ends, wheels = circles[:2], circles[2:]
    wz = max(z for _, z, _ in wheels)
    ramps = [geo.convex_hull_2d(_circle_pts([e, min(wheels, key=lambda w: abs(w[0] - e[0]))])) for e in ends]
    across = geo.convex_hull_2d(_circle_pts(wheels))
    y_lo, y_hi = sorted((ends[0][0], ends[1][0]))
    out = []
    for y, z in loop:
        if z > wz and y_lo < y < y_hi:
            tops = [zz for zz in (_upper_z(h, y) for h in ramps) if zz is not None]
            flat = _upper_z(across, y)
            if flat is not None:
                env = max((cz + math.sqrt(r * r - (y - cy) ** 2) for cy, cz, r in wheels if abs(y - cy) < r),
                          default=flat)
                tops.append(flat - 0.3 * (flat - env))
            if tops:
                z = min(z, max(tops))
        out.append((y, z))
    return out


def track_belt(circles, x_center, width, thickness, spacing, tile_length, sag=None, drape=False):
    """Closed track belt around wheel circles [(y, z, r), ...] (side view). drape: the top run rests on the road
    wheels (circles[2:]) instead of running straight from the sprocket (circles[0]) to the idler (circles[1]).

    UVs: outer face uses u 0..0.75 across the track width, inner/side faces share the 0.75..1 strip;
    v runs along the belt in tiles of `tile_length` metres so PdxMeshAdvancedAnim can scroll it.
    """
    import bmesh
    from mathutils import Vector

    hull = geo.convex_hull_2d(_circle_pts(circles))
    if drape:
        hull = _drape(geo.resample_loop(hull, spacing / 4)[0], circles)
    loop, arcs, total = geo.resample_loop(hull, spacing)
    # snap the loop length to whole texture tiles so the scroll seam is invisible
    tiles = max(1, round(total / tile_length))
    v_scale = tiles / total

    # convex hull is counter-clockwise in (y, z); outward normal is the right-hand perpendicular
    n = len(loop)
    normals = []
    for i in range(n):
        p0, p1 = Vector(loop[i - 1]), Vector(loop[(i + 1) % n])
        d = (p1 - p0).normalized()
        normals.append(Vector((d.y, -d.x)))

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    hw = width / 2
    ring = []
    for i in range(n):
        p, nrm = Vector(loop[i]), normals[i]
        o = p + nrm * thickness
        ring.append([bm.verts.new((x_center - hw, p.x, p.y)), bm.verts.new((x_center + hw, p.x, p.y)),
                     bm.verts.new((x_center + hw, o.x, o.y)), bm.verts.new((x_center - hw, o.x, o.y))])
    # quads: inner (0-1), outer (2-3), sides (1-2) (3-0)
    strips = [((3, 2), (0.0, 0.75)), ((1, 0), (0.75, 1.0)), ((2, 1), (0.75, 0.80)), ((0, 3), (0.95, 1.0))]
    for i in range(n):
        j = (i + 1) % n
        v0 = arcs[i] * v_scale
        v1 = (arcs[j] if j else total) * v_scale
        for (a, b), (u0, u1) in strips:
            f = bm.faces.new((ring[i][a], ring[i][b], ring[j][b], ring[j][a]))
            for loop_, (uu, vv) in zip(f.loops, ((u0, v0), (u1, v0), (u1, v1), (u0, v1))):
                loop_[uv].uv = (uu, vv)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def hatch_round(radius, height, segments=16):
    return geo.lathe([(0.0, height), (radius * 0.85, height), (radius, height * 0.6), (radius, 0.0)],
                     segments, axis="Z")


def cupola(radius, height, blocks, segments=20):
    """Pz III/IV style commander cupola: armoured drum with vision block covers and a round hatch."""
    drum = geo.lathe([(radius, 0.0), (radius, height * 0.78), (radius * 0.9, height), (radius * 0.75, height),
                      (radius * 0.75, height * 0.9)], segments, axis="Z", close_axis=False)
    hatch = geo.move(hatch_round(radius * 0.74, 0.045, segments), z=height * 0.9)
    parts = [drum, hatch]
    for b in range(blocks):
        a = 2 * math.pi * (b + 0.5) / blocks
        cover = geo.box(0, 0, 0, 0.05, 0.16, 0.06)
        geo.move(cover, x=radius + 0.012, z=height * 0.55)
        geo.rotate(cover, a, "Z")
        parts.append(cover)
    return geo.merge(*parts)


def gun_barrel(sections, segments=14):
    """Lathe along -Y (forward). sections: [(r, y), ...] going forward from the mantlet face."""
    bm = geo.lathe([(r, -y) for r, y in sections], segments, axis="Y")
    return bm


def muzzle_brake_double(radius, length, segments=14):
    """Double-baffle brake (KwK 40): two chambers with open side ports approximated by recessed bands."""
    L = length
    prof = [(0.0, 0.0), (radius * 0.55, 0.0), (radius * 0.9, -0.01), (radius, -0.03), (radius, -L * 0.38),
            (radius * 0.72, -L * 0.42), (radius * 0.72, -L * 0.52), (radius, -L * 0.56), (radius, -L * 0.94),
            (radius * 0.85, -L), (radius * 0.35, -L), (radius * 0.33, -L + 0.02), (0.0, -L + 0.02)]
    return geo.lathe(prof, segments, axis="Y")


def muffler(radius, length, segments=12):
    return geo.lathe([(0.0, -length / 2 - 0.02), (radius * 0.9, -length / 2), (radius, -length / 2 + 0.02),
                      (radius, length / 2 - 0.02), (radius * 0.9, length / 2), (0.0, length / 2 + 0.02)],
                     segments, axis="X")


def mg_barrel(length, radius=0.018, jacket_r=0.028, segments=8):
    """MG 34 in a ball mount: perforated jacket + muzzle, along -Y."""
    return geo.lathe([(0.0, 0.0), (jacket_r, 0.0), (jacket_r, -length * 0.75), (radius, -length * 0.78),
                      (radius, -length), (0.0, -length)], segments, axis="Y")


def ball_mount(radius, segments=12):
    return geo.lathe([(0.0, -radius * 0.75), (radius * 0.6, -radius * 0.6), (radius, 0.0), (radius, 0.03)],
                     segments, axis="Y")


def tow_shackle():
    return geo.merge(geo.box(0, 0, 0, 0.04, 0.12, 0.10), geo.cylinder(0.025, 0.12, 8, axis="X", center=(0, -0.05, 0)))


def headlight(radius=0.07, depth=0.09, segments=10):
    bm = geo.lathe([(0.0, 0.0), (radius * 0.8, 0.0), (radius, -depth * 0.4), (radius * 0.95, -depth),
                    (0.0, -depth - 0.01)], segments, axis="Y")
    return bm


def jerrycan_like_box(sx, sy, sz):
    return geo.chamfer(geo.box(0, 0, 0, sx, sy, sz), min(sx, sy, sz) * 0.12)


def tool(length, radius=0.02, segments=6, axis="Y"):
    return geo.cylinder(radius, length, segments, axis=axis)


def shovel(length=1.1):
    handle = geo.cylinder(0.018, length * 0.75, 6, axis="Y", center=(0, length * 0.125, 0))
    blade = geo.box(0, -length * 0.36, 0, 0.022, 0.28, 0.24)
    return geo.merge(handle, blade)


def track_link_spare(width, pitch, thickness):
    return geo.chamfer(geo.box(0, 0, 0, width, pitch * 0.92, thickness), thickness * 0.3)
