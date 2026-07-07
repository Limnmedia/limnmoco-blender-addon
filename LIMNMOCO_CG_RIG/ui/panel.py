import bpy


MAIN_PANEL_ID = "LIMNMOCO_PT_main_panel"


def get_control_props(context):
    control = bpy.data.objects.get("LIMN_CONTROL")

    if control is None or not hasattr(control, "limnmoco"):
        return None

    return control.limnmoco


class LIMNMOCO_PT_MainPanel(bpy.types.Panel):
    bl_label = "LIMNMOCO CG Rig Beta"
    bl_idname = MAIN_PANEL_ID
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LIMNMOCO"

    def draw(self, context):
        layout = self.layout
        p = get_control_props(context)

        if p is None:
            layout.operator("limnmoco.update_rig", text="Build LIMNMOCO Rig")
            return

        row = layout.row()
        row.operator("limnmoco.update_rig", text="Update")
        row.operator("limnmoco.rebuild_rig", text="Rebuild")

        live_text = "Live Update: ON" if p.live_update else "Live Update: OFF"
        layout.operator("limnmoco.toggle_live_update", text=live_text)

        box = layout.box()
        box.label(text="Solved LIMNMOCO Axes")
        box.label(text=f"Track: {p.solved_track:.4f}")
        box.label(text=f"Swing: {p.solved_swing:.4f} deg")
        box.label(text=f"Boom: {p.solved_boom:.4f} deg")
        box.label(text=f"Error: {p.error_length:.8f}")
        box.label(text=f"Limit Status: {p.limit_message}")


class LIMNMOCO_PT_ViewPanel(bpy.types.Panel):
    bl_label = "View"
    bl_idname = "LIMNMOCO_PT_view_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LIMNMOCO"
    bl_parent_id = MAIN_PANEL_ID
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        p = get_control_props(context)

        if p is None:
            layout.operator("limnmoco.update_rig", text="Build LIMNMOCO Rig")
            return

        live_box = layout.box()
        live_box.prop(p, "live_update")
        live_text = "Live Update: ON" if p.live_update else "Live Update: OFF"
        live_box.operator("limnmoco.toggle_live_update", text=live_text)

        layout.prop(p, "show_solver_geometry")
        layout.prop(p, "show_physical_crane")
        layout.prop(p, "show_camera_axes")
        layout.prop(p, "show_camera_axis_planes")
        layout.prop(p, "show_range_guides")
        layout.prop(p, "show_motion_envelope")
        layout.prop(p, "show_envelope_point_cloud")


class LIMNMOCO_PT_SolverPanel(bpy.types.Panel):
    bl_label = "Solver"
    bl_idname = "LIMNMOCO_PT_solver_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LIMNMOCO"
    bl_parent_id = MAIN_PANEL_ID

    def draw(self, context):
        layout = self.layout
        p = get_control_props(context)

        if p is None:
            layout.operator("limnmoco.update_rig", text="Build LIMNMOCO Rig")
            return

        box = layout.box()
        box.label(text="Virtual Translation")
        box.prop(p, "vtrack")
        box.prop(p, "vew")
        box.prop(p, "vheight")

        box = layout.box()
        box.label(text="Virtual Rotation")
        box.prop(p, "vpan")
        box.prop(p, "vtilt")
        box.prop(p, "vroll")

        box = layout.box()
        box.label(text="Camera / Nodal Offset")
        box.prop(p, "offset_x")
        box.prop(p, "offset_y")
        box.prop(p, "offset_z")


class LIMNMOCO_PT_CranePanel(bpy.types.Panel):
    bl_label = "Crane"
    bl_idname = "LIMNMOCO_PT_crane_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LIMNMOCO"
    bl_parent_id = MAIN_PANEL_ID
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        p = get_control_props(context)

        if p is None:
            layout.operator("limnmoco.update_rig", text="Build LIMNMOCO Rig")
            return

        box = layout.box()
        box.label(text="Rig Model")
        box.prop(p, "rig_model")
        box.label(text="v02 scope: LIMNMOCO Crane only.")

        box = layout.box()
        box.label(text="Geometry")
        box.prop(p, "boom_length")
        box.prop(p, "extension_length")

        box = layout.box()
        box.label(text="Display Limits")
        row = box.row()
        row.prop(p, "track_min")
        row.prop(p, "track_max")

        row = box.row()
        row.prop(p, "swing_min")
        row.prop(p, "swing_max")

        row = box.row()
        row.prop(p, "boom_min")
        row.prop(p, "boom_max")


class LIMNMOCO_PT_PrevizPanel(bpy.types.Panel):
    bl_label = "Previz"
    bl_idname = "LIMNMOCO_PT_previz_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LIMNMOCO"
    bl_parent_id = MAIN_PANEL_ID
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        p = get_control_props(context)

        if p is None:
            layout.operator("limnmoco.update_rig", text="Build LIMNMOCO Rig")
            return

        layout.operator("limnmoco.send_to_zero", text="Zero Out")

        layout.label(text="Move LIMNMOCO_RIG_ROOT to place crane in scene.")


print("[PANEL] Loaded")
