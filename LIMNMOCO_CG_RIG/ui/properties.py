import bpy
from bpy.props import FloatProperty, EnumProperty, StringProperty
from bpy.props import BoolProperty



class LIMNMOCOProperties(bpy.types.PropertyGroup):
    rig_model: EnumProperty(
        name="Rig Model",
        description="v02 implements LIMNMOCO Crane only",
        items=[
            ("LIMNMOCO_CRANE", "LIMNMOCO Crane", "The scoped v02 crane model"),
        ],
        default="LIMNMOCO_CRANE",
    )
    show_solver_geometry: BoolProperty(name="Show Solver Geometry", default=True)
    show_physical_crane: BoolProperty(name="Show Physical Crane", default=True)
    show_camera_axes: BoolProperty(name="Show Camera Axes", default=True)
    show_range_guides: BoolProperty(name="Show Range Guides", default=True)

    vtrack: FloatProperty(name="VTrack / Y", default=8.0)
    vew: FloatProperty(name="VEW / X", default=2.0)
    vheight: FloatProperty(name="VHeight / Z", default=3.0)

    vpan: FloatProperty(name="VPan", default=0.0)
    vtilt: FloatProperty(name="VTilt", default=0.0)
    vroll: FloatProperty(name="VRoll", default=0.0)

    boom_length: FloatProperty(name="Boom Length", default=10.0, min=0.001)
    track_min: FloatProperty(name="Track Min", default=-25.0)
    track_max: FloatProperty(name="Track Max", default=25.0)

    swing_min: FloatProperty(name="Swing Min", default=-70.0)
    swing_max: FloatProperty(name="Swing Max", default=70.0)

    boom_min: FloatProperty(name="Boom Min", default=-20.0)
    boom_max: FloatProperty(name="Boom Max", default=70.0)
    extension_length: FloatProperty(name="Level Extension", default=2.8)

    offset_x: FloatProperty(name="Camera Offset X", default=0.0)
    offset_y: FloatProperty(name="Camera Offset Y", default=0.0)
    offset_z: FloatProperty(name="Camera Offset Z", default=0.0)

    solved_track: FloatProperty(name="Solved Track", default=0.0)
    solved_swing: FloatProperty(name="Solved Swing", default=0.0)
    solved_boom: FloatProperty(name="Solved Boom", default=0.0)
    error_length: FloatProperty(name="Error", default=0.0)
    limit_status: FloatProperty(name="Limit Status", default=0.0)
    limit_message: StringProperty(name="Limit Message", default="OK")
    

    
    print("[PROPERTIES] Loaded")