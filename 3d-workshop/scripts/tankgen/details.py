"""Bake-only detail geometry, placed on armour surfaces through a Frame (origin + in-plane axes + outward normal).

Everything here goes into the high-poly bake source (Vehicle.detail), so it can be dense: it costs nothing in game.
"""

import math

import bmesh
from mathutils import Matrix, Vector

from . import geo


class Frame:
    """Surface frame: point(a, b, h) = origin + a*u + b*v + h*n."""

    def __init__(self, origin, u, v, n=None):
        self.o = Vector(origin)
        self.u = Vector(u).normalized()
        self.v = Vector(v).normalized()
        self.n = Vector(n).normalized() if n is not None else self.u.cross(self.v).normalized()

    def point(self, a, b, h=0.0):
        return self.o + self.u * a + self.v * b + self.n * h

    def matrix(self, a=0.0, b=0.0, h=0.0):
        """Local space: X = u, Y = v, Z = n, origin at point(a, b, h)."""
        m = Matrix((self.u, self.v, self.n)).transposed().to_4x4()
        m.translation = self.point(a, b, h)
        return m

    @staticmethod
    def from_points(p0, p1, p2, outward_hint):
        """Frame on the plane p0 (origin), p1 (u direction), p2 (v direction); flips n to face outward_hint."""
        p0, p1, p2 = Vector(p0), Vector(p1), Vector(p2)
        u = (p1 - p0).normalized()
        v = (p2 - p0)
        v = (v - u * v.dot(u)).normalized()
        n = u.cross(v)
        if n.dot(Vector(outward_hint)) < 0:
            v = -v
            n = -n
        return Frame(p0, u, v, n)


def _place(bm, frame, a, b, h=0.0, rot=0.0):
    m = frame.matrix(a, b, h) @ Matrix.Rotation(rot, 4, "Z")
    geo.transform(bm, m)
    return bm


def _merge(parts):
    parts = [p for p in parts if p is not None]
    if not parts:
        return bmesh.new()
    return geo.merge(*parts)


# ---- primitives in local space (Z = surface normal) -----------------------------------------------------------
def _hex_bolt(r, h):
    return geo.lathe([(0.0, h), (r * 0.9, h), (r, h * 0.7), (r, 0.0), (0.0, -0.003)], 6, axis="Z")


def _rivet(r):
    return geo.lathe([(0.0, r * 0.55), (r * 0.6, r * 0.42), (r, 0.0), (0.0, -0.003)], 8, axis="Z")


# ---- public generators ---------------------------------------------------------------------------------------
def bolts(frame, points_ab, r=0.016, h=0.012):
    return _merge([_place(_hex_bolt(r, h), frame, a, b) for a, b in points_ab])


def rivets(frame, points_ab, r=0.012):
    return _merge([_place(_rivet(r), frame, a, b) for a, b in points_ab])


def line(a0, b0, a1, b1, n):
    if n == 1:
        return [((a0 + a1) / 2, (b0 + b1) / 2)]
    return [(a0 + (a1 - a0) * i / (n - 1), b0 + (b1 - b0) * i / (n - 1)) for i in range(n)]


def rect_border(a0, b0, a1, b1, spacing, inset=0.0):
    a0, b0, a1, b1 = a0 + inset, b0 + inset, a1 - inset, b1 - inset
    pts = []
    na = max(2, round((a1 - a0) / spacing) + 1)
    nb = max(2, round((b1 - b0) / spacing) + 1)
    pts += line(a0, b0, a1, b0, na) + line(a0, b1, a1, b1, na)
    pts += line(a0, b0, a0, b1, nb)[1:-1] + line(a1, b0, a1, b1, nb)[1:-1]
    return pts


def circle(ca, cb, radius, n, phase=0.0):
    return [(ca + radius * math.cos(phase + 2 * math.pi * i / n), cb + radius * math.sin(phase + 2 * math.pi * i / n))
            for i in range(n)]


def weld_bead(frame, points_ab, r=0.013, step=0.026):
    """Chain of flattened beads along a polyline on the surface (plate joints)."""
    parts = []
    for (a0, b0), (a1, b1) in zip(points_ab, points_ab[1:]):
        length = math.hypot(a1 - a0, b1 - b0)
        n = max(1, int(length / step))
        ang = math.atan2(b1 - b0, a1 - a0)
        for i in range(n + 1):
            t = i / n
            bead = geo.lathe([(0.0, r * 0.45), (r * 0.8, r * 0.3), (r, 0.0), (0.0, -0.003)], 6, axis="Z")
            geo.transform(bead, Matrix.Diagonal((1.35, 1.0, 1.0, 1.0)))
            parts.append(_place(bead, frame, a0 + (a1 - a0) * t, b0 + (b1 - b0) * t, 0.0, ang))
    return _merge(parts)


