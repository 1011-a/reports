---
title: Glossary
subtitle: Acronyms and technical terms used throughout this report, defined in one place.
eyebrow: DeepSeek V4
layout: page
permalink: /deepseek-v4/glossary/
---

<details class="page-toc" open markdown="1">
<summary>On this page</summary>

* TOC
{:toc}
</details>

Terms are listed alphabetically. Where a term has a primary source, that paper or section is linked.

---

## Architecture

### CSA — Compressed Sparse Attention

V4's first attention variant. Compresses the KV cache of every **m** (= 4) tokens into one entry, then applies DSA to select the top-k of those compressed entries for full attention. Local fidelity is preserved by a small **sliding window** of recent uncompressed entries. See [tech report Section 2.3.1](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/DeepSeek_V4.pdf), and [the CSA architecture diagram](/deepseek-v4/technical/#hybrid-attention-csa--hca-with-dsa-inside-csa) in the technical page.

### HCA — Heavily Compressed Attention

V4's second attention variant. Aggressively compresses every **m′** (= 128) tokens into one entry, with no further DSA selection (since the count is already small) but the same sliding-window addition. Used interleaved with CSA across V4's layer stack; the per-layer schedule is encoded in `compress_ratios`. See [tech report Section 2.3.2](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/DeepSeek_V4.pdf).

### DSA — DeepSeek Sparse Attention

