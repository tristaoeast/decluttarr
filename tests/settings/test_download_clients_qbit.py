import pytest

from requests.cookies import RequestsCookieJar
from src.settings._download_clients_qbit import QbitClient


@pytest.mark.parametrize(
    "cookie_name, cookie_value, expected",
    [
        # Legacy format
        ("SID", "abc", {"SID": "abc"}),
        # New dynamic port format (qBit 5.2+)
        ("QBT_SID_8080", "xyz", {"QBT_SID_8080": "xyz"}),
        ("QBT_SID_12345", "token123", {"QBT_SID_12345": "token123"}),
    ],
)
def test_extract_sid_success(cookie_name, cookie_value, expected):
    """Test successful extraction for various valid cookie names."""
    jar = RequestsCookieJar()
    jar.set(cookie_name, cookie_value)

    assert QbitClient.extract_sid(jar) == expected


@pytest.mark.parametrize(
    "cookies",
    [
        {},  # Empty jar (open-auth qBittorrent returns no Set-Cookie, e.g. Decypharr)
        {"WRONG_NAME": "value"},  # No SID-style cookie present
        {
            "sid": "lowercase_is_not_a_qbit_sid"
        },  # Case-sensitive: lowercase "sid" is not a qBit SID
    ],
)
def test_extract_sid_no_cookie_returns_empty(cookies):
    """No SID/QBT_SID_* cookie -> return {} (tolerate cookieless / open-auth
    qBittorrent) rather than raising. Decypharr's qBit mock authenticates open and
    returns no Set-Cookie; an empty cookie dict lets requests proceed against such
    servers. (tristaoeast fork modification.)"""
    jar = RequestsCookieJar()
    for name, val in cookies.items():
        jar.set(name, val)

    assert QbitClient.extract_sid(jar) == {}
