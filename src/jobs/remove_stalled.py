"""Removes stalled downloads."""

from src.jobs.removal_job import RemovalJob


class RemoveStalled(RemovalJob):
    queue_scope = "normal"
    blocklist = True

    async def _find_affected_items(self):
        conditions = [
            ("warning", "The download is stalled with no connections"),
            # tristaoeast fork: also treat a generic qBittorrent error as a removable stall. A
            # minimal qBit mock (e.g. Decypharr) surfaces dead / uncached downloads as qBit
            # `error`, which the *arr reports with errorMessage "qBittorrent is reporting an
            # error" and status "warning" (never "failed"), so neither upstream remove_stalled
            # nor remove_failed_downloads catch it. The strike grace + blocklist re-search make
            # this safe against transient errors.
            ("warning", "qBittorrent is reporting an error"),
        ]
        return self.queue_manager.filter_queue(self.queue, conditions)
