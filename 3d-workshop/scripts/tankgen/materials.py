"""Bake materials: per material kind, one node graph per bake pass.

Passes:
  "normal" - Principled BSDF with procedural bump (Zimmerit, cast texture, dents) -> NORMAL bake
  "color"  - Emission of the final albedo (camo, AO, edge wear, dust, markings)   -> EMIT bake
  "spec"   - Emission of (0, specular, metalness), HOI4 spec R/G/B               -> EMIT bake
  "gloss"  - Emission of glossiness, packed into spec alpha                       -> EMIT bake
Coordinates come from object space of the joined body, in game units (metres * scale).
"""

import bpy

# colours (linear) - RAL 7028 Dunkelgelb, RAL 6003 Olivgrün, RAL 8017 Rotbraun, RAL 7021 Dunkelgrau
DUNKELGELB = (0.50, 0.40, 0.21)
OLIVGRUN = (0.105, 0.125, 0.065)
ROTBRAUN = (0.12, 0.055, 0.035)
PRIMER = (0.20, 0.07, 0.04)  # red oxide primer under chips
DUST = (0.42, 0.36, 0.26)
MUD = (0.16, 0.12, 0.08)

PAINTED = {"paint", "paint_cast", "skirt", "steel_paint", "rubber_wheel", "wheel_plain"}

# (specular, metalness, glossiness) per kind
SPEC = {
    "paint": (0.30, 0.0, 0.38),
    "paint_cast": (0.28, 0.0, 0.32),
    "skirt": (0.30, 0.0, 0.36),
    "steel_paint": (0.32, 0.0, 0.42),
    "wheel_plain": (0.30, 0.0, 0.36),
    "rubber_wheel": (0.30, 0.0, 0.36),
    "rubber": (0.18, 0.0, 0.22),
    "steel": (0.50, 0.75, 0.45),
    "track_steel": (0.45, 0.60, 0.35),
    "track": (0.45, 0.60, 0.35),
    "wood": (0.15, 0.0, 0.22),
    "glass": (0.60, 0.0, 0.80),
    "exhaust": (0.20, 0.35, 0.20),
}

BASE = {
    "rubber": (0.025, 0.025, 0.024),
    "steel": (0.10, 0.095, 0.09),
    "track_steel": (0.08, 0.06, 0.05),
    "track": (0.08, 0.06, 0.05),
    "wood": (0.25, 0.14, 0.06),
    "glass": (0.02, 0.03, 0.035),
    "exhaust": (0.10, 0.04, 0.02),
}


class Graph:
    def __init__(self, mat):
        mat.use_nodes = True
        self.nt = mat.node_tree
        self.nt.nodes.clear()
        self.x = 0

    def n(self, kind, **props):
        node = self.nt.nodes.new(kind)
        node.location = (self.x, 0)
        self.x += 180
        for k, v in props.items():
            if k.startswith("in_"):
                key = k[3:]
                key = int(key) if key.isdigit() else key.replace("_", " ")
                node.inputs[key].default_value = v
            else:
                setattr(node, k, v)
        return node

    def link(self, a, b, out=0, inp=0):
        self.nt.links.new(a.outputs[out] if not hasattr(a, "is_output") else a, b.inputs[inp])

    def math(self, op, a, b=None, clamp=False):
        node = self.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        self._in(node, 0, a)
        if b is not None:
            self._in(node, 1, b)
        return node

    def mix(self, fac, a, b):
        node = self.n("ShaderNodeMix", data_type="RGBA", blend_type="MIX")
        self._in(node, "Factor", fac)
        self._in(node, 6, a)
        self._in(node, 7, b)
        return node

    def _in(self, node, idx, val):
        if isinstance(val, bpy.types.Node):
            # Mix/Map nodes expose several typed outputs; take the one matching the target socket
            target = node.inputs[idx]
            outs = [o for o in val.outputs if o.enabled]
            match = next((o for o in outs if o.type == target.type), outs[0])
            self.nt.links.new(match, target)
        elif isinstance(val, bpy.types.NodeSocket):
            self.nt.links.new(val, node.inputs[idx])
        else:
            sock = node.inputs[idx]
            if sock.type == "RGBA" and not isinstance(val, (tuple, list)):
                val = (val, val, val, 1.0)
            elif sock.type == "RGBA" and len(val) == 3:
                val = (*val, 1.0)
            sock.default_value = val

    # common inputs ------------------------------------------------------------------------------------------
    def obj_coords(self):
        tc = self.n("ShaderNodeTexCoord")
        return tc.outputs["Object"]

    def xyz(self, co):
        sep = self.n("ShaderNodeSeparateXYZ")
        self.nt.links.new(co, sep.inputs[0])
        return sep

    def noise(self, co, scale, detail=3.0, rough=0.55, dist=0.0):
        node = self.n("ShaderNodeTexNoise", noise_dimensions="3D", in_Scale=scale, in_Detail=detail,
                      in_Roughness=rough, in_Distortion=dist)
        self.nt.links.new(co, node.inputs["Vector"])
        return node

    def ramp(self, src, a, b):
        """Smooth 0..1 between a and b."""
        node = self.n("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP", in_1=a, in_2=b, in_3=0.0, in_4=1.0)
        self._in(node, 0, src)
        return node


