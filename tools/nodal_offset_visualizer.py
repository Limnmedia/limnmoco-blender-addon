"""Standalone LIMNMOCO nodal-offset nesting visualizer.

Run this file from Blender's Scripting workspace.  It intentionally does not
import or register the LIMNMOCO add-on.  Change the constants below and run it
again to replace only the dedicated stub collection.
"""

import math

import bpy
from mathutils import Matrix, Vector


# ---------------------------------------------------------------------------
# Editable inputs (distances are Blender units; angles are degrees).
# ---------------------------------------------------------------------------

PAN_DEG = 25.0
TILT_DEG = -20.0
ROLL_DEG = 35.0
OFFSET_LOCAL = (0.75, 1.25, 0.45)

ROLL_DISC_RADIUS = 1.15
ROLL_DISC_THICKNESS = 0.015
ROLL_RING_OUTER_RADIUS = 1.65
ROLL_RING_INNER_RADIUS = 1.28
ROLL_RING_DEPTH = 0.42
ROLL_DISC_TO_HEX = 1.5
TILT_DISC_RADIUS = 1.15
TILT_DISC_THICKNESS = 0.015
TILT_RING_OUTER_RADIUS = 1.65
TILT_RING_INNER_RADIUS = 1.28
TILT_RING_DEPTH = 0.42
TILT_DISC_TO_HEX = 1.5
PAN_DISC_RADIUS = 1.15
PAN_DISC_THICKNESS = 0.015
PAN_RING_OUTER_RADIUS = 1.65
PAN_RING_INNER_RADIUS = 1.28
PAN_RING_DEPTH = 0.42
PAN_DISC_TO_HEX = 1.5
CRANE_CONNECTION_SIZE = 0.55
CRANE_CONNECTION_HEIGHT = 0.9
AXIS_LINE_RADIUS = 0.045
AXIS_LINE_SIDES = 12
NODAL_POINT_WORLD = (0.0, 0.0, 0.0)
READOUT_LOCATION = (-3.0, -2.2, 2.4)
READOUT_SIZE = 0.18
PLANE_SIZE = 3.2
LINE_WIDTH = 0.035
TEXT_SIZE = 0.22


COLLECTION_NAME = "LIMNMOCO_NODAL_OFFSET_STUB"
PREFIX = "LIMNMOCO_STUB_"

RED = (0.90, 0.04, 0.10, 1.0)
GREEN = (0.10, 0.75, 0.20, 1.0)
BLUE = (0.08, 0.30, 0.95, 1.0)
YELLOW = (1.0, 0.72, 0.05, 1.0)
CYAN = (0.05, 0.85, 0.95, 1.0)
ORANGE = (1.0, 0.28, 0.04, 1.0)
PURPLE = (0.62, 0.16, 0.95, 1.0)
WHITE = (0.95, 0.95, 0.95, 1.0)
GRAY = (0.55, 0.55, 0.55, 1.0)


def remove_stub_collection():
    """Remove only the collection owned by this script, including its objects."""
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if collection is None:
        return

    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)


def material(name, color, alpha=1.0):
    """Create/reuse a clearly stub-owned material without touching add-on data."""
    mat = bpy.data.materials.get(PREFIX + name)
    if mat is None:
        mat = bpy.data.materials.new(PREFIX + name)
    mat.diffuse_color = (*color[:3], alpha)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (*color[:3], alpha)
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
    # Blender 4.x uses surface_render_method; older versions use blend_method.
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "DITHERED" if alpha < 1.0 else "DITHERED"
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "BLEND" if alpha < 1.0 else "OPAQUE"
        mat.show_transparent_back = False
    return mat


def link_object(obj, collection):
    collection.objects.link(obj)
    return obj


