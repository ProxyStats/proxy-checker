import asyncio
import time
from typing import Optional

import aiohttp

from .models import AnonymityLevel, ProxyResult, ProxyType

# Public IP check endpoints (multiple fallbacks)
IP_CHECK_URLS = [
    "http://httpbin.org/ip",
    "http://api.ipify.org?format=json",
]

GEO_URL = "http://ip-api.com/json/{ip}?fields=country,countryCode"

TEST_URL = "http://httpbin.org/ip"


async def _get_real_ip(session: aiohttp.ClientSession) -> Optional[str]:
    """Get the real IP address without proxy."""
    for url in IP_CHECK_URLS:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                data = await resp.json()
                return data.get("origin", data.get("ip", "")).split(",")[0].strip()
        except Exception:
            continue
    return None


async def check_http_proxy(
    host: str,
    port: int,
    proxy_type: ProxyType,
    timeout: float = 10.0,
    real_ip: Optional[str] = None,
) -> ProxyResult:
    """Check HTTP/HTTPS proxy."""
    proxy_url = f"http://{host}:{port}"
    connector = aiohttp.TCPConnector(ssl=False)

    start = time.monotonic()
    try:
        async with aiohttp.ClientSession(
            connector=connector,
            headers={"User-Agent": "Mozilla/5.0 (compatible; proxy-checker/1.0)"},
        ) as session:
            async with session.get(
                TEST_URL,
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(total=timeout),
                allow_redirects=True,
            ) as resp:
                latency = (time.monotonic() - start) * 1000
                data = await resp.json(content_type=None)
                proxy_ip = data.get("origin", "").split(",")[0].strip()

                # Determine anonymity
                anonymity = AnonymityLevel.UNKNOWN
                if real_ip and proxy_ip:
                    if real_ip in proxy_ip:
                        anonymity = AnonymityLevel.TRANSPARENT
                    else:
                        anonymity = AnonymityLevel.ELITE

                # Get geo info
                country, country_code = await _get_geo(session, proxy_ip)

                return ProxyResult(
                    host=host,
                    port=port,
                    proxy_type=proxy_type,
                    is_alive=True,
                    latency_ms=round(latency, 1),
                    anonymity=anonymity,
                    country=country,
                    country_code=country_code,
                )
    except asyncio.TimeoutError:
        return ProxyResult(host=host, port=port, proxy_type=proxy_type, is_alive=False, error="timeout")
    except Exception as e:
        return ProxyResult(host=host, port=port, proxy_type=proxy_type, is_alive=False, error=str(e)[:80])


async def check_socks_proxy(
    host: str,
    port: int,
    proxy_type: ProxyType,
    timeout: float = 10.0,
    real_ip: Optional[str] = None,
) -> ProxyResult:
    """Check SOCKS4/SOCKS5 proxy using aiohttp-socks."""
    try:
        from aiohttp_socks import ProxyConnector
    except ImportError:
        return ProxyResult(
            host=host, port=port, proxy_type=proxy_type, is_alive=False,
            error="aiohttp-socks not installed: pip install fast-proxy-checker[socks]"
        )

    proxy_url = f"{proxy_type.value}://{host}:{port}"

    start = time.monotonic()
    try:
        connector = ProxyConnector.from_url(proxy_url, ssl=False)
        async with aiohttp.ClientSession(
            connector=connector,
            headers={"User-Agent": "Mozilla/5.0 (compatible; proxy-checker/1.0)"},
        ) as session:
            async with session.get(
                TEST_URL,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as resp:
                latency = (time.monotonic() - start) * 1000
                data = await resp.json(content_type=None)
                proxy_ip = data.get("origin", "").split(",")[0].strip()

                anonymity = AnonymityLevel.UNKNOWN
                if real_ip and proxy_ip:
                    if real_ip in proxy_ip:
                        anonymity = AnonymityLevel.TRANSPARENT
                    else:
                        anonymity = AnonymityLevel.ELITE

                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as direct:
                    country, country_code = await _get_geo(direct, proxy_ip)

                return ProxyResult(
                    host=host,
                    port=port,
                    proxy_type=proxy_type,
                    is_alive=True,
                    latency_ms=round(latency, 1),
                    anonymity=anonymity,
                    country=country,
                    country_code=country_code,
                )
    except asyncio.TimeoutError:
        return ProxyResult(host=host, port=port, proxy_type=proxy_type, is_alive=False, error="timeout")
    except Exception as e:
        return ProxyResult(host=host, port=port, proxy_type=proxy_type, is_alive=False, error=str(e)[:80])


async def _get_geo(session: aiohttp.ClientSession, ip: str) -> tuple[Optional[str], Optional[str]]:
    """Get country info for an IP."""
    if not ip:
        return None, None
    try:
        async with session.get(
            GEO_URL.format(ip=ip),
            timeout=aiohttp.ClientTimeout(total=3),
        ) as resp:
            data = await resp.json(content_type=None)
            return data.get("country"), data.get("countryCode")
    except Exception:
        return None, None
