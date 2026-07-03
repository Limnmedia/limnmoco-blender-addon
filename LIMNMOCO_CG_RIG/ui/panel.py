import bpy

class LIMNMOCO_PT_MainPanel(bpy.types.Panel):
    bl_label = "LIMNMOCO CG Rig"
    bl_idname = "LIMNMOCO_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LIMNMOCO"

    def draw(self, context):
        layout = self.layout
        control = bpy.data.objects.get("LIMN_CONTROL")

        if control is None or not hasattr(control, "limnmoco"):
            layout.operator("limnmoco.update_rig", text="Build LIMNMOCO Rig")
            return

        p = control.limnmoco

        row = layout.row()
        row.operator("limnmoco.send_to_zero", text="Zero Out")
        row.operator("limnmoco.update_rig", text="Update")
        row.operator("limnmoco.rebuild_rig", text="Rebuild")

        box = layout.box()
        box.label(text="Viewport Layers")
        box.prop(p, "show_solver_geometry")
        box.prop(p, "show_physical_crane")
        box.prop(p, "show_camera_axes")
        box.prop(p, "show_range_guides")
        
        box = layout.box()
        box.label(text="Rig Model")
        box.prop(p, "rig_model")
        box.label(text="v02 scope: LIMNMOCO Crane only.")

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
        box.label(text="Crane Geometry")
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

        box = layout.box()
        box.label(text="Camera / Nodal Offset")
        box.prop(p, "offset_x")
        box.prop(p, "offset_y")
        box.prop(p, "offset_z")

        box = layout.box()
        box.label(text="Solved LIMNMOCO Axes")
        box.label(text=f"Track: {p.solved_track:.4f}")
        box.label(text=f"Swing: {p.solved_swing:.4f}°")
        box.label(text=f"Boom: {p.solved_boom:.4f}°")
        box.label(text=f"Error: {p.error_length:.8f}")

        box.label(text=f"Limit Status: {p.limit_message}")
        
print("[PANEL] Loaded")