def make_curve(name, points, collection, color, bevel=LINE_WIDTH, parent=None, dashed=False):
    curve = bpy.data.curves.new(PREFIX + name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = bevel
    curve.bevel_resolution = 2
    curve.resolution_u = 1
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, co in zip(spline.points, points):
        point.co = (*co, 1.0)
    if dashed:
        # A dashed effect is intentionally omitted: a solid, thin local vector
        # remains readable in all viewport shading modes.
        curve.bevel_depth = bevel * 0.75
    obj = link_object(bpy.data.objects.new(PREFIX + name, curve), collection)
    obj.data.materials.append(material(name + "_MAT", color))
    if parent is not None:
        obj.parent = parent
    return obj


def make_mesh(name, vertices, faces, collection, color, alpha=0.18, parent=None):
    mesh = bpy.data.meshes.new(PREFIX + name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = link_object(bpy.data.objects.new(PREFIX + name, mesh), collection)
    obj.data.materials.append(material(name + "_MAT", color, alpha))
    if parent is not None:
        obj.parent = parent
    return obj


def make_sphere(name, location, collection, color, radius=0.11, parent=None):
    # Build a small UV sphere directly; avoiding bpy.ops keeps existing
    # selection and active-object state untouched.
    segments = 16
    rings = 8
    vertices = [(0.0, 0.0, radius)]
    for ring in range(1, rings):
        phi = math.pi * ring / rings
        for segment in range(segments):
            theta = 2.0 * math.pi * segment / segments
            vertices.append((
                radius * math.sin(phi) * math.cos(theta),
                radius * math.sin(phi) * math.sin(theta),
                radius * math.cos(phi),
            ))
    bottom = len(vertices)
    vertices.append((0.0, 0.0, -radius))
    faces = []
    for segment in range(segments):
        faces.append((0, 1 + segment, 1 + (segment + 1) % segments))
    for ring in range(rings - 2):
        start = 1 + ring * segments
        next_start = start + segments
        for segment in range(segments):
            a = start + segment
            b = start + (segment + 1) % segments
            c = next_start + (segment + 1) % segments
            d = next_start + segment
            faces.append((a, b, c, d))
    last = 1 + (rings - 2) * segments
    for segment in range(segments):
        faces.append((last + segment, bottom, last + (segment + 1) % segments))
    mesh = bpy.data.meshes.new(PREFIX + name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = link_object(bpy.data.objects.new(PREFIX + name, mesh), collection)
    obj.location = location
    obj.data.materials.append(material(name + "_MAT", color))
    if parent is not None:
        obj.parent = parent
    return obj


def make_text(name, body, location, collection, color=WHITE, parent=None, rotation=None):
    text_curve = bpy.data.curves.new(PREFIX + name, "FONT")
    text_curve.body = body
    text_curve.align_x = "CENTER"
    text_curve.size = TEXT_SIZE
    text_curve.extrude = 0.005
    obj = link_object(bpy.data.objects.new(PREFIX + name, text_curve), collection)
    obj.location = location
    obj.data.materials.append(material(name + "_MAT", color))
    if rotation is not None:
        obj.rotation_euler = rotation
    if parent is not None:
        obj.parent = parent
    return obj


def make_axis(name, axis, label, color, collection, parent, length=1.0):
    end = Vector(axis) * length
    make_curve(name + "_AXIS", [(0.0, 0.0, 0.0), end], collection, color, parent=parent)
    make_text(name + "_LABEL", label, end + Vector(axis) * 0.18, collection, color, parent=parent)


def make_plane(name, normal, color, collection, parent):
    """Make a square plane in the parent's local XY plane, centered at origin."""
    half = PLANE_SIZE / 2.0
    vertices = [(-half, -half, 0), (half, -half, 0), (half, half, 0), (-half, half, 0)]
    return make_mesh(name, vertices, [(0, 1, 2, 3)], collection, color, alpha=0.14, parent=parent)


def make_hex_ring(name, collection, parent, outer_radius, inner_radius, depth, offset_vector, color):
    """Create a thick six-sided annular prism in the local X-Z plane."""
    sides = 6
    outer = outer_radius
    inner = inner_radius
    half_depth = depth / 2.0

    # Each perimeter is duplicated at both Y faces.  The object is positioned
    # by an explicit local-frame vector supplied by the owning disc.
    vertices = []
    for y in (-half_depth, half_depth):
        for radius in (outer, inner):
            for index in range(sides):
                angle = 2.0 * math.pi * index / sides + math.pi / 6.0
                vertices.append((radius * math.cos(angle), y, radius * math.sin(angle)))

    outer_back = 0
    inner_back = sides
    outer_front = 2 * sides
    inner_front = 3 * sides
    faces = []

    for index in range(sides):
        next_index = (index + 1) % sides
        # Front/back annular faces.
        faces.append((outer_front + index, outer_front + next_index,
                      inner_front + next_index, inner_front + index))
        faces.append((outer_back + next_index, outer_back + index,
                      inner_back + index, inner_back + next_index))
        # Outer and inner walls.
        faces.append((outer_back + index, outer_back + next_index,
                      outer_front + next_index, outer_front + index))
        faces.append((inner_back + next_index, inner_back + index,
                      inner_front + index, inner_front + next_index))

    ring = make_mesh(name, vertices, faces, collection, color, alpha=0.82, parent=parent)
    ring.location = offset_vector
    return ring


def make_disc(name, collection, parent, radius, thickness, color, normal_axis="Y"):
    """Create a solid circular disc with a selectable local face normal."""
    normal_axis = normal_axis.upper()
    if normal_axis not in {"X", "Y", "Z"}:
        raise ValueError("normal_axis must be X, Y, or Z")

    sides = 32
    half_depth = thickness / 2.0
    vertices = []

    for depth in (-half_depth, half_depth):
        center = [0.0, 0.0, 0.0]
        center["XYZ".index(normal_axis)] = depth
        vertices.append(tuple(center))
        for index in range(sides):
            angle = 2.0 * math.pi * index / sides
            point = [0.0, 0.0, 0.0]
            plane_axes = [axis for axis in "XYZ" if axis != normal_axis]
            point["XYZ".index(plane_axes[0])] = radius * math.cos(angle)
            point["XYZ".index(plane_axes[1])] = radius * math.sin(angle)
            point["XYZ".index(normal_axis)] = depth
            vertices.append(tuple(point))

    back_center = 0
    back_start = 1
    front_center = sides + 1
    front_start = sides + 2
    faces = []
    for index in range(sides):
        next_index = (index + 1) % sides
        faces.append((back_center, back_start + next_index, back_start + index))
        faces.append((front_center, front_start + index, front_start + next_index))
        faces.append((back_start + index, back_start + next_index,
                      front_start + next_index, front_start + index))

    return make_mesh(name, vertices, faces, collection, color, alpha=0.65, parent=parent)


def make_axis_cylinder(name, collection, center, endpoint, color):
    """Create a one-ended cylinder whose object origin is at center."""
    center = Vector(center)
    endpoint = Vector(endpoint)
    direction = endpoint - center
    length = direction.length
    if length <= 1e-6:
        raise ValueError(name + " needs distinct center and endpoint")

    sides = AXIS_LINE_SIDES
    radius = AXIS_LINE_RADIUS
    vertices = []
    for z in (0.0, length):
        for index in range(sides):
            angle = 2.0 * math.pi * index / sides
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), z))

    faces = []
    for index in range(sides):
        next_index = (index + 1) % sides
        faces.append((index, next_index, sides + next_index, sides + index))
    faces.append(tuple(range(sides - 1, -1, -1)))
    faces.append(tuple(range(sides, 2 * sides)))

    line = make_mesh(name, vertices, faces, collection, color, alpha=1.0, parent=None)
    line.location = center
    line.rotation_mode = "XYZ"
    line.rotation_euler = Vector((0.0, 0.0, 1.0)).rotation_difference(direction.normalized()).to_euler()
    return line


