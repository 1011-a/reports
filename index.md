---
title: Reports
subtitle: Long-form technical reports on AI models, systems, and tooling.
layout: home
permalink: /
featured:
  - title: DeepSeek V4
    eyebrow: Latest report · DeepSeek-AI · Released 2026-04-24
    url: /deepseek-v4/
    image: /assets/images/deepseek-v4/v4-cover.png
    dek: A primary-source-backed deep dive on DeepSeek V4 — architecture from `config.json` and the official tech report, full benchmark tables, decision frameworks for Pro vs Flash, V3 → V4 migration guide, and a candid limitations section sourced from DeepSeek's own Section 6.
    findings:
      - "**1M context as a default tier, not a premium one.** V4-Pro hits ~27% of V3.2's single-token FLOPs and ~10% of its KV cache at 1M, via the hybrid CSA + HCA attention design — the architectural feature that makes the pricing work."
      - "**Output cost is 7.2× cheaper than Opus 4.7 and 8.6× cheaper than GPT-5.5** at frontier-class quality. A 32M-token-per-month agent fleet costs ~$4.76 on V4-Flash."
      - "**V4-Pro reuses V3's exact backbone shape** (7168 / 61 / 128). The 671B → 1.6T parameter growth is purely a wider MoE expert pool, not a fresh-init gamble. Risk reduction, deliberate."
      - "**Training stability is held together by techniques DeepSeek themselves don't fully understand** (Anticipatory Routing, SwiGLU Clamping). They publish this honestly in Section 4.2.3."
---

This is a long-lived hub for in-depth research reports. Each topic lives in its own subdirectory with primary-source citations, configuration extracts, and benchmarks. New reports are added over time without restructuring.

Reports are deliberately structured as references, not blog posts: facts are sourced, claims are date-stamped, and material corrections land on a public [errata](/deepseek-v4/errata/) page rather than silent rewrites. See the [changelog](/changelog/) for dated entries across all topics, or browse the source on [GitHub](https://github.com/1011-a/reports).
