# Fork notice

This repository is a fork of [ManiMatter/decluttarr](https://github.com/ManiMatter/decluttarr),
licensed under the GNU General Public License v3.0 (see `LICENSE`).

## Modifications by tristaoeast

**Date:** 2026-06-07

Goal: make Decluttarr work against a **minimal qBittorrent-compatible mock** — specifically
[Decypharr](https://github.com/sirrobot01/decypharr)'s built-in qBittorrent API — which
authenticates open (no login cookie) and returns `null` for several endpoints where real
qBittorrent returns lists/objects. All changes are in
`src/settings/_download_clients_qbit.py` and preserve real-qBittorrent behavior — they only
add tolerance for the mock's responses:

- **`extract_sid()`** — return an empty cookie dict (`{}`) instead of raising
  `QbitError("No qBit cookie found")` when the login response carries no `SID` / `QBT_SID_*`
  cookie. Decypharr authenticates open and returns `200 "Ok."` with no `Set-Cookie`; upstream
  would crash-loop. Upstream's own config already documents qBit `username`/`password` as
  optional, so a cookieless server is a supported configuration.
- **`create_tag()`** — when `GET /torrents/tags` returns `null` (tags unsupported on the
  mock), skip tag creation instead of crashing on `tag not in None`.
- **`check_connected()`** — tolerate `GET /sync/maindata` being unimplemented (HTTP 404) or
  returning a `null` body / missing `server_state.connection_status`. On any failure to
  determine status, assume connected so the cleaning loop is never blocked; only an explicit
  `"disconnected"` is treated as offline.
- **`get_protected_and_private()` / `get_qbit_items()`** — treat a `null` tag list / torrent
  list as empty.

Tests in `tests/settings/test_download_clients_qbit.py` were updated/added accordingly:
`test_extract_sid_no_cookie_returns_empty` (replacing the previous `test_extract_sid_failures`),
plus `test_create_tag_tolerates_null_tag_list` and
`test_check_connected_tolerates_incomplete_maindata`.

This notice is provided to satisfy GPL-3.0 §5(a) — "carry prominent notices stating that you
modified it, and giving a relevant date." All modifications remain under GPL-3.0.
