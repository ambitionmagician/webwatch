# WebWatch

by Dr. Brent Allen Jensen

Watch web pages for changes. Give WebWatch a list of URLs; it fetches
each one, hashes the content, and tells you which pages are NEW,
UNCHANGED, CHANGED, or unreachable — remembering the last state
between runs.

Run it from cron once an hour and you have a change log for the pages
you care about: terms of service, a pricing page, a status page, a
document that should never change.

## Quickstart

```bash
pip install -r requirements.txt        # just `requests`

cat > urls.txt <<'EOF'
https://example.com/
https://example.com/terms
EOF

python3 webwatch.py urls.txt                       # first run: all NEW
python3 webwatch.py urls.txt --snapshots snaps/    # later: CHANGED pages saved
```

Changes are also appended, timestamped, to `webwatch.log`.

## Options

| Flag | Default | Meaning |
|---|---|---|
| `--state` | `webwatch_state.json` | Where the hashes live between runs |
| `--snapshots DIR` | — | Save a copy of each page whose content changed |
| `--timeout` | 30 | Per-request timeout in seconds |

## Requirements

- Python 3.10+, `requests`

## Notes

- The hash covers the raw response body. Pages with rotating ads,
  timestamps, or CSRF tokens will report CHANGED constantly — that is
  the tool being honest, not broken. Watch stable pages, or pages
  whose every change genuinely matters.
- Be a good citizen: a handful of pages on a polite interval, with the
  default identifiable user agent.

## Support this work

If this tool saved you time or taught you something, donations keep the work going:

- BTC: 15McijPo79Zx58NGyEf2PvaPtGqGmpztWn
- ETH: 0x8C25164E9234E6A30b8E44485B79c5cE8419cF2B

## License

MIT — see [LICENSE](LICENSE).
