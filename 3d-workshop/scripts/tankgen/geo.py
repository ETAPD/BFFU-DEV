"""Geometry primitives for the tank generator.

Axes match what io_pdx_mesh imports: +X = vehicle left, -Y = forward, +Z = up. Everything is built in metres;
build.py applies the game scale at the very end.
"""

import math

import bmesh
import bpy
from mathutils import Matrix, Vector


def new_object(name, bm, material=None, collection=None):
    mesh = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    (collection or bpy.context.scene.collection).objects.link(obj)
    if material:
        mesh.materials.append(material)
    return obj


def _cap(bm, verts, flip=False):
    if len(verts) >= 3:
        face = bm.faces.new(list(reversed(verts)) if flip else verts)
        return face
    return None


def prism_x(profile_yz, x0, x1, cap=True):
    """Extrude a side-view polygon [(y, z), ...] (counter-clockwise seen from +X) from x0 to x1."""
    bm = bmesh.new()
    a = [bm.verts.new((x0, y, z)) for y, z in profile_yz]
    b = [bm.verts.new((x1, y, z)) for y, z in profile_yz]
    n = len(profile_yz)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap:
        _cap(bm, a)
        _cap(bm, b, flip=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def prism_z(plan_xy, z0, z1, cap=True):
    """Extrude a plan polygon [(x, y), ...] vertically."""
    return loft_z(plan_xy, z0, plan_xy, z1, cap=cap)


def loft_z(bottom_xy, z0, top_xy, z1, cap=True):
    """Connect two plan polygons with the same vertex count: sloped walls (turrets, superstructures)."""
    assert len(bottom_xy) == len(top_xy)
    bm = bmesh.new()
    a = [bm.verts.new((x, y, z0)) for x, y in bottom_xy]
    b = [bm.verts.new((x, y, z1)) for x, y in top_xy]
    n = len(a)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap:
        _cap(bm, a)
        _cap(bm, b)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def loft(bottom_xyz, top_xyz, cap=True):
    """Connect two rings of 3D points (same count): faceted armour shells whose roof isn't flat, e.g. a turret
    roof that slopes down to the front plate. Caps are triangulated fans, so non-planar rings are fine."""
    assert len(bottom_xyz) == len(top_xyz)
    bm = bmesh.new()
    a = [bm.verts.new(p) for p in bottom_xyz]
    b = [bm.verts.new(p) for p in top_xyz]
    n = len(a)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap:
        for ring in (a, b):
            c = bm.verts.new(sum((v.co for v in ring), Vector()) / n)
            for i in range(n):
                bm.faces.new((ring[i], ring[(i + 1) % n], c))
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def wall_loft(bottom_xy, top_xy, z0, z1, thickness):
    """Thin wall whose bottom edge follows a different plan line than its top edge (diagonal cuts on Schürzen).
    Thickness grows to the left of the top polyline."""
    bm = bmesh.new()
    top = [Vector(p) for p in top_xy]
    bot = [Vector(p) for p in bottom_xy]
    n = len(top)

    def offsets(pts):
        out = []
        for i in range(n):
            d0 = (pts[i] - pts[i - 1]).normalized() if i > 0 else (pts[1] - pts[0]).normalized()
            d1 = (pts[i + 1] - pts[i]).normalized() if i < n - 1 else d0
            d = (d0 + d1).normalized()
            left = Vector((-d.y, d.x))
            out.append(left * thickness / max(0.3, left.dot(Vector((-d0.y, d0.x)))))
        return out

    ot, ob = offsets(top), offsets(bot)
    rows = []
    for i in range(n):
        rows.append([bm.verts.new((bot[i].x, bot[i].y, z0)), bm.verts.new((top[i].x, top[i].y, z1)),
                     bm.verts.new((top[i].x + ot[i].x, top[i].y + ot[i].y, z1)),
                     bm.verts.new((bot[i].x + ob[i].x, bot[i].y + ob[i].y, z0))])
    for i in range(n - 1):
        a, b = rows[i], rows[i + 1]
        for k in range(4):
            k2 = (k + 1) % 4
            bm.faces.new((a[k], b[k], b[k2], a[k2]))
    bm.faces.new(rows[0])
    bm.faces.new(list(reversed(rows[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def wall_z(polyline_xy, z0, z1, thickness):
    """Thin vertical wall along an open plan polyline (turret skirts). Thickness grows to the polyline's left."""
    bm = bmesh.new()
    pts = [Vector((x, y)) for x, y in polyline_xy]
    n = len(pts)
    offs = []
    for i in range(n):
        d0 = (pts[i] - pts[i - 1]).normalized() if i > 0 else (pts[1] - pts[0]).normalized()
        d1 = (pts[i + 1] - pts[i]).normalized() if i < n - 1 else d0
        d = (d0 + d1).normalized()
        left = Vector((-d.y, d.x))
        miter = 1.0 / max(0.3, left.dot(Vector((-d0.y, d0.x))))
        offs.append(left * thickness * miter)
    rows = []
    for i, p in enumerate(pts):
        o = p + offs[i]
        rows.append([bm.verts.new((p.x, p.y, z0)), bm.verts.new((p.x, p.y, z1)),
                     bm.verts.new((o.x, o.y, z1)), bm.verts.new((o.x, o.y, z0))])
    for i in range(n - 1):
        a, b = rows[i], rows[i + 1]
        for k in range(4):
            k2 = (k + 1) % 4
            bm.faces.new((a[k], b[k], b[k2], a[k2]))
    bm.faces.new(rows[0])
    bm.faces.new(list(reversed(rows[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def lathe(profile, segments, axis="X", angle=2 * math.pi, close_axis=True):
    """Revolve [(r, a), ...] (radius, position along axis) around the axis through the origin."""
    bm = bmesh.new()
    rings = []
    full = abs(angle - 2 * math.pi) < 1e-6
    steps = segments if full else segments + 1
    for s in range(steps):
        t = angle * s / segments
        c, sn = math.cos(t), math.sin(t)
        ring = []
        for r, a in profile:
            if axis == "X":
                co = (a, r * c, r * sn)
            elif axis == "Y":
                co = (r * c, a, r * sn)
            else:
                co = (r * c, r * sn, a)
            ring.append(co)
        rings.append(ring)
    verts = [[None] * len(profile) for _ in rings]
    pole = {}
    for s, ring in enumerate(rings):
        for k, co in enumerate(ring):
            if profile[k][0] < 1e-6 and close_axis:
                if k not in pole:
                    pole[k] = bm.verts.new(co)
                verts[s][k] = pole[k]
            else:
                verts[s][k] = bm.verts.new(co)
    count = len(rings) if full else len(rings) - 1
    for s in range(count):
        s2 = (s + 1) % len(rings)
        for k in range(len(profile) - 1):
            quad = [verts[s][k], verts[s][k + 1], verts[s2][k + 1], verts[s2][k]]
            uniq = []
            for v in quad:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) >= 3:
                try:
                    bm.faces.new(uniq)
                except ValueError:
                    pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    # lathe surfaces are often open (wheel faces, tyres), where recalc_face_normals guesses; the pivot is the
    # axis, so outward simply means pointing away from the origin
    bm.normal_update()
    flip = [f for f in bm.faces if f.normal.dot(f.calc_center_median()) < 0]
    if flip:
        bmesh.ops.reverse_faces(bm, faces=flip)
    return bm


def box(cx, cy, cz, sx, sy, sz):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(cx, cy, cz), verts=bm.verts)
    return bm


def cylinder(radius, length, segments=12, axis="X", center=(0, 0, 0), radius2=None):
    r2 = radius if radius2 is None else radius2
    bm = lathe([(0, -length / 2), (radius, -length / 2), (r2, length / 2), (0, length / 2)], segments, axis=axis)
    bmesh.ops.translate(bm, vec=center, verts=bm.verts)
    return bm


def transform(bm, matrix):
    bmesh.ops.transform(bm, matrix=matrix, verts=bm.verts)
    return bm


def move(bm, x=0.0, y=0.0, z=0.0):
    bmesh.ops.translate(bm, vec=(x, y, z), verts=bm.verts)
    return bm


def rotate(bm, angle, axis="Z", origin=(0, 0, 0)):
    o = Vector(origin)
    m = Matrix.Translation(o) @ Matrix.Rotation(angle, 4, axis) @ Matrix.Translation(-o)
    return transform(bm, m)


def merge(*bms):
    """Merge several bmeshes into the first one (the others are freed)."""
    out = bms[0]
    for other in bms[1:]:
        mesh = bpy.data.meshes.new("_tmp")
        other.to_mesh(mesh)
        other.free()
        out.from_mesh(mesh)
        bpy.data.meshes.remove(mesh)
    return out


def chamfer(bm, width, angle_deg=35.0, segments=1):
    """Bevel edges sharper than angle_deg: soft highlights instead of aliased razor edges."""
    bm.normal_update()
    edges = [e for e in bm.edges if e.is_manifold and len(e.link_faces) == 2
             and e.calc_face_angle(0.0) > math.radians(angle_deg)]
    if edges:
        bmesh.ops.bevel(bm, geom=edges, offset=width, segments=segments, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
    return bm


def inset_panel(bm, face_select, thickness, depth):
    """Inset matching faces and push them in/out (hatches, plates)."""
    faces = [f for f in bm.faces if face_select(f)]
    if faces:
        res = bmesh.ops.inset_individual(bm, faces=faces, thickness=thickness, depth=depth)
    return bm


def convex_hull_2d(points):
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def resample_loop(points, spacing):
    """Resample a closed 2D polyline at even arc-length spacing; returns points and arc positions."""
    segs = []
    total = 0.0
    n = len(points)
    for i in range(n):
        a, b = Vector(points[i]), Vector(points[(i + 1) % n])
        length = (b - a).length
        segs.append((a, b, total, length))
        total += length
    count = max(8, round(total / spacing))
    step = total / count
    out, arcs = [], []
    k = 0
    for i in range(count):
        s = i * step
        while k < len(segs) - 1 and segs[k][2] + segs[k][3] < s:
            k += 1
        a, b, s0, length = segs[k]
        t = 0.0 if length == 0 else (s - s0) / length
        p = a.lerp(b, min(max(t, 0.0), 1.0))
        out.append((p.x, p.y))
        arcs.append(s)
    return out, arcs, total


def smooth_shade(obj, angle_deg=40.0):
    mesh = obj.data
    for p in mesh.polygons:
        p.use_smooth = True
    # sharp edges above the angle keep crisp silhouettes; chamfers between them read smooth
    bm = bmesh.new()
    bm.from_mesh(mesh)
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > math.radians(angle_deg):
            e.smooth = False
    bm.to_mesh(mesh)
    bm.free()
    mod = obj.modifiers.new("wn", "WEIGHTED_NORMAL")
    mod.keep_sharp = True
    mod.mode = "FACE_AREA"
