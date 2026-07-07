print("")
print("===================================================")
print("LIMNMOCO CG RIG v0.3.2 BETA - ARCHITECTURE PASS")
print("===================================================")
print("")

bl_info = {
    "name": "LIMNMOCO CG Rig Beta",
    "author": "LIMNMEDIA / Christopher Weinberg",
    "version": (0, 3, 2),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > LIMNMOCO",
    "description": "Beta reference solver and previz tool for the LIMNMOCO Swing-Boom-Track crane CG rig.",
    "category": "3D View",
    "doc_url": "https://limnmedia.com",
    "tracker_url": "https://github.com/",
}

import bpy
import sys
from pathlib import Path
from bpy.props import PointerProperty

if not __package__:
    _addon_dir = Path(__file__).resolve().parent
    _addon_parent = str(_addon_dir.parent)

    if _addon_parent not in sys.path:
        sys.path.insert(0, _addon_parent)

    __package__ = "LIMNMOCO_CG_RIG"
    __path__ = [str(_addon_dir)]
    sys.modules.setdefault(__package__, sys.modules[__name__])

from .ui.properties import LIMNMOCOProperties
from .ui.operators import (
    LIMNMOCO_OT_UpdateRig,
    LIMNMOCO_OT_ToggleLiveUpdate,
    LIMNMOCO_OT_RebuildRig,
    LIMNMOCO_OT_SendToZero,
)
from .ui.panel import (
    LIMNMOCO_PT_MainPanel,
    LIMNMOCO_PT_ViewPanel,
    LIMNMOCO_PT_SolverPanel,
    LIMNMOCO_PT_CranePanel,
    LIMNMOCO_PT_PrevizPanel,
)

classes = (
    LIMNMOCOProperties,
    LIMNMOCO_OT_UpdateRig,
    LIMNMOCO_OT_ToggleLiveUpdate,
    LIMNMOCO_OT_SendToZero,
    LIMNMOCO_OT_RebuildRig,
    LIMNMOCO_PT_MainPanel,
    LIMNMOCO_PT_ViewPanel,
    LIMNMOCO_PT_SolverPanel,
    LIMNMOCO_PT_CranePanel,
    LIMNMOCO_PT_PrevizPanel,
)


def register():
    print("[REGISTER] LIMNMOCO CG Rig v0.3.2 Beta")
    print("[REGISTER] Starting")
    from .debug.install_check import print_install_check

    print_install_check(__name__, __file__, bl_info, bpy)

    for cls in classes:
        print("[REGISTER] Registering:", cls.__name__)
        bpy.utils.register_class(cls)

    bpy.types.Object.limnmoco = PointerProperty(
        type=LIMNMOCOProperties
    )

    print("[REGISTER] Complete")


def unregister():
    print("[UNREGISTER] Starting")

    if hasattr(bpy.types.Object, "limnmoco"):
        del bpy.types.Object.limnmoco

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as exc:
            print("[UNREGISTER] Warning:", exc)

    print("[UNREGISTER] Complete")
