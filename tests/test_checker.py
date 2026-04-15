import pytest
from proxy_checker.checker import parse_proxy_line
from proxy_checker.models import ProxyType


def test_parse_basic():
    result = parse_proxy_line("1.2.3.4:8080")
    assert result == ("1.2.3.4", 8080, ProxyType.HTTP)


def test_parse_socks5_scheme():
    result = parse_proxy_line("socks5://10.0.0.1:1080")
    assert result == ("10.0.0.1", 1080, ProxyType.SOCKS5)


def test_parse_socks4_scheme():
    result = parse_proxy_line("socks4://10.0.0.1:1080")
    assert result == ("10.0.0.1", 1080, ProxyType.SOCKS4)


def test_parse_with_auth():
    result = parse_proxy_line("socks5://user:pass@10.0.0.1:1080")
    assert result == ("10.0.0.1", 1080, ProxyType.SOCKS5)


def test_parse_comment():
    result = parse_proxy_line("# this is a comment")
    assert result is None


def test_parse_empty():
    result = parse_proxy_line("")
    assert result is None


def test_parse_invalid_port():
    result = parse_proxy_line("1.2.3.4:99999")
    assert result is None


def test_parse_default_type_override():
    result = parse_proxy_line("1.2.3.4:1080", default_type=ProxyType.SOCKS5)
    assert result == ("1.2.3.4", 1080, ProxyType.SOCKS5)


def test_proxy_result_address():
    from proxy_checker.models import ProxyResult, AnonymityLevel
    r = ProxyResult(host="1.2.3.4", port=8080, proxy_type=ProxyType.HTTP, is_alive=True, latency_ms=120.5)
    assert r.address == "1.2.3.4:8080"
    assert r.url == "http://1.2.3.4:8080"


def test_proxy_result_to_dict():
    from proxy_checker.models import ProxyResult
    r = ProxyResult(host="1.2.3.4", port=8080, proxy_type=ProxyType.HTTP, is_alive=True)
    d = r.to_dict()
    assert d["host"] == "1.2.3.4"
    assert d["type"] == "http"
    assert d["alive"] is True


def test_parse_port_boundary_low():
    assert parse_proxy_line("1.2.3.4:0") is None


def test_parse_port_boundary_high():
    assert parse_proxy_line("1.2.3.4:65536") is None


def test_parse_port_valid_max():
    result = parse_proxy_line("1.2.3.4:65535")
    assert result == ("1.2.3.4", 65535, ProxyType.HTTP)


def test_parse_https_scheme():
    result = parse_proxy_line("https://1.2.3.4:8443")
    assert result == ("1.2.3.4", 8443, ProxyType.HTTPS)


def test_parse_whitespace_lines():
    assert parse_proxy_line("   ") is None
    assert parse_proxy_line("\t") is None


def test_proxy_result_url_socks5():
    from proxy_checker.models import ProxyResult
    r = ProxyResult(host="1.2.3.4", port=1080, proxy_type=ProxyType.SOCKS5, is_alive=True)
    assert r.url == "socks5://1.2.3.4:1080"


def test_proxy_result_dead():
    from proxy_checker.models import ProxyResult, AnonymityLevel
    r = ProxyResult(host="1.2.3.4", port=8080, proxy_type=ProxyType.HTTP, is_alive=False, error="timeout")
    d = r.to_dict()
    assert d["alive"] is False
    assert d["error"] == "timeout"
    assert d["latency_ms"] is None
