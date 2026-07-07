"""Install-time diagnostics for LIMNMOCO."""

from __future__ import annotations

import importlib
import platform
import sys
from pathlib import Path
from typing import Any, Dict


EXPECTED_SUBPACKAGES = ("blender", "core", "debug", "rigs", "ui")


def _version_text(value: Any) -> str:
    if isinstance(value, (tuple, list)):
        return ".".join(str(part) for part in value)
    return str(value)


def print_install_check(module_name: str, module_file: str, bl_info: Dict[str, Any], bpy_module: Any) -> None:
    """Print harmless diagnostics during register()."""
    print(f"[LIMNMOCO][INSTALL] Version: {_version_text(bl_info.get('version', 'unknown'))}")
    print(f"[LIMNMOCO][INSTALL] Blender: {_version_text(getattr(getattr(bpy_module, 'app', None), 'version', 'unknown'))}")
    print(f"[LIMNMOCO][INSTALL] Python: {sys.version.split()[0]}")
    print(f"[LIMNMOCO][INSTALL] Platform: {platform.system().lower()}")
    print(f"[LIMNMOCO][INSTALL] Module: {module_name}")
    print(f"[LIMNMOCO][INSTALL] File: {Path(module_file)}")

    for subpackage in EXPECTED_SUBPACKAGES:
        import_name = f"{module_name}.{subpackage}"
        try:
            importlib.import_module(import_name)
        except Exception as exc:
            print(f"[LIMNMOCO][INSTALL] Import FAILED: {import_name}: {type(exc).__name__}: {exc}")
        else:
            print(f"[LIMNMOCO][INSTALL] Import OK: {import_name}")