The lightning-indexer + top-k selection mechanism introduced in [DeepSeek-V3.2 (arXiv:2512.02556)](https://arxiv.org/abs/2512.02556). In V4, DSA lives **inside CSA** as the selector that picks which compressed entries actually receive attention. The `index_*` fields in `config.json` parameterise it (`index_n_heads: 64`, `index_topk: 1024` for V4-Pro).

### MLA — Multi-head Latent Attention

DeepSeek's earlier attention design from V2/V3, where keys and values live in a low-rank latent space (`kv_lora_rank: 512` in V3) and are reconstructed on demand. V4 retains MLA as the substrate; CSA/HCA add compression and selection on top. The single-KV-head config (`num_key_value_heads: 1`) is the visible signature.

### MoE — Mixture of Experts

A transformer architecture where each FFN layer contains many *experts*; a learned router activates only a few per token. V4-Pro: 384 routed experts + 1 shared expert, top-6 active per token. Total parameters 1.6T, active 49B per token.

### DeepSeekMoE

DeepSeek's specific MoE design: fine-grained routed experts, a shared expert always active, and **auxiliary-loss-free balancing** (`noaux_tc`). Introduced in the V3 series and continuous through V4 with only minor adjustments.

### mHC — Manifold-Constrained Hyper-Connections

V4's residual-stream design. An extension of [Hyper-Connections (HC, arXiv:2409.19606)](https://arxiv.org/abs/2409.19606) that projects HC's mixing matrices onto the **Birkhoff polytope** (the manifold of doubly-stochastic matrices) via the Sinkhorn–Knopp algorithm. This restores the identity-mapping property HC sacrifices, at ~6–7% extra training compute. V4 config exposes the parameters: `hc_mult: 4`, `hc_sinkhorn_iters: 20`, `hc_eps: 1e-06`. Primary source: [arXiv:2512.24880](https://arxiv.org/abs/2512.24880).

### MTP — Multi-Token Prediction

A training objective that asks the model to predict the next *D* tokens at each position, not just the next one. V3 introduced it; V4 retains it (`num_nextn_predict_layers: 1`). Densifies training signal and may help the model "pre-plan" its representations. MTP loss weight in V4 is **0.3**.

### Hash routing

A fixed-by-construction routing scheme: each token deterministically maps to specific experts via a hash of the token id. V4 uses 3 hash-routing layers (`num_hash_layers: 3`) alongside the learned `noaux_tc` router as a load-balance safety net at 384-expert scale.

### `noaux_tc`

V4 / V3.2 / V3's auxiliary-loss-free top-k expert selector. Routes tokens to the top **K** experts by a learned scoring function (`scoring_func: sqrtsoftplus` in V4) without an explicit load-balancing auxiliary loss. The "tc" indicates the threshold-correction variant.

---

## Training

### GRPO — Group Relative Policy Optimization

A reinforcement-learning algorithm DeepSeek uses for specialist training. Compares groups of candidate responses to compute relative advantages, avoiding the need for a separate value network. Used inside V4's specialist training before they're consolidated via OPD.

### OPD — On-Policy Distillation

V4's post-training consolidation step that **replaces** V3.2's mixed-RL stage. Domain specialists (each trained with GRPO) are distilled into a single set of weights via on-policy supervised distillation. Primary source: tech report Section 5.1.

### Muon

The optimiser V4 uses for the majority of modules, replacing AdamW. Source: [Jordan et al., 2024](https://kellerjordan.github.io/posts/muon/). Reported to give faster convergence and greater training stability, with DeepSeek-specific adaptations described in tech report Section 2.4.

### Anticipatory Routing

A V4 training-stability technique: at step **t**, the routing indices are computed using *historical* network parameters **θ_{t−Δt}**, not current parameters **θ_t**. Triggered dynamically on loss-spike detection. ~20% wall-clock overhead. Theoretical underpinnings are explicitly an open question for DeepSeek (Section 4.2.3).

### SwiGLU Clamping

A V4 training-stability technique: the linear component of SwiGLU is clamped to **[−10, 10]** and the gate component to **≤ 10**. Eliminates outlier activations correlated with MoE-router-driven loss spikes. Visible in `config.json` as `swiglu_limit: 10.0`.

### YaRN — Yet another RoPE eNgineering

A method for extending the effective context window of a RoPE-based model beyond what was seen in training. V4 trains at 64K context (`original_max_position_embeddings: 65536`) and extends to 1M via YaRN with `factor: 16`. The hybrid CSA/HCA architecture is what makes the extended context actually useful at inference.

---

## Numerical formats

### FP8 — 8-bit floating point (e4m3)

The base weight format for V4: 1 sign bit, 4 exponent bits, 3 mantissa bits. Block-quantised at 128×128 with a UE8M0-formatted scale. Used for everything that isn't a routed-expert weight or the lightning-indexer attention path.

### FP4 — 4-bit floating point

Used for V4's **routed expert weights** and the **lightning-indexer attention** computation. Quantisation-aware-trained (QAT), not post-training-quantised. The win is mostly memory and bandwidth — FP4 × FP8 has the same compute throughput as FP8 × FP8 on current hardware.

### UE8M0

The scale format for V4's FP8 quantisation: 8-bit unsigned exponent, 0 mantissa bits. Encodes scales as powers of 2.

---

## Inference

### MQA — Multi-Query Attention

After CSA's top-k selection, the core attention runs as MQA: each query head has its own projection, but the keys and values are shared across heads. Reduces compute and KV-cache for the actual attention computation.

### Grouped Output Projection

V4's strategy for keeping the output projection FLOPs manageable when the head count is large. Heads are split into groups (`o_groups: 16` in V4-Pro, 8 in V4-Flash); each group is projected to a smaller intermediate then concatenated. See tech report Section 2.3.1.

### Sliding window

V4 attaches a small set of recent **uncompressed** KV entries to both CSA and HCA layers to enhance local fine-grained dependencies. `sliding_window: 128` in `config.json`.

### Reasoning-effort modes

V4's three inference modes — **Non-Think** (no reasoning trace, 8K reasoning context), **High** (128K), **Max** (384K). Reasoning-effort is exposed as a request-time toggle. V4-Pro-Max is "the maximum-reasoning-effort mode of V4-Pro" — what most benchmarks compare against.

---

## Other

### Cache-hit / cache-miss pricing

DeepSeek's API offers context caching: tokens served from a previously-computed prefix are billed at the **cache-hit** rate (V4-Pro: $0.145 / 1M); fresh-processed tokens are billed at the **cache-miss** rate ($1.74 / 1M).

### V4-Pro-Max

Not a separate model — it's the "maximum reasoning effort mode of DeepSeek-V4-Pro." Most DeepSeek-published headline numbers compare V4-Pro-Max to other vendors' max-effort modes (Opus-4.6-Max, GPT-5.4-xHigh, Gemini-3.1-Pro-High).

### `deepseek-chat` / `deepseek-reasoner`

Legacy V3-era model IDs. Currently route to V4-Flash in Non-Think and Thinking modes respectively. Both are **scheduled for retirement after 2026-07-24, 15:59 UTC**.

### Ascend

Huawei's family of NPU accelerators. The V4 tech report explicitly names "NVIDIA GPUs and HUAWEI Ascend NPUs" as deployment targets, with day-0 expert-parallelism optimised for both platforms.

### Engram

The conditional-memory paper ([Cheng et al., arXiv:2601.07372](https://arxiv.org/abs/2601.07372)) cited by V4's tech report Section 6 as the direction sparser embedding modules are heading for V5. Not part of V4 itself.
