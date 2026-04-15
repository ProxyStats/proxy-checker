import asyncio
from typing import AsyncIterator, Iterable, Optional

import aiohttp

from .models import ProxyResult, ProxyType
from .protocols import check_http_proxy, check_socks_proxy, _get_real_ip


def parse_proxy_line(line: str, default_type: ProxyType = ProxyType.HTTP) -> Optional[tuple[str, int, ProxyType]]:
    """Parse a proxy line like '1.2.3.4:8080' or 'socks5://1.2.3.4:8080'."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    proxy_type = default_type

    # Parse scheme prefix
    for scheme in ("socks5://", "socks4://", "https://", "http://"):
        if line.lower().startswith(scheme):
            type_map = {
                "socks5://": ProxyType.SOCKS5,
                "socks4://": ProxyType.SOCKS4,
                "https://": ProxyType.HTTPS,
                "http://": ProxyType.HTTP,
            }
            proxy_type = type_map[scheme]
            line = line[len(scheme):]
            break

    # Strip auth if present (user:pass@host:port)
    if "@" in line:
        line = line.split("@", 1)[1]

    parts = line.rsplit(":", 1)
    if len(parts) != 2:
        return None
    host = parts[0].strip()
    try:
        port = int(parts[1].strip())
    except ValueError:
        return None

    if not host or not (1 <= port <= 65535):
        return None

    return host, port, proxy_type


async def check_proxy(
    host: str,
    port: int,
    proxy_type: ProxyType = ProxyType.HTTP,
    timeout: float = 10.0,
    real_ip: Optional[str] = None,
) -> ProxyResult:
    """Check a single proxy."""
    if proxy_type in (ProxyType.HTTP, ProxyType.HTTPS):
        return await check_http_proxy(host, port, proxy_type, timeout, real_ip)
    else:
        return await check_socks_proxy(host, port, proxy_type, timeout, real_ip)


async def check_proxies(
    proxies: Iterable[str],
    proxy_type: ProxyType = ProxyType.HTTP,
    concurrency: int = 500,
    timeout: float = 10.0,
    detect_real_ip: bool = True,
) -> AsyncIterator[ProxyResult]:
    """
    Check multiple proxies concurrently, yielding results as they complete.

    Args:
        proxies: Iterable of proxy strings (host:port or scheme://host:port)
        proxy_type: Default proxy type if not specified in the proxy string
        concurrency: Max concurrent checks
        timeout: Per-proxy timeout in seconds
        detect_real_ip: Whether to fetch real IP for anonymity detection
    """
    semaphore = asyncio.Semaphore(concurrency)
    real_ip: Optional[str] = None

    if detect_real_ip:
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                real_ip = await _get_real_ip(session)
        except Exception:
            pass

    parsed = []
    for line in proxies:
        result = parse_proxy_line(line, default_type=proxy_type)
        if result:
            parsed.append(result)

    async def bounded_check(host: str, port: int, ptype: ProxyType) -> ProxyResult:
        async with semaphore:
            return await check_proxy(host, port, ptype, timeout, real_ip)

    tasks = [bounded_check(h, p, t) for h, p, t in parsed]

    for coro in asyncio.as_completed(tasks):
        yield await coro
