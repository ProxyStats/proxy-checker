from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ProxyType(str, Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class AnonymityLevel(str, Enum):
    TRANSPARENT = "transparent"
    ANONYMOUS = "anonymous"
    ELITE = "elite"
    UNKNOWN = "unknown"


@dataclass
class ProxyResult:
    host: str
    port: int
    proxy_type: ProxyType
    is_alive: bool
    latency_ms: Optional[float] = None
    anonymity: AnonymityLevel = AnonymityLevel.UNKNOWN
    country: Optional[str] = None
    country_code: Optional[str] = None
    error: Optional[str] = None

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"

    @property
    def url(self) -> str:
        return f"{self.proxy_type.value}://{self.host}:{self.port}"

    def to_dict(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "type": self.proxy_type.value,
            "alive": self.is_alive,
            "latency_ms": self.latency_ms,
            "anonymity": self.anonymity.value,
            "country": self.country,
            "country_code": self.country_code,
            "error": self.error,
        }