def rotation_matrix():
    pan = Matrix.Rotation(math.radians(PAN_DEG), 4, "Z")
    tilt = Matrix.Rotation(math.radians(TILT_DEG), 4, "X")
    roll = Matrix.Rotation(math.radians(ROLL_DEG), 4, "Y")
    return pan @ tilt @ roll


def make_joint(name, collection, parent, allowed_axis):
    """Create a neutral nested joint constrained to one local rotation axis."""
    joint = link_object(bpy.data.objects.new(PREFIX + name, None), collection)
    joint.empty_display_type = "PLAIN_AXES"
    joint.empty_display_size = 0.5
    if parent is not None:
        joint.parent = parent

    constraint = joint.constraints.new("LIMIT_ROTATION")
    constraint.name = PREFIX + name + "_AXIS_CONSTRAINT"
    constraint.owner_space = "LOCAL"
    for axis in ("x", "y", "z"):
        setattr(constraint, "use_limit_" + axis, axis != allowed_axis.lower())
        if axis != allowed_axis.lower():
            setattr(constraint, "min_" + axis, 0.0)
            setattr(constraint, "max_" + axis, 0.0)
    return joint


def make_geometry_frame(name, collection, parent, rotation):
    """Orient the reusable X-Z rotor mesh to its physical stage axis."""
    frame = link_object(bpy.data.objects.new(PREFIX + name, None), collection)
    frame.empty_display_type = "PLAIN_AXES"
    frame.empty_display_size = 0.35
    frame.parent = parent
    frame.rotation_euler = rotation
    return frame


