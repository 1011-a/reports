# Tests

The `run.py` harness implements the three reproducible test prompts specified
at <https://1011-a.github.io/reports/deepseek-v4/testing/>. Drop in your
`DEEPSEEK_API_KEY` and execute.

```sh
export DEEPSEEK_API_KEY="sk-..."
pip install openai
python tests/run.py                 # runs all three tests
python tests/run.py test-1-coding   # runs a single test by id
```

Transcripts land in `tests/transcripts/` as JSON files, one per run, with the
full request, response, latency, and token usage. The directory is gitignored
by default so commit them deliberately if you want them on the public site.

See the [Independent Testing](https://1011-a.github.io/reports/deepseek-v4/testing/)
page for the prompt rationale, pass criteria, verdict signals, and cost
estimates per run.