def hinge(frame, a, b, length, r=0.022, along_u=True):
    """Hinge barrel with two straps, axis along u (or v)."""
    barrel = geo.cylinder(r, length, 10, axis="X")
    geo.move(barrel, z=r * 0.8)
    straps = [geo.box(s * length * 0.3, -0.06, 0.006, length * 0.22, 0.12, 0.012) for s in (-1, 1)]
    bm = _merge([barrel] + straps)
    return _place(bm, frame, a, b, 0.0, 0.0 if along_u else math.pi / 2)


def handle(frame, a, b, width=0.16, height=0.05, r=0.009, rot=0.0):
    """Grab handle: U-shaped bar standing off the plate."""
    hw = width / 2
    parts = [geo.cylinder(r, width, 6, axis="X", center=(0, 0, height)),
             geo.cylinder(r, height, 6, axis="Z", center=(-hw, 0, height / 2)),
             geo.cylinder(r, height, 6, axis="Z", center=(hw, 0, height / 2))]
    return _place(_merge(parts), frame, a, b, 0.0, rot)


def grille(frame, a0, b0, a1, b1, slats, depth=0.025, tilt_deg=35.0, frame_w=0.025):
    """Louvred grille: raised frame with tilted slats along u."""
    w, h = a1 - a0, b1 - b0
    ca, cb = (a0 + a1) / 2, (b0 + b1) / 2
    parts = [geo.box(ca, b0 + frame_w / 2, depth / 2, w, frame_w, depth),
             geo.box(ca, b1 - frame_w / 2, depth / 2, w, frame_w, depth),
             geo.box(a0 + frame_w / 2, cb, depth / 2, frame_w, h, depth),
             geo.box(a1 - frame_w / 2, cb, depth / 2, frame_w, h, depth)]
    inner = h - 2 * frame_w
    pitch = inner / slats
    for i in range(slats):
        slat = geo.box(0, 0, 0, w - 2 * frame_w, pitch * 0.85, 0.006)
        geo.rotate(slat, math.radians(tilt_deg), "X")
        geo.move(slat, x=ca, y=b0 + frame_w + pitch * (i + 0.5), z=depth * 0.55)
        parts.append(slat)
    bm = _merge(parts)
    geo.transform(bm, frame.matrix())
    return bm


def mesh_grille(frame, a0, b0, a1, b1, cells_a, cells_b, depth=0.02, wire=0.006):
    """Wire-mesh screen over an opening (engine intakes)."""
    parts = []
    for i in range(cells_a + 1):
        a = a0 + (a1 - a0) * i / cells_a
        parts.append(geo.box(a, (b0 + b1) / 2, depth, wire, b1 - b0, wire))
    for j in range(cells_b + 1):
        b = b0 + (b1 - b0) * j / cells_b
        parts.append(geo.box((a0 + a1) / 2, b, depth, a1 - a0, wire, wire))
    bm = _merge(parts)
    geo.transform(bm, frame.matrix())
    return bm


def plate(frame, a0, b0, a1, b1, thickness=0.012, chamfer=0.004):
    """Raised appliqué plate / hatch lid."""
    bm = geo.box((a0 + a1) / 2, (b0 + b1) / 2, thickness / 2, a1 - a0, b1 - b0, thickness)
    geo.chamfer(bm, chamfer)
    geo.transform(bm, frame.matrix())
    return bm


def vision_block(frame, a, b, w=0.12, h=0.035, depth=0.02):
    """Dark glass block recessed in an armoured slot (kind 'glass')."""
    bm = geo.box(a, b, depth * 0.3, w, h, depth * 0.6)
    geo.transform(bm, frame.matrix())
    return bm


def lifting_hook(frame, a, b, r=0.02, rot=0.0):
    ring = geo.lathe([(0.04, 0.0), (0.045, 0.012), (0.04, 0.024), (0.035, 0.012)], 10, axis="Y", close_axis=False)
    geo.transform(ring, Matrix.Rotation(math.pi / 2, 4, "X"))
    base = geo.box(0, 0, 0.008, 0.07, 0.03, 0.016)
    geo.move(ring, z=0.05)
    return _place(_merge([ring, base]), frame, a, b, 0.0, rot)


def wheel_hub_bolts(center, axis_sign, ring_r, n, r=0.011, h=0.009, x_face=0.0):
    """Bolt ring on a wheel face whose axle is world X (wheel face normal = axis_sign * X)."""
    f = Frame(Vector(center) + Vector((x_face, 0, 0)), (0, 1, 0), (0, 0, 1), (axis_sign, 0, 0))
    return bolts(f, circle(0, 0, ring_r, n, math.pi / n), r, h)
