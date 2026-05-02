#!/usr/bin/env python3
"""Lint asset sizes that would land on the deployed site.

Catches the failure mode where someone commits an unoptimised image
that bloats every page on the site (every page that embeds it loads
the asset on first paint). Per-asset budget defaults to 1.5 MB; per-
directory total budget to 12 MB; bumpable via env vars.

This is a soft lint — it warns and exits 1 on overage so CI fails,
but the actual file isn't modified. Optimisation strategies live in
the docs (resize, strip metadata, prefer JPEG for photos, PNG for
diagrams with text).

Usage:  scripts/lint-page-weight.py
Exit:   0 if under budget, 1 otherwise.
"""

from __future__ import annotations
import os
import pathlib
import sys

PER_FILE_KB = int(os.environ.get("MAX_ASSET_KB", "1536"))   # 1.5 MB
TOTAL_KB = int(os.environ.get("MAX_ASSETS_TOTAL_KB", "12288"))  # 12 MB

EXCLUDE_PARTS = {"_site", ".git", ".github", "node_modules", "vendor", ".bundle"}
ASSET_DIRS = [pathlib.Path("assets")]


def main() -> int:
    over_per_file: list[tuple[pathlib.Path, int]] = []
    total_kb = 0

    for asset_dir in ASSET_DIRS:
        if not asset_dir.exists():
            continue
        for asset in asset_dir.rglob("*"):
            if asset.is_dir():
                continue
            if any(p in EXCLUDE_PARTS for p in asset.parts):
                continue
            if asset.name.startswith("."):
                continue
            size_kb = asset.stat().st_size / 1024
            total_kb += size_kb
            if size_kb > PER_FILE_KB:
                over_per_file.append((asset, int(size_kb)))

    bad = False
    if over_per_file:
        bad = True
        print(f"Files exceeding per-asset budget ({PER_FILE_KB} KB):")
        for path, kb in sorted(over_per_file, key=lambda x: -x[1]):
            print(f"  {path}  {kb} KB")

    if total_kb > TOTAL_KB:
        bad = True
        print(
            f"\nTotal assets size {int(total_kb)} KB exceeds "
            f"directory budget {TOTAL_KB} KB."
        )

    if bad:
        print(
            "\n[error] Page weight over budget. Resize / re-encode the "
            "offenders, or bump the budget via\n"
            "        MAX_ASSET_KB / MAX_ASSETS_TOTAL_KB if the size is "
            "intentional.\n",
            file=sys.stderr,
        )
        return 1

    print(f"OK — assets total {int(total_kb)} KB / {TOTAL_KB} KB budget.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
