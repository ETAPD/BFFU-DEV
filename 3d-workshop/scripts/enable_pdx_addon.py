# Run: blender -b --python enable_pdx_addon.py
# Enables the io_pdx_mesh add-on and saves it into Blender's user preferences.
import addon_utils
import bpy

addon_utils.enable("io_pdx_mesh", default_set=True, persistent=True)
print("io_pdx_mesh loaded/enabled:", addon_utils.check("io_pdx_mesh"))
print("pdx operators:", dir(bpy.ops.io_pdx_mesh))
bpy.ops.wm.save_userpref()
