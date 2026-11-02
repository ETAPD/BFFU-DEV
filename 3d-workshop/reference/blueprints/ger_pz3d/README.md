# ger_pz3d — traced from a non-free drawing

Sources: hull, running gear, turret and gun as ger_pz3c (the-blueprints.com C side view, https://www.the-blueprints.com/blueprints/tanks/ww2-tanks-germany-1/35144/view/pzkpfw_iii_ausf_c/); the D cupola from the-blueprints.com turret comparison (https://www.the-blueprints.com/blueprints/tanks/ww2-tanks-germany-1/35141/view/pzkpfw_iii_/). The overlay here is on the C side view.

That drawing is commercial, so it is used only as private tracing reference (agreed with the project owner) and is
not in the repository: the crops, calibration and the drawing overlays live in the git-ignored
`reference/blueprints_nonfree/ger_pz3d/`. To check the model, download the drawing again, crop and resample it as the
spec docstring says, and run overlay_render.py on it. `outline_{side,top,front,rear}.png` here are the model's own
line renders at 175 px/m in those views (no drawing).
