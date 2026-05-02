---
title: Self-Hosting V4
subtitle: Hardware budgets, serving frameworks, and the realistic options for running V4-Pro and V4-Flash on your own infrastructure.
eyebrow: DeepSeek V4
layout: page
permalink: /deepseek-v4/self-hosting/
---

<div class="page-tldr" markdown="1">
<span class="page-tldr__label">In one paragraph · Last verified 2026-04-27</span>

**V4-Flash on 2× H100 80GB or 1× H200 is a tractable single-server target**; V4-Pro at 1.6T total parameters is cluster-class only (8× H100/H200/B200 or Huawei Ascend 910C). Serving frameworks supported day-0: **NVIDIA NIM** (A100/H100/H200/B200), **SGLang** (LMSYS Day-0 walkthrough), **vLLM** (vLLM-Ascend tutorial), **llama.cpp/GGUF** (Flash only), **MLX** (Flash on M2/M3 Ultra 192GB). Real-world throughput: V4-Pro on 8× B200 hits **~199 tok/s**, V4-Flash on 4× H200 hits **~266 tok/s**; B200 delivers ~3× the throughput of H200 on V4 specifically. **TTFT 300–500ms in Non-Think mode** is the headline interactive-UX advantage. The hidden cost of self-hosting: you lose DeepSeek's prefix-cache discount (12× cheaper input on cache hits) — usually pure money on the table for caching-friendly workloads.
</div>

<details class="page-toc" open markdown="1">
<summary>On this page</summary>

* TOC
{:toc}
</details>

The honest version: **V4-Pro is a cluster-class deployment**; **V4-Flash is the realistic single-node target**. This page walks through hardware budgets, serving stacks, and when self-hosting makes sense versus calling the API.

---

## When to self-host

