import bpy
from ..debug.log import scene

print("[SCENE] Loaded")

COLLECTION_NAME = "LIMNMOCO_CG_RIG"

def get_collection():
    print("[SCENE] get_collection()")
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        scene("Creating collection:", COLLECTION_NAME)
        col = bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(col)
    return col

def clear_generated(col):
    keep = {"LIMN_CONTROL", "LIMN_CAMERA"}
    for obj in list(col.objects):
        if obj.name not in keep:
            bpy.data.objects.remove(obj, do_unlink=True)

def reset_collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        return
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
