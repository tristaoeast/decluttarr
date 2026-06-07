import pytest
from unittest.mock import AsyncMock, MagicMock, patch

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


def _make_qbit_client():
    """Minimal QbitClient for unit tests (settings mocked; make_request is patched per test)."""
    return QbitClient(MagicMock(), base_url="http://decypharr:8282", name="Decypharr")


@pytest.mark.asyncio
async def test_create_tag_tolerates_null_tag_list():
    """A minimal qBit mock (e.g. Decypharr) returns null for /torrents/tags. create_tag must
    skip gracefully instead of crashing on `tag not in None`, and must NOT POST createTags
    (the mock doesn't support tags). (tristaoeast fork modification.)"""
    client = _make_qbit_client()
    with patch(
        "src.settings._download_clients_qbit.make_request", new_callable=AsyncMock
    ) as mock_request:
        resp = MagicMock()
        resp.json = MagicMock(return_value=None)  # Decypharr returns null, not []
        mock_request.return_value = resp

        await client.create_tag("Keep")  # must not raise

        # Only the GET /torrents/tags happened — no createTags POST when tags are unsupported.
        assert mock_request.await_count == 1


@pytest.mark.asyncio
async def test_check_connected_tolerates_incomplete_maindata():
    """A minimal qBit mock may omit server_state/connection_status (returns null). check_connected
    must assume connected (True) rather than crash, so the cleaning loop is never blocked.
    (tristaoeast fork modification.)"""
    client = _make_qbit_client()
    with patch(
        "src.settings._download_clients_qbit.make_request", new_callable=AsyncMock
    ) as mock_request:
        resp = MagicMock()
        resp.json = MagicMock(return_value=None)  # Decypharr: no maindata payload
        mock_request.return_value = resp

        assert await client.check_connected() is True
