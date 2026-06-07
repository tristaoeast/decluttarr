# Fork notice

This repository is a fork of [ManiMatter/decluttarr](https://github.com/ManiMatter/decluttarr),
licensed under the GNU General Public License v3.0 (see `LICENSE`).

## Modifications by tristaoeast

**Date:** 2026-06-07

- **`src/settings/_download_clients_qbit.py` — `QbitClient.extract_sid()`**: tolerate a
  cookieless / open-auth qBittorrent endpoint. Upstream raises
  `QbitError("No qBit cookie found")` when the login response carries no `SID` /
  `QBT_SID_*` cookie; this fork returns an empty cookie dict (`{}`) instead, so the client
  issues cookieless requests and works against servers that authenticate open and return
  no `Set-Cookie` (e.g. [Decypharr](https://github.com/sirrobot01/decypharr)'s qBittorrent
  mock). Upstream's own config already documents qBit `username`/`password` as optional, so
  a cookieless server is a supported configuration. The test
  `tests/settings/test_download_clients_qbit.py::test_extract_sid_no_cookie_returns_empty`
  was updated (from the previous `test_extract_sid_failures`) to assert the new behavior.

This notice is provided to satisfy GPL-3.0 §5(a) — "carry prominent notices stating that
you modified it, and giving a relevant date." All modifications remain under GPL-3.0.
