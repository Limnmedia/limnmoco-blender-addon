"""Build a portable Blender add-on ZIP for LIMNMOCO_CG_RIG."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from typing import Iterable, List


ADDON_MODULE = "LIMNMOCO_CG_RIG"


def sorted_files(source_dir: Path) -> List[Path]:
    files = [
        path
        for path in source_dir.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".pyo"}
    ]
    return sorted(files, key=lambda path: sort_key(path.relative_to(source_dir)))


def sort_key(relative_path: Path) -> tuple:
    parts = relative_path.parts
    key = []
    for part in parts:
        key.append((part != "__init__.py", part.lower()))
    return tuple(key)


def build_zip(source_dir: Path, output_zip: Path) -> List[str]:
    source_dir = source_dir.resolve()
    output_zip = output_zip.resolve()

    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    output_zip.parent.mkdir(parents=True, exist_ok=True)
    entries: List[str] = []

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted_files(source_dir):
            arcname = (Path(ADDON_MODULE) / file.relative_to(source_dir)).as_posix()
            archive.write(file, arcname)
            entries.append(arcname)

    return entries


def print_listing(entries: Iterable[str]) -> None:
    print("Archive listing:")
    for entry in entries:
        print(entry)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("LIMNMOCO_CG_RIG"),
        help="Folder containing the add-on files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("releases") / "LIMNMOCO_CG_RIG_v0.3.2-beta.zip",
        help="ZIP file to write.",
    )
    args = parser.parse_args()

    entries = build_zip(args.source_dir, args.output)
    print(f"Built: {args.output}")
    print_listing(entries)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
