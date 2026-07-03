import bpy
from ..rigs.limnmoco_crane import solve_limmoco_crane
from ..debug.report import solver_report
from ..debug.log import section
from ..blender.scene import get_collection, clear_generated, reset_collection
from ..blender.objects import ensure_control, draw_limmoco_crane_result
from ..blender.camera import ensure_camera, apply_camera_transform, draw_camera_axes
from ..blender.rig_visualizer import draw_limmoco_crane_body, draw_range_guides

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

def update_rig():
    print("")
    print("[UPDATE] update_rig()")
    print("")
    section("UPDATE LIMNMOCO CG RIG")

    col = get_collection()
    print("[UPDATE] Collection OK")
    control = ensure_control(col)
    print("[UPDATE] Control OK")
    cam = ensure_camera(col)
    print("[UPDATE] Camera OK")
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
    apply_camera_transform(cam, result)
    
    if p.show_solver_geometry:
        draw_limmoco_crane_result(result, col)

    if p.show_physical_crane:
        draw_limmoco_crane_body(result, col)

    if p.show_range_guides:
        draw_range_guides(result, p, col)

    if p.show_camera_axes:
        draw_camera_axes(result, col)
    
    solver_report(result)

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
        self.report({"INFO"}, "LIMNMOCO CG Rig updated")
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
    bl_description = "Delete generated LIMNMOCO objects and rebuild the rig"

    def execute(self, context):
        reset_collection()
        update_rig()
        self.report({"INFO"}, "LIMNMOCO CG Rig rebuilt")
        return {"FINISHED"}
