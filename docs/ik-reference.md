# IK Reference

This document summarizes the current LIMNMOCO Blender reference solver so it can be reviewed before firmware porting.

## Solver

Source:

```text
LIMNMOCO_CG_RIG/rigs/limnmoco_crane.py
```

Function:

```python
solve_limmoco_crane(
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
)
```

## Virtual Inputs

The virtual translation axes describe the desired camera/nodal point in world space:

- `VEW`: X / east-west
- `VTrack`: Y / track/depth
- `VHeight`: Z / height

The virtual rotation axes describe camera orientation:

- `VPan`: rotation around Z
- `VTilt`: rotation around X
- `VRoll`: rotation around Y

Rotation composition is defined in:

```text
LIMNMOCO_CG_RIG/core/transforms.py
```

The current order is:

```text
Rz(VPan) * Rx(VTilt) * Ry(VRoll)
```

## Mechanical Model

The current scoped rig model is:

```text
Track base
  -> Swing pivot
  -> Boom arm
  -> Level parallelogram extension
  -> Pan center / camera mount
  -> Camera nodal point
```

The key assumption is that the boom pitches up/down while the extension stays level.

Consequences:

- Boom contributes vertical height.
- Boom contributes horizontal reach through its horizontal projection.
- Level extension contributes full horizontal reach.

## Solve Steps

1. Build target vector from virtual translation axes.
2. Build virtual orientation matrix from virtual rotation axes.
3. Rotate the local camera/nodal offset into world space.
4. Subtract the rotated offset from the nodal target to get the pan-center target.
5. Solve boom angle from height:

```text
boom = asin(pan_target.z / boom_length)
```

6. Compute horizontal reach:

```text
horizontal_reach = boom_length * cos(boom) + extension_length
```

7. Solve swing from east-west offset:

```text
swing = asin(pan_target.x / horizontal_reach)
```

8. Solve track from depth:

```text
track = pan_target.y - horizontal_reach * cos(swing)
```

9. Reconstruct base, arm tip, pan center, and nodal point.
10. Report reconstruction error.

## Firmware Porting Notes

For the firmware spike, keep the first port deliberately narrow:

- Port the math into the legacy `m7` virtual path.
- Preserve the current axis/sign conventions unless hardware testing proves otherwise.
- Add a standalone host-side IK test harness before flashing hardware.
- Validate motor indices and scale conversions before calling motion commands.
- Treat the Blender solver as the reference behavior, not as production firmware code.

Open items for developer review:

- Confirm units expected by firmware versus Blender scene units.
- Confirm sign conventions for swing, boom, track, pan, tilt, and roll.
- Confirm nodal offset orientation and physical measurement origin.
- Confirm mechanical limits and clamp behavior.
- Decide whether unreachable targets should clamp, reject, or report an error.
