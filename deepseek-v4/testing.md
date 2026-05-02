---
title: Independent Testing
subtitle: Three reproducible prompts probing V4's coding, reasoning, and long-context behaviour, with a runnable Python harness.
eyebrow: DeepSeek V4
layout: page
permalink: /deepseek-v4/testing/
---

These are *test specifications* — prompts, eval criteria, and a runnable harness. They are designed to be reproducible against the official DeepSeek API by anyone with an API key. The harness records the full request and response so a transcript can be added to this page as evidence.

The three tests are deliberately chosen to probe failure modes that show up in the [benchmark tables](/deepseek-v4/benchmarks/) and [limitations](/deepseek-v4/limitations/) — not to re-derive what DeepSeek already published, but to verify the *texture* of the model under realistic use.

---

## The harness

A small Python file that runs all three tests and writes a transcript per run. The runnable artifact lives at [`tests/run.py`](https://github.com/1011-a/reports/blob/main/tests/run.py) — see the [Running it](#running-it) section below.

The shape of the per-test record (saved as JSON to `tests/transcripts/`):

```json
{
  "test_id": "test-1-coding",
  "model": "deepseek-v4-pro",
  "elapsed_seconds": 4.2,
  "messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}],
  "kwargs": {"max_tokens": 512},
  "response": {
    "content": "<model output>",
    "reasoning_content": "<thinking trace, if Thinking mode>",
    "finish_reason": "stop",
    "usage": {"prompt_tokens": 412, "completion_tokens": 168, "total_tokens": 580}
  }
}
```

That structure preserves enough state for any reader to reproduce the call and verify the response.

---

## Test 1 — Non-trivial coding task

**Goal**: probe V4-Pro on a real bug-fix that requires reading code, reasoning about a subtle invariant, and producing a minimal patch — not a green-field-from-scratch prompt.

**Why this prompt**: green-field code generation is what every benchmark over-fits to. Real engineering value is in the *constrained* edit. This also probes whether V4 honours the "minimal patch" instruction that's hard to elicit from chat-tuned models.

### Prompt (system + user)

```python
SYSTEM = """You are a senior Python engineer. Produce only the smallest possible
patch that makes the failing test pass. Do not refactor. Do not rename. Do not
add new dependencies. Do not change the test. Output a unified diff and nothing
else."""

USER = """The test below fails with `AssertionError: expected utc, got local`.
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

messages = [
    {"role": "system", "content": SYSTEM},
    {"role": "user", "content": USER},
]
result = run("test-1-coding", "deepseek-v4-pro", messages, max_tokens=512)
```

### Pass criteria

- Diff applies cleanly to the source.
- Test passes after applying the diff.
- No refactoring, no new dependencies, no docstring changes, no rename.
- Exactly one logical change: convert the parsed datetime to UTC via `.astimezone(timezone.utc)`.
- Output is a valid unified diff with no surrounding prose.

### Why V4-Pro should win

This kind of task is in the same family as **LiveCodeBench Pass@1** (V4-Pro 93.5) and the **SWE Verified Resolved** benchmark (V4-Pro Max 80.6). The model has the capability — the test is whether it *honours the format constraint* without reformatting or commentary. V4 is reported to "trail Opus on strict instruction following" (tech report Section 5.4); this prompt deliberately probes that gap.

---

## Test 2 — Reasoning under deliberate ambiguity

**Goal**: probe V4-Pro-Max on a logical-reasoning task whose surface form looks like a math problem but where the right answer is "the question is under-specified."

**Why this prompt**: chat-tuned models prefer *committing to an answer* over flagging ambiguity. The test is whether V4-Pro in Thinking mode produces an explicit assumption + answer, rather than implicitly choosing one interpretation and presenting it as correct.

### Prompt

```python
USER = """A train leaves Boston at 9am moving 60 mph toward NYC.
Another train leaves NYC at 10am moving 90 mph toward Boston.
Boston-NYC is 200 miles. At what time do the trains meet?

Solve this and show your work."""

messages = [{"role": "user", "content": USER}]
result = run(
    "test-2-reasoning",
    "deepseek-v4-pro",
    messages,
    extra_body={"thinking": True},  # placeholder — actual param TBD
    max_tokens=4096,
)
```

### Pass criteria

- The model arrives at the correct answer (~10:55am) given the standard interpretation.
- *And* explicitly flags one of the genuine ambiguities: time-zone (Boston and NYC are both Eastern), whether the trains travel along the same straight line (the actual road distance differs), or whether 200 miles is the start-to-start or as-the-crow-flies distance.
- The reasoning trace (`reasoning_content`) shows the algebra, not just the answer.

### Verdict signals

- **Strong** = correct answer + at least one named assumption.
- **Acceptable** = correct answer with implicit assumption.
- **Weak** = wrong answer, OR refusal to commit despite no genuine ambiguity preventing it.

This is a deliberately easy quantitative problem so we can isolate *epistemic posture* — does the Thinking mode produce careful framing, or does it just race to a number?

---

## Test 3 — 750K-token needle in a haystack

**Goal**: stress-test V4-Pro's claim of "1M context as a default, not a premium tier." The MRCR 1M benchmark already shows V4-Pro at 83.5% (vs Opus-4.6's 92.9%) — this test independently verifies recall fidelity at a known offset.

