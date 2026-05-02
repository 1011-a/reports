---
title: DeepSeek V4
subtitle: A research report on DeepSeek V4, released 2026-04-24.
eyebrow: Report
layout: page
permalink: /deepseek-v4/
updated: 2026-04-27
---

> **Status** — V4 is released. DeepSeek launched the V4 Preview on April 24, 2026, shipping two production-ready open-weights models — **V4-Pro** and **V4-Flash** — under the MIT license. This report is being built incrementally; see the [changelog](/changelog/) for what's been added.

## How to read this report

This page is the executive summary. Pick the path that matches what you came for:

- **"What's the takeaway in 5 minutes?"** → [The V4 thesis](/deepseek-v4/thesis/) — six observations that will still matter about V4 a year from now.
- **"Just tell me if I should use it."** → [Benchmarks — V4-Pro-Max vs frontier](/deepseek-v4/benchmarks/#v4-pro-max-vs-frontier-closedopen-models-tech-report-table-6) and [Limitations — what DeepSeek themselves call out](/deepseek-v4/limitations/#what-deepseek-themselves-call-out).
- **"How do I call the API?"** → [API — Quick start](/deepseek-v4/api/#quick-start--60-seconds). One curl, then JSON mode and tool use further down the page.
- **"I'm already on V3 — should I move?"** → [V3 → V4 Migration Guide](/deepseek-v4/migration/). One-line code change, July 24 retirement deadline, cost recalibration worksheet.
- **"How does it actually work?"** → [Technical Details — architecture overview](/deepseek-v4/technical/#architecture-overview), then [V3 → V3.2 → V4 diff](/deepseek-v4/technical/#v3--v32--v4-architectural-diff).
- **"What's the catch?"** → [Limitations — training stability is held together by techniques DeepSeek doesn't fully understand](/deepseek-v4/limitations/#2-training-stability-is-held-together-by-techniques-deepseek-doesnt-fully-understand) is the most candid section in V4's tech report.
- **"How can I verify it for myself?"** → [Independent Testing](/deepseek-v4/testing/) — three reproducible prompts with a Python harness.
- **"Should I run V4 on my own hardware?"** → [Self-hosting V4](/deepseek-v4/self-hosting/) — hardware budgets, serving frameworks, and when the API is the better answer.
- **"What does CSA/HCA/mHC/OPD/etc. mean?"** → [Glossary](/deepseek-v4/glossary/) — every acronym in the report, defined in one place.
- **"What did this report get wrong?"** → [Errata](/deepseek-v4/errata/) — material corrections, dated and traceable.

Total reading time end-to-end: ~25 minutes. Each subpage is independently navigable.

![DeepSeek V4 tech-report cover and headline figure]({{ "/assets/images/deepseek-v4/v4-cover.png" | relative_url }})
*Cover page of `DeepSeek_V4.pdf`. The headline chart compares V4-Pro-Max to Claude Opus 4.6 Max, GPT-5.4 xHigh, and Gemini 3.1 Pro High; the right panels show V4's FLOPs and KV-cache reductions vs V3.2 at 1M context.*

![DeepSeek V4 spec sheet]({{ "/assets/images/deepseek-v4/v4-spec-en.png" | relative_url }})
*Official DeepSeek V4 specification card. Source: [api-docs.deepseek.com](https://api-docs.deepseek.com/news/news260424).*

---

## At a glance

| | DeepSeek V4-Pro | DeepSeek V4-Flash |
|:--|:--|:--|
| **Total params** | 1.6T | 284B |
| **Active params** | 49B | 13B |
| **Context** | 1M tokens | 1M tokens |
| **Architecture** | MoE + DeepSeek Sparse Attention (DSA) | MoE + DeepSeek Sparse Attention (DSA) |
| **Modes** | Thinking / Non-Thinking | Thinking / Non-Thinking |
| **License** | MIT (open weights) | MIT (open weights) |
| **API model ID** | `deepseek-v4-pro` | `deepseek-v4-flash` |
| **Input (cache-miss)** | $1.74 / 1M tokens | $0.14 / 1M tokens |
| **Input (cache-hit)** | $0.145 / 1M tokens | $0.028 / 1M tokens |
| **Output** | $3.48 / 1M tokens | $0.28 / 1M tokens |

Sources: [DeepSeek API Docs — V4 Preview Release](https://api-docs.deepseek.com/news/news260424){: .text-grey-dk-000 } · [DeepSeek API Pricing](https://api-docs.deepseek.com/quick_start/pricing){: .text-grey-dk-000 }

---

## What's new vs V3

- **DeepSeek Sparse Attention (DSA)** — token-wise compression that, in 1M-token settings, brings V4-Pro to roughly **27% of single-token inference FLOPs** and **10% of the KV cache** of V3.2.
- **1M context as the default** across all official services.
- **Two-tier lineup** (Pro for frontier reasoning, Flash for cost-sensitive deployment).
- **Hybrid Thinking / Non-Thinking modes** in a single model — replacing the V3-era split between `deepseek-chat` and `deepseek-reasoner`.
- **Aggressive pricing** — V4-Flash output at $0.28 / 1M tokens is roughly an order of magnitude below frontier closed models.

---

## Site map

Thirteen pages, grouped by intended use. The sidebar mirrors this grouping.

### Read first

- [The V4 thesis](/deepseek-v4/thesis/) — six observations that will still matter about V4 a year from now. Curatorial editorial summary.
- [API documentation](/deepseek-v4/api/) — endpoints, auth, JSON mode, function calling, cost calculator, cross-vendor pricing, alternative providers, "Choosing V4-Pro vs V4-Flash" decision flow with concrete app patterns.
- [V3 → V4 migration](/deepseek-v4/migration/) — one-line code change, July 24 retirement deadline, cost recalibration with explicit ratios.

### Detail

- [News & timeline](/deepseek-v4/news/) — release timeline, official announcement quotes, press coverage, community reception (Hacker News + Simon Willison + community quants), industry reactions, geopolitical / IP controversy.
- [Technical details](/deepseek-v4/technical/) — config-backed architecture (CSA + HCA, mHC, MoE expert counts), V3 → V3.2 → V4 diff, training pipeline, training-stability candor, FP4/FP8 quantisation, architecture-decisions journal.
- [Benchmarks](/deepseek-v4/benchmarks/) — official Tables 1, 6, and 7 verbatim, formal-reasoning Putnam regimes, MRCR long-context curve, reasoning-effort scaling, win-rate analysis vs Opus.
- [Self-hosting](/deepseek-v4/self-hosting/) — hardware budgets per variant, serving framework matrix (NIM / SGLang / vLLM / GGUF / MLX), real-world throughput numbers, when the API is the better answer.
- [Independent testing](/deepseek-v4/testing/) — three reproducible test prompts with a Python harness (coding, reasoning, 750K-token needle).
- [Limitations & safety](/deepseek-v4/limitations/) — DeepSeek's own Section 6 candor, V3-era red-team findings that likely extrapolate, content-filtering on the hosted API.

### Reference

- [References](/deepseek-v4/references/) — full bibliography with access dates.
- [Glossary](/deepseek-v4/glossary/) — ~25 acronyms (CSA, HCA, DSA, MLA, mHC, MoE, OPD, GRPO, YaRN, etc.) defined in one place.
- [Errata](/deepseek-v4/errata/) — material corrections to past claims, dated and traceable.

Cross-site:

- [Changelog](/changelog/) — dated log of every iteration's contribution.

---

## Migration note

DeepSeek's existing `deepseek-chat` and `deepseek-reasoner` endpoints currently route to V4-Flash in Non-Thinking and Thinking modes respectively. Both will be **fully retired after 2026-07-24, 15:59 UTC**. New code should target `deepseek-v4-pro` or `deepseek-v4-flash` directly.

Source: [DeepSeek API Docs — V4 Preview Release](https://api-docs.deepseek.com/news/news260424).

---

## Citing this report

This is a living document. If you reference a specific claim, link to the section anchor and note the access date — the page may have been re-verified or corrected since.

**Suggested citation format**:

```
1011-a. (2026). DeepSeek V4 — research report. Reports.
Retrieved <ACCESS_DATE> from https://1011-a.github.io/reports/deepseek-v4/
```

**BibTeX**:

```bibtex
@misc{1011a_deepseekv4_2026,
  author       = {{1011-a}},
  title        = {DeepSeek V4 --- research report},
  howpublished = {Reports},
  year         = {2026},
  url          = {https://1011-a.github.io/reports/deepseek-v4/},
  note         = {Accessed: <ACCESS_DATE>}
}
```

For specific subpages, append the subpage path (e.g., `/deepseek-v4/benchmarks/`) to the URL. Every long page has a "Last verified" date stamp under its TL;DR — that's the most accurate reference point for when its claims were last reconciled with primary sources.

If you spot something materially wrong, the [Errata](/deepseek-v4/errata/) page documents prior corrections; new errata can be opened as issues at [github.com/1011-a/reports](https://github.com/1011-a/reports/issues).

The full source of this report — markdown, configs, and rendered figures — lives at the same GitHub URL under MIT-equivalent terms (the report cites primary sources whose own licenses apply to their content).
