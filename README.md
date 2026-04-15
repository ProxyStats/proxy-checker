# proxy-checker

[![PyPI](https://img.shields.io/pypi/v/fast-proxy-checker)](https://pypi.org/project/fast-proxy-checker/)
[![Downloads](https://img.shields.io/pypi/dm/fast-proxy-checker)](https://pypi.org/project/fast-proxy-checker/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/fast-proxy-checker)](https://pypi.org/project/fast-proxy-checker/)
[![Stars](https://img.shields.io/github/stars/ProxyStats/proxy-checker?style=social)](https://github.com/ProxyStats/proxy-checker)

**Fast async proxy validator** — HTTP/HTTPS/SOCKS4/SOCKS5, 500+ proxies/minute.

![demo](demo.gif)

Checks latency, anonymity level, and country. Works as a library or CLI tool.

---

## Installation

```bash
pip install fast-proxy-checker          # HTTP/HTTPS support
pip install "fast-proxy-checker[socks]" # + SOCKS4/SOCKS5 support
```

## Quick Start

### CLI

```bash
# Check proxies from a file
proxy-checker check proxies.txt

# Check SOCKS5 proxies with custom concurrency
proxy-checker check proxies.txt --type socks5 --threads 200

# Export results to CSV
proxy-checker check proxies.txt --output results.csv --format csv

# Fetch fresh proxies from public sources and check them
proxy-checker fetch --count 100 --type http
proxy-checker fetch --count 50 --type socks5 --output alive.txt
```

### Python API

```python
import asyncio
from proxy_checker import check_proxies, ProxyType

async def main():
    proxies = ["1.2.3.4:8080", "5.6.7.8:3128"]
    async for result in check_proxies(proxies, ProxyType.HTTP, concurrency=100):
        if result.is_alive:
            print(f"{result.address}  {result.latency_ms}ms  [{result.country_code}]")

asyncio.run(main())
```

## Features

- **Async** — built on `asyncio` + `aiohttp`, checks hundreds of proxies in parallel
- **All protocols** — HTTP, HTTPS, SOCKS4, SOCKS5
- **Anonymity detection** — transparent / anonymous / elite
- **Country detection** — via ip-api.com
- **Multiple output formats** — TXT, CSV, JSON
- **Free proxy lists** — auto-updated daily (see [`proxies/`](proxies/))
- **CLI + library** — use from terminal or import in your code

---

> 💡 **Need reliable proxies?** Free lists work for testing, but production scraping needs stable providers.
> Check [**ProxyStats.io**](https://proxystats.io) — independent benchmarks of residential & datacenter proxy providers with real-world latency, success rate, and cost data.

---

## Free Proxy Lists (updated daily)

Auto-validated by this tool via GitHub Actions — only working proxies included:

| List | Type | Raw URL |
|------|------|---------|
| [proxies/http.txt](proxies/http.txt) | HTTP | `raw.githubusercontent.com/ProxyStats/proxy-checker/main/proxies/http.txt` |
| [proxies/socks4.txt](proxies/socks4.txt) | SOCKS4 | `raw.githubusercontent.com/ProxyStats/proxy-checker/main/proxies/socks4.txt` |
| [proxies/socks5.txt](proxies/socks5.txt) | SOCKS5 | `raw.githubusercontent.com/ProxyStats/proxy-checker/main/proxies/socks5.txt` |

Free proxies are unstable by nature — IPs die within hours. For production workloads see [ProxyStats.io](https://proxystats.io).

## Output Example

```
  proxy-checker  checking 500 proxies  (concurrency=500, timeout=10s)

  OK  45.77.31.10:8080           234.1ms  elite         [US]
  OK  103.152.112.157:80         891.2ms  anonymous     [ID]
  OK  181.78.18.1:999            445.7ms  elite         [CO]
  ...

  Results: 87 alive / 413 dead / 500 total

  Need reliable proxies? → https://proxystats.io
```

## CLI Reference

```
Usage: proxy-checker [OPTIONS] COMMAND [ARGS]...

Commands:
  check  Check proxies from a file
  fetch  Fetch free proxies from public sources and check them

Options for `check`:
  FILE                    Path to proxy list (one proxy per line)
  --type [http|https|socks4|socks5]   Default: http
  --threads INTEGER       Concurrency  [default: 500]
  --timeout FLOAT         Timeout per proxy in seconds  [default: 10.0]
  --output PATH           Save results to file
  --format [txt|csv|json] Output format  [default: txt]
  --all                   Show dead proxies too
```

## Proxy List Format

One proxy per line. Scheme prefix is optional:

```
1.2.3.4:8080
socks5://10.0.0.1:1080
http://user:pass@1.2.3.4:3128
```

## Python API Reference

```python
from proxy_checker import check_proxy, check_proxies, ProxyType, ProxyResult

# Check a single proxy
result: ProxyResult = await check_proxy("1.2.3.4", 8080, ProxyType.HTTP)

# Check many proxies (async generator, yields as results arrive)
async for result in check_proxies(
    proxies,           # list of strings
    proxy_type=ProxyType.HTTP,
    concurrency=500,
    timeout=10.0,
):
    print(result.is_alive, result.latency_ms, result.country)
```

`ProxyResult` fields: `host`, `port`, `proxy_type`, `is_alive`, `latency_ms`, `anonymity`, `country`, `country_code`, `error`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome.

```bash
git clone https://github.com/ProxyStats/proxy-checker
cd proxy-checker
pip install -e ".[socks]"
pytest tests/
```

## License

MIT — see [LICENSE](LICENSE)

---

<p align="center">
  <b>⭐ Star this repo if it helped you</b> — it helps others discover it.
</p>

<p align="center">
  Made by <a href="https://proxystats.io">ProxyStats</a> — independent proxy benchmarks.
</p>
