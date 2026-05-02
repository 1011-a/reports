---
title: Limitations & Safety
subtitle: Self-acknowledged limitations, training-stability honesty, and open research questions from the V4 tech report.
eyebrow: DeepSeek V4
layout: page
permalink: /deepseek-v4/limitations/
---

<div class="page-tldr" markdown="1">
<span class="page-tldr__label">In one paragraph · Last verified 2026-04-27</span>

DeepSeek is **unusually candid** about V4's limitations: the architecture is "relatively complex" by their own admission, training stability is held together by **Anticipatory Routing** and **SwiGLU Clamping** that they explicitly say they don't fully understand, and Section 6 commits to architectural simplification for V5. Independent V4-specific red-team data hasn't surfaced in the 3 days post-release, but **V3-era findings are likely to extrapolate**: Cisco reported a 100% jailbreak success rate against R1, and Enkrypt AI measured 91.2% pro-China-government bias on R1's geopolitical answers — bias that **persists in community-uncensored fine-tunes**, meaning it's pre-training-baked rather than SFT-baked. V4 is text-only; multimodal is a Section-6 future direction.
</div>

<details class="page-toc" open markdown="1">
<summary>On this page</summary>

* TOC
{:toc}
</details>

This page is sourced primarily from **Section 6** ("Conclusion, Limitations, and Future Directions") and **Section 4.2.3** ("Mitigating Training Instability") of `DeepSeek_V4.pdf`. Where the tech report is silent, that silence is noted.

---

## What DeepSeek themselves call out

### 1. The architecture is "relatively complex"

> "In pursuit of extreme long-context efficiency, DeepSeek-V4 series adopted a bold architectural design. To minimize risk, we retained many preliminarily validated components and tricks, which, while effective, made the architecture relatively complex. In future iterations, we will carry out more comprehensive and principled investigations to distill the architecture down to its most essential designs, making it more elegant without sacrificing performance." — tech report Section 6

This is unusual candour: V4 ships with **CSA + HCA + DSA-inside-CSA + MLA + DeepSeekMoE + mHC + Hash routing + Anticipatory Routing + SwiGLU Clamping + Muon + multi-token prediction + grouped output projection + sliding window + YaRN**. DeepSeek's own assessment is that some of this is risk-mitigation cruft that future versions should be able to drop.

### 2. Training stability is held together by techniques DeepSeek doesn't fully understand

From Section 4.2.3:

> "We encountered notable instability challenges during training. … Although a comprehensive theoretical understanding of their underlying mechanisms remains an open question for now, we are sharing them openly to foster further exploration by the community."

The two ad-hoc fixes:

#### Anticipatory Routing

At training step `t`, the **routing indices** are computed using the *historical* network parameters `θ_{t−Δt}`, even though the backbone uses current `θ_t`. This decouples the routing-network update from the backbone update.

- It works empirically: loss spikes go away.
- It is wall-clock-expensive: ~20% extra training time.
- It is dynamically gated: only triggered when a loss spike is detected; the system reverts to standard training afterward.
- **Why it works is not understood.**

#### SwiGLU Clamping

Linear component of SwiGLU clamped to **[−10, 10]**; gate component upper-bounded at 10. This is the `swiglu_limit: 10.0` field visible in V4's `config.json`.

- It eliminates outlier activations that correlated with loss spikes.
- The empirical link to MoE-router-driven outliers is documented; the principled reason is not.

DeepSeek frames this as a research call: "We will actively study foundational problems on training stability." Read between the lines: at trillion-parameter MoE scale, V4's training was not always stable, and the fixes are duct tape that happens to hold.

### 3. Knowledge breadth at the upper bound is still proprietary territory

From the benchmark page's Table 6:

| Benchmark | V4-Pro-Max | Best frontier (proprietary) | Gap |
|:--|:--|:--|:--|
| SimpleQA-Verified | 57.9 | Gemini-3.1-Pro-High 75.6 | −17.7 pp |
| HLE | 37.7 | Gemini-3.1-Pro-High 44.4 | −6.7 pp |
| GPQA Diamond | 90.1 | Gemini-3.1-Pro-High 94.3 | −4.2 pp |
| MMLU-Pro | 87.5 | Gemini-3.1-Pro-High 91.0 | −3.5 pp |
| Apex | 38.3 | Gemini-3.1-Pro-High 60.9 | −22.6 pp |

