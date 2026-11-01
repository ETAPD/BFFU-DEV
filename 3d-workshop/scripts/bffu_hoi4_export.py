"""BFFU - export HOI4 unit textures (File > Export HOI4 textures (BFFU)...).

Writes one set of DDS files per texture set, packed the way HOI4's PdxMeshAdvanced shader reads them
(gfx/FX/pdxmesh.shader, PDX_IMPROVED_BLINN_PHONG path):

  <set>_diffuse.dds  BC1/DXT1  RGB = base colour
  <set>_normal.dds   BC3/DXT5  R = normal X (copy), G = normal X, B = glow mask (black unless EXPORT_EMISSIVE), A = normal Y
  <set>_spec.dds     BC3/DXT5  R = unused, G = specular level, B = metalness, A = glossiness

Painter exports PNGs into a temp folder, then texconv converts them to DDS with full mip chains.
"""

import os
import subprocess
import tempfile

import substance_painter.export
import substance_painter.logging
import substance_painter.project
import substance_painter.textureset
import substance_painter.ui
from PySide6 import QtCore, QtGui, QtWidgets

TEXCONV = r"C:\Users\Roberts (ME)\Documents\GitHub\BFFU-DEV\3d-workshop\bin\texconv.exe"
DEFAULT_OUT = r"C:\Users\Roberts (ME)\Documents\GitHub\BFFU-DEV\gfx\models\units\tanks"

# HOI4 wants OpenGL (green up): the shader builds B = cross(N, T) * w in a space the exporter mirrored from
# Blender's, which flips B to image-down, and then negates the sampled Y again (UnpackRRxGNormal)
NORMAL_MAP = "Normal_OpenGL"

# Normal-map blue is HOI4's glow mask. Off by default: Painter 12's OpenPBR shader defaults emission colour
# to white (brightness 0), so reading it would make the whole unit glow. Only enable for projects that paint
# black everywhere except lights.
EXPORT_EMISSIVE = False

PLUGIN_ACTIONS = []


def log(msg):
    substance_painter.logging.info("[BFFU HOI4] " + msg)


def channel(dest, src_type, src_name, src_channel="R"):
    return {"destChannel": dest, "srcChannel": src_channel, "srcMapType": src_type, "srcMapName": src_name}


def hoi4_preset():
    png = {"fileFormat": "png", "bitDepth": "8", "dithering": False, "paddingAlgorithm": "infinite"}
    return {
        "name": "BFFU_HOI4",
        "maps": [
            {
                "fileName": "$textureSet_diffuse",
                "channels": [channel(c, "documentMap", "baseColor", c) for c in "RGB"],
                "parameters": png,
            },
            {
                "fileName": "$textureSet_normal",
                "channels": [
                    channel("R", "virtualMap", NORMAL_MAP, "R"),
                    channel("G", "virtualMap", NORMAL_MAP, "R"),
                    channel("B", "documentMap", "emissive", "R")
                    if EXPORT_EMISSIVE
                    else channel("B", "defaultMap", "black"),
                    channel("A", "virtualMap", NORMAL_MAP, "G"),
                ],
                "parameters": png,
            },
            {
                "fileName": "$textureSet_spec",
                "channels": [
                    channel("R", "defaultMap", "black"),
                    channel("G", "documentMap", "specularlevel"),
                    channel("B", "documentMap", "metallic"),
                    channel("A", "virtualMap", "Glossiness"),
                ],
                "parameters": png,
            },
        ],
    }


def ensure_channels():
    """The preset reads Specular Level, so add it (0.5 default, close to vanilla tanks) where missing."""
    CT = substance_painter.textureset.ChannelType
    CF = substance_painter.textureset.ChannelFormat
    for ts in substance_painter.textureset.all_texture_sets():
        stack = ts.get_stack()
        if not stack.has_channel(CT.Specularlevel):
            stack.add_channel(CT.Specularlevel, CF.L8)
            log(f"added Specular Level channel to {ts.name()}")


def to_dds(png_path, out_dir):
    fmt = "BC1_UNORM" if png_path.endswith("_diffuse.png") else "BC3_UNORM"
    # --ignore-srgb: Painter tags PNGs as sRGB and texconv would otherwise linearise them, HOI4 wants raw values
    cmd = [TEXCONV, "-nologo", "-y", "-m", "0", "--ignore-srgb", "-f", fmt, "-o", out_dir, png_path]
    result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode != 0:
        raise RuntimeError(f"texconv failed on {png_path}:\n{result.stdout}\n{result.stderr}")
    return os.path.join(out_dir, os.path.splitext(os.path.basename(png_path))[0] + ".dds")


def export_textures(out_dir):
    """Export every texture set of the open project as HOI4 DDS files into out_dir, returns the written paths."""
    if not os.path.isfile(TEXCONV):
        raise RuntimeError(f"texconv not found: {TEXCONV}")
    os.makedirs(out_dir, exist_ok=True)

    ensure_channels()
    tmp = tempfile.mkdtemp(prefix="bffu_hoi4_")
    config = {
        "exportShaderParams": False,
        "exportPath": tmp,
        "defaultExportPreset": "BFFU_HOI4",
        "exportPresets": [hoi4_preset()],
        "exportList": [{"rootPath": ts.name()} for ts in substance_painter.textureset.all_texture_sets()],
        "exportParameters": [{"parameters": {"paddingAlgorithm": "infinite"}}],
    }
    result = substance_painter.export.export_project_textures(config)
    if result.status != substance_painter.export.ExportStatus.Success:
        raise RuntimeError(f"Painter export failed: {result.message}")

    written = []
    for pngs in result.textures.values():
        for png in pngs:
            written.append(to_dds(png, out_dir))
    for path in written:
        log("wrote " + path)
    return written


def export_hoi4():
    if not substance_painter.project.is_open():
        QtWidgets.QMessageBox.warning(None, "BFFU HOI4", "Open a project first.")
        return

    settings = QtCore.QSettings("BFFU", "hoi4_export")
    out_dir = QtWidgets.QFileDialog.getExistingDirectory(
        None, "Export HOI4 DDS textures to", settings.value("out_dir", DEFAULT_OUT)
    )
    if not out_dir:
        return
    settings.setValue("out_dir", out_dir)

    try:
        written = export_textures(out_dir)
    except RuntimeError as err:
        QtWidgets.QMessageBox.critical(None, "BFFU HOI4", str(err))
        return
    QtWidgets.QMessageBox.information(None, "BFFU HOI4", "Exported:\n" + "\n".join(written))


def start_plugin():
    action = QtGui.QAction("Export HOI4 textures (BFFU)...")
    action.triggered.connect(export_hoi4)
    substance_painter.ui.add_action(substance_painter.ui.ApplicationMenu.File, action)
    PLUGIN_ACTIONS.append(action)


def close_plugin():
    for action in PLUGIN_ACTIONS:
        substance_painter.ui.delete_ui_element(action)
    PLUGIN_ACTIONS.clear()


if __name__ == "__main__":
    start_plugin()
