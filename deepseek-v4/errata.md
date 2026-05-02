---
title: Errata
subtitle: Corrections to claims this report has gotten wrong, dated and traceable.
eyebrow: DeepSeek V4
layout: page
permalink: /deepseek-v4/errata/
---

<details class="page-toc" open markdown="1">
<summary>On this page</summary>

* TOC
{:toc}
</details>

Public reports lose credibility when they silently rewrite history. This page tracks every claim the report has materially gotten wrong, what the correction is, and where the fix landed.

If you spot something we've gotten wrong, open an issue on [github.com/1011-a/reports](https://github.com/1011-a/reports/issues) and it'll show up here once verified.

---

## 2026-04-26 — CSA / HCA naming reverted to official terminology

**Where**: `technical.md`, *Hybrid attention* section.

**Originally claimed (iteration 2)**: V4's two attention layers should be called **"Compress-4-Attention"** and **"Compress-128-Attention"**, with CSA / HCA framed as "earlier shorthand."

**Corrected (iteration 3)**: The official names from `DeepSeek_V4.pdf` Section 2.3 are **CSA (Compressed Sparse Attention)** and **HCA (Heavily Compressed Attention)**. The numbers `4` and `128` in the `compress_ratios` array are the per-layer **compression ratios `m` and `m′`**, not layer names.

**Root cause**: I bought the third-party "Compress-4 / Compress-128" framing from secondary sources (Digital Applied, BuildFastWithAI) before downloading the official tech report. Once the PDF was in hand, the official Section-2.3 terminology made the third-party shorthand wrong.

**Lesson**: prefer primary sources from day one even when they're slightly harder to acquire.

---

## 2026-04-27 — V3 context window: 128K → 160K

**Where**: `technical.md`, V3 → V3.2 → V4 diff table.

**Originally claimed (iteration 2)**: DeepSeek-V3 supports 128K context.

**Corrected (iteration 9)**: V3's `config.json` shows `max_position_embeddings: 163840` (= 160K) with YaRN factor 40. The 128K figure was inherited from informal community discussion that conflated V3's effective context with the original training-time context.

**Root cause**: relied on third-party summaries instead of pulling V3's `config.json` directly. Same lesson as the CSA/HCA correction — primary-source verification first.

---

## 2026-04-27 — Build-time Liquid escaping discipline added after two consecutive failures

**Where**: `CHANGELOG.md`, `deepseek-v4/errata.md`.

**What broke (twice in two iterations)**: iter-21's commit landed a Liquid parse error in the new errata entry; iter-22's first commit landed a different Liquid parse error in `CHANGELOG.md`. Both were caused by writing Liquid syntax inside markdown inline code (single backticks), assuming the backticks would escape it. They do not — Jekyll's Liquid pre-processes the file *before* markdown rendering, so a substring that looks like `{` `% if x %}` (in inline code) gets parsed as a real Liquid tag with no matching `endif` and crashes the build.

**Hotfixes**: iter-21's hotfix wrapped the affected paragraph in `{` `% raw %}…{` `% endraw %}` blocks; iter-22's hotfix rephrased to avoid the literal.

**Root cause**: documenting a bug that *itself* involves Liquid syntax requires the Liquid syntax to be in the prose, but the prose is rendered by Liquid, so the documentation triggers the bug being documented. Recursively unfortunate.

**Permanent fix (iteration 23)**: added `scripts/lint-liquid.py` and a GitHub Actions workflow that runs on every push and PR touching markdown. The lint specifically catches the failure mode that occurred (unguarded `{` `%` or `{` `{` literals inside inline code), without false-positiving on legitimate bare Liquid usage like `{` `{ "/assets/x.png" | relative_url }}` in image references. Future iterations will see CI fail before deploy if they reintroduce the pattern.

**Lessons** (in addition to the iter-20 sidebar lessons):
- **A failure that recurs is a process failure**, not just a content failure. Two consecutive iterations needing the same hotfix means an automated guardrail was overdue.
- **Heuristic CI lints are cheap and earn back their cost on the first prevented failure.** This one is 60 lines of Python.
- **Documenting a bug class while writing in the same syntax that triggers it is a special hazard.** Always reach for `raw` first, prose second.

