"""
proxy-checker — Fast async proxy validator.

Supports HTTP/HTTPS/SOCKS4/SOCKS5.
"""

from .checker import check_proxies, check_proxy
from .models import AnonymityLevel, ProxyResult, ProxyType

__version__ = "1.0.0"
__all__ = ["check_proxy", "check_proxies", "ProxyResult", "ProxyType", "AnonymityLevel"]
