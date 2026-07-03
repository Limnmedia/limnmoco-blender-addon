import bpy
from mathutils import Vector

from ..core.transforms import blender_camera_rotation_from_virtual_matrix
from ..debug.log import scene
from .objects import make_line


print("[CAMERA] Loaded")


def ensure_camera(col):
    """
    Ensure the scene has one persistent LIMN_CAMERA object.

    This object is not deleted during normal rig updates.
    Generated debug lines/points are deleted and rebuilt,
    but the actual camera stays persistent.
    """

    scene("ensure_camera()")

    cam = bpy.data.objects.get("LIMN_CAMERA")

    if cam is None:
        scene("Creating LIMN_CAMERA")

        cam_data = bpy.data.cameras.new("LIMN_CAMERA_DATA")
        cam = bpy.data.objects.new("LIMN_CAMERA", cam_data)
        cam.show_name = True
        col.objects.link(cam)

    elif cam.name not in col.objects:
        scene("Linking existing LIMN_CAMERA to collection")
        col.objects.link(cam)

    bpy.context.scene.camera = cam
    return cam


def apply_camera_transform(cam, result):
    """
    Move and rotate the Blender camera from the solved rig result.

    LIMNMOCO virtual convention:
        +Y = camera forward
        +Z = camera up
        +X = camera right

    Blender camera convention:
        local -Z = camera forward
        local +Y = camera up

    The correction lives in:
        core/transforms.py
    """

    scene("apply_camera_transform()")
    scene("Camera location:", result.nodal)

    cam.location = result.nodal

    blender_rotation = blender_camera_rotation_from_virtual_matrix(
        result.rotation
    )

    cam.rotation_euler = blender_rotation.to_euler()

    scene("Camera rotation:", cam.rotation_euler)


def draw_camera_axes(result, col):
    """
    Draw simple camera orientation debug axes.

    These are viewport helpers only.
    They are regenerated on each update.

    CAM_FORWARD = virtual +Y
    CAM_UP      = virtual +Z
    CAM_RIGHT   = virtual +X
    """

    scene("draw_camera_axes()")

    nodal = result.nodal
    rotation = result.rotation

    forward = rotation @ Vector((0, 1, 0))
    up = rotation @ Vector((0, 0, 1))
    right = rotation @ Vector((1, 0, 0))

    make_line(
        "CAM_FORWARD_virtual_plus_Y",
        nodal,
        nodal + forward * 2.0,
        col,
        0.03,
    )

    make_line(
        "CAM_UP_virtual_plus_Z",
        nodal,
        nodal + up * 1.2,
        col,
        0.02,
    )

    make_line(
        "CAM_RIGHT_virtual_plus_X",
        nodal,
        nodal + right * 1.2,
        col,
        0.02,
    )