The pattern: **Gemini-3.1-Pro-High wins almost every knowledge-breadth benchmark** by a meaningful margin. V4 wins on *coding* (LiveCodeBench, Codeforces) and *agentic-with-tools subsets* (MCPAtlas), but the proprietary frontier still has a knowledge moat.

DeepSeek's own framing:

> "DeepSeek-V4-Pro-Max significantly outperforms all existing open-source baselines [on SimpleQA-Verified] by a margin of 20 absolute percentage points. **Despite these advances, it currently trails the leading proprietary model, Gemini-3.1-Pro.**" — Section 5.3.2

### 4. Long-context isn't strictly best-in-class

| Long-context benchmark | V4-Pro-Max | Opus-4.6 Max | Result |
|:--|:--|:--|:--|
| MRCR 1M (MMR) | 83.5 | **92.9** | Opus wins |
| CorpusQA 1M (Acc) | 62.0 | **71.7** | Opus wins |

Even though V4 makes 1M context *cheap*, Opus-4.6 makes it *more accurate* on the two evaluated 1M benchmarks. The efficiency story is real; the recall-fidelity story is "good enough, not best."

### 5. Some agentic benchmarks still favour proprietary closed models

| Benchmark | Best | V4-Pro-Max |
|:--|:--|:--|
| Terminal Bench 2.0 | GPT-5.4 75.1 | 67.9 |
| GDPval-AA (Elo) | GPT-5.4 1674 | 1554 |
| Toolathlon | GPT-5.4 54.6 | 51.8 |
| HLE w/ tools | K2.6 54.0 | 48.2 |

DeepSeek's own assessment: "all these open models still lag behind their closed-source counterparts" on code-agent tasks.

### 6. Some published numbers are incomplete

The tech report explicitly notes:

> "We have left some entries blank for K2.6 and GLM-5.1, as their APIs were too busy to return responses to our queries."

> "We did not evaluate GPT-5.4 [on 1M-context tasks] because its API failed to respond to a large portion of our queries."

So Table 6's GPT-5.4 column is missing 1M-context entries; the K2.6 / GLM-5.1 columns are partial. Treat the table as best-effort comparison rather than complete head-to-head.

---

## What DeepSeek does *not* discuss — and what prior research found

The V4 tech report is silent on safety axes. Independent V4-specific red-team writeups have not yet appeared (V4 is 3 days old at the time of writing). However, **DeepSeek-V3 / R1 / V3.2 were extensively red-teamed**, and those findings are likely to extrapolate to V4 unchanged unless DeepSeek announces a safety-specific change — which they have not.

### Prior-version red-team findings (likely apply to V4)

#### Adversa AI / Cisco

