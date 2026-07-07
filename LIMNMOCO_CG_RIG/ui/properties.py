import bpy
from bpy.props import FloatProperty, EnumProperty, StringProperty
from bpy.props import BoolProperty


_LIVE_UPDATE_RUNNING = False


def live_update_if_enabled(self, context):
    global _LIVE_UPDATE_RUNNING

    if _LIVE_UPDATE_RUNNING or not self.live_update:
        return

    _LIVE_UPDATE_RUNNING = True

    try:
        self.show_motion_envelope = False
        self.show_envelope_point_cloud = False

        from .operators import update_rig
        update_rig(select_control=False)
    finally:
        _LIVE_UPDATE_RUNNING = False


def visual_update_if_enabled(self, context):
    global _LIVE_UPDATE_RUNNING

    if _LIVE_UPDATE_RUNNING or not self.live_update:
        return

    _LIVE_UPDATE_RUNNING = True

    try:
        from .operators import update_rig
        update_rig(select_control=False)
    finally:
        _LIVE_UPDATE_RUNNING = False


class LIMNMOCOProperties(bpy.types.PropertyGroup):
    rig_model: EnumProperty(
        name="Rig Model",
        description="v02 implements LIMNMOCO Crane only",
        items=[
            ("LIMNMOCO_CRANE", "LIMNMOCO Crane", "The scoped v02 crane model"),
        ],
        default="LIMNMOCO_CRANE",
    )
    show_solver_geometry: BoolProperty(name="Show Solver Geometry", default=True, update=visual_update_if_enabled)
    show_physical_crane: BoolProperty(name="Show Abstract Crane Mechanics", default=True, update=visual_update_if_enabled)
    show_camera_axes: BoolProperty(name="Show Camera Axes", default=True, update=visual_update_if_enabled)
    show_camera_axis_planes: BoolProperty(name="Show Camera Axis Planes", default=False, update=visual_update_if_enabled)
    show_range_guides: BoolProperty(name="Show Range Guides", default=True, update=visual_update_if_enabled)
    show_motion_envelope: BoolProperty(name="Show Envelope", default=False, update=visual_update_if_enabled)
    show_envelope_point_cloud: BoolProperty(name="Show Point Cloud", default=False, update=visual_update_if_enabled)
    show_point_labels: BoolProperty(name="Show Point Labels", default=False, update=visual_update_if_enabled)
    live_update: BoolProperty(name="Live Update", default=False)

    vtrack: FloatProperty(name="VTrack / Y", default=8.0, update=live_update_if_enabled)
    vew: FloatProperty(name="VEW / X", default=2.0, update=live_update_if_enabled)
    vheight: FloatProperty(name="VHeight / Z", default=3.0, update=live_update_if_enabled)

    vpan: FloatProperty(name="VPan", default=0.0, update=live_update_if_enabled)
    vtilt: FloatProperty(name="VTilt", default=0.0, update=live_update_if_enabled)
    vroll: FloatProperty(name="VRoll", default=0.0, update=live_update_if_enabled)

    boom_length: FloatProperty(name="Boom Length", default=85.77, min=0.001, update=live_update_if_enabled)
    track_min: FloatProperty(name="Track Min", default=-75.0, update=live_update_if_enabled)
    track_max: FloatProperty(name="Track Max", default=25.0, update=live_update_if_enabled)

    swing_min: FloatProperty(name="Swing Min", default=-70.0, update=live_update_if_enabled)
    swing_max: FloatProperty(name="Swing Max", default=70.0, update=live_update_if_enabled)

    boom_min: FloatProperty(name="Boom Min", default=-45.0, update=live_update_if_enabled)
    boom_max: FloatProperty(name="Boom Max", default=45.0, update=live_update_if_enabled)
    extension_length: FloatProperty(name="Level Extension", default=2.8, update=live_update_if_enabled)

    offset_x: FloatProperty(name="Camera Offset X", default=0.0, update=live_update_if_enabled)
    offset_y: FloatProperty(name="Camera Offset Y", default=0.0, update=live_update_if_enabled)
    offset_z: FloatProperty(name="Camera Offset Z", default=0.0, update=live_update_if_enabled)

    solved_track: FloatProperty(name="Solved Track", default=0.0)
    solved_swing: FloatProperty(name="Solved Swing", default=0.0)
    solved_boom: FloatProperty(name="Solved Boom", default=0.0)
    error_length: FloatProperty(name="Error", default=0.0)
    limit_status: FloatProperty(name="Limit Status", default=0.0)
    limit_message: StringProperty(name="Limit Message", default="OK")
    
    
    

    
    print("[PROPERTIES] Loaded")
