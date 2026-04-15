# Contributing to proxy-checker

Bug reports, feature requests, and PRs are welcome.

## Getting started

```bash
git clone https://github.com/proxystats/proxy-checker
cd proxy-checker
pip install -e ".[socks]"
pytest tests/
```

## Guidelines

- Add tests for new features or bug fixes
- Keep PRs focused — one change per PR
- Run `pytest tests/` before submitting

## Reporting bugs

Open an issue with:
- Python version
- OS
- Command you ran
- Expected vs actual output
