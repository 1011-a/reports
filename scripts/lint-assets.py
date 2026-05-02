#!/usr/bin/env python3
"""Detect orphaned assets (image files committed but not referenced in any markdown).

Catches the failure mode that iter-27 hit: rendering and committing a figure but
forgetting to actually embed it in a page, leaving a dangling 460 KB PNG that
nobody can reach via the site.

Heuristic: for each file under `assets/images/`, check whether its filename
appears literally anywhere in any markdown file in the repo. This is a permissive
match (a `<img src=...>` reference or any `[alt](path)` markdown reference will
both contain the filename), but it's also generous about how authors might
write the path (relative_url filter, baseurl variations, deeplinks, etc.).

False-negative: an asset referenced only via dynamic Liquid / JavaScript would
slip through. We don't have any of those today.

Usage:  scripts/lint-assets.py
Exit:   0 if every asset is referenced, 1 otherwise.
"""

from __future__ import annotations
import pathlib
import sys

ASSET_DIRS = [pathlib.Path("assets/images")]
EXCLUDE_PARTS = {"_site", ".git", ".github", "node_modules", "vendor", ".bundle"}


def collect_markdown_text() -> str:
    text = []
    for path in pathlib.Path(".").rglob("*.md"):
        if any(part in EXCLUDE_PARTS for part in path.parts):
            continue
        text.append(path.read_text(encoding="utf-8"))
    return "\n".join(text)


def find_orphans(haystack: str) -> list[pathlib.Path]:
    orphans: list[pathlib.Path] = []
    for asset_dir in ASSET_DIRS:
        if not asset_dir.exists():
            continue
        for asset in asset_dir.rglob("*"):
            if asset.is_dir():
                continue
            if asset.name.startswith("."):
                continue
            if asset.name not in haystack:
                orphans.append(asset)
    return sorted(orphans)


def main(argv: list[str]) -> int:
    md_text = collect_markdown_text()
    orphans = find_orphans(md_text)

    if orphans:
        print("Orphaned assets (committed but not referenced in any markdown):")
        for o in orphans:
            size_kb = o.stat().st_size / 1024
            print(f"  {o} ({size_kb:.0f} KB)")
        print(
            "\n[error] Either embed these in a page, or remove them.\n",
            file=sys.stderr,
        )
        return 1

    print("OK — all assets are referenced in at least one markdown file.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
