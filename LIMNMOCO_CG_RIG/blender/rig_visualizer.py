import math
import bpy
from mathutils import Vector

from ..debug.log import scene
from .objects import (
    make_sphere,
    make_line,
    make_cube_marker,
    make_simple_material,
    LIMN_BLUE,
    LIMN_RED,
    LIMN_YELLOW,
    LIMN_BLACK,
    LIMN_GRAY,
)

print("[RIG VISUALIZER] Loaded")


RANGE_TRACK_COLOR = (0.380, 0.600, 1.000, 1.0)
RANGE_SWING_COLOR = (1.000, 0.450, 0.520, 1.0)
RANGE_BOOM_COLOR = (1.000, 0.920, 0.500, 1.0)

ENVELOPE_BLUE = (0.000, 0.278, 0.733, 1.0)
ENVELOPE_RED = (0.894, 0.000, 0.169, 1.0)
ENVELOPE_YELLOW = (0.996, 0.820, 0.255, 1.0)
ENVELOPE_VOLUME_COLOR = (0.380, 0.600, 1.000, 0.16)
PLANE_XY_COLOR = (1.000, 0.450, 0.520, 0.18)
PLANE_YZ_COLOR = (0.380, 0.600, 1.000, 0.18)
PLANE_XZ_COLOR = (1.000, 0.920, 0.500, 0.18)


def make_transparent_material(name, color):
    mat = bpy.data.materials.get(name)

    if mat is None:
        mat = bpy.data.materials.new(name)

    mat.diffuse_color = color
    mat.use_nodes = True

    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    if bsdf:
        bsdf.inputs["Base Color"].default_value = color

        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = color[3]

    mat.blend_method = "BLEND"
    mat.show_transparent_back = True

    if hasattr(mat, "use_screen_refraction"):
        mat.use_screen_refraction = False

    return mat


def make_mesh_object(name, verts, faces, col, color):
    mesh = bpy.data.meshes.new(f"{name}_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    obj.show_name = False
    obj.display_type = "TEXTURED"
    obj.color = color

    mat = make_transparent_material(f"{name}_MAT", color)
    mesh.materials.append(mat)
    obj.active_material = mat

    col.objects.link(obj)
    return obj


def make_axis_plane(name, center, axis_a, axis_b, size, col, color):
    half = size * 0.5
    a = axis_a.normalized() * half
    b = axis_b.normalized() * half
    verts = [
        tuple(center - a - b),
        tuple(center + a - b),
        tuple(center + a + b),
        tuple(center - a + b),
    ]
    faces = [(0, 1, 2, 3)]

    return make_mesh_object(name, verts, faces, col, color)

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
    bevel=0.03,
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
    bevel=0.03,
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
    bevel=0.03,
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
    obj.show_name = False
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

def draw_limmoco_crane_body(result, props, col):
    """
    Draw an abstract physical crane mechanics layer.

    This is an educational rig diagram, not CAD. It names the
    primary mechanism pieces so artists can understand the solved
    crane layout directly in the Blender outliner.
    """

    scene("draw_limmoco_crane_body()")

    base = result.base
    arm_tip = result.arm_tip
    pan_center = result.pan_center
    nodal = result.nodal

    column_height = max(
        1.2,
        min(4.0, abs(arm_tip.z) * 0.2 + 1.0),
    )
    column_top = base + Vector((0, 0, column_height))

    make_line(
        "CRANE_MECH_TrackRail",
        Vector((0, props.track_min, 0)),
        Vector((0, props.track_max, 0)),
        col,
        bevel=0.08,
        color=LIMN_BLUE,
    )

    make_cube_marker(
        "CRANE_MECH_BaseCarriage",
        base,
        size=0.55,
        col=col,
        label_offset=Vector((0.40, 0.20, 0.55)),
        color=LIMN_BLACK,
    )

    make_line(
        "CRANE_MECH_SwingColumn",
        base,
        column_top,
        col,
        bevel=0.08,
        color=LIMN_BLACK,
    )

    make_cube_marker(
        "CRANE_MECH_SwingColumnTop",
        column_top,
        size=0.34,
        col=col,
        label_offset=Vector((0.35, 0.20, 0.35)),
        color=LIMN_BLACK,
    )

    make_line(
        "CRANE_MECH_BoomArm",
        base,
        arm_tip,
        col,
        bevel=0.07,
        color=LIMN_YELLOW,
    )

    make_line(
        "CRANE_MECH_ExtensionArm",
        arm_tip,
        pan_center,
        col,
        bevel=0.055,
        color=LIMN_BLACK,
    )

    make_cube_marker(
        "CRANE_MECH_PanHead",
        pan_center,
        size=0.32,
        col=col,
        label_offset=Vector((0.30, 0.30, 0.45)),
        color=LIMN_RED,
    )

    make_cube_marker(
        "CRANE_MECH_CameraBlock",
        nodal,
        size=0.22,
        col=col,
        label_offset=Vector((0.25, -0.25, 0.45)),
        color=LIMN_BLUE,
    )

    make_line(
        "CRANE_MECH_PanHead_to_CameraBlock",
        pan_center,
        nodal,
        col,
        bevel=0.025,
        color=LIMN_GRAY,
    )


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
        bevel=0.05,
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
        bevel=0.05,
        color=RANGE_BOOM_COLOR,
    )
    
