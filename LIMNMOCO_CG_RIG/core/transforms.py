import math
from mathutils import Matrix

def rotation_matrix_from_virtual_axes(vpan, vtilt, vroll):
    """
    Scoped v02 convention:
    - VPan rotates around Z.
    - VTilt rotates around X.
    - VRoll rotates around Y.
    """
    pan = math.radians(vpan)
    tilt = math.radians(vtilt)
    roll = math.radians(vroll)

    rz = Matrix.Rotation(pan, 4, "Z")
    rx = Matrix.Rotation(tilt, 4, "X")
    ry = Matrix.Rotation(roll, 4, "Y")

    return rz @ rx @ ry

def blender_camera_rotation_from_virtual_matrix(rotation):
    """
    Blender cameras look through local -Z.
    LIMNMOCO virtual forward is +Y.
    """
    return rotation @ Matrix.Rotation(math.radians(90), 4, "X")
