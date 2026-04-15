import asyncio
import csv
import json
from pathlib import Path
from typing import Optional

import click

from .checker import check_proxies, parse_proxy_line
from .models import ProxyResult, ProxyType


PROXYSTATS_MSG = (
    "\n  Need reliable proxies? → https://proxystats.io\n"
    "  Independent benchmarks of 50+ proxy providers.\n"
)


def _write_results(results: list[ProxyResult], output: Optional[Path], fmt: str) -> None:
    alive = [r for r in results if r.is_alive]

    if fmt == "txt":
        lines = [f"{r.host}:{r.port}" for r in alive]
        content = "\n".join(lines)
    elif fmt == "csv":
        import io
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["host", "port", "type", "alive", "latency_ms", "anonymity", "country", "country_code", "error"])
        writer.writeheader()
        for r in results:
            writer.writerow(r.to_dict())
        content = buf.getvalue()
    elif fmt == "json":
        content = json.dumps([r.to_dict() for r in results], indent=2)
    else:
        content = "\n".join(f"{r.host}:{r.port}" for r in alive)

    if output:
        output.write_text(content, encoding="utf-8")
        click.echo(f"\n  Saved {len(alive)} alive proxies → {output}")
    else:
        click.echo(content)


@click.group()
@click.version_option()
def cli() -> None:
    """Fast async proxy checker — HTTP/HTTPS/SOCKS4/SOCKS5."""


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--type", "proxy_type", type=click.Choice(["http", "https", "socks4", "socks5"]), default="http", show_default=True, help="Proxy type (if not specified in file)")
@click.option("--threads", default=500, show_default=True, help="Concurrent checks")
@click.option("--timeout", default=10.0, show_default=True, help="Timeout per proxy (seconds)")
@click.option("--output", "-o", type=click.Path(path_type=Path), default=None, help="Output file path")
@click.option("--format", "fmt", type=click.Choice(["txt", "csv", "json"]), default="txt", show_default=True, help="Output format")
@click.option("--alive-only/--all", default=True, show_default=True, help="Show only alive proxies in terminal")
def check(file: Path, proxy_type: str, threads: int, timeout: float, output: Optional[Path], fmt: str, alive_only: bool) -> None:
    """Check proxies from a FILE (one proxy per line).

    \b
    Examples:
      proxy-checker check proxies.txt
      proxy-checker check proxies.txt --type socks5 --threads 200
      proxy-checker check proxies.txt --output alive.txt --format csv
    """
    ptype = ProxyType(proxy_type)
    lines = file.read_text(encoding="utf-8", errors="ignore").splitlines()
    total = sum(1 for l in lines if parse_proxy_line(l, ptype))

    click.echo(f"\n  proxy-checker  checking {total} proxies  (concurrency={threads}, timeout={timeout}s)\n")

    results: list[ProxyResult] = []
    alive_count = 0
    dead_count = 0

    async def run() -> None:
        nonlocal alive_count, dead_count
        async for result in check_proxies(lines, ptype, threads, timeout):
            results.append(result)
            if result.is_alive:
                alive_count += 1
                country_str = f"  [{result.country_code}]" if result.country_code else ""
                click.echo(
                    f"  OK  {result.address:<25}  {result.latency_ms:>7.1f}ms"
                    f"  {result.anonymity.value:<12}{country_str}"
                )
            else:
                dead_count += 1
                if not alive_only:
                    click.echo(f"  XX  {result.address:<25}  {result.error or 'failed'}", err=True)

    asyncio.run(run())

    click.echo(f"\n  Results: {alive_count} alive / {dead_count} dead / {total} total")
    click.echo(PROXYSTATS_MSG)

    if output or fmt != "txt":
        _write_results(results, output, fmt)


@cli.command()
@click.option("--count", default=100, show_default=True, help="Number of proxies to fetch and check")
@click.option("--type", "proxy_type", type=click.Choice(["http", "socks4", "socks5"]), default="http", show_default=True)
@click.option("--output", "-o", type=click.Path(path_type=Path), default=None)
@click.option("--format", "fmt", type=click.Choice(["txt", "csv", "json"]), default="txt", show_default=True)
def fetch(count: int, proxy_type: str, output: Optional[Path], fmt: str) -> None:
    """Fetch free proxies from public sources and check them.

    \b
    Examples:
      proxy-checker fetch --count 200 --type socks5
      proxy-checker fetch --output fresh.txt
    """
    import aiohttp

    ptype = ProxyType(proxy_type)

    SOURCES = {
        "http": [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        ],
        "socks4": [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
        ],
        "socks5": [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        ],
    }

    async def fetch_and_check() -> list[ProxyResult]:
        raw_proxies: list[str] = []
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            for url in SOURCES.get(proxy_type, []):
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        text = await resp.text()
                        raw_proxies.extend(text.splitlines())
                        if len(raw_proxies) >= count * 3:
                            break
                except Exception:
                    continue

        raw_proxies = list(dict.fromkeys(raw_proxies))[:count * 3]
        click.echo(f"\n  Fetched {len(raw_proxies)} proxies, checking {min(len(raw_proxies), count * 3)}...\n")

        results: list[ProxyResult] = []
        alive: list[ProxyResult] = []

        async for result in check_proxies(raw_proxies, ptype, concurrency=500, timeout=10.0):
            results.append(result)
            if result.is_alive:
                alive.append(result)
                country_str = f"  [{result.country_code}]" if result.country_code else ""
                click.echo(
                    f"  OK  {result.address:<25}  {result.latency_ms:>7.1f}ms"
                    f"  {result.anonymity.value:<12}{country_str}"
                )
            if len(alive) >= count:
                break

        return results

    results = asyncio.run(fetch_and_check())
    alive_count = sum(1 for r in results if r.is_alive)
    click.echo(f"\n  Found {alive_count} working {proxy_type} proxies")
    click.echo(PROXYSTATS_MSG)
    _write_results(results, output, fmt)


def main() -> None:
    cli()
