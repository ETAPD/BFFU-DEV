"""Bake-only detail for the Panther D: the shared Panther detail (ger_panther_g_detail) read from this spec."""

from . import ger_panther_g_detail as gd


def build(v, S):
    gd.build(v, S)
