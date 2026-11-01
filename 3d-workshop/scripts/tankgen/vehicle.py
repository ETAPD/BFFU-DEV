"""Collects parts with their material kind and bone, then turns them into a rigged, PDX-ready model."""

import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import geo

# preview colours per material kind (the real look comes from the bake)
KIND_COLORS = {
    "paint": (0.60, 0.52, 0.34, 1),
    "paint_cast": (0.58, 0.50, 0.33, 1),
    "skirt": (0.60, 0.52, 0.34, 1),
    "rubber": (0.05, 0.05, 0.05, 1),
    "rubber_wheel": (0.30, 0.28, 0.22, 1),
    "wheel_plain": (0.30, 0.28, 0.22, 1),
    "steel_paint": (0.55, 0.48, 0.32, 1),
    "track_steel": (0.28, 0.25, 0.22, 1),
    "steel": (0.35, 0.33, 0.30, 1),
    "track": (0.25, 0.22, 0.20, 1),
    "wood": (0.45, 0.30, 0.15, 1),
    "glass": (0.05, 0.08, 0.10, 1),
    "exhaust": (0.30, 0.18, 0.10, 1),
}


class Part:
    def __init__(self, name, obj, kind, bone):
        self.name, self.obj, self.kind, self.bone = name, obj, kind, bone


class Vehicle:
    def __init__(self, name):
        self.name = name
        self.parts = []
        self.details = []  # high-poly only: baked into the textures, never exported
        self.bones = {}  # name -> (head xyz, parent)
        self.locators = {}  # name -> (xyz, bone)
        self.collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(self.collection)

    # ---- building -------------------------------------------------------------------------------------------
    def add(self, name, bm, kind="paint", bone="chassie", chamfer=None, smooth_angle=40.0):
        if chamfer:
            geo.chamfer(bm, chamfer)
        obj = geo.new_object(name, bm, collection=self.collection)
        obj["kind"] = kind
        obj["bone"] = bone
        obj["smooth_angle"] = smooth_angle
        self.parts.append(Part(name, obj, kind, bone))
        return obj

    def detail(self, name, bm, kind="paint"):
        """Bake-only geometry (bolts, rivets, hinges, grille slats, weld beads)."""
        if not bm.verts:
            bm.free()
            return None
        obj = geo.new_object(name, bm, collection=self.collection)
        obj["kind"] = kind
        obj.hide_render = False
        self.details.append((obj, kind))
        return obj

    def mirror_x(self, name, bm_factory, kind="paint", bone="chassie", chamfer=None, x=0.0, **kw):
        """Add a part on the left (+X) and its mirror image on the right (-X)."""
        for side, suffix in ((1, "_l"), (-1, "_r")):
            bm = bm_factory()
            if side < 0:
                geo.transform(bm, Matrix.Scale(-1, 4, (1, 0, 0)))
                bmesh.ops.reverse_faces(bm, faces=bm.faces)
            self.add(name + suffix, bm, kind, bone, chamfer, **kw)

    def bone(self, name, head, parent=None):
        self.bones[name] = (Vector(head), parent)

    def locator(self, name, xyz, bone):
        self.locators[name] = (Vector(xyz), bone)

    # ---- finishing ------------------------------------------------------------------------------------------
    def preview_materials(self):
        mats = {}
        for p in self.parts:
            if p.kind not in mats:
                m = bpy.data.materials.new("prev_" + p.kind)
                m.diffuse_color = KIND_COLORS.get(p.kind, (1, 0, 1, 1))
                mats[p.kind] = m
            p.obj.data.materials.clear()
            p.obj.data.materials.append(mats[p.kind])

    def triangle_count(self):
        return sum(sum(len(poly.vertices) - 2 for poly in p.obj.data.polygons) for p in self.parts)

    def shade(self):
        for p in self.parts:
            geo.smooth_shade(p.obj, p.obj.get("smooth_angle", 40.0))

    def scale_all(self, s):
        m = Matrix.Scale(s, 4)
        for p in self.parts:
            p.obj.data.transform(m)
        for obj, _ in self.details:
            obj.data.transform(m)
        self.bones = {k: (h * s, par) for k, (h, par) in self.bones.items()}
        self.locators = {k: (xyz * s, b) for k, (xyz, b) in self.locators.items()}