def sample_envelope_grid(props):
    points = {}
    track_steps = 5
    swing_steps = 9
    boom_steps = 5

    boom_len = props.boom_length
    ext_len = props.extension_length

    for ti in range(track_steps):
        track_t = ti / (track_steps - 1)
        track = props.track_min + (props.track_max - props.track_min) * track_t

        for si in range(swing_steps):
            swing_t = si / (swing_steps - 1)
            swing_deg = props.swing_min + (props.swing_max - props.swing_min) * swing_t
            swing_rad = math.radians(swing_deg)

            for bi in range(boom_steps):
                boom_t = bi / (boom_steps - 1)
                boom_deg = props.boom_min + (props.boom_max - props.boom_min) * boom_t
                boom_rad = math.radians(boom_deg)

                reach = boom_len * math.cos(boom_rad) + ext_len
                z = boom_len * math.sin(boom_rad)

                x = reach * math.sin(swing_rad)
                y = track + reach * math.cos(swing_rad)

                points[(ti, si, bi)] = Vector((x, y, z))

    return points, track_steps, swing_steps, boom_steps


def draw_envelope_outer_mesh(grid, track_steps, swing_steps, boom_steps, col):
    if not grid:
        return

    vertices = []
    index_by_key = {}

    for key, loc in grid.items():
        index_by_key[key] = len(vertices)
        vertices.append(tuple(loc))

    faces = []

    def add_face(a, b, c, d):
        faces.append((
            index_by_key[a],
            index_by_key[b],
            index_by_key[c],
            index_by_key[d],
        ))

    for ti in (0, track_steps - 1):
        for si in range(swing_steps - 1):
            for bi in range(boom_steps - 1):
                add_face(
                    (ti, si, bi),
                    (ti, si + 1, bi),
                    (ti, si + 1, bi + 1),
                    (ti, si, bi + 1),
                )

    for si in (0, swing_steps - 1):
        for ti in range(track_steps - 1):
            for bi in range(boom_steps - 1):
                add_face(
                    (ti, si, bi),
                    (ti + 1, si, bi),
                    (ti + 1, si, bi + 1),
                    (ti, si, bi + 1),
                )

    for bi in (0, boom_steps - 1):
        for ti in range(track_steps - 1):
            for si in range(swing_steps - 1):
                add_face(
                    (ti, si, bi),
                    (ti + 1, si, bi),
                    (ti + 1, si + 1, bi),
                    (ti, si + 1, bi),
                )

    make_mesh_object("ENVELOPE_OUTER_MESH", vertices, faces, col, ENVELOPE_VOLUME_COLOR)


def draw_camera_axis_planes(result, props, col):
    scene("draw_camera_axis_planes()")

    center = result.nodal
    rotation = result.rotation
    size = max(2.0, min(12.0, props.boom_length * 0.08))

    right = rotation @ Vector((1, 0, 0))
    forward = rotation @ Vector((0, 1, 0))
    up = rotation @ Vector((0, 0, 1))

    make_axis_plane(
        "CAM_PLANE_XY_RightForward",
        center,
        right,
        forward,
        size,
        col,
        PLANE_XY_COLOR,
    )
    make_axis_plane(
        "CAM_PLANE_YZ_ForwardUp",
        center,
        forward,
        up,
        size,
        col,
        PLANE_YZ_COLOR,
    )
    make_axis_plane(
        "CAM_PLANE_XZ_RightUp",
        center,
        right,
        up,
        size,
        col,
        PLANE_XZ_COLOR,
    )


def draw_reach_envelope(result, props, col, show_points=False):
    scene("draw_reach_envelope()")
    print("[RIG VISUALIZER V2] draw_reach_envelope()")

    grid, track_steps, swing_steps, boom_steps = sample_envelope_grid(props)
    draw_envelope_outer_mesh(grid, track_steps, swing_steps, boom_steps, col)

    if not show_points:
        return

    for (ti, si, bi), loc in grid.items():
        make_sphere(
            f"ENVELOPE_POINT_{ti}_{si}_{bi}",
            loc,
            0.045,
            col,
            label_offset=Vector((0, 0, 0.12)),
            color=RANGE_TRACK_COLOR,
            show_label=False,
        )
