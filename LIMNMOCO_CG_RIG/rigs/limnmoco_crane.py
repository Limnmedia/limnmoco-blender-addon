import math
from mathutils import Vector

from ..core.transforms import rotation_matrix_from_virtual_axes
from ..core.result import RigSolveResult

print("[CRANE SOLVER] Loaded")

RIG_NAME = "LIMNMOCO Crane"


# ============================================================
# SMALL UTILITY
# ============================================================

def clamp(value, lo, hi):
    """
    Clamp a value between a low and high limit.

    This prevents asin() from receiving values slightly outside
    -1.0 to +1.0 because of either user input or floating point noise.
    """

    return max(lo, min(hi, value))


# ============================================================
# MAIN SOLVER
# ============================================================

def solve_limmoco_crane(
    vtrack,
    vew,
    vheight,
    vpan,
    vtilt,
    vroll,
    boom_length,
    extension_length,
    offset_x,
    offset_y,
    offset_z,
):
    """
    Solve the current supported rig:

        Swing / Boom / Track Crane

    This is the scoped v02 rig model.

    It is intentionally NOT trying to solve every possible
    camera support system yet.

    ------------------------------------------------------------
    VIRTUAL INPUTS
    ------------------------------------------------------------

    The virtual translation axes define the desired camera/nodal
    point in world space:

        VEW      -> X
        VTrack   -> Y
        VHeight  -> Z

    The virtual rotation axes define the desired camera orientation:

        VPan
        VTilt
        VRoll

    ------------------------------------------------------------
    PHYSICAL OUTPUTS
    ------------------------------------------------------------

    The solver produces physical-style rig values:

        Track position
        Swing angle
        Boom angle

    ------------------------------------------------------------
    MECHANICAL MODEL
    ------------------------------------------------------------

    The rig is modeled as:

        Track base
            ->
        Swing pivot
            ->
        Boom arm
            ->
        Level parallelogram extension
            ->
        Pan center / camera mount
            ->
        Camera nodal point

    The important assumption:

        The boom can pitch up and down,
        but the extension stays level.

    That means:

        The boom contributes vertical height.
        The boom contributes only its horizontal projection.
        The extension contributes full horizontal reach.
    """

    # --------------------------------------------------------
    # 1. Build virtual target position
    # --------------------------------------------------------
    print("[CRANE SOLVER] solve_limmoco_crane()")
    
    target = Vector((
        vew,       # X / East-West
        vtrack,    # Y / Track / Depth
        vheight,   # Z / Height
    ))
    print("[CRANE SOLVER] Target:", target)
    # --------------------------------------------------------
    # 2. Build virtual camera orientation
    # --------------------------------------------------------
 
    rotation = rotation_matrix_from_virtual_axes(
        vpan,
        vtilt,
        vroll,
    )
    # --------------------------------------------------------
    # 3. Convert camera/nodal offset into world space
    # --------------------------------------------------------

    offset_local = Vector((
        offset_x,
        offset_y,
        offset_z,
    ))

    offset_world = rotation @ offset_local
    print("[CRANE SOLVER] Rotation Built")
    # --------------------------------------------------------
    # 4. Solve for the pan-center target
    # --------------------------------------------------------
    #
    # The virtual target is the nodal/camera point.
    #
    # The crane mechanics do not directly place the nodal point.
    # They place the pan center / camera mount.
    #
    # Therefore we subtract the rotated camera offset to get the
    # pan center position the mechanism must solve for.
    #

    pan_target = target - offset_world

    # --------------------------------------------------------
    # 5. Read rig geometry
    # --------------------------------------------------------

    boom_len = max(0.001, boom_length)
    level_ext_len = extension_length

    # --------------------------------------------------------
    # 6. Solve boom angle from height
    # --------------------------------------------------------
    #
    # With the base at Z = 0:
    #
    #   pan_target.z = boom_len * sin(boom)
    #
    # Therefore:
    #
    #   boom = asin(pan_target.z / boom_len)
    #
    # If the target is physically too high or too low, clamp.
    #

    boom_ratio = clamp(
        pan_target.z / boom_len,
        -1.0,
        1.0,
    )

    boom_rad = math.asin(boom_ratio)
    print("[CRANE SOLVER] Boom:", math.degrees(boom_rad))
    # --------------------------------------------------------
    # 7. Compute horizontal reach
    # --------------------------------------------------------
    #
    # The boom's horizontal projection:
    #
    #   boom_len * cos(boom)
    #
    # The parallelogram extension stays level, so it contributes
    # its full length horizontally.
    #
    # Total reach from swing pivot to pan center:
    #
    #   horizontal_reach =
    #       boom horizontal projection
    #       + level extension length
    #

    boom_horizontal_projection = boom_len * math.cos(boom_rad)

    horizontal_reach = (
        boom_horizontal_projection
        + level_ext_len
    )

    if abs(horizontal_reach) < 0.000001:
        horizontal_reach = 0.000001

    # --------------------------------------------------------
    # 8. Solve swing angle from X
    # --------------------------------------------------------
    #
    #   pan_target.x = horizontal_reach * sin(swing)
    #
    # Therefore:
    #
    #   swing = asin(pan_target.x / horizontal_reach)
    #

    swing_ratio = clamp(
        pan_target.x / horizontal_reach,
        -1.0,
        1.0,
    )

    swing_rad = math.asin(swing_ratio)
    print("[CRANE SOLVER] Swing:", math.degrees(swing_rad))
    # --------------------------------------------------------
    # 9. Solve track position from Y
    # --------------------------------------------------------
    #
    #   pan_target.y =
    #       track
    #       + horizontal_reach * cos(swing)
    #
    # Therefore:
    #
    #   track =
    #       pan_target.y
    #       - horizontal_reach * cos(swing)
    #

    track = (
        pan_target.y
        - horizontal_reach * math.cos(swing_rad)
    )

    # --------------------------------------------------------
    # 10. Reconstruct solved physical points
    # --------------------------------------------------------

    base = Vector((
        0,
        track,
        0,
    ))

    arm_tip = Vector((
        boom_len
        * math.sin(swing_rad)
        * math.cos(boom_rad),

        track
        + boom_len
        * math.cos(swing_rad)
        * math.cos(boom_rad),

        boom_len
        * math.sin(boom_rad),
    ))

    level_extension_vector = Vector((
        level_ext_len * math.sin(swing_rad),
        level_ext_len * math.cos(swing_rad),
        0,
    ))

    pan_center = arm_tip + level_extension_vector

    nodal = pan_center + offset_world

    error = target - nodal

    # --------------------------------------------------------
    # 11. Return structured result
    # --------------------------------------------------------
    print("[CRANE SOLVER] Returning Result")
    return RigSolveResult(
        rig_name=RIG_NAME,
        target=target,
        rotation=rotation,
        offset_world=offset_world,
        pan_target=pan_target,

        base=base,
        arm_tip=arm_tip,
        pan_center=pan_center,
        nodal=nodal,

        error=error,

        track=track,
        swing_deg=math.degrees(swing_rad),
        boom_deg=math.degrees(boom_rad),
    )