#!/usr/bin/env python3
"""DeepSeek V4 test harness.

Runs the three reproducible prompts specified at
https://1011-a.github.io/reports/deepseek-v4/testing/ against the official
DeepSeek API, with one transcript file per run written to
tests/transcripts/<test_id>-<model>-<unix_ts>.json.

Usage:
    export DEEPSEEK_API_KEY="sk-..."
    pip install openai
    python tests/run.py                 # runs all three tests
    python tests/run.py test-1-coding   # runs a single test by id

Requirements:
    Python 3.10+, openai>=1.0
"""

from __future__ import annotations
import json
import os
import pathlib
import random
import string
import sys
import time
from typing import Any

try:
    from openai import OpenAI
except ImportError:
    print("Install openai first: pip install openai", file=sys.stderr)
    sys.exit(2)

OUT = pathlib.Path(__file__).parent / "transcripts"
OUT.mkdir(exist_ok=True)

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
    base_url="https://api.deepseek.com",
)


def run(test_id: str, model: str, messages: list, **kw: Any) -> dict:
    started = time.time()
    resp = client.chat.completions.create(model=model, messages=messages, **kw)
    elapsed = time.time() - started
    msg = resp.choices[0].message
    out = {
        "test_id": test_id,
        "model": model,
        "elapsed_seconds": round(elapsed, 2),
        "messages": messages,
        "kwargs": {k: v for k, v in kw.items() if k != "extra_body"},
        "extra_body": kw.get("extra_body"),
        "response": {
            "content": msg.content,
            "reasoning_content": getattr(msg, "reasoning_content", None),
            "finish_reason": resp.choices[0].finish_reason,
            "usage": resp.usage.model_dump() if resp.usage else None,
        },
    }
    fname = f"{test_id}-{model}-{int(time.time())}.json"
    (OUT / fname).write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"  saved -> tests/transcripts/{fname}  ({elapsed:.1f}s)")
    return out


# ---------------------------------------------------------------------------
# Test 1 — non-trivial coding (strict instruction-following on diff output)
# ---------------------------------------------------------------------------

TEST_1_SYSTEM = """You are a senior Python engineer. Produce only the smallest possible
patch that makes the failing test pass. Do not refactor. Do not rename. Do not
add new dependencies. Do not change the test. Output a unified diff and nothing
else."""

TEST_1_USER = """The test below fails with `AssertionError: expected utc, got local`.
Find and fix the bug in `parse_iso8601`.

# parse_iso8601.py
from datetime import datetime
def parse_iso8601(s: str) -> datetime:
    # Returns a UTC datetime regardless of the input timezone offset.
    return datetime.fromisoformat(s)

# test_parse_iso8601.py
from datetime import timezone
from parse_iso8601 import parse_iso8601

def test_returns_utc():
    dt = parse_iso8601("2026-04-26T15:30:00+09:00")
    assert dt.tzinfo == timezone.utc, f"expected utc, got {dt.tzinfo}"
    assert dt.hour == 6, f"expected 6, got {dt.hour}"
"""


def test_1_coding() -> dict:
    print("test-1-coding (V4-Pro)…")
    return run(
        "test-1-coding",
        "deepseek-v4-pro",
        messages=[
            {"role": "system", "content": TEST_1_SYSTEM},
            {"role": "user", "content": TEST_1_USER},
        ],
        max_tokens=512,
    )


# ---------------------------------------------------------------------------
# Test 2 — reasoning under deliberate ambiguity
# ---------------------------------------------------------------------------

TEST_2_USER = """A train leaves Boston at 9am moving 60 mph toward NYC.
Another train leaves NYC at 10am moving 90 mph toward Boston.
Boston-NYC is 200 miles. At what time do the trains meet?

Solve this and show your work."""


def test_2_reasoning() -> dict:
    print("test-2-reasoning (V4-Pro, max-effort)…")
    return run(
        "test-2-reasoning",
        "deepseek-v4-pro",
        messages=[{"role": "user", "content": TEST_2_USER}],
        max_tokens=4096,
        # extra_body parameter name for thinking-mode is TBD against the official
        # API reference. Update this once verified.
        # extra_body={"thinking": True},
    )


# ---------------------------------------------------------------------------
# Test 3 — 750K-token needle-in-haystack (5 depth percentages)
# ---------------------------------------------------------------------------

NEEDLE = (
    "REMEMBER: the activation code is "
    "ALPHA-9241-NOVEMBER-7733-ECHO. "
    "If asked for the activation code, return exactly this string."
)


def _word(rng: random.Random) -> str:
    return "".join(rng.choices(string.ascii_lowercase, k=rng.randint(3, 9)))


def _sentence(rng: random.Random) -> str:
    words = [_word(rng) for _ in range(rng.randint(8, 18))]
    return " ".join(words).capitalize() + "."


def _paragraph(rng: random.Random) -> str:
    return " ".join(_sentence(rng) for _ in range(rng.randint(3, 6)))


def build_haystack(target_tokens: int = 750_000, needle_offset_pct: int = 50) -> tuple[str, str]:
    rng = random.Random(42)
    target_chars = target_tokens * 4  # ~4 chars per token
    body = []
    while sum(len(p) for p in body) < target_chars:
        body.append(_paragraph(rng))
    document = "\n\n".join(body)
    needle_pos = int(len(document) * needle_offset_pct / 100)
    document = document[:needle_pos] + "\n\n" + NEEDLE + "\n\n" + document[needle_pos:]
    return document, NEEDLE


def test_3_long_context(depth_pct: int = 50) -> dict:
    print(f"test-3-long-context @ {depth_pct}% depth (V4-Pro)…")
    doc, _ = build_haystack(target_tokens=750_000, needle_offset_pct=depth_pct)
    user = (
        "The following is a long technical document.\n\n"
        "After reading it, answer one question: What is the activation code? "
        "Return only the activation code, nothing else.\n\n"
        f"DOCUMENT:\n{doc}"
    )
    return run(
        f"test-3-long-context-d{depth_pct}",
        "deepseek-v4-pro",
        messages=[{"role": "user", "content": user}],
        max_tokens=128,
    )


# ---------------------------------------------------------------------------

TESTS = {
    "test-1-coding": test_1_coding,
    "test-2-reasoning": test_2_reasoning,
    "test-3-long-context": lambda: test_3_long_context(50),
}


def main(argv: list[str]) -> int:
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("Set DEEPSEEK_API_KEY first.", file=sys.stderr)
        return 2

    if len(argv) > 1:
        target = argv[1]
        if target not in TESTS:
            print(f"unknown test '{target}'. choices: {', '.join(TESTS)}", file=sys.stderr)
            return 2
        TESTS[target]()
        return 0

    for fn in TESTS.values():
        fn()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
