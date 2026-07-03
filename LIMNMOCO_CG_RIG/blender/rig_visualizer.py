import math
import bpy
from mathutils import Vector

from ..debug.log import scene
from .objects import (
    make_sphere,
    make_line,
    make_simple_material,
    LIMN_BLACK,
    LIMN_GRAY,
)

print("[RIG VISUALIZER] Loaded")


RANGE_TRACK_COLOR = (0.380, 0.600, 1.000, 1.0)
RANGE_SWING_COLOR = (1.000, 0.450, 0.520, 1.0)
RANGE_BOOM_COLOR = (1.000, 0.920, 0.500, 1.0)

# ============================================================
# RANGE GUIDE HELPERS
# ============================================================

def make_arc_xy(
    name,
    center,
    radius,
    z,
    start_deg,
    end_deg,
    col,
    steps=48,
    bevel=0.01,
    color=None,
):
    """
    Draw an arc in the XY plane.

    Used for swing range.

    Angle convention matches the crane solver:
    X = radius * sin(angle)
    Y = radius * cos(angle)
    """

    pts = []

    start = math.radians(start_deg)
    end = math.radians(end_deg)

    for i in range(steps + 1):
        t = i / steps
        a = start + (end - start) * t

        pts.append(Vector((
            center.x + radius * math.sin(a),
            center.y + radius * math.cos(a),
            z,
        )))
    
    if color is None:
        color = RANGE_SWING_COLOR

    make_polyline(
        name,
        pts,
        col,
        bevel=bevel,
        color=color,
    )


def make_arc_yz(
    name,
    center,
    radius,
    x,
    start_deg,
    end_deg,
    col,
    steps=24,
    bevel=0.01,
    color=None,
):
    """
    Draw an arc in the YZ plane.

    Used for boom range side profile.
    """

    pts = []

    start = math.radians(start_deg)
    end = math.radians(end_deg)

    for i in range(steps + 1):
        t = i / steps
        a = start + (end - start) * t

        pts.append(Vector((
            x,
            center.y + radius * math.cos(a),
            center.z + radius * math.sin(a),
        )))
        
    if color is None:
        color = RANGE_BOOM_COLOR
        
    make_polyline(
        name,
        pts,
        col,
        bevel=bevel,
        color=color,
    )




def make_polyline(
    name,
    points,
    col,
    bevel=0.01,
    color=LIMN_GRAY,
):
    """
    Draw a multi-point curve as ONE object.

    This is used for range arcs so the outliner does not fill with
    RANGE_Swing_000, RANGE_Swing_001, etc.
    """

    print("[RIG VISUALIZER V2] make_polyline:", name, "points:", len(points), "color:", color)

    if len(points) < 2:
        print("[RIG VISUALIZER V2][WARNING] Not enough points for", name)
        return None

    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = bevel
    curve.resolution_u = 1

    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)

    for point, vec in zip(spline.points, points):
        point.co = (vec.x, vec.y, vec.z, 1)

    obj = bpy.data.objects.new(name, curve)
    obj.show_name = True
    obj.color = color

    mat = make_simple_material(name, color)
    curve.materials.clear()
    curve.materials.append(mat)
    obj.active_material = mat

    col.objects.link(obj)

    print("[RIG VISUALIZER V2][POLYLINE CREATED]", obj.name, "mat:", obj.active_material.name)

    return obj


# ============================================================
# MAIN VISUALIZER
# ============================================================

def draw_limmoco_crane_body(result, col):
    """
    Draw the simple physical crane body.

    This is separate from the Blender camera.
    The actual persistent LIMN_CAMERA remains at the nodal point.
    """

    scene("draw_limmoco_crane_body()")

    make_sphere("CRANE_Base_TrackPivot", result.base, 0.20, col)
    make_sphere("CRANE_ArmTip", result.arm_tip, 0.18, col)
    make_sphere("CRANE_PanCenter", result.pan_center, 0.18, col)

    make_line(
        "CRANE BoomArm Parallelogram",
        result.base,
        result.arm_tip,
        col,
        0.05,
    )

 #   make_line(
 #       "CRANE_LevelExtension",
 #       result.arm_tip,
 #       result.pan_center,
 #       col,
  #      0.04,
 #   )


def draw_range_guides(result, props, col):
    """
    Draw display-only mechanical range guides.

    These do NOT clamp or constrain the CG rig.
    They only show the intended physical working envelope.
    """

    scene("draw_range_guides()")

    # Track range.
    make_line(
        "RANGE_Track_MinMax",
        Vector((0, props.track_min, 0)),
        Vector((0, props.track_max, 0)),
        col,
        bevel=0.06,
        color=RANGE_TRACK_COLOR,
    )

    # Swing range at the solved boom height.
    boom_height = result.arm_tip.z
    horizontal_reach = (
        (result.pan_center - result.base).to_2d().length
    )

    make_arc_xy(
        "RANGE_Swing",
        result.base,
        horizontal_reach,
        boom_height,
        props.swing_min,
        props.swing_max,
        col,
        steps=24,
        bevel=0.018,
        color=RANGE_SWING_COLOR,
    )

    # Boom range side profile.
    make_arc_yz(
        "RANGE_Boom",
        result.base,
        props.boom_length,
        0,
        props.boom_min,
        props.boom_max,
        col,
        steps=24,
        bevel=0.018,
        color=RANGE_BOOM_COLOR,
    )