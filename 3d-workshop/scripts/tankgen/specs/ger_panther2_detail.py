"""Bake-only detail for the Panther II (prototype and Schmalturm): the shared Panther detail (ger_panther_g_detail)
read from the spec, which places the wheel bolts for the overlapped steel wheels."""

from . import ger_panther_g_detail as gd


def build(v, S):
    gd.build(v, S)