def make_translation_null(name, collection, parent=None):
    """Create a neutral translation controller for a nested stage."""
    null = link_object(bpy.data.objects.new(PREFIX + name, None), collection)
    null.empty_display_type = "CUBE"
    null.empty_display_size = 0.65
    null.rotation_euler = (0.0, 0.0, 0.0)
    if parent is not None:
        null.parent = parent

    constraint = null.constraints.new("LIMIT_ROTATION")
    constraint.name = PREFIX + name + "_ROTATION_LOCK"
    constraint.owner_space = "LOCAL"
    for axis in ("x", "y", "z"):
        setattr(constraint, "use_limit_" + axis, True)
        setattr(constraint, "min_" + axis, 0.0)
        setattr(constraint, "max_" + axis, 0.0)
    return null


def add_rotation_constraint(obj, allowed_axis):
    """Constrain an object to rotation around one local axis only."""
    constraint = obj.constraints.new("LIMIT_ROTATION")
    constraint.name = PREFIX + obj.name + "_AXIS_CONSTRAINT"
    constraint.owner_space = "LOCAL"
    allowed_axis = allowed_axis.lower()
    for axis in ("x", "y", "z"):
        locked = axis != allowed_axis
        setattr(constraint, "use_limit_" + axis, locked)
        if locked:
            setattr(constraint, "min_" + axis, 0.0)
            setattr(constraint, "max_" + axis, 0.0)
    return constraint


def make_cube(name, collection, parent, size, location):
    """Create a basic cube connection block without changing scene selection."""
    half = size / 2.0
    vertices = [
        (-half, -half, -half), (half, -half, -half),
        (half, half, -half), (-half, half, -half),
        (-half, -half, half), (half, -half, half),
        (half, half, half), (-half, half, half),
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5),
        (0, 4, 5, 1), (1, 5, 6, 2),
        (2, 6, 7, 3), (4, 0, 3, 7),
    ]
    cube = make_mesh(name, vertices, faces, collection, WHITE, alpha=1.0, parent=parent)
    cube.location = location
    return cube


def parent_at_current_world_transform(obj, parent):
    """Parent an object while keeping its evaluated world transform."""
    bpy.context.view_layer.update()
    world_matrix = obj.matrix_world.copy()
    parent_world_matrix = parent.matrix_world.copy()
    obj.parent = parent
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = parent_world_matrix.inverted() @ world_matrix
    return obj


def add_aim_constraint(obj, target):
    """Aim a cylinder's local +Z axis at the camera nodal point."""
    constraint = obj.constraints.new("TRACK_TO")
    constraint.name = PREFIX + obj.name + "_AIM_AT_NODAL"
    constraint.target = target
    constraint.track_axis = "TRACK_Z"
    constraint.up_axis = "UP_Y"
    return constraint


def format_vector(vector):
    return "(%+.3f, %+.3f, %+.3f)" % tuple(vector)


