# LIMNMOCO Blender Add-on

Blender reference rig and solver tooling for the LIMNMOCO motion-control crane.

This repository packages the `LIMNMOCO_CG_RIG` add-on as a focused Blender integration, separate from the firmware repository. The add-on provides a viewport-side control panel for virtual camera axes, crane geometry, nodal offset, display limits, and solved physical crane axes.

## Current Scope

Version `0.2.2` is a reference solver build for the LIMNMOCO Swing-Boom-Track crane model.

It supports:

- Virtual translation axes: `VTrack`, `VEW`, `VHeight`
- Virtual rotation axes: `VPan`, `VTilt`, `VRoll`
- Crane geometry controls: boom length and level extension length
- Camera / nodal offset controls
- Solved physical outputs: track, swing, and boom
- Viewport visualization for solver geometry, physical crane body, camera axes, and range guides

This add-on is not the firmware. It is a CG/reference environment for developing, validating, and communicating the rig model before changes are moved into embedded code.

## Installation

1. Open Blender 4.x.
2. Go to `Edit > Preferences > Add-ons`.
3. Choose `Install...`.
4. Select `releases/LIMNMOCO_CG_RIG_v0.2.2.zip`.
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
  LIMNMOCO_CG_RIG_v0.2.2.zip
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

## Development Notes

This repository intentionally stays separate from `limnmoco`, the firmware repository. Firmware ports should copy or translate the solver behavior only after the Blender reference model has been reviewed and tested.

Before using solver behavior on hardware:

- Run the solver in Blender with representative crane values.
- Compare solved Track/Swing/Boom values against expected mechanical ranges.
- Review nodal offset conventions and axis signs.
- Port the math into a firmware spike branch with a host-side IK test harness.

## License

Copyright (c) 2026 Limnmedia LLC.

This Blender add-on is licensed under the GNU General Public License, version 3 or later (`GPL-3.0-or-later`), in keeping with Blender add-on distribution expectations for Python code that integrates with Blender's `bpy` API.

See `LICENSE.md` for details.
