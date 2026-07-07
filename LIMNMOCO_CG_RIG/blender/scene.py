import bpy
from ..debug.log import scene

print("[SCENE] Loaded")

COLLECTION_NAME = "LIMNMOCO_CG_RIG"
PERSISTENT_OBJECT_NAMES = {
    "LIMN_CONTROL",
    "LIMNMOCO_RIG_ROOT",
    "LIMN_TRACK_CTRL",
    "LIMN_SWING_CTRL",
    "LIMN_BOOM_CTRL",
    "LIMN_EXTENSION_CTRL",
    "LIMN_PAN_CTRL",
    "LIMN_TILT_CTRL",
    "LIMN_ROLL_CTRL",
    "LIMN_CAMERA",
}

def get_collection():
    print("[SCENE] get_collection()")
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        scene("Creating collection:", COLLECTION_NAME)
        col = bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(col)
    return col

def clear_generated(col):
    """
    Clear generated LIMNMOCO visualization objects.

    Keep persistent scene/control objects and rig controls.
    """

    for obj in list(col.objects):
        if obj.name in PERSISTENT_OBJECT_NAMES:
            print("[SCENE] Keeping:", obj.name)
            continue

        print("[SCENE] Removing generated:", obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)


def reset_collection():
    """
    Rebuild collection contents while preserving persistent rig objects.
    """

    col = bpy.data.collections.get(COLLECTION_NAME)

    if col is None:
        return

    clear_generated(col)
RIG_ROOT_NAME = "LIMNMOCO_RIG_ROOT"

def ensure_rig_root(col):
    print("[SCENE] ensure_rig_root()")

    root = bpy.data.objects.get(RIG_ROOT_NAME)

    if root is None:
        print("[SCENE] Creating", RIG_ROOT_NAME)
        root = bpy.data.objects.new(RIG_ROOT_NAME, None)
        root.empty_display_type = "ARROWS"
        root.empty_display_size = 2.0
        root.show_name = False
        col.objects.link(root)

    elif root.name not in col.objects:
        col.objects.link(root)

    return root


def parent_to_root(obj, root):
    if obj is None or root is None:
        return

    if obj == root:
        return

    obj.parent = root
