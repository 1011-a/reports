#!/usr/bin/env python3
"""Verify in-site anchor links resolve to actual headings.

The report uses many cross-page deep-links of the form
[label](/deepseek-v4/api/#choosing-v4-pro-vs-v4-flash) and same-page
links like [Choosing the model](#choosing-v4-pro-vs-v4-flash). When a
heading changes, those links silently rot.

Heuristic: walk all .md files. For each, build the kramdown auto-ID set
from H2/H3/H4 headings (kramdown rule: lowercase, replace non-alphanum
runs with -, strip leading/trailing -). Then for every internal anchor
link on every page, check the anchor against the target page's ID set.

Limitations:
- Doesn't validate external URLs or images.
- Doesn't validate links to non-markdown pages (we don't have any).
- Custom kramdown id-overrides via {#id} blocks aren't extracted (we
  don't use them yet).

Usage:  scripts/lint-anchors.py
Exit:   0 if all in-site anchor links resolve, 1 otherwise.
"""

from __future__ import annotations
import pathlib
import re
import sys

EXCLUDE_PARTS = {"_site", ".git", ".github", "node_modules", "vendor", ".bundle"}

HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)(?:\s*\{#([^}]+)\})?\s*$", re.MULTILINE)
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
SETEXT_HEADING_RE = re.compile(r"^([^\n]+)\n=+\s*$|^([^\n]+)\n-+\s*$", re.MULTILINE)


def kramdown_id(heading_text: str) -> str:
    """Approximate kramdown's auto-ID rule.

    Kramdown's actual behaviour (verified against rendered HTML):
    - Lowercase
    - **Remove** non-word, non-hyphen, non-whitespace characters entirely
      (em-dashes, commas, slashes, etc. — not converted to hyphens)
    - Convert each whitespace character to a hyphen, **without** collapsing
      runs (so " — " becomes "--" because the em-dash is deleted and the
      two surrounding spaces each become a hyphen)
    - Strip leading/trailing hyphens
    """
    text = heading_text
    # Strip Markdown emphasis markers (don't count as part of id text)
    text = re.sub(r"[`*_]", "", text)
    # Strip Liquid output expressions
    text = re.sub(r"\{\{[^}]*\}\}", "", text)
    # Lowercase
    text = text.lower()
    # Pass 1: strip non-word, non-hyphen, non-whitespace chars
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    # Pass 2: each whitespace becomes a hyphen (no collapse)
    text = re.sub(r"\s", "-", text)
    return text.strip("-")


def collect_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for match in HEADING_RE.finditer(text):
        title = match.group(2).strip()
        explicit = match.group(3)
        if explicit:
            ids.add(explicit)
        else:
            ids.add(kramdown_id(title))
    return ids


def page_url(path: pathlib.Path) -> str:
    """Map a markdown file to its likely permalink path used in links."""
    # Read frontmatter for explicit permalink
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^permalink:\s*(\S+)", text, re.MULTILINE)
    if m:
        return m.group(1).rstrip("/")
    # Fallback: directory-style URL (e.g., deepseek-v4/api -> /deepseek-v4/api)
    rel = "/" + str(path.with_suffix("")).removesuffix("/index").lstrip("./")
    return rel


def main(argv: list[str]) -> int:
    md_files = [
        p for p in pathlib.Path(".").rglob("*.md")
        if not any(part in EXCLUDE_PARTS for part in p.parts)
    ]

    # Build URL -> id-set map
    page_ids: dict[str, set[str]] = {}
    for path in md_files:
        url = page_url(path)
        text = path.read_text(encoding="utf-8")
        page_ids[url.rstrip("/")] = collect_ids(text)

    # Walk all links
    bad: list[tuple[pathlib.Path, int, str, str]] = []
    for path in md_files:
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for link in LINK_RE.finditer(line):
                href = link.group(2)
                # Strip optional title in quotes after URL
                href = href.split(" ", 1)[0]
                if "#" not in href:
                    continue
                url, _, anchor = href.partition("#")
                if not anchor:
                    continue
                if url.startswith(("http://", "https://", "mailto:")):
                    continue
                if url == "":
                    # Same-page anchor — resolve against current page
                    target_url = page_url(path).rstrip("/")
                else:
                    target_url = url.rstrip("/")
                if target_url not in page_ids:
                    bad.append((path, lineno, href, "page not found"))
                    continue
                if anchor not in page_ids[target_url]:
                    bad.append((path, lineno, href, "anchor not on page"))

    if bad:
        print("Broken in-site anchor links:")
        for path, lineno, href, why in bad:
            print(f"  {path}:L{lineno}: {href} ({why})")
        print(
            f"\n[error] {len(bad)} broken anchor link(s). Either fix the link or "
            "update the target heading.\n",
            file=sys.stderr,
        )
        return 1

    print("OK — all in-site anchor links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