def update_nodal_offset_readout(scene=None, depsgraph=None):
    """Refresh the practical three-component nodal offset readout."""
    readout = bpy.data.objects.get(PREFIX + "NODAL_OFFSET_READOUT")
    nodal = bpy.data.objects.get(PREFIX + "CAMERA_NODAL_POINT")
    if readout is None or nodal is None:
        return

    nodal_world = nodal.matrix_world.translation.copy()
    origin = Vector((0.0, 0.0, 0.0))
    offset = nodal_world - origin
    lines = [
        "CAMERA NODAL OFFSET",
        "",
        "Camera axes mapped to Blender Z-up world",
        "",
        "VTrack / camera Z / Blender Y: %+.3f" % offset.y,
        "VEW / camera X / Blender X: %+.3f" % offset.x,
        "NS / camera Y / Blender Z: %+.3f" % offset.z,
    ]

    readout.data.body = "\n".join(lines)


def remove_readout_handlers():
    """Prevent duplicate handlers when the script is rerun in Blender."""
    for handler in list(bpy.app.handlers.depsgraph_update_post):
        if getattr(handler, "__name__", "") == "update_nodal_offset_readout":
            bpy.app.handlers.depsgraph_update_post.remove(handler)


def build():
    remove_stub_collection()
    remove_readout_handlers()
    collection = bpy.data.collections.new(COLLECTION_NAME)
    bpy.context.scene.collection.children.link(collection)

    crane_connection = make_cube(
        "CRANE_CONNECTION_CUBE", collection, None,
        CRANE_CONNECTION_SIZE,
        (0.0, 0.0, PAN_DISC_TO_HEX + CRANE_CONNECTION_HEIGHT),
    )
    crane_connection.lock_rotation = (True, True, True)

    # Match the saved mechanical hierarchy:
    # Crane Cube
    #   └─ Pan Disc
    #       ├─ Pan Hex
    #       └─ Tilt Disc
    #           ├─ Tilt Hex
    #           └─ Roll Disc
    #               └─ Roll Hex
    pan_disc = make_disc(
        "PAN_DISC", collection, crane_connection,
        PAN_DISC_RADIUS, PAN_DISC_THICKNESS, RED,
    )
    pan_disc.matrix_world = Matrix.Rotation(math.radians(-90.0), 4, "X")
    pan_disc.location = (0.0, 0.0, -(PAN_DISC_TO_HEX + CRANE_CONNECTION_HEIGHT))
    pan_disc.lock_rotation = (True, True, False)
    pan_disc.lock_location = (True, True, True)

    pan_ring = make_hex_ring(
        "PAN_HEX_RING", collection, pan_disc,
        PAN_RING_OUTER_RADIUS, PAN_RING_INNER_RADIUS,
        PAN_RING_DEPTH, (0.0, -PAN_DISC_TO_HEX, 0.0), YELLOW,
    )
    pan_ring.lock_rotation = (True, True, True)
    pan_ring.lock_location = (True, True, True)

    tilt_disc = make_disc(
        "TILT_DISC", collection, pan_disc,
        TILT_DISC_RADIUS, TILT_DISC_THICKNESS, ORANGE, normal_axis="X",
    )
    # Keep the tilt control's local X aligned with the pan frame's X.  The
    # mesh itself has an X normal, so the disc remains in the Y-Z plane.
    tilt_disc.rotation_euler = (0.0, 0.0, 0.0)
    # Tilt is the local-X rotation.  Keep local Y/Z locked, matching the
    # physical tilt stage while retaining the saved pan/roll conventions.
    tilt_disc.lock_rotation = (False, True, True)
    tilt_disc.lock_location = (True, True, True)

    tilt_ring = make_hex_ring(
        "TILT_HEX_RING", collection, tilt_disc,
        TILT_RING_OUTER_RADIUS, TILT_RING_INNER_RADIUS,
        TILT_RING_DEPTH, (-TILT_DISC_TO_HEX, 0.0, 0.0), PURPLE,
    )
    # The reusable hex mesh is built in X-Z.  Rotate this ring in its own
    # plane so it is parallel to the tilt disc's Y-Z plane.
    tilt_ring.rotation_euler = (0.0, 0.0, math.radians(-90.0))
    tilt_ring.lock_rotation = (True, True, True)
    tilt_ring.lock_location = (True, True, True)

    roll_disc = make_disc(
        "ROLL_DISC", collection, tilt_disc,
        ROLL_DISC_RADIUS, ROLL_DISC_THICKNESS, CYAN,
    )
    # Re-orient the nested roll stage after making tilt local-X neutral.  The
    # resulting roll disc is still X-Z in world space and roll remains local Y.
    roll_disc.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    roll_disc.lock_rotation = (True, False, True)
    roll_disc.lock_location = (True, True, True)

    roll_ring = make_hex_ring(
        "ROLL_HEX_RING", collection, roll_disc,
        ROLL_RING_OUTER_RADIUS, ROLL_RING_INNER_RADIUS,
        ROLL_RING_DEPTH, (0.0, -ROLL_DISC_TO_HEX, 0.0), BLUE,
    )
    roll_ring.lock_rotation = (False, False, False)
    roll_ring.lock_location = (False, False, False)

    # Independent deflection indicators: their origins are the evaluated hex
    # centers, not their local locations after parenting.
    bpy.context.view_layer.update()
    nodal_point = make_sphere(
        "CAMERA_NODAL_POINT", NODAL_POINT_WORLD, collection,
        YELLOW, radius=0.13,
    )
    readout = make_text(
        "NODAL_OFFSET_READOUT", "", READOUT_LOCATION, collection,
        WHITE, rotation=(math.radians(90.0), 0.0, 0.0),
    )
    readout.data.align_x = "LEFT"
    readout.data.size = READOUT_SIZE
    if hasattr(readout.data, "space_line"):
        readout.data.space_line = 1.05
    roll_axis_line = make_axis_cylinder(
        "ROLL_AXIS_CENTER_LINE", collection,
        roll_ring.matrix_world.translation, nodal_point.location, BLUE,
    )
    parent_at_current_world_transform(roll_axis_line, roll_ring)
    add_aim_constraint(roll_axis_line, nodal_point)
    tilt_axis_line = make_axis_cylinder(
        "TILT_AXIS_CENTER_LINE", collection,
        tilt_ring.matrix_world.translation, nodal_point.location, PURPLE,
    )
    parent_at_current_world_transform(tilt_axis_line, tilt_ring)
    add_aim_constraint(tilt_axis_line, nodal_point)
    pan_axis_line = make_axis_cylinder(
        "PAN_AXIS_CENTER_LINE", collection,
        pan_ring.matrix_world.translation, nodal_point.location, YELLOW,
    )
    parent_at_current_world_transform(pan_axis_line, pan_ring)
    add_aim_constraint(pan_axis_line, nodal_point)

    bpy.context.view_layer.update()
    bpy.app.handlers.depsgraph_update_post.append(update_nodal_offset_readout)
    update_nodal_offset_readout(bpy.context.scene, None)

    print("[LIMNMOCO SAVED-HIERARCHY ROTOR STUB]")
    print("Parenting: crane -> pan -> tilt -> roll, with hexes under discs")
    print("Roll axis: local Y")
    print("Roll disc plane: X-Z")
    print("Roll hex local offset: (0, -Y)", ROLL_DISC_TO_HEX)
    print("Roll disc thickness:", ROLL_DISC_THICKNESS)
    print("Roll ring radii:", ROLL_RING_INNER_RADIUS, ROLL_RING_OUTER_RADIUS)
    print("Tilt axis: local X")
    print("Tilt disc plane: Y-Z")
    print("Tilt hex local offset: (-X, 0, 0)", TILT_DISC_TO_HEX)
    print("Tilt disc thickness:", TILT_DISC_THICKNESS)
    print("Pan axis: local Z")
    print("Pan disc plane: X-Y")
    print("Pan hex local offset: (0, -Y)", PAN_DISC_TO_HEX)
    print("Pan disc thickness:", PAN_DISC_THICKNESS)
    print("Axis line world origins:", tuple(roll_axis_line.matrix_world.translation),
          tuple(tilt_axis_line.matrix_world.translation), tuple(pan_axis_line.matrix_world.translation))
    print("Axis line parents:", roll_axis_line.parent.name,
          tilt_axis_line.parent.name, pan_axis_line.parent.name)
    print("Camera nodal point:", tuple(nodal_point.location))
    print("Crane connection cube:", crane_connection.name)


build()
