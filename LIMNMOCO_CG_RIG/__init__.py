print("")
print("===================================================")
print("LIMNMOCO CG RIG v0.2.2 — REFERENCE SOLVER BUILD")
print("===================================================")
print("")

bl_info = {
    "name": "LIMNMOCO CG Rig",
    "author": "LIMNMEDIA / Christopher Weinberg",
    "version": (0, 2, 2),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > LIMNMOCO",
    "description": "Reference solver build for the LIMNMOCO Swing-Boom-Track crane CG rig.",
    "category": "3D View",
    "doc_url": "https://limnmedia.com",
    "tracker_url": "https://github.com/",
}

import bpy
from bpy.props import PointerProperty

from .ui.properties import LIMNMOCOProperties
from .ui.operators import LIMNMOCO_OT_UpdateRig, LIMNMOCO_OT_RebuildRig, LIMNMOCO_OT_SendToZero
from .ui.panel import LIMNMOCO_PT_MainPanel

classes = (
    LIMNMOCOProperties,
    LIMNMOCO_OT_UpdateRig,
    LIMNMOCO_OT_SendToZero,
    LIMNMOCO_OT_RebuildRig,
    LIMNMOCO_PT_MainPanel,
)

def register():
    print("[REGISTER] LIMNMOCO CG Rig v0.2.2")
    print("[REGISTER] Starting")

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