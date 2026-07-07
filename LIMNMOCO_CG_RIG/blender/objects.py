print("[OBJECTS_V3] Loaded")

import bpy
from mathutils import Vector

from ..debug.log import scene


# ============================================================
# SIMPLE DE STIJL / LIMN VIEWPORT COLORS
# ============================================================

LIMN_RED = (0.894, 0.000, 0.169, 1.0)
LIMN_BLUE = (0.000, 0.278, 0.733, 1.0)
LIMN_YELLOW = (0.996, 0.820, 0.255, 1.0)
LIMN_BLACK = (0.000, 0.000, 0.000, 1.0)
LIMN_PURPLE = (0.500, 0.250, 0.800, 1.0)
LIMN_GRAY = (0.500, 0.500, 0.500, 1.0)


# ============================================================
# COLOR HELPERS
# ============================================================

def make_simple_material(name, color):
    """
    Make a very simple Blender material.

    This intentionally avoids shader complexity.
    It matches the standalone color test that worked in Blender.
    """

    mat_name = f"{name}_MAT"

    print("[OBJECTS_V3][MATERIAL] get/create:", mat_name, color)

    mat = bpy.data.materials.get(mat_name)

    if mat is None:
        mat = bpy.data.materials.new(mat_name)

    mat.diffuse_color = color
    return mat


def apply_color_to_mesh(obj, color):
    """
    Apply color to a mesh object such as a sphere.
    """

    print("[OBJECTS_V3][MESH COLOR]", obj.name, color)

    obj.color = color

    mat = make_simple_material(obj.name, color)

    if obj.data:
        obj.data.materials.clear()
        obj.data.materials.append(mat)

    obj.active_material = mat


def apply_color_to_curve(obj, curve, color):
    """
    Apply color to a curve object.

    Curves are the line objects in this add-on.
    The material MUST be placed on curve.materials.
    """

    print("[OBJECTS_V3][CURVE COLOR]", obj.name, color)

    obj.color = color

    mat = make_simple_material(obj.name, color)

    curve.materials.clear()
    curve.materials.append(mat)

    obj.active_material = mat


# ============================================================
# COLLECTION HELPERS
# ============================================================

def link_to_collection(obj, col):
    """
    Move object into the LIMNMOCO collection only.
    """

    print("[OBJECTS_V3] link_to_collection:", obj.name)

    for old in list(obj.users_collection):
        old.objects.unlink(obj)

    col.objects.link(obj)


# ============================================================
# BASIC OBJECT HELPERS
# ============================================================

def make_empty(name, loc, col, display="PLAIN_AXES", size=0.6):
    """
    Create a simple Blender Empty.
    """

    scene("make_empty:", name, loc)
    print("[OBJECTS_V3] make_empty:", name, loc)

    obj = bpy.data.objects.new(name, None)
    obj.location = loc
    obj.empty_display_type = display
    obj.empty_display_size = size
    obj.show_name = False

    col.objects.link(obj)
    return obj


def ensure_control(col):
    """
    Ensure the persistent LIMN_CONTROL object exists.
    """

    print("[OBJECTS_V3] ensure_control()")

    control = bpy.data.objects.get("LIMN_CONTROL")

    if control is None:
        scene("Creating LIMN_CONTROL")
        control = make_empty(
            "LIMN_CONTROL",
            Vector((0, 0, 0)),
            col,
            "CUBE",
            0.8,
        )

    elif control.name not in col.objects:
        col.objects.link(control)

    control.show_name = False
    return control


def make_label_empty(name, loc, col, label_offset):
    """
    Labels are intentionally disabled for the beta viewport.
    """

    return None


def make_sphere(
    name,
    loc,
    radius,
    col,
    label_offset=None,
    color=LIMN_GRAY,
    show_label=False,
):
    """
    Create a colored debug sphere.

    Use keyword args for label_offset and color to avoid argument-order bugs.
    """

    if label_offset is None:
        label_offset = Vector((0.25, 0.25, 0.25))

    scene("make_sphere:", name, loc)
    print("[OBJECTS_V3] make_sphere:", name, loc, "color:", color)

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12,
        ring_count=6,
        radius=radius,
        location=loc,
    )

    obj = bpy.context.object
    obj.name = name

    apply_color_to_mesh(obj, color)
    link_to_collection(obj, col)

    return obj


def make_line(
    name,
    a,
    b,
    col,
    bevel=0.02,
    color=LIMN_BLACK,
):
    """
    Create a colored curve line.

    This copies the standalone curve material pattern that worked:
        curve.materials.append(mat)
        obj.active_material = mat
    """

    scene("make_line:", name, a, b)
    print("[OBJECTS_V3] make_line:", name, "color:", color)

    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = bevel
    curve.resolution_u = 1

    spline = curve.splines.new("POLY")
    spline.points.add(1)

    spline.points[0].co = (a.x, a.y, a.z, 1)
    spline.points[1].co = (b.x, b.y, b.z, 1)

    obj = bpy.data.objects.new(name, curve)
    obj.show_name = False

    apply_color_to_curve(obj, curve, color)

    col.objects.link(obj)

    print("[OBJECTS_V3][LINE CREATED]", obj.name, "mat:", obj.active_material.name)

    return obj