---

## 2026-04-27 — Per-topic sidebar was silently broken from iter 4 to iter 20

**Where**: `_layouts/page.html`.

**Originally claimed (iterations 4–19)**: when describing the site design, iter 4's commit said the per-topic sidebar was "generated once from `_config.yml`'s `sidebar:` map" and that "future report topics drop in by adding one block." Subsequent iterations described the sidebar as functional, including the iter-19 framing of glossary and errata as new sidebar entries.

{% raw %}
**What was actually true**: from iter 4 (when I dropped the `just-the-docs` remote theme) until iter 20, **the sidebar did not render on any page**. The layout used a `| second` Liquid filter to extract the topic slug from the URL — that filter is provided by `just-the-docs` as a plugin extension, not by Jekyll core. Once the theme was gone, `topic_slug` always resolved to nil, `site.sidebar[nil]` returned nil, and `{% if sidebar_items %}` falsy-killed the entire `<aside>` block. Any reader who landed on a subpage between 2026-04-26 and 2026-04-27 saw page content but no sidebar at all.
{% endraw %}

{% raw %}
**Corrected (iteration 20 bugfix)**: replaced `| split: "/" | second` with explicit array indexing — `url_parts[1]` — which is portable across Jekyll's Liquid implementation. After the fix, sidebars (now grouped Read-first / Detail / Reference) render on all topic pages.
{% endraw %}

**Root cause**: I removed the theme that provided a custom Liquid filter, kept the layout that relied on the filter, didn't curl-check the rendered HTML to verify the sidebar was actually present, and described the design as working in the iteration changelog. Several iterations later (12, 13, 14, 19) I added items to the sidebar config without ever loading a page to see them appear.

**Lessons**:
- **Curl-verify rendered HTML, not just build success.** A green Pages build only proves the site deployed without errors — not that any specific feature works. From now on, after CSS/layout changes, I should curl a representative page and grep for the expected markup.
- **Theme-removal audits**: when removing a dependency, any layout/include that referenced theme-provided helpers must be reviewed.
- **Don't trust your own changelog**: the iter-4 commit confidently described the sidebar as functional. Verify-then-report.

This is the most embarrassing correction in the report's history so far. Documenting it here exactly because the report's value depends on its willingness to do that.

---

## 2026-04-26 → 2026-04-27 — V4 quantisation: FP8 only → FP8 base + FP4 routed experts + FP4 indexer

**Where**: `technical.md`, *Quantisation* section.

**Originally claimed (iteration 2)**: V4 ships in pure FP8 e4m3 format. (Several third-party sources had reported "native FP4 expert weights" and I'd flagged that as likely conflated with NVIDIA Blackwell marketing.)

**Corrected (iteration 3)**: After reading tech report Section 3.4, the actual story is mixed-precision: **FP8 base**, **FP4 (QAT) for routed experts**, **FP4 for the lightning-indexer attention path**. Both earlier framings were partly right — the open-weight checkpoint's headline format is FP8, but the most parameter-heavy paths are FP4.

**Root cause**: the `quantization_config` JSON block only describes the base format. The FP4 details live in the tech report prose (Section 3.4) and the model-card text, not in the structured config.

---

## Tracking the fix

Each correction above is committed in the public history of this repo:

```
git log --oneline -- deepseek-v4/technical.md
```

The `git blame` of any specific claim will surface the iteration in which the current wording was set.

---

## What this page does *not* track

- **Stylistic edits** — sentence rewrites, headline tweaks, layout changes.
- **Additions** — new sources or numbers that were not previously stated wrong, just unstated.
- **Forward-looking speculation** — anything in the [Future-proofing](/deepseek-v4/migration/#future-proofing--what-v5-is-likely-to-look-like) section is by definition unverified prediction. If those predictions miss, that's not errata; the section is structured as speculation from the start.

If a piece of original analysis later proves wrong (e.g., the "CSA may be dropped in V5" speculation does or doesn't hold up), it'll land here as a confirmed correction at that point, not before.
