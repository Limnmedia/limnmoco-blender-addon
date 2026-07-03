from dataclasses import dataclass
from mathutils import Vector, Matrix

@dataclass
class RigSolveResult:
    rig_name: str
    target: Vector
    rotation: Matrix
    offset_world: Vector
    pan_target: Vector
    base: Vector
    arm_tip: Vector
    pan_center: Vector
    nodal: Vector
    error: Vector
    track: float
    swing_deg: float
    boom_deg: float
