from .log import section, solver, warning

def fmt_vec(v):
    return f"X {v.x: .4f} | Y {v.y: .4f} | Z {v.z: .4f}"

def solver_report(result):
    section(f"SOLVER REPORT - {result.rig_name}")
    solver("TARGET       ", fmt_vec(result.target))
    solver("PAN TARGET   ", fmt_vec(result.pan_target))
    solver("OFFSET WORLD ", fmt_vec(result.offset_world))
    solver("")
    solver("TRACK        ", f"{result.track: .4f}")
    solver("SWING        ", f"{result.swing_deg: .4f} deg")
    solver("BOOM         ", f"{result.boom_deg: .4f} deg")
    solver("")
    solver("BASE         ", fmt_vec(result.base))
    solver("ARM TIP      ", fmt_vec(result.arm_tip))
    solver("PAN CENTER   ", fmt_vec(result.pan_center))
    solver("NODAL        ", fmt_vec(result.nodal))
    solver("")
    solver("ERROR LENGTH ", f"{result.error.length: .8f}")
    if result.error.length > 0.001:
        warning("Solver error is larger than expected.")
