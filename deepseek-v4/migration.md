---
title: V3 → V4 Migration Guide
subtitle: What changes, what stays the same, and how to estimate the cost / capability delta for an existing DeepSeek-V3 deployment.
eyebrow: DeepSeek V4
layout: page
permalink: /deepseek-v4/migration/
updated: 2026-04-27
---

<div class="page-tldr" markdown="1">
<span class="page-tldr__label">In one paragraph · Last verified 2026-04-27</span>

The migration is **a one-line code change**: swap `deepseek-chat` or `deepseek-reasoner` for `deepseek-v4-flash` or `deepseek-v4-pro`. Auth, base URL, request shape, streaming, and tools are unchanged. Hard deadline: **2026-07-24, 15:59 UTC** — legacy IDs return 404 after that. Cost re-routing usually wins: a `deepseek-reasoner` workload migrating to **V4-Flash + Thinking** lands ~4.9× cheaper. Watch for the documented format-strictness regression vs Opus before flipping production traffic on instruction-strict prompts.
</div>

<details class="page-toc" open markdown="1">
<summary>On this page</summary>

* TOC
{:toc}
</details>

If you have an existing DeepSeek V3 (or V3.2, R1, `deepseek-chat`, `deepseek-reasoner`) integration, this is the page that tells you how much work the move costs and what you get back.

**The headline: it's a one-line code change**, plus a deliberate decision about which V4 variant fits your workload. The harder questions are about cost optimisation and behavioural deltas.

---

## At a glance

