# Fork notice

This repository is a fork of [ManiMatter/decluttarr](https://github.com/ManiMatter/decluttarr),
licensed under the GNU General Public License v3.0 (see `LICENSE`).

## Modifications by tristaoeast

**Date:** 2026-06-07

Goal: make Decluttarr work against a **minimal qBittorrent-compatible mock** — specifically
[Decypharr](https://github.com/sirrobot01/decypharr)'s built-in qBittorrent API — which
authenticates open (no login cookie), returns `null` for several endpoints where real
qBittorrent returns lists/objects, and surfaces dead downloads as a generic qBit `error`.
All changes preserve real-qBittorrent behavior — they only add tolerance for the mock's
responses and error semantics.

### `src/settings/_download_clients_qbit.py`
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

### `src/jobs/remove_stalled.py`
- Also match the arr's generic `("warning", "qBittorrent is reporting an error")` queue state,
  not only `"The download is stalled with no connections"`. Decypharr surfaces dead / uncached
  downloads as qBit `error`, which the \*arr reports as a *warning* (never `"failed"`), so no
  upstream job removed them. With `blocklist=True` + the strike grace, such items are removed,
  blocklisted, and re-searched.

### `src/jobs/remove_failed_imports.py`
- Use `queue_scope = "full"` (not `"normal"`) so import-blocked items the \*arr could not match to
  a series/movie are seen. Title-mismatch blocks ("…title mismatch; automatic import is not
  possible") become "unknown" queue entries, absent from the normal queue. `_is_valid_item` still
  gates to completed / warning / importBlocked, so active downloads are not affected.

### Tests
`tests/settings/test_download_clients_qbit.py` (cookieless / null-tags / maindata-404 cases) and
`tests/jobs/test_remove_stalled.py` (the generic-qBit-error case) were updated/added accordingly.

This notice is provided to satisfy GPL-3.0 §5(a) — "carry prominent notices stating that you
modified it, and giving a relevant date." All modifications remain under GPL-3.0.