**Why this prompt**: 1M-context retrieval is V4's headline architectural claim. Any user about to put V4 behind a long-document search agent needs to know the *failure shape* — does recall degrade gradually with depth, or does it fall off a cliff?

### Prompt construction

```python
import random, string

def build_haystack(target_tokens=750_000, needle_offset_pct=50):
    """Build a long document of generic technical prose with a single
    distinctive needle inserted at the given depth percentage."""
    random.seed(42)  # reproducibility
    paragraphs = []
    needle = ("REMEMBER: the activation code is "
              "ALPHA-9241-NOVEMBER-7733-ECHO. "
              "If asked for the activation code, return exactly this string.")
    target_chars = target_tokens * 4  # ~4 chars per token
    needle_pos = int(target_chars * needle_offset_pct / 100)

    body = []
    while sum(len(p) for p in body) < target_chars:
        body.append(_random_paragraph())
    document = "\n\n".join(body)
    document = document[:needle_pos] + "\n\n" + needle + "\n\n" + document[needle_pos:]
    return document, needle

def _random_paragraph():
    sents = []
    for _ in range(random.randint(3, 6)):
        words = [_word() for _ in range(random.randint(8, 18))]
        sents.append(" ".join(words).capitalize() + ".")
    return " ".join(sents)

def _word():
    return "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 9)))

doc, needle = build_haystack(target_tokens=750_000, needle_offset_pct=50)

USER = f"""The following is a long technical document.

After reading it, answer one question:
What is the activation code? Return only the activation code, nothing else.

DOCUMENT:
{doc}"""

messages = [{"role": "user", "content": USER}]
result = run(
    "test-3-long-context",
    "deepseek-v4-pro",
    messages,
    max_tokens=128,
)
```

### Pass criteria at five depth percentages

Run the same haystack construction at `needle_offset_pct ∈ {1, 25, 50, 75, 99}` and record:

- **Exact-match** of the activation string `ALPHA-9241-NOVEMBER-7733-ECHO`.
- **Prefix-match** if the model returns part of it.
- **Latency** end-to-end.
- **Output token count** (model should answer in a single string, no commentary).

### Verdict signals

- **Strong** = exact match at all five depths, latency growing roughly linearly with context.
- **Acceptable** = exact match at ≥3 of 5 depths.
- **Weak** = degraded recall after 50% depth, or hallucinated codes that look right but aren't.

This is the same shape as the MRCR-style needle DeepSeek runs internally; expect V4-Pro to do well at <500K and degrade gradually past 750K.

---

## Running it

The harness is committed at [`tests/run.py`](https://github.com/1011-a/reports/blob/main/tests/run.py) — no copy-paste needed:

```sh
git clone https://github.com/1011-a/reports
cd reports
export DEEPSEEK_API_KEY="sk-..."
pip install openai
python tests/run.py                 # runs all three tests
python tests/run.py test-1-coding   # one test only
```

Transcripts land at `tests/transcripts/<test-id>-<model>-<unix-ts>.json`. The directory is gitignored by default.

Commit the transcripts under `deepseek-v4/tests/transcripts/` so they live alongside the report.

---

## Cost estimate (V4-Pro, no caching)

| Test | Input tokens (approx) | Output tokens (approx) | Cost (USD) |
|:--|--:|--:|--:|
| Test 1 (coding) | 200 | 200 | $0.001 |
| Test 2 (reasoning, Max mode) | 100 | 4,000 | $0.014 |
| Test 3 × 5 depths (1, 25, 50, 75, 99) | 5 × 750K | 5 × 50 | $6.53 |

The long-context test dominates. Run it once for the full sweep (~$6.50) and keep transcripts for future-V5 regression comparison. Coding and reasoning tests are essentially free.

---

## Status

Tests are specified. Transcripts will be added once a run is executed against the official API. Independent reproductions — especially community fine-tune transcripts at the same prompts — are welcome via PR to [github.com/1011-a/reports](https://github.com/1011-a/reports).