| Axis | What you do |
|:--|:--|
| **Code** | Change the `model` parameter to `deepseek-v4-pro` or `deepseek-v4-flash`. That's it. |
| **Auth, base URL, request shape, streaming, tools, JSON mode** | Unchanged. |
| **Hard deadline** | `deepseek-chat` and `deepseek-reasoner` are **retired after 2026-07-24, 15:59 UTC**. After that date they will return 404. |
| **Budget recalibration** | Recompute monthly spend with the [cross-vendor table](/deepseek-v4/api/#cross-vendor-pricing-usd-per-1m-tokens-mainline-tier-no-caching) — most workloads land **30–60% cheaper** on V4-Flash, similar or slightly cheaper on V4-Pro. |
| **Capability recalibration** | Decide whether your prompts can now use the 1M-context window meaningfully (most existing prompts won't change). |

---

## Step 1 — change the model parameter

The minimum-viable migration. If you're using the OpenAI Python SDK against `https://api.deepseek.com`:

```diff
  resp = client.chat.completions.create(
-     model="deepseek-chat",
+     model="deepseek-v4-flash",
      messages=messages,
  )
```

Or for the reasoning model:

```diff
  resp = client.chat.completions.create(
-     model="deepseek-reasoner",
+     model="deepseek-v4-pro",  # or stay on v4-flash for cheaper Thinking mode
      messages=messages,
  )
```

That's the entire required change. If your code stops working, the issue is **not** the model swap — it's something else (auth, network, malformed request).

---

## Step 2 — pick the right variant

V3 had two models (`chat` and `reasoner`). V4 collapses to two new ones, but the axis is different:

| If you were using… | And you wanted… | Switch to | Why |
|:--|:--|:--|:--|
| `deepseek-chat` | Cheap general chat | `deepseek-v4-flash` | Half the input cost of `chat`, better quality across all benchmarks (Table 1). |
| `deepseek-chat` | Best quality, cost not the object | `deepseek-v4-pro` | Frontier-class with V4-Pro-Max reasoning effort. |
| `deepseek-reasoner` | CoT for reasoning | `deepseek-v4-pro` (Thinking mode) | More capable reasoning, hybrid Thinking/Non-Think modes. |
| `deepseek-reasoner` | CoT but on a budget | `deepseek-v4-flash` (Thinking mode) | Flash-Max often within 1 pp of Pro-High on math (Table 7). |
| `deepseek-r1` | Open-weights reasoning | Self-host `DeepSeek-V4-Flash` | Same MIT license, MoE with 13B active params. |

V4's hybrid Thinking/Non-Thinking switch means **one model serves both your chat and reasoner endpoints**. Most existing V3 deployments can collapse two models into one, simplifying their operational footprint.

---

## Step 3 — recalibrate cost

Pull last month's V3 spend, multiply by the relevant ratio:

| Old model | New model | Input cost ratio | Output cost ratio |
|:--|:--|--:|--:|
| `deepseek-chat` ($0.27 in / $1.10 out) | `deepseek-v4-flash` | **0.52×** | **0.25×** |
| `deepseek-reasoner` ($0.55 in / $2.19 out) | `deepseek-v4-pro` | **3.16×** | **1.59×** |
| `deepseek-reasoner` | `deepseek-v4-flash` (with Thinking) | **0.25×** | **0.13×** |

(Old V3 prices from DeepSeek's V3-era pricing card; new prices verified from [api-docs.deepseek.com](https://api-docs.deepseek.com/quick_start/pricing).)

**Worked example** — a team running 30M tokens/mo of input + 5M tokens/mo of output through `deepseek-reasoner`:

- **Old monthly cost**: 30 × $0.55 + 5 × $2.19 = $16.50 + $10.95 = **$27.45**
- **New on V4-Pro**: 30 × $1.74 + 5 × $3.48 = $52.20 + $17.40 = $69.60 (**2.5× more expensive** — but with much better capability)
- **New on V4-Flash + Thinking**: 30 × $0.14 + 5 × $0.28 = $4.20 + $1.40 = **$5.60** (**4.9× cheaper than V3-reasoner**)

Most teams should land somewhere between these two depending on quality requirements. The tech report's Table 7 shows V4-Flash-Max often matches V3.x-class reasoning quality — so for many workloads the right move is **Flash + Thinking**, not Pro.

---

## Step 4 — capability deltas to be aware of

Things V4 does *differently*, not just better:

### 1. Context window: 160K → 1M

V3's 160K (`max_position_embeddings: 163840`) becomes V4's 1M (`max_position_embeddings: 1048576`). If your existing prompts hit the V3 cap, V4 unlocks ~6× more headroom. If they didn't, **nothing changes** — the model just has more space available.

Use cases newly enabled:
- Whole-codebase analysis (most repos fit in 1M).
- Multi-document literature reviews.
- Multi-turn conversation logs without summarisation.

### 2. Reasoning is hybrid, not separate

V3 split chat-vs-reasoner into two model IDs. V4 puts both modes in a single model with a **reasoning-effort axis** (Non-Think / High / Max). Caller-side implication: if your code branches on "is this a reasoning call?" today, you can collapse that branch.

The reasoning-effort modes use different context windows for the chain-of-thought:

| Mode | Reasoning context |
|:--|:--|
| Non-Think | 8K |
| High | 128K |
| Max | **384K** |

Max mode genuinely uses long context for thought, not just the user prompt. Plan for the latency / cost implications.

### 3. New API features

Both work on V3 too, but worth flagging because V4 documents them with specific examples now:

- **JSON mode** (`response_format={"type": "json_object"}`) — see [API page](/deepseek-v4/api/#json-mode).
- **Function calling** with optional strict-mode against a beta endpoint — see [API page](/deepseek-v4/api/#function-calling--tool-use).

### 4. Behavioural deltas vs V3

DeepSeek's own assessment in their tech report (Section 5.4) flags one regression to watch for: **V4-Pro-Max occasionally overlooks specific formatting constraints** vs Opus, and is less proficient at condensing extensive text inputs into succinct summaries. The same is likely true vs V3.x for these specific axes.

If your existing V3 integration depends on precise format adherence (XML-bracketed output, hard-line-length limits, etc.), test before cutting over.

### 5. Knowledge gap closes for non-English content

V4 reports significant gains on Chinese-language benchmarks (C-Eval 92.1 / 93.1 vs V3.2's 90.4) and on multilingual knowledge (MultiLoKo 51.1 for Pro-Base vs V3.2's 38.7). If you have a Chinese-language application, the migration is more compelling than for English-only.

---

## Step 5 — the retirement deadline

```
2026-07-24 15:59 UTC — deepseek-chat and deepseek-reasoner cease to respond.
```

Until then, the legacy IDs **transparently route to V4-Flash** (Non-Think and Thinking modes respectively). So you have two strictly-positive choices:

1. **Migrate explicitly to `deepseek-v4-flash` or `deepseek-v4-pro` now** — the only required change is the `model` parameter, and you get to pick the variant deliberately.
2. **Do nothing until July 24** — your existing code keeps working on the V4-Flash backend with no behaviour change you'll notice. After the deadline, you must have moved.

There is no "stay on V3" option after July 24, 2026 unless you self-host the open weights.

---

## Step 6 — operational checklist

Before flipping production traffic:

- [ ] Update the `model` parameter in production code paths.
- [ ] Re-run your prompt-regression suite (you have one, right?). Pay particular attention to format-strict prompts.
- [ ] Verify cost projections against this month's traffic.
- [ ] Decide whether to consolidate `chat`-style and `reasoner`-style call sites onto a single model.
- [ ] Update telemetry: model name in logs, dashboards, alerting.
- [ ] If you use the legacy IDs, set a calendar reminder for **2026-07-15** to confirm the cutover ahead of the July 24 deadline.

---

## Future-proofing — what V5 is likely to look like

V4 is a **preview** release. Section 6 of the V4 tech report explicitly commits DeepSeek to seven future directions; planning a V4 deployment without thinking about which of those land in V5 (likely Q4 2026 or Q1 2027) leaves cost and migration savings on the table.

| Likely V5 change | Plan now |
|:--|:--|
| **Architectural simplification** — DeepSeek explicitly commits to distilling V4's stack to "its most essential designs." | Don't write code that depends on the *internals* of CSA/HCA/mHC layer schedules. The API surface should stay stable; the implementation will not. |
| **Multimodality** — committed in Section 6, missing in V4. | If your application needs image/video/audio, V4 isn't the answer. Either wait for V5 or bridge through a multimodal model on the input side. |
| **Sparser embedding modules** — Section 6 cites Cheng et al.'s [Engram](https://arxiv.org/abs/2601.07372) (conditional memory) as a research direction. | Likely manifests as memory-augmented or retrieval-augmented capability inside the model. May reduce the need for external RAG layers. |
| **Lower-latency architectures** — committed for "more responsive long-context deployment." | Streaming-token-out latencies will likely improve in V5. If you're currently working around V4-Flash latency at the long tail, that pain point may resolve naturally. |
| **Long-horizon multi-round agentic tasks** — research direction. | Today's V4-Pro is competitive on single-turn agent tasks (Terminal-Bench 67.9, SWE-Pro 55.4) but not yet on long-horizon ones. V5 likely targets this gap directly. |
| **Better data curation and synthesis** — ongoing. | Knowledge-breadth gaps vs Gemini-3.1-Pro (SimpleQA-Verified 57.9 vs 75.6) are a function of pre-training data composition. V5 is likely where DeepSeek closes more of that gap. |
| **Training-stability theory** — turn Anticipatory Routing and SwiGLU Clamping from empirical fixes to principled methods. | Doesn't directly affect deployment, but a V5 with more principled training will likely be cheaper to retrain or fine-tune downstream. |

### Pricing-trajectory expectation

V4 launched at substantially lower prices than the V3 / V3.2 generation. The historical DeepSeek pricing trajectory: each major release cuts effective $/intelligence by roughly half. If that pattern holds, V5 may launch at:

- V5-Flash: ~$0.07 in / $0.14 out
- V5-Pro: ~$0.87 in / $1.74 out

These are **purely extrapolation**. DeepSeek has not announced V5 pricing or even confirmed V5 timing. Plan budgets against current V4 prices but don't lock in long-term contracts that assume V4 prices hold.

### What V4 commitments likely persist into V5

Some V4 design choices look load-bearing across generations:

- **MIT license on open weights** — three releases now (V3, V3.2, V4) under MIT. Likely V5 too.
- **OpenAI-compatible API surface** — `base_url` + drop-in OpenAI-SDK call shape. Same model-parameter-only migration story should apply V4 → V5.
- **DeepSeek Sparse Attention** — used in V3.2 and V4, fundamental enough that V5 will almost certainly retain it.
- **DeepSeekMoE** — the MoE backbone has been continuous from V2 onward.
- **Auxiliary-loss-free balancing (`noaux_tc`)** — DeepSeek's own contribution; will keep iterating, won't drop.

### What V4 commitments are at risk

Probably-not-load-bearing pieces that V5 might drop:

- **Hash routing** as a load-balance backstop — explicitly framed as a training-stability aid; once `noaux_tc` matures, hash routing may go.
- **The exact CSA + HCA split** — if a unified learned-compression scheme outperforms in ablation, the m/m′ duality goes.
- **Anticipatory Routing as a runtime knob** — DeepSeek explicitly wants to understand and replace it.

If your code depends on observing any of these specific implementation details (e.g., scraping `compress_ratios` to schedule something), be prepared to re-engineer in the V5 era.

---

## Source documents

- [DeepSeek V4 Preview Release announcement](https://api-docs.deepseek.com/news/news260424) — official deprecation timeline.
- [DeepSeek API pricing](https://api-docs.deepseek.com/quick_start/pricing) — current per-token rates.
- [Hugging Face — DeepSeek-V4-Pro](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) — open-weights model card.
- This report's [Benchmarks](/deepseek-v4/benchmarks/) page — Tables 1, 6, and 7 give the head-to-head capability picture used in the Step 2 routing recommendations.
