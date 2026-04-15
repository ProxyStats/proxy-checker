# Contributing

Thanks for considering a contribution!

## Quick start

1. Fork the repo
2. `pip install -e ".[socks]"`
3. Make your changes
4. `pytest tests/`
5. Open a PR

## What we love

- Performance improvements (benchmarks welcome)
- New proxy sources for daily auto-update
- Protocol support (HTTP/2, HTTP/3)
- Bug fixes with a failing test included

## What to skip

- Major API breaking changes without discussion
- Vendor-specific integrations (keep it generic)

## Code style

`ruff format .` before committing.