Use the [hosted DeepSeek API](https://api-docs.deepseek.com) or an [alternative provider](/deepseek-v4/api/#alternative-api-providers--where-else-to-call-v4) unless one of these applies:

| Reason | Notes |
|:--|:--|
| **Compliance / data residency** — you can't send tokens to the PRC-jurisdiction API. | NIM (US), DeepInfra (US), or self-hosted on your own VPC are the answer. |
| **Per-token economics at very high volume** — your spend has crossed the breakeven where renting GPUs by the hour beats per-token API pricing. | Run a small batch through both, compare. With V4-Flash at $0.14/$0.28 per 1M tokens, the breakeven is *high* — typically multi-billion-token-per-month workloads. |
| **Latency floor** — you need predictable single-digit-second TTFB independent of API queue depth. | Direct serving on hardware you control. |
| **Custom fine-tuning** — you're running domain-specialised V4 weights. | Required; the hosted API doesn't accept fine-tunes. |
| **Air-gapped deployment** — the model has to run somewhere with no internet. | Required. |

If none of these apply, the API is faster, cheaper, and more reliable than your first deployment will be.

---

## Hardware budgets

### V4-Flash (recommended local target)

- **Total params**: 284B (`hidden_size: 4096`, 43 layers, 64 heads).
- **Active params**: 13B per token.
- **On-disk weight footprint**:
  - Original FP8 + FP4 mixed: roughly **150 GB** (the FP4-routed-experts save substantial space).
  - GGUF Q8: ~170 GB on disk ([tecaprovn/deepseek-v4-flash-gguf](https://huggingface.co/tecaprovn/deepseek-v4-flash-gguf)).
  - MLX 8-bit: 302 GB ([mlx-community/deepseek-ai-DeepSeek-V4-Flash-8bit](https://huggingface.co/mlx-community/deepseek-ai-DeepSeek-V4-Flash-8bit)).
- **Realistic minimum hardware**:
  - **2× H100 80GB** (NVLink) — runs in mixed FP8/FP4, comfortable headroom for 256K context.
  - **1× H200 141GB** — fits weights + a useful KV cache budget at moderate context.
  - **1× B200 192GB** — same picture, faster on the FP4 path.
  - **Apple M2/M3 Ultra (192GB unified)** via MLX — feasible at small batch and moderate context; community has reported single-digit tokens/sec.
  - **Consumer hardware** (4090, M3 Max 64–96GB) — only with aggressive sub-Q4 quantisation, and per the [community-quantisations note](/deepseek-v4/news/#community-quantisations-within-48-hours-of-release), sub-Q4 is unlikely to produce usable output because V4 ships in FP8 + FP4 already.
- **KV cache budget**: at 1M context, V4-Flash uses ~7% of V3.2's KV cache (per tech report Section 2.3.4). Practically: **plan ~30 GB extra HBM headroom for 1M context** beyond the weight footprint.

### V4-Pro (cluster-class)

- **Total params**: 1.6T (`hidden_size: 7168`, 61 layers, 128 heads).
- **Active params**: 49B per token.
- **On-disk weight footprint**: roughly **800 GB** in mixed FP8 + FP4. Even at 4-bit GGUF, ~800 GB is not realistic for consumer hardware.
- **Realistic minimum hardware**:
  - **8× H100 80GB** with TP+EP+PP parallelism — the standard "MoE-large" cluster shape.
  - **8× H200 141GB** — substantially better KV-cache headroom for long context.
  - **NVIDIA Blackwell 8× B200 cluster** — the fastest path; FP4 tensor cores match the QAT'd routed experts directly.
  - **Huawei Ascend 910/910C clusters** — explicitly supported per the V4 tech report Section 3.1; pricing in mainland-China deployments is reportedly competitive.
  - **Mac Studio, single-server prosumer hardware**: not feasible. The MoE expert pool alone is too wide.
- **KV cache budget**: at 1M context, V4-Pro uses ~10% of V3.2's KV cache. Plan **~80 GB HBM** extra for 1M context across the cluster.

For both variants the architectural-decision rationale ("V4-Pro reuses V3's exact backbone shape (7168 / 61 / 128); the parameter growth comes entirely from MoE expansion") is on the [Architecture decisions](/deepseek-v4/technical/#architecture-decisions-journal) page.

---

## Serving frameworks (released or working as of 2026-04-27)

### NVIDIA NIM

The cleanest path for teams with NVIDIA-class hardware. The [V4-Pro NIM container](https://catalog.ngc.nvidia.com/orgs/nim/teams/deepseek-ai/containers/deepseek-v4-pro) supports A100, H100, H200, and B200; the V4-Flash container has the same backing. Drop-in OpenAI-compatible endpoint at the container.

Tradeoff: NVIDIA Open Model Agreement licensing on top of the model's MIT, which adds some operational friction for teams that need the licensing chain documented end-to-end.

### SGLang

LMSYS published a Day-0 walkthrough ([*DeepSeek-V4 on Day 0*](https://www.lmsys.org/blog/2026-04-25-deepseek-v4/)) covering V4 deployment via SGLang with the FP4 + FP8 mixed-precision path enabled. Recommended for teams already running SGLang for V3.

### vLLM

vLLM-Ascend documents a [V4-tutorial path](https://docs.vllm.ai/projects/ascend/en/v0.13.0/tutorials/DeepSeek-V4.html) for Huawei Ascend deployments. Standard vLLM (NVIDIA path) is also expected to support V4 via its DeepSeekMoE backend; check vLLM's release notes for the specific commit / version that adds CSA + HCA support.

### llama.cpp / GGUF

For V4-Flash only, realistically. The community-published [tecaprovn/deepseek-v4-flash-gguf](https://huggingface.co/tecaprovn/deepseek-v4-flash-gguf) registers as a 158B-parameter model under the `deepseek2` GGUF architecture. Runs via standard llama.cpp; expect single-digit tokens/sec on Apple Silicon, faster on NVIDIA with `cuBLAS`.

### MLX (Apple Silicon)

The [mlx-community 8-bit conversion](https://huggingface.co/mlx-community/deepseek-ai-DeepSeek-V4-Flash-8bit) runs via [`mlx-lm`](https://github.com/ml-explore/mlx-lm) 0.31.3+. 302 GB on disk; you'll want a 192 GB+ unified-memory Mac Studio. Tokens/sec figures from the community are mid-single-digit at small batch.

---

## Memory budget math (worked example)

A team wants to serve V4-Flash for an internal agent product. Expected workload: 32K-context input, 4K-context output, batch size 8.

| Component | Memory (rough) |
|:--|--:|
| Model weights (FP8 + FP4 mixed) | ~150 GB |
| KV cache for 8 × 36K tokens at FP8, 1 KV head, MLA-compressed | ~2 GB |
| Activations (batch 8, 36K) | ~6 GB |
| Framework overhead (vLLM / SGLang) | ~4 GB |
| **Total HBM needed** | **~162 GB** |

Fits cleanly on **2× H100 80GB** with NVLink, or **1× H200**. Doubling context to 1M roughly doubles the KV cache (still small thanks to V4's 7% KV cache vs V3.2 — ~20 GB at 1M for batch 1) but pushes total memory only into the 175 GB range, comfortable on 2× H100 with margin.

**Caveat**: this back-of-envelope math ignores expert-parallelism overheads, framework-specific quirks, and any custom kernels. Always benchmark on the specific cluster before committing.

---

## Real-world throughput (community-published, not DeepSeek-published)

DeepSeek has not published official per-GPU latency or throughput figures for V4. The numbers below are from third-party measurements within 72 hours of release; treat them as ballpark, and benchmark on your own cluster before sizing.

### Single-stream decode throughput (tokens/sec/GPU)

LMSYS's [Day-0 walkthrough](https://www.lmsys.org/blog/2026-04-25-deepseek-v4/) measured single-batch decode at OSL=4096 on a 30K-token prefix:

| Configuration | Peak TPS | Under load | Drop |
|:--|--:|--:|:--|
| **V4-Pro (1.6T)** on **B200 × 8**, TP=8 | 199 | 180 | -10% |
| **V4-Flash (285B)** on **H200 × 4**, TP=4 | 266 | 240 | -10% |

**B200 vs H200 ratio**: roughly **3× higher throughput** for V4 on B200 vs H200 in aggregate batched serving — the FP4 tensor cores match V4's QAT'd routed-expert weights directly.

### Framework comparisons

For DeepSeekMoE-class workloads on H100s ([Particula benchmark](https://particula.tech/blog/sglang-vs-vllm-inference-engine-comparison)):

- **SGLang on H100 × 8**: ~16,200 aggregate tokens/sec (batched serving).
- **vLLM on H100 × 8**: ~12,500 aggregate tokens/sec.
- **Advantage**: SGLang ~29% over vLLM at the time of measurement.

This advantage is for older DeepSeek versions; V4-specific numbers are LMSYS's Day-0 measurements above. Both engines are iterating quickly post-launch.

### Time-to-first-token

| Variant + mode | TTFT (typical) | Source |
|:--|--:|:--|
| V4-Flash, Non-Think | 300–500ms | [BSWEN coding test](https://docs.bswen.com/blog/2026-04-26-deepseek-v4-flash-performance-metrics/) |
| V4-Flash, Reasoning Max | 1.04s | [Artificial Analysis](https://artificialanalysis.ai/models/deepseek-v4-flash) |
| Open-weight median (for context) | 2.12s | Artificial Analysis |
| V4-Flash output rate | 83–150 tok/s | Multiple, varies by provider |

The 300–500ms TTFT in Non-Think mode is genuinely fast — at the lower end it's close to "type-and-display" latency on a fast network. This is one place V4-Flash punches above its weight class for interactive use.

### Caveats on these numbers

- **Reasoning effort dominates** any throughput comparison. Flash-Max generates the same chain-of-thought tokens as Pro-Max for a given problem; the per-token cost is lower but the token count is the same. End-to-end latency for hard reasoning tasks can be 30+ seconds either way.
- **Provider variance**: 83 tok/s vs 150 tok/s is the same model on different upstream hosts. OpenRouter routes to whichever provider has capacity, so real production latency is not deterministic.
- **Long-context degradation**: at 1M context the per-token decode cost grows beyond what these numbers show. The CSA + HCA architecture cuts FLOPs to ~27% of V3.2 at 1M, but ~27% of a much-larger workload is still substantial.

---

## What you don't get from self-hosting

- **Context caching**. The hosted DeepSeek API offers prefix caching at 12× discount on cache-hit input tokens. Recreating that infrastructure in your own deployment is non-trivial — you'd need to integrate with vLLM's prefix cache, persist it across restarts, and route requests by prefix hash. For most teams the hosted API's caching is a pure cost win you walk away from.
- **Auto-failover and capacity** that the hosted API gives you for free.
- **Pricing transparency**. Once you're paying GPU-hours, your effective per-token cost depends on utilisation, batch shapes, and how good your dispatch logic is. Easy to be surprised by a 3× difference vs the hosted API in either direction.

---

## When to revisit

The community is iterating quickly on V4 deployment in the days after launch. Revisit this page if you're planning a deployment more than a month from the V4 release:

- New quantisations may make consumer-class V4-Flash feasible.
- vLLM and TensorRT-LLM support typically lands within 1–2 weeks of a new MoE arch.
- Distillation work usually appears at the 3–6 month mark — a smaller "V4-Mini" community model could change the local-deploy economics dramatically.

For now (2026-04-27), **the realistic local-deploy story is V4-Flash on 2× H100 or 1× H200, served via NIM or SGLang.**
