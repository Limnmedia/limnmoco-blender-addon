import bpy
from ..rigs.limnmoco_crane import solve_limmoco_crane
from ..debug.report import solver_report
from ..debug.log import section
from ..blender.scene import get_collection, clear_generated, reset_collection, ensure_rig_root, parent_to_root
from ..blender.objects import ensure_control, draw_limmoco_crane_result
from ..blender.camera import ensure_camera, draw_camera_axes
from ..blender.rig_controls import ensure_rig_controls, drive_rig_controls, parent_generated_visuals
from ..blender.rig_visualizer import (
    draw_limmoco_crane_body,
    draw_range_guides,
    draw_reach_envelope,
    draw_camera_axis_planes,
)

print("[OPERATORS] Loaded")

def solve_selected_rig(p):
    return solve_limmoco_crane(
        p.vtrack,
        p.vew,
        p.vheight,
        p.vpan,
        p.vtilt,
        p.vroll,
        p.boom_length,
        p.extension_length,
        p.offset_x,
        p.offset_y,
        p.offset_z,
    )


def reset_props_to_launch_defaults(p):
    """
    Reset user-facing rig settings to the same defaults used on launch.

    Live Update is disabled first so this reset does not trigger a solve
    for every individual property assignment.
    """

    p.live_update = False

    p.show_solver_geometry = True
    p.show_physical_crane = True
    p.show_camera_axes = True
    p.show_camera_axis_planes = False
    p.show_range_guides = True
    p.show_motion_envelope = False
    p.show_envelope_point_cloud = False
    p.show_point_labels = False

    p.rig_model = "LIMNMOCO_CRANE"

    p.vtrack = 8.0
    p.vew = 2.0
    p.vheight = 3.0

    p.vpan = 0.0
    p.vtilt = 0.0
    p.vroll = 0.0

    p.boom_length = 85.77
    p.extension_length = 2.8

    p.track_min = -75.0
    p.track_max = 25.0
    p.swing_min = -70.0
    p.swing_max = 70.0
    p.boom_min = -45.0
    p.boom_max = 45.0

    p.offset_x = 0.0
    p.offset_y = 0.0
    p.offset_z = 0.0

    p.solved_track = 0.0
    p.solved_swing = 0.0
    p.solved_boom = 0.0
    p.error_length = 0.0
    p.limit_status = 0.0
    p.limit_message = "OK"


def reset_object_transform(obj):
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)


def update_rig(select_control=True):
    print("")
    print("[UPDATE] update_rig()")
    print("")

    section("UPDATE LIMNMOCO CG RIG")

    col = get_collection()
    print("[UPDATE] Collection OK")

    root = ensure_rig_root(col)
    print("[UPDATE] Rig Root OK")

    control = ensure_control(col)
    print("[UPDATE] Control OK")

    cam = ensure_camera(col)
    print("[UPDATE] Camera OK")

    controls = ensure_rig_controls(root, cam, col)
    print("[UPDATE] Rig Controls OK")

    # Parent persistent objects early.
    parent_to_root(control, root)

    p = control.limnmoco

    clear_generated(col)
    print("[UPDATE] Beginning Solve")

    result = solve_selected_rig(p)

    p.solved_track = result.track
    p.solved_swing = result.swing_deg
    p.solved_boom = result.boom_deg
    p.error_length = result.error.length

    limit_flags = []

    if result.track < p.track_min or result.track > p.track_max:
        limit_flags.append("TRACK")

    if result.swing_deg < p.swing_min or result.swing_deg > p.swing_max:
        limit_flags.append("SWING")

    if result.boom_deg < p.boom_min or result.boom_deg > p.boom_max:
        limit_flags.append("BOOM")

    if limit_flags:
        p.limit_status = 1.0
        p.limit_message = " + ".join(limit_flags)
    else:
        p.limit_status = 0.0
        p.limit_message = "OK"

    print("[UPDATE] Limit Status:", p.limit_message)

    print("[UPDATE] Solve Complete")
    drive_rig_controls(controls, cam, result, p)

    if p.show_solver_geometry:
        draw_limmoco_crane_result(result, col, show_labels=False)

    if p.show_physical_crane:
        draw_limmoco_crane_body(result, p, col)

    if p.show_range_guides:
        draw_range_guides(result, p, col)

    if p.show_motion_envelope or p.show_envelope_point_cloud:
        draw_reach_envelope(
            result,
            p,
            col,
            show_points=p.show_envelope_point_cloud,
        )

    if p.show_camera_axes:
        draw_camera_axes(result, col)

    if p.show_camera_axis_planes:
        draw_camera_axis_planes(result, p, col)

    # Parent generated objects AFTER they have been created.
    print("[UPDATE] Parenting generated visualization to rig controls")
    parent_generated_visuals(col, root, controls)

    solver_report(result)

    if select_control:
        bpy.ops.object.select_all(action="DESELECT")
        control.select_set(True)
        bpy.context.view_layer.objects.active = control

    return result

class LIMNMOCO_OT_UpdateRig(bpy.types.Operator):
    bl_idname = "limnmoco.update_rig"
    bl_label = "Update LIMNMOCO CG Rig"
    bl_description = "Solve the LIMNMOCO crane and update the CG rig"

    def execute(self, context):
        update_rig()
        control = bpy.data.objects.get("LIMN_CONTROL")

        if control is not None and hasattr(control, "limnmoco"):
            control.limnmoco.live_update = True

        self.report({"INFO"}, "LIMNMOCO CG Rig updated")
        return {"FINISHED"}


class LIMNMOCO_OT_ToggleLiveUpdate(bpy.types.Operator):
    bl_idname = "limnmoco.toggle_live_update"
    bl_label = "Toggle Live Update"
    bl_description = "Toggle automatic rig updates when solver values change"

    def execute(self, context):
        col = get_collection()
        control = ensure_control(col)
        p = control.limnmoco

        if not p.live_update:
            p.show_motion_envelope = False
            p.show_envelope_point_cloud = False
            p.live_update = True
            update_rig(select_control=False)
            self.report({"INFO"}, "LIMNMOCO Live Update enabled")
        else:
            p.live_update = False
            self.report({"INFO"}, "LIMNMOCO Live Update disabled")

        return {"FINISHED"}


class LIMNMOCO_OT_SendToZero(bpy.types.Operator):
    bl_idname = "limnmoco.send_to_zero"
    bl_label = "Send To Zero"
    bl_description = "Set virtual camera translation and rotation axes to zero"

    def execute(self, context):
        col = get_collection()
        control = ensure_control(col)
        p = control.limnmoco

        print("[ZERO] Sending virtual axes to zero")

        p.vtrack = 0.0
        p.vew = 0.0
        p.vheight = 0.0

        p.vpan = 0.0
        p.vtilt = 0.0
        p.vroll = 0.0

        update_rig()

        self.report({"INFO"}, "LIMNMOCO sent to zero")
        return {"FINISHED"}
    
class LIMNMOCO_OT_RebuildRig(bpy.types.Operator):
    bl_idname = "limnmoco.rebuild_rig"
    bl_label = "Rebuild Rig"
    bl_description = "Reset LIMNMOCO settings to launch defaults and rebuild the rig"

    def execute(self, context):
        col = get_collection()
        root = ensure_rig_root(col)
        control = ensure_control(col)
        reset_props_to_launch_defaults(control.limnmoco)
        reset_object_transform(root)
        reset_collection()
        update_rig()
        control.limnmoco.live_update = True
        self.report({"INFO"}, "LIMNMOCO CG Rig reset and rebuilt")
        return {"FINISHED"}
