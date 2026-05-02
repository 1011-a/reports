#!/usr/bin/env python3
"""Lint for unguarded Liquid literals inside inline code in markdown.

Jekyll's Liquid pre-processes the file *before* markdown rendering, so
sequences like `{% if x %}` or `{{ foo }}` inside inline-code backticks
still get parsed as real Liquid tags. To document Liquid syntax safely,
wrap the surrounding paragraph in `{% raw %}…{% endraw %}` first.

This lint catches the pattern that broke iter-21 and iter-22 builds:
unguarded `{` followed by `%` or `{` inside `…` backticks. It does NOT
flag bare Liquid usage elsewhere — `{{ "/assets/x" | relative_url }}`
in the page body is legitimate and should pass.

Usage:  scripts/lint-liquid.py
Exit:   0 if clean, 1 if any unguarded Liquid found.
"""

from __future__ import annotations
import pathlib
import re
import sys

RAW_BLOCK = re.compile(r"\{%\s*raw\s*%\}.*?\{%\s*endraw\s*%\}", re.DOTALL)
INLINE_CODE = re.compile(r"`([^`\n]+)`")
LIQUID_TOKEN = re.compile(r"\{%|\{\{")

EXCLUDE_PARTS = {"_site", ".git", ".github", "node_modules", "vendor", ".bundle"}


def lint_file(path: pathlib.Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    # Mask out properly-guarded raw blocks so their content isn't checked.
    masked = RAW_BLOCK.sub(lambda m: " " * len(m.group()), text)

    issues: list[tuple[int, str]] = []
    for lineno, line in enumerate(masked.splitlines(), start=1):
        for code in INLINE_CODE.finditer(line):
            if LIQUID_TOKEN.search(code.group(1)):
                issues.append((lineno, line.rstrip()))
                break
    return issues


def main(argv: list[str]) -> int:
    root = pathlib.Path(".")
    bad = False

    for path in sorted(root.rglob("*.md")):
        if any(part in EXCLUDE_PARTS for part in path.parts):
            continue
        issues = lint_file(path)
        if not issues:
            continue
        bad = True
        print(f"\n{path}")
        for lineno, line in issues:
            snippet = line if len(line) <= 120 else line[:117] + "..."
            print(f"  L{lineno}: {snippet}")

    if bad:
        print(
            "\n[error] Unguarded Liquid literal in inline code.\n"
            "        Wrap the paragraph in {% raw %} ... {% endraw %} or rephrase\n"
            "        so the literal does not appear inside backticks.\n",
            file=sys.stderr,
        )
        return 1

    print("OK — no unguarded Liquid literals in inline code.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