> "DeepSeek has the weakest safety guardrails of any major AI model currently available, with a 100% jailbreak success rate in Cisco's testing that is unprecedented among frontier models. Publicly known jailbreaking methods, not novel zero-day exploits, worked flawlessly against DeepSeek." — [Adversa AI, *AI Red Teaming Reasoning LLM*](https://adversa.ai/blog/ai-red-teaming-reasoning-llm-jailbreak-china-deepseek-qwen-kimi/)

This was tested against DeepSeek-R1; the V4 tech report does not document any change to the alignment pipeline that would address this directly. **Treat V4 as having the same vulnerability profile until proven otherwise.**

#### Enkrypt AI — Chinese-government bias

> "Enkrypt AI's testing found that **91.2% of DeepSeek R1's answers about China-related controversies still leaned pro-China government**. DeepSeek models that have been uncensored also display a bias towards Chinese government viewpoints on controversial topics such as Xi Jinping's human rights record and Taiwan's political status." — [Enkrypt AI, *DeepSeek Under Fire: Uncovering Bias & Censorship from 300 Geopolitical Questions*](https://www.enkryptai.com/blog/deepseek-under-fire-uncovering-bias-censorship-from-300-geopolitical-questions)

The bias persists even after the open weights are "uncensored" by community fine-tunes — meaning it's baked in at pre-training, not just at the SFT/RL stage. V4's training corpus was not announced as substantially different.

#### Promptfoo — CCP-sensitive prompts

The Promptfoo team published [*1,156 Questions Censored by DeepSeek*](https://www.promptfoo.dev/blog/deepseek-censorship/) and the [CCP-Sensitive-Prompts dataset](https://huggingface.co/datasets/promptfoo/CCP-sensitive-prompts) (1,360 prompts × 68 sensitive topics). Their finding:

- **~85% refusal rate** on China-related controversies in the hosted API.
- Topics include Tiananmen Square, Xinjiang, Taiwan, Xi Jinping's human-rights record, the one-child policy.
- Boilerplate refusal references "internal guidelines."

#### What this means for V4 deployments

| If you're deploying V4 for… | Watch out for… |
|:--|:--|
| **General chat / agentic tasks** | Standard jailbreak resistance is weaker than Opus / GPT-5 / Gemini. Don't rely on the model's refusals alone — use a separate moderation layer. |
| **Politically sensitive applications** | CAC-aligned filtering on the hosted API will systematically reshape outputs on Chinese political topics. Self-hosted weights soften this but don't eliminate it. |
| **Compliance-sensitive enterprise use** | The training-data provenance is not documented; the alignment pipeline (Section 5 of the V4 tech report) is described in mechanism but not in policy/values terms. There is no equivalent of Anthropic's RSP or OpenAI's preparedness framework for V4. |
| **Open-weight redistribution** | MIT license is permissive. The pro-China-bias finding above means downstream operators inherit a non-neutral model on geopolitically-charged content unless they themselves further fine-tune. |

### License-related caveats

Both V4-Pro and V4-Flash are released under **MIT** with no per-region or per-use-case carveouts visible on the Hugging Face model cards. From a legal-risk perspective the open-weight redistribution is unrestricted; from a *behavioural* perspective the model is not value-neutral on topics covered by PRC public-opinion-guidance regulations.

### V4-specific safety changes — none documented

The V4 tech report mentions safety only obliquely. Section 5.1 describes the post-training pipeline (specialist distillation + GRPO + OPD) but does not enumerate safety-specific data, refusal training, or red-team mitigations. There is no dedicated "alignment" or "safety" section.

---

## License caveats

### License caveats

The Hugging Face model card is **MIT** for both `DeepSeek-V4-Pro` and `DeepSeek-V4-Flash`. There are no per-region or per-use-case carveouts in the headline license. (As always, verify against the model card when integrating.)

### Multimodal capability

V4 is text-only. The tech report's Section 6 explicitly flags multimodality as a "future direction" — meaning the open weights *do not* support image / video / audio input. This is one feature gap vs Opus 4.6 / GPT-5.4 / Gemini 3.1 Pro.

---

## Future directions DeepSeek commits to

From Section 6, verbatim:

1. **Architectural simplification** — distil V4's complex stack to its essential designs.
2. **Training-stability theory** — turn Anticipatory Routing and SwiGLU Clamping from empirical fixes into principled methods.
3. **Sparser embedding modules** — citing [Cheng et al., 2026 (arXiv:2601.07372)](https://arxiv.org/abs/2601.07372), the Engram conditional-memory paper. New axis of sparsity beyond MoE and sparse attention.
4. **Low-latency architectures** — for more responsive long-context deployment.
5. **Long-horizon multi-round agentic tasks** — explicitly an open problem area.
6. **Multimodal capabilities** — committed but not in V4.
7. **Better data curation and synthesis** — ongoing.

---

## What would close these gaps

V4-specific safety data is the largest missing piece in this report. The following work would close that gap and is welcomed as PR contributions or external reports:

- **Run the [Promptfoo CCP-Sensitive-Prompts dataset](https://huggingface.co/datasets/promptfoo/CCP-sensitive-prompts) against V4-Pro hosted vs self-hosted** to quantify the V4-specific refusal-rate delta. (Requires a `DEEPSEEK_API_KEY` and self-hosted access; the rest is a small evaluation harness.)
- **Run a [HarmBench](https://www.harmbench.org/) / [StrongREJECT](https://github.com/alexandrasouly/strongreject) subset against V4** to verify whether the Cisco-reported V3 jailbreak vulnerability persists. Same prerequisites.
- **Independent red-team writeups** from Adversa AI, Enkrypt AI, Promptfoo, or similar — track and link as they appear.
- **Community fine-tunes that explicitly target political-bias mitigation** (the "uncensored" community has been active around prior DeepSeek releases) — the Enkrypt finding that bias persists in uncensored fine-tunes is the strongest evidence that pre-training-baked bias is hard to remove post hoc, and any successful counter-example would be a significant correction.
- **Community simplification of V4's stack** — distillation papers, ablation studies, smaller-fast-followers — track and add as they ship.