def make_cube_marker(
    name,
    loc,
    size,
    col,
    label_offset=None,
    color=LIMN_BLUE,
    show_label=False,
):
    """
    Create a cube marker at an exact solved point.

    Used when multiple semantic points share the same coordinate.
    A cube reads differently from a sphere without moving the point.
    """

    if label_offset is None:
        label_offset = Vector((0.25, 0.25, 0.25))

    scene("make_cube_marker:", name, loc)
    print("[OBJECTS_V3] make_cube_marker:", name, loc, "color:", color)

    bpy.ops.mesh.primitive_cube_add(
        size=size,
        location=loc,
    )

    obj = bpy.context.object
    obj.name = name
    obj.show_name = False

    apply_color_to_mesh(obj, color)
    link_to_collection(obj, col)

    return obj


def make_ring_marker(
    name,
    loc,
    major_radius,
    minor_radius,
    col,
    label_offset=None,
    color=LIMN_PURPLE,
    show_label=False,
):
    """
    Create a torus/ring marker at an exact solved point.

    Used for Target because a ring can surround other markers
    without hiding them completely.
    """

    if label_offset is None:
        label_offset = Vector((0.25, 0.25, 0.25))

    scene("make_ring_marker:", name, loc)
    print("[OBJECTS_V3] make_ring_marker:", name, loc, "color:", color)

    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=32,
        minor_segments=8,
        location=loc,
    )

    obj = bpy.context.object
    obj.name = name
    obj.show_name = False
    print("[SPHERE COLOR CHECK]", name, color)
    apply_color_to_mesh(obj, color)
    link_to_collection(obj, col)

    return obj

# ============================================================
# LIMNMOCO DEBUG RESULT DRAWING
# ============================================================

def draw_limmoco_crane_result(result, col, show_labels=False):
    """
    Draw minimal solver/debug visualization.

    Spheres are semantic colors.
    Primary mechanical lines are black.
    World axes follow RGB-ish De Stijl convention.
    """

    scene("draw_limmoco_crane_result()")
    print("[OBJECTS_V3] draw_limmoco_crane_result()")

    # --------------------------------------------------------
    # Solved point markers
    # --------------------------------------------------------

    make_ring_marker(
        "PT_TARGET",
        result.target,
        major_radius=0.36,
        minor_radius=0.025,
        col=col,
        label_offset=Vector((0.30, 0.30, 0.30)),
        color=LIMN_PURPLE,
        show_label=show_labels,
    )

    make_sphere(
        "PT_BASE_BOOM_SWING_PIVOT",
        result.base,
        0.28,
        col,
        label_offset=Vector((0.30, 0.30, 1.30)),
        color=LIMN_BLACK,
        show_label=show_labels,
    )

    make_sphere(
        "PT_ARM_TIP",
        result.arm_tip,
        0.14,
        col,
        label_offset=Vector((0.30, -0.30, 1.30)),
        color=LIMN_RED,
        show_label=show_labels,
    )

    make_cube_marker(
        "PT_PAN_CENTER",
        result.pan_center,
        size=0.22,
        col=col,
        label_offset=Vector((-0.30, 0.30, 0.45)),
        color=LIMN_BLUE,
        show_label=show_labels,
    )

    make_sphere(
        "PT_CAMERA_NODAL",
        result.nodal,
        0.06,
        col,
        label_offset=Vector((0.00, 0.00, 0.70)),
        color=LIMN_YELLOW,
        show_label=show_labels,
    )

    # --------------------------------------------------------
    # Mechanical relationship lines
    # --------------------------------------------------------

    make_line(
        "LN_BOOM_PARALLELOGRAM",
        result.base,
        result.arm_tip,
        col,
        bevel=0.04,
        color=LIMN_YELLOW,
    )
    
    make_line(
        "LN_LEVEL_EXTENSION",
        result.arm_tip,
        result.pan_center,
        col,
        bevel=0.035,
        color=LIMN_BLACK,
    )


    make_line(
        "LN_CAMERA_OFFSET_PAN_CENTER_TO_NODAL",
        result.pan_center,
        result.nodal,
        col,
        bevel=0.025,
        color=LIMN_YELLOW,
    )

    make_line(
        "LN_ERROR_NODAL_TO_TARGET",
        result.nodal,
        result.target,
        col,
        bevel=0.015,
        color=LIMN_RED,
    )

    # --------------------------------------------------------
    # World reference axes
    # --------------------------------------------------------

    make_line(
        "LN_AXIS_X_VEW",
        Vector((-10, 0, 0)),
        Vector((10, 0, 0)),
        col,
        bevel=0.006,
        color=LIMN_RED,
    )

    make_line(
        "LN_AXIS_Y_VTRACK",
        Vector((0, -10, 0)),
        Vector((0, 10, 0)),
        col,
        bevel=0.006,
        color=LIMN_BLUE,
    )

    make_line(
        "LN_AXIS_Z_VHEIGHT",
        Vector((0, 0, 0)),
        Vector((0, 0, 10)),
        col,
        bevel=0.006,
        color=LIMN_YELLOW,
    )
