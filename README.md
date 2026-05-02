# Reports

A growing collection of deep-dive technical reports on AI models, systems, and tooling. Published as a GitHub Pages site at <https://1011-a.github.io/reports>.

## What's here

| Report | Subdirectory | Status |
|:--|:--|:--|
| [DeepSeek V4](https://1011-a.github.io/reports/deepseek-v4/) | `deepseek-v4/` | In progress, primary-source-cited, [errata](https://1011-a.github.io/reports/deepseek-v4/errata/) tracked |

Each report is a long-form, multi-page reference. The DeepSeek V4 report covers Overview, News, Technical Details, API, Migration, Benchmarks, Self-Hosting, Independent Testing, Limitations, References, Glossary, Errata, and an editorial Thesis page. See the [Site map on the V4 topic landing](https://1011-a.github.io/reports/deepseek-v4/#site-map) for the full inventory.

## Repo layout

```
/index.md                                Landing page listing all topics
/<topic>/                                One subdirectory per report topic
  index.md                                 Topic landing + reading paths
  <subpage>.md                             Topic subpages (technical, api, …)
  configs/                                 Mirrored config.json + tokenizer files
/assets/images/<topic>/                  Topic-namespaced images
/assets/css/style.css                    Hand-tuned editorial design system
/_layouts/                               Custom Jekyll layouts
/_includes/                              Header / footer partials
/CHANGELOG.md                            Dated log of every iteration's contribution
/_config.yml                             Site config (topics + grouped sidebar)
/scripts/                                CI lints (Liquid, asset-orphan, anchor-link)
/.github/workflows/lint.yml              GitHub Actions running the three lints
/tests/                                  Reproducible API test harness
```

The site is built with vanilla **Jekyll 4.x** (no remote theme — design is hand-rolled in `_layouts/` + `assets/css/style.css`) and uses kramdown for markdown. Pretty URLs (`permalink: pretty`) are configured.

## Local preview

```sh
bundle install
bundle exec jekyll serve
# -> http://127.0.0.1:4000/reports/
```

## CI checks

Three Python lints run on every push and PR via `.github/workflows/lint.yml`:

| Lint | What it catches |
|:--|:--|
| `scripts/lint-liquid.py` | Unguarded Liquid tags or output expressions inside markdown inline code. Jekyll's Liquid pre-processes before markdown, so backticks don't escape it — the lint catches the iter-21 / iter-22 build-failure pattern |
| `scripts/lint-assets.py` | Image files in `assets/images/` not referenced by any `.md` |
| `scripts/lint-anchors.py` | Internal `#anchor` links pointing at non-existent kramdown headings |
| `scripts/lint-page-weight.py` | Per-file (default 1.5 MB) and total (default 12 MB) asset budgets — flags unoptimised images |

Run them locally:

```sh
python3 scripts/lint-liquid.py
python3 scripts/lint-assets.py
python3 scripts/lint-anchors.py
python3 scripts/lint-page-weight.py
```

## Reporting issues / errata

Material corrections to the report should be raised as [GitHub issues](https://github.com/1011-a/reports/issues). Every accepted correction lands on the per-topic Errata page (e.g., [DeepSeek V4 errata](https://1011-a.github.io/reports/deepseek-v4/errata/)), dated and traceable.

## License

Site source under [MIT](LICENSE); primary-source content cited within (papers, model cards, news articles, etc.) retains its own license terms — see [`NOTICE.md`](NOTICE.md) for the file-level breakdown.
