# LIMNMOCO Blender Add-on

LIMNMOCO CG Rig is a Blender add-on for visualizing and testing the LIMNMOCO motion-control crane model in a virtual camera workflow. It provides a View3D sidebar panel for positioning a virtual camera target, solving the current Swing-Boom-Track crane model, and displaying the resulting Track, Swing, and Boom values with supporting viewport geometry.

## About

The LIMNMOCO CG Rig add-on is a reference solver and visualization tool for developing LIMNMOCO motion-control workflows inside Blender. It lets artists and technical users describe a desired virtual camera position using LIMNMOCO-style virtual axes, then solves a scoped physical crane model and draws the result in the Blender scene.

The current add-on focuses on a single rig model: the LIMNMOCO Swing-Boom-Track crane. It supports virtual translation, virtual rotation, crane geometry values, camera/nodal offset, display limits, solved physical axes, and viewport visualization. The solver is intended as a practical reference for layout, validation, and future firmware work rather than a complete hardware-control system.

## Features

- Blender 4.x add-on with a `LIMNMOCO` View3D sidebar panel
- Builds and updates a LIMNMOCO CG rig in the current scene
- Supports the current `LIMNMOCO Crane` rig model
- Virtual translation controls:
  - `VTrack / Y`
  - `VEW / X`
  - `VHeight / Z`
- Virtual rotation controls:
  - `VPan`
  - `VTilt`
  - `VRoll`
- Crane geometry controls:
  - Boom Length
  - Level Extension
- Camera / nodal offset controls:
  - Camera Offset X
  - Camera Offset Y
  - Camera Offset Z
- Solver output display:
  - Solved Track
  - Solved Swing
  - Solved Boom
  - Reconstruction Error
  - Limit Status
- Optional viewport layers:
  - Solver Geometry
  - Physical Crane
  - Camera Axes
  - Range Guides
- Scene operators:
  - Build / Update LIMNMOCO Rig
  - Zero Out virtual axes
  - Rebuild generated rig objects
- Reference IK-style solve for the Swing-Boom-Track crane:
  - Converts virtual camera target and offset into pan-center target
  - Solves boom from height
  - Solves swing from east-west offset
  - Solves track from depth
  - Reconstructs solved points and reports error

## Workflow

Install and enable the add-on in Blender, then open the `LIMNMOCO` tab in the 3D View sidebar. Use `Build LIMNMOCO Rig` to create the control object, camera, and generated visualization objects.

From there, adjust the virtual translation and rotation values to describe the desired camera position and orientation. The add-on solves the scoped LIMNMOCO crane model and updates the scene with the calculated Track, Swing, and Boom values. The viewport layers can be toggled to show solver geometry, physical crane visualization, camera axes, and range guides.

The add-on is useful for checking whether a virtual camera layout produces reasonable physical crane values before translating the solver behavior into firmware or testing on hardware.

## Project Purpose

LIMNMOCO sits between physical motion-control hardware, stop-motion production workflows, Dragonframe/Kuper-style axis thinking, virtual camera layout, and Blender visualization. This add-on provides a practical bridge between those domains: it gives the team a visible reference model for how virtual camera intent maps onto physical crane axes.

The current source represents the following axis conventions directly:

- `VEW` maps to world X / east-west
- `VTrack` maps to world Y / track/depth
- `VHeight` maps to world Z / height
- `VPan` rotates around Z
- `VTilt` rotates around X
- `VRoll` rotates around Y
- Blender camera orientation is adapted from the LIMNMOCO virtual rotation convention

## Installation

1. Open Blender 4.x.
2. Go to `Edit > Preferences > Add-ons`.
3. Choose `Install...`.
4. Select `releases/LIMNMOCO_CG_RIG_v0.3.1-beta.zip`.
5. Enable `LIMNMOCO CG Rig`.
6. Open the 3D View sidebar and use the `LIMNMOCO` tab.

## Repository Layout

```text
LIMNMOCO_CG_RIG/
  blender/     Blender object, camera, scene, material, and visualizer helpers
  core/        Shared transform and result structures
  debug/       Console/report helpers
  rigs/        Crane solver implementation
  ui/          Blender panel, properties, and operators
docs/
  ik-reference.md
releases/
  LIMNMOCO_CG_RIG_v0.3.1-beta.zip
```

## Solver Reference

The primary solver entry point is:

```text
LIMNMOCO_CG_RIG/rigs/limnmoco_crane.py
```

The solver maps virtual camera intent into physical crane axes:

```text
virtual target + orientation + geometry -> track, swing, boom
```

See `docs/ik-reference.md` for the current math model and firmware-porting notes.

## Current Development Notes

This repository intentionally stays separate from `limnmoco`, the firmware repository. Firmware ports should copy or translate the solver behavior only after the Blender reference model has been reviewed and tested.

Before using solver behavior on hardware:

- Run the solver in Blender with representative crane values.
- Compare solved Track/Swing/Boom values against expected mechanical ranges.
- Review nodal offset conventions and axis signs.
- Port the math into a firmware spike branch with a host-side IK test harness.

Additional notes:

- The add-on is labeled in source as `v0.3.1` beta.
- Only the `LIMNMOCO Crane` rig model is currently exposed in the UI.
- Range guides are visual aids; they do not physically constrain or clamp the rig.
- Limit status is reported in the UI when solved Track, Swing, or Boom values fall outside configured display limits.
- The code contains extensive console logging and debug print output.
- The solver currently clamps some trigonometric inputs to avoid invalid `asin()` calls, so unreachable targets may produce clamped solve values rather than a hard failure.
- The add-on does not currently send commands to hardware.
- The add-on does not currently communicate with Dragonframe, Kuper, or the LIMNMOCO firmware directly.

## License

Copyright (c) 2026 Limnmedia LLC.

This Blender add-on is licensed under the GNU General Public License, version 3 or later (`GPL-3.0-or-later`), in keeping with Blender add-on distribution expectations for Python code that integrates with Blender's `bpy` API.

See `LICENSE.md` for details.
