# ger_panther_a — traced from non-free drawings

Sources: the-blueprints.com, "Sd.Kfz. 171 Pz.Kpfw.V Ausf.A Panther" sheets by Dr Dan Saranga, public 500 px previews:
- ID 72501 (two sides, front, rear; late A with Kugelblende and Schürzen):
  https://www.the-blueprints.com/blueprints/tanks/ww2-tanks-germany-2/72501/view/sdkfz_171_pzkpfwv_ausfa_panther/
- ID 72503 (four-view; top view used only):
  https://www.the-blueprints.com/blueprints/tanks/ww2-tanks-germany-2/72503/view/sdkfz_171_pzkpfwv_ausfa_panther/

No free-licence four-view of any Panther exists (see VARIANTS.md), so with the project owner's agreement these
commercial drawings are used only as private tracing reference, as for the Panzer III. The sheets, crops,
calibration grids and drawing overlays live in the git-ignored `reference/blueprints_nonfree/ger_panther_a/`. To
check the model, download the previews again, crop and resample them as the spec docstring says (each view
calibrated on its own against the documented 6.87 m / 8.66 m / 3.27 m / 2.99 m) and run overlay_render.py on them.

`outline_{side,top,front,rear}.png` here are the model's own line renders at 175 px/m in those views (no drawing).
`photos/` holds the free-licence museum and wartime photos checked (credits in `photos/CREDITS.md`).
