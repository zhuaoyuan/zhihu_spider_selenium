#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
from pathlib import Path

DATE_RE = re.compile(r"^(\d{8})_")


def parse_yyyymmdd(value: str) -> dt.date:
    try:
        return dt.datetime.strptime(value, "%Y%m%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid date '{value}', expected YYYYMMDD") from exc


def iter_md_files(base_dirs: list[Path]) -> list[Path]:
    files: list[Path] = []
    for base in base_dirs:
        if not base.exists():
            continue
        files.extend(base.rglob("*.md"))
    return files


def extract_file_date(path: Path) -> dt.date | None:
    m = DATE_RE.match(path.name)
    if not m:
        return None
    try:
        return dt.datetime.strptime(m.group(1), "%Y%m%d").date()
    except ValueError:
        return None


def flatten_name(data_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(data_root)
    parts = list(rel.parts)
    return "_".join(parts)


def unique_target(path: Path) -> Path:
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    idx = 1
    while True:
        candidate = path.with_name(f"{stem}__dup{idx}{suffix}")
        if not candidate.exists():
            return candidate
        idx += 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Copy md files from data/column and data/user whose filename date "
            "(YYYYMMDD prefix) is >= fromdate, into flattened newest_{from}_{end} directory."
        )
    )
    parser.add_argument("fromdate", type=parse_yyyymmdd, help="start date (YYYYMMDD), inclusive")
    parser.add_argument(
        "--data-root",
        default="data",
        type=Path,
        help="data root path (default: data)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show selected files without copying",
    )
    args = parser.parse_args()

    data_root = args.data_root.resolve()
    sources = [data_root / "column", data_root / "user"]

    all_md = iter_md_files(sources)
    selected: list[tuple[Path, dt.date]] = []

    for md in all_md:
        file_date = extract_file_date(md)
        if file_date is None:
            continue
        if file_date >= args.fromdate:
            selected.append((md, file_date))

    if not selected:
        print(f"No matching files found for >= {args.fromdate.strftime('%Y%m%d')}")
        return 0

    enddate = max(d for _, d in selected)
    out_dir = data_root / f"newest_{args.fromdate.strftime('%Y%m%d')}_{enddate.strftime('%Y%m%d')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for src, _ in sorted(selected, key=lambda x: str(x[0])):
        new_name = flatten_name(data_root, src)
        target = unique_target(out_dir / new_name)
        if args.dry_run:
            print(f"[dry-run] {src} -> {target}")
            copied += 1
            continue

        shutil.copy2(src, target)
        copied += 1

    print(f"Matched: {len(selected)}")
    print(f"Output: {out_dir}")
    print(f"Copied: {copied}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
