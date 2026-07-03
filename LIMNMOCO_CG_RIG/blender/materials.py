import bpy

print("[MATERIALS] Loaded")


LIMN_RED = (0.894, 0.000, 0.169, 1.0)
LIMN_BLUE = (0.000, 0.278, 0.733, 1.0)
LIMN_YELLOW = (0.996, 0.820, 0.255, 1.0)
LIMN_BLACK = (0.000, 0.000, 0.000, 1.0)
LIMN_WHITE = (1.000, 1.000, 1.000, 1.0)
LIMN_PURPLE = (0.500, 0.250, 0.800, 1.0)

LIMN_LIGHT_RED = (1.000, 0.450, 0.520, 1.0)
LIMN_LIGHT_BLUE = (0.380, 0.600, 1.000, 1.0)
LIMN_LIGHT_YELLOW = (1.000, 0.920, 0.500, 1.0)
LIMN_GRAY = (0.500, 0.500, 0.500, 1.0)

def make_simple_material(name, color):
    mat_name = f"{name}_MAT"

    mat = bpy.data.materials.get(mat_name)

    if mat is None:
        mat = bpy.data.materials.new(mat_name)

    mat.use_nodes = True

    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    if bsdf:
        bsdf.inputs["Base Color"].default_value = color

        # Transparency
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = color[3]

    mat.blend_method = 'BLEND'
    mat.shadow_method = 'NONE'

    mat.diffuse_color = color

    return mat

def get_material(name, color):
    print("[MATERIALS] Get/Create:", name, color)

    mat = bpy.data.materials.get(name)

    if mat is None:
        mat = bpy.data.materials.new(name)

    # Force reset so old white node settings do not survive reloads.
    mat.use_nodes = False
    mat.diffuse_color = color

    return mat


def assign_material(obj, material):
    print("[COLOR] Setting object color", material.diffuse_color, "on", obj.name)

    obj.color = material.diffuse_color

    if hasattr(obj, "active_material"):
        obj.active_material = None


def mat_target():
    return get_material("LIMN_Target_Purple", LIMN_PURPLE)

def mat_base():
    return get_material("LIMN_Base_Black", LIMN_BLACK)

def mat_arm_tip():
    return get_material("LIMN_ArmTip_Red", LIMN_RED)

def mat_pan_center():
    return get_material("LIMN_PanCenter_Blue", LIMN_BLUE)

def mat_nodal():
    return get_material("LIMN_Nodal_Yellow", LIMN_YELLOW)

def mat_axis_x():
    return get_material("LIMN_Axis_X_Red", LIMN_RED)

def mat_axis_y():
    return get_material("LIMN_Axis_Y_Blue", LIMN_BLUE)

def mat_axis_z():
    return get_material("LIMN_Axis_Z_Yellow", LIMN_YELLOW)

def mat_crane_structure():
    return get_material("LIMN_Crane_Structure_Black", LIMN_BLACK)

def mat_camera_virtual():
    return get_material("LIMN_Camera_Virtual_Purple", LIMN_PURPLE)

def mat_range_track():
    return get_material("LIMN_Range_Track_LightBlue", LIMN_LIGHT_BLUE)

def mat_range_swing():
    return get_material("LIMN_Range_Swing_LightRed", LIMN_LIGHT_RED)

def mat_range_boom():
    return get_material("LIMN_Range_Boom_LightYellow", LIMN_LIGHT_YELLOW)

def mat_error():
    return get_material("LIMN_Error_Red", LIMN_RED)

def mat_default():
    return get_material("LIMN_Default_Gray", LIMN_GRAY)