def _true_normal_z(g):
    geo = g.n("ShaderNodeNewGeometry")
    sep = g.n("ShaderNodeSeparateXYZ")
    g.nt.links.new(geo.outputs["True Normal"], sep.inputs[0])
    return sep


def _edge_mask(g):
    """Convex edge mask from the Bevel node (works in Cycles bakes)."""
    bev = g.n("ShaderNodeBevel", samples=8, in_Radius=0.02)
    geo = g.n("ShaderNodeNewGeometry")
    dot = g.n("ShaderNodeVectorMath", operation="DOT_PRODUCT")
    g.nt.links.new(bev.outputs[0], dot.inputs[0])
    g.nt.links.new(geo.outputs["True Normal"], dot.inputs[1])
    inv = g.math("SUBTRACT", 1.0, dot.outputs["Value"])
    return g.ramp(inv, 0.02, 0.18)


def _balkenkreuz(g, co, centres, size):
    """Black cross with white outline on the vehicle sides. centres: [(sign_x, y, z)]. Returns (black, white)."""
    sep = g.xyz(co)
    black_total = None
    white_total = None
    for sx, cy, cz in centres:
        dy = g.math("ABSOLUTE", g.math("SUBTRACT", sep.outputs["Y"], cy))
        dz = g.math("ABSOLUTE", g.math("SUBTRACT", sep.outputs["Z"], cz))
        nx = g.xyz(g.n("ShaderNodeNewGeometry").outputs["True Normal"])
        facing = g.math("GREATER_THAN", g.math("MULTIPLY", nx.outputs["X"], sx), 0.8)
        side = g.math("MULTIPLY", g.math("GREATER_THAN", g.math("MULTIPLY", sep.outputs["X"], sx), 0.3), facing)
        arm, half = size * 0.11, size * 0.5
        border = size * 0.055

        def cross(a, h):
            bar1 = g.math("MULTIPLY", g.math("LESS_THAN", dy, h), g.math("LESS_THAN", dz, a))
            bar2 = g.math("MULTIPLY", g.math("LESS_THAN", dy, a), g.math("LESS_THAN", dz, h))
            return g.math("MAXIMUM", bar1, bar2)

        black = g.math("MULTIPLY", cross(arm, half), side)
        white = g.math("MULTIPLY", cross(arm + border, half + border), side)
        black_total = black if black_total is None else g.math("MAXIMUM", black_total, black)
        white_total = white if white_total is None else g.math("MAXIMUM", white_total, white)
    return black_total, white_total


def build(mat, kind, mode, ctx):
    """ctx: dict with 'scale' (game units per metre), 'crosses' [(sx, y, z)], 'cross_size'."""
    g = Graph(mat)
    out = g.n("ShaderNodeOutputMaterial")
    s = ctx["scale"]
    co = g.obj_coords()

    if mode == "normal":
        bsdf = g.n("ShaderNodeBsdfPrincipled")
        g.nt.links.new(bsdf.outputs[0], out.inputs["Surface"])
        height = None
        if kind in ("paint",):
            # Zimmerit: ribbed anti-magnetic paste on vertical hull/turret armour, ~5 cm ribs in 15 cm bands
            nz = _true_normal_z(g)
            vertical = g.ramp(g.math("ABSOLUTE", nz.outputs["Z"]), 0.55, 0.25)
            wave = g.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="Z", wave_profile="SIN",
                       in_Scale=3.2 / s, in_Distortion=1.5, in_Detail=1.0)
            g.nt.links.new(co, wave.inputs["Vector"])
            ribs = g.math("MULTIPLY", wave.outputs["Fac"], vertical)
            height = ribs
        elif kind in ("paint_cast",):
            height = g.noise(co, 9.0 / s, 4.0, 0.6).outputs["Fac"]
        elif kind in ("skirt",):
            height = g.noise(co, 1.2 / s, 2.0, 0.5).outputs["Fac"]
        elif kind in ("track_steel", "exhaust"):
            height = g.noise(co, 14.0 / s, 4.0, 0.7).outputs["Fac"]
        if height is not None:
            strength = {"paint": 0.35, "paint_cast": 0.25, "skirt": 0.35, "track_steel": 0.3, "exhaust": 0.3}[kind]
            bump = g.n("ShaderNodeBump", in_Strength=strength, in_Distance=0.01)
            g._in(bump, "Height", height)
            g.nt.links.new(bump.outputs[0], bsdf.inputs["Normal"])
        return

    emit = g.n("ShaderNodeEmission", in_Strength=1.0)
    g.nt.links.new(emit.outputs[0], out.inputs["Surface"])
    sep = g.xyz(co)
    nz = _true_normal_z(g)
    edge = _edge_mask(g)
    chip_noise = g.noise(co, 6.0 / s, 4.0, 0.7)
    chips = g.math("MULTIPLY", edge, g.ramp(chip_noise.outputs["Fac"], 0.52, 0.62))
    height_m = g.math("DIVIDE", sep.outputs["Z"], s)
    low = g.ramp(height_m, 1.25, 0.3)  # dust and mud on the lower hull and running gear
    dirt_noise = g.noise(co, 2.5 / s, 5.0, 0.65)
    up = g.ramp(nz.outputs["Z"], 0.55, 0.9)  # dust settles on horizontal faces

    # occlusion traced live on the high-poly source: broad shadow between parts, plus tight crevice shadow
    # round every bolt, hinge and plate joint (this is most of what makes a texture read as detailed)
    ao_big = g.n("ShaderNodeAmbientOcclusion", samples=16, in_Distance=0.9 * s)
    ao_small = g.n("ShaderNodeAmbientOcclusion", samples=16, in_Distance=0.06 * s)
    big = g.math("POWER", ao_big.outputs["AO"], 1.6)
    crevice = g.math("POWER", ao_small.outputs["AO"], 2.0)
    ao = g.math("MULTIPLY", g.math("ADD", g.math("MULTIPLY", big, 0.85), 0.15),
                g.math("ADD", g.math("MULTIPLY", crevice, 0.65), 0.35))
    grime = g.math("SUBTRACT", 1.0, crevice)  # where dirt and old oil collect: round bolts, in seams

    if mode in ("spec", "gloss"):
        sp, mt, gl = SPEC.get(kind, (0.3, 0.0, 0.35))
        if kind in PAINTED:
            dust = g.math("MAXIMUM", g.math("MULTIPLY", low, 0.8), g.math("MULTIPLY", up, 0.35))
            metal = g.math("MULTIPLY", chips, 0.65)
            gloss = g.math("ADD", g.math("MULTIPLY", g.math("SUBTRACT", 1.0, dust), gl - 0.12), 0.12)
            gloss = g.math("ADD", gloss, g.math("MULTIPLY", chips, 0.15))
            spec = g.math("ADD", sp, g.math("MULTIPLY", chips, 0.2))
        else:
            metal, gloss, spec = mt, gl, sp
            if kind in ("track", "track_steel", "steel"):
                gloss = g.math("ADD", gl, g.math("MULTIPLY", edge, 0.25))
        if mode == "gloss":
            g._in(emit, "Color", gloss)
            return
        comb = g.n("ShaderNodeCombineXYZ")
        g._in(comb, 0, 0.0)
        g._in(comb, 1, spec)
        g._in(comb, 2, metal)
        g.nt.links.new(comb.outputs[0], emit.inputs["Color"])
        return

    # ---- colour ---------------------------------------------------------------------------------------------
    if kind in PAINTED:
        camo_on = kind not in ("wheel_plain",)
        col = DUNKELGELB
        base = g.n("ShaderNodeRGB")
        base.outputs[0].default_value = (*col, 1.0)
        tint = g.noise(co, 0.8 / s, 2.0, 0.5)
        paint = g.mix(g.math("MULTIPLY", g.math("SUBTRACT", tint.outputs["Fac"], 0.5), 0.35), base, (0.42, 0.32, 0.16))
        if camo_on:
            # hand-sprayed Olivgrün and Rotbraun bands with soft over-spray edges
            # ~1 m wide sprayed bands; noise Fac clusters around 0.5, so thresholds sit just off-centre
            band1 = g.noise(co, 0.85 / s, 2.0, 0.5, dist=0.8)
            band2 = g.noise(co, 1.05 / s, 2.0, 0.5, dist=1.1)
            m1 = g.ramp(band1.outputs["Fac"], 0.565, 0.59)
            m2 = g.ramp(band2.outputs["Fac"], 0.425, 0.40)
            paint = g.mix(m1, paint, OLIVGRUN)
            paint = g.mix(m2, paint, ROTBRAUN)
        if ctx.get("crosses") and kind == "skirt":
            black, white = _balkenkreuz(g, co, ctx["crosses"], ctx["cross_size"])
            paint = g.mix(white, paint, (0.62, 0.60, 0.55))
            paint = g.mix(black, paint, (0.015, 0.015, 0.015))
        # weathering: chipped edges to primer/steel, streaks, dust, mud
        paint = g.mix(g.math("MULTIPLY", chips, 0.9), paint, PRIMER)
        paint = g.mix(g.math("MULTIPLY", edge, 0.6), paint, (0.72, 0.64, 0.50))
        dust_amt = g.math("MAXIMUM", g.math("MULTIPLY", up, 0.45),
                          g.math("MULTIPLY", low, g.math("ADD", 0.55, g.math("MULTIPLY", dirt_noise.outputs["Fac"], 0.8))),
                          clamp=True)
        paint = g.mix(dust_amt, paint, DUST)
        # rain streaks: vertical faces only, noise stretched down the plate
        streak_co = g.n("ShaderNodeMapping", in_Scale=(9.0, 9.0, 0.7))
        g.nt.links.new(co, streak_co.inputs["Vector"])
        streaks = g.noise(streak_co.outputs[0], 1.6 / s, 3.0, 0.6)
        vertical = g.ramp(g.math("ABSOLUTE", nz.outputs["Z"]), 0.4, 0.15)
        paint = g.mix(g.math("MULTIPLY", g.ramp(streaks.outputs["Fac"], 0.55, 0.75), g.math("MULTIPLY", vertical, 0.35)),
                      paint, (0.18, 0.15, 0.10))
        paint = g.mix(g.math("MULTIPLY", grime, 0.9), paint, (0.07, 0.06, 0.04))
        # uneven fading and touch-ups over large areas, so no plate is one flat colour
        fade = g.noise(co, 0.6 / s, 4.0, 0.6)
        tone = g.n("ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
        g._in(tone, "Factor", g.math("MULTIPLY", g.ramp(fade.outputs["Fac"], 0.35, 0.7), 0.45))
        g._in(tone, 6, paint)
        g._in(tone, 7, (0.72, 0.68, 0.6))
        paint = tone
        if kind == "skirt":
            # thin 5 mm plates take a beating: scratches through to bare/rusty steel
            sc_co = g.n("ShaderNodeMapping", in_Scale=(1.0, 14.0, 1.0))
            g.nt.links.new(co, sc_co.inputs["Vector"])
            scratches = g.ramp(g.noise(sc_co.outputs[0], 3.0 / s, 2.0, 0.5).outputs["Fac"], 0.66, 0.70)
            paint = g.mix(g.math("MULTIPLY", scratches, 0.7), paint, (0.16, 0.08, 0.04))
        mud = g.math("MULTIPLY", g.ramp(height_m, 0.55, 0.15), g.ramp(dirt_noise.outputs["Fac"], 0.42, 0.58))
        paint = g.mix(mud, paint, MUD)
        final = paint
    else:
        base = g.n("ShaderNodeRGB")
        base.outputs[0].default_value = (*BASE.get(kind, (0.1, 0.1, 0.1)), 1.0)
        final = base
        if kind in ("steel", "track_steel", "track"):
            rust = g.ramp(dirt_noise.outputs["Fac"], 0.45, 0.65)
            final = g.mix(g.math("MULTIPLY", rust, 0.6), final, (0.16, 0.07, 0.03))
            final = g.mix(g.math("MULTIPLY", edge, 0.5), final, (0.30, 0.29, 0.27))
        if kind == "exhaust":
            soot = g.ramp(dirt_noise.outputs["Fac"], 0.35, 0.65)
            final = g.mix(soot, (0.18, 0.07, 0.03), (0.03, 0.025, 0.02))
        if kind == "rubber":
            final = g.mix(g.math("MULTIPLY", low, 0.5), final, DUST)
    shaded = g.n("ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
    g._in(shaded, "Factor", 1.0)
    g._in(shaded, 6, final)
    g._in(shaded, 7, ao)
    g.nt.links.new(shaded.outputs[2], emit.inputs["Color"])
