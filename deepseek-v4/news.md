---
title: Overview & News
subtitle: Release timeline, official announcements, and press coverage for DeepSeek V4.
eyebrow: DeepSeek V4
layout: page
permalink: /deepseek-v4/news/
---


## Release timeline

| Date (UTC) | Event | Source |
|:--|:--|:--|
| 2025-12 | DeepSeek-V3.2 paper introduces **DeepSeek Sparse Attention (DSA)** — the attention mechanism that V4 builds on. | [arXiv:2512.02556](https://arxiv.org/abs/2512.02556) |
| 2025-12-31 / 2026-01-05 | DeepSeek posts the **mHC: Manifold-Constrained Hyper-Connections** paper (v1 then v2) — the residual-stream technique that becomes load-bearing for V4. Wenfeng Liang appears as last author. | [arXiv:2512.24880](https://arxiv.org/abs/2512.24880) |
| 2026-04-24 | DeepSeek publishes the **V4 Preview** announcement; `deepseek-v4-pro` and `deepseek-v4-flash` go live in the API; weights published on Hugging Face under MIT; `DeepSeek_V4.pdf` tech report posted on the Pro model card. | [DeepSeek API Docs](https://api-docs.deepseek.com/news/news260424) |
| 2026-04-24 | V4 becomes available in `chat.deepseek.com` via Expert Mode (V4-Pro, Thinking) and Instant Mode (V4-Flash, Non-Thinking). | [DeepSeek API Docs](https://api-docs.deepseek.com/news/news260424) |
| 2026-04-25 | LMSYS publishes a Day-0 deep-dive on V4 deployment with SGLang, including FP4 expert-weight handling and verified-RL training. | [LMSYS Blog](https://www.lmsys.org/blog/2026-04-25-deepseek-v4/) |
| 2026-07-24 15:59 | Hard retirement of legacy `deepseek-chat` and `deepseek-reasoner` endpoints (currently routing to V4-Flash). | [DeepSeek API Docs](https://api-docs.deepseek.com/news/news260424) |

---

## Official announcement — key claims

From the DeepSeek V4 Preview Release post (2026-04-24):

- **"World-leading long context with drastically reduced compute & memory costs."**
- **1M context** is the standard default across all official services.
- V4-Pro reaches its efficiency target through **token-wise compression and DeepSeek Sparse Attention (DSA)**: at 1M tokens, ~27% of V3.2's single-token inference FLOPs and ~10% of the KV cache.
- The API is OpenAI- and Anthropic-compatible: callers keep the same `base_url` and only swap the model name.
- Open weights are published under the **MIT license** on Hugging Face.

Source: [api-docs.deepseek.com/news/news260424](https://api-docs.deepseek.com/news/news260424)

---

## Press coverage

| Outlet | Headline | Date | Link |
|:--|:--|:--|:--|
| CNBC | "China's DeepSeek releases preview of long-awaited V4 model as AI race intensifies" | 2026-04-24 | [cnbc.com](https://www.cnbc.com/2026/04/24/deepseek-v4-llm-preview-open-source-ai-competition-china.html) |
| Bloomberg | "DeepSeek Unveils Newest Flagship AI Model a Year after Upending Silicon Valley" | 2026-04-24 | [bloomberg.com](https://www.bloomberg.com/news/articles/2026-04-24/deepseek-unveils-newest-flagship-a-year-after-ai-breakthrough) |
| Al Jazeera | "China's DeepSeek unveils latest models a year after upending global tech" | 2026-04-24 | [aljazeera.com](https://www.aljazeera.com/economy/2026/4/24/chinas-deepseek-unveils-latest-model-a-year-after-upending-global-tech) |
| Euronews | "China's DeepSeek releases new AI model V4. Here's everything to know as the AI race speeds up" | 2026-04-24 | [euronews.com](https://www.euronews.com/next/2026/04/24/chinas-deepseek-releases-new-ai-model-v4-heres-everything-to-know-as-the-ai-race-speeds-up) |
| VentureBeat | "DeepSeek-V4 arrives with near state-of-the-art intelligence at 1/6th the cost of Opus 4.7, GPT-5.5" | 2026-04-24 | [venturebeat.com](https://venturebeat.com/technology/deepseek-v4-arrives-with-near-state-of-the-art-intelligence-at-1-6th-the-cost-of-opus-4-7-gpt-5-5) |
| Artificial Analysis | "DeepSeek is back among the leading open weights models with V4 Pro and V4 Flash" | 2026-04-24 | [artificialanalysis.ai](https://artificialanalysis.ai/articles/deepseek-is-back-among-the-leading-open-weights-models-with-v4-pro-and-v4-flash) |

---

## Community reception

Captured on 2026-04-26, two days after release.

### Simon Willison

In *DeepSeek V4 — almost on the frontier, a fraction of the price* ([simonwillison.net, 2026-04-24](https://simonwillison.net/2026/Apr/24/deepseek-v4/)), Willison ran his SVG-pelican benchmark against both V4 models via OpenRouter:

> "Flash produced a solid result with good bicycle details, while Pro's output showed anatomical issues — an oversized body and misaligned features."

His pricing benchmark — the cleanest summary in the wild:

> "**V4-Flash is the cheapest of the small models** and **V4-Pro is the cheapest of the larger frontier models.** Flash undercuts GPT-5.4 Nano (\$0.20/\$1.25) and Gemini 3.1 Flash-Lite (\$0.25/\$1.50). Pro at \$1.74/\$3.48 beats Gemini 3.1 Pro and GPT-5.4."

He paraphrased DeepSeek's own framing of where V4 sits relative to the frontier:

> "V4-Pro trails state-of-the-art frontier models by approximately 3 to 6 months, though reasoning capabilities narrow this gap."

### Hacker News

Three threads on the front page within 24 hours: [v4 announcement](https://news.ycombinator.com/item?id=47884971), [tech report](https://news.ycombinator.com/item?id=47885014), [coding-focused breakdown](https://news.ycombinator.com/item?id=47885230). Top-comment themes:

- **Pricing is the headline.** "Flash is only $0.28 / 1M and seems quite competent." ([HN 47885014](https://news.ycombinator.com/item?id=47885014))
- **Closes the open-vs-closed gap.** "Looks like DeepSeek is just about 2 months behind the leaders now."
- **Practical capability.** "The Common Lisp code was very good." (a non-trivial test the user posted with their own V4-Flash transcript).
- **Value math for heavy users.** A 40M-token-per-month workload with prefix caching lands at \$30–70/mo on V4-Pro — "around double the usage compared to GPT-5.5 on the \$200 sub."
- **Local deployment is theoretically reachable but slow.** "Theoretically with streaming, any model that fits the disk can run on consumer hardware, just terribly slow."

### Hugging Face Forums

A thread titled [*DeepSeek V4 is live in preview — should your team switch?*](https://discuss.huggingface.co/t/deepseek-v4-is-live-in-preview-should-your-team-switch/175560) is gathering migration-cost reports from teams with existing V3.x integrations. Headline finding: **the only required change is the `model` parameter** — `base_url`, auth, and request shape are unchanged.

### Adoption signals (within first 4 days)

#### OpenRouter market share (2026-04)

Independent of V4-specific traffic, OpenRouter's April 2026 market data shows **Chinese-origin models** (Xiaomi, Alibaba, MiniMax, DeepSeek, Moonshot, Zhipu) crossing **45% of total platform traffic**.

A sharper data point: in the **week of March 30 – April 5, 2026**, OpenRouter served:

| Origin | Tokens that week | Share |
|:--|:--|:--|
| Chinese models | **12.96T** | ~80% |
| US models | 3.03T | ~19% |

Total platform volume that week: 27T tokens. The Chinese share grew 31.48% week-on-week into early April. Source: [Dataconomy](https://dataconomy.com/2026/02/25/chinese-ai-models-hit-61-market-share-on-openrouter/), [aicost.org](https://aicost.org/blog/openrouter-monthly-token-usage-ranking-2026-chinese-models-dominate).

V4 launching into that traffic mix — at headline pricing of $0.14 / $0.28 for Flash and $1.74 / $3.48 for Pro — is now expected to deepen that share further. The pricing-leadership story isn't "DeepSeek will eventually win share" — it's "the share is already there; V4 makes it stickier."

#### OpenClaw makes V4-Flash its default model (2026-04-27)

[TechNode reported](https://technode.com/2026/04/27/deepseek-v4-becomes-default-model-for-openclaw/) on 2026-04-27 — three days after release — that **OpenClaw switched its default model to V4-Flash**. The article frames the decision as a capability-density bet:

> "V4 Flash, designed with 284 billion parameters and 13 billion activated parameters, is now the default model, delivering Max mode inference performance close to the 1.6 trillion parameter V4 Pro."

This validates the report's [Choosing-the-model](/deepseek-v4/api/#choosing-v4-pro-vs-v4-flash) recommendation that Flash-Max often gets "within 1 pp of Pro-High" on math/code (Tables 6 and 7) at fractional cost.

---

### Industry reactions (date-stamped)

**Neil Shah, VP of Research at Counterpoint Research** (via [CNN](https://www.cnn.com/2026/04/24/tech/chinas-ai-deepseek-v4-intl-hnk)):

> "DeepSeek's V4 preview [is] a serious flex"

— specifically calling out the lower-than-prior-models inference cost.

**Ivan Su, Senior Equity Analyst at Morningstar** (via CNN, same article):

> V4's debut is unlikely to have the same market impact as R1, because traders have already priced in the reality that Chinese AI is competitive and cheaper to use.

This reads as: V4 is a strong product, but the *thesis* it represents (open-weight Chinese frontier-class) is no longer surprising. Markets digested R1's January 2025 jolt; V4 is the natural next step, not a paradigm shift.

**Lian Jye Su, Chief Analyst at Omdia** (via [US News](https://www.usnews.com/news/business/articles/2026-04-24/chinas-deepseek-rolls-out-a-long-anticipated-update-of-its-ai-model)):

> "Based on the benchmark results, it does appear DeepSeek V4 is going to be very competitive against its U.S. rivals."

Omdia frames the gap as "**3 to 6 months** behind state-of-the-art on the hardest coding and reasoning benchmarks, but delivers near-frontier performance at roughly a third of the API cost." That's the same lag Simon Willison cited at launch (see [Community reception](#simon-willison)) — independent confirmation from a different analyst house.

---

### Geopolitical / IP controversy (2026-04 ongoing)

The April 24 V4 launch coincided with a sharper Western public stance on Chinese model distillation:

- **Anthropic and OpenAI** have accused DeepSeek of "illegally extracting capabilities" from their models — i.e., training V3/R1/V4 against Anthropic and OpenAI completions to copy capabilities.
- **Michael Kratsios, White House OSTP director**, on 2026-04-23 issued a memo accusing "foreign entities primarily based in China" of conducting "industrial-scale" campaigns to "distill" frontier AI models from US companies. The memo did not name DeepSeek, but the context made the implication clear.
- Source: [TechCrunch coverage](https://techcrunch.com/2026/04/24/deepseek-previews-new-ai-model-that-closes-the-gap-with-frontier-models/).

**For deployers**: this is a legal-risk axis to watch but not — at this writing — an obstacle to using V4 commercially. The MIT licence on the open weights is unaffected by these accusations; the legal exposure (if any) sits with DeepSeek, not its downstream users. But the political environment around Chinese open-weight models in the US is hardening, and a deployer who commits operational dependencies to V4 should plan for the possibility that future regulation tightens beyond what the current MIT licence permits.

---

### Community quantisations (within 48 hours of release)

Two community conversions had landed by 2026-04-26:

| Conversion | Format | Size on disk | Repo |
|:--|:--|:--|:--|
| **V4-Flash GGUF** | GGUF (deepseek2 architecture, registered as 158B params) | ~170 GB | [tecaprovn/deepseek-v4-flash-gguf](https://huggingface.co/tecaprovn/deepseek-v4-flash-gguf) |
| **V4-Flash 8-bit MLX** | MLX 8-bit (mlx-lm 0.31.3) | 302 GB | [mlx-community/deepseek-ai-DeepSeek-V4-Flash-8bit](https://huggingface.co/mlx-community/deepseek-ai-DeepSeek-V4-Flash-8bit) — **11K downloads in the first month** |
| **Unsloth V4-Flash** | Fine-tuning-optimised re-pack of the official weights | (varies) | [unsloth/DeepSeek-V4-Flash](https://huggingface.co/unsloth/DeepSeek-V4-Flash) |
| **Unsloth V4-Pro** | Fine-tuning-optimised re-pack of the official weights | (varies) | [unsloth/DeepSeek-V4-Pro](https://huggingface.co/unsloth/DeepSeek-V4-Pro) |

**Important caveat for further quantisation**: V4 ships in mixed FP4 (routed experts + lightning indexer) + FP8 (everything else). Sub-Q4 quantisation is unlikely to produce usable output because the source weights are *already* at 4-bit precision in the most parameter-heavy modules. The GGUF and MLX-8bit conversions both up-cast and re-quantise.

**V4-Pro at 1.6T parameters** is not yet a realistic local-deploy target — even at GGUF 4-bit it would land somewhere around 800 GB on disk, far above any consumer hardware. Flash is the realistic local target.

**Unsloth's variants** of both V4-Pro and V4-Flash appeared 1–2 days after release. Unsloth specialises in low-VRAM fine-tuning; their re-packs use the same MIT-licensed weights but reorganised to make LoRA / QLoRA training tractable on smaller setups. For teams planning to fine-tune V4 (rather than infer against it), the Unsloth variants are usually the fastest path.

Source: [tecaprovn/deepseek-v4-flash-gguf](https://huggingface.co/tecaprovn/deepseek-v4-flash-gguf), [mlx-community/deepseek-ai-DeepSeek-V4-Flash-8bit](https://huggingface.co/mlx-community/deepseek-ai-DeepSeek-V4-Flash-8bit), [unsloth/DeepSeek-V4-Pro](https://huggingface.co/unsloth/DeepSeek-V4-Pro), [unsloth/DeepSeek-V4-Flash](https://huggingface.co/unsloth/DeepSeek-V4-Flash), [allthings.how — DeepSeek V4 GGUF Status](https://allthings.how/deepseek-v4-gguf-status-what-runs-locally-and-what-doesnt/).

---

## Watching for

Threads to monitor as the V4 ecosystem matures:

- **r/LocalLLaMA and X / Twitter** for substantive technical reception once community threads accumulate beyond launch-week chatter.
- **DeepSeek's own [API change log](https://api-docs.deepseek.com/updates)** for V4-specific updates (price changes, new endpoints, deprecations beyond the July 24 retirement).
- **Hugging Face model card READMEs** for V4-Pro and V4-Flash to stabilise — these will eventually carry community usage notes that are currently scattered across third-party blogs.
- **Further community fine-tunes, distillations, and quantisations** beyond the iter-35 snapshot of GGUF + MLX + Unsloth.
