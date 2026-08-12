from dataclasses import dataclass
from collections import deque
from PySide6.QtCore import QDateTime

@dataclass
class ProgressRecord:
    time_ms: int
    percent: float

class ProgressCalc:
    '''
    Helper class for calculating a rolling progress estimate
    '''
    def __init__(self):
        # -- Inputs --
        # time window of records to keep & calculate over
        self.window_ms: int = 15_000
        # min time/percent elapsed to wait until we start reporting time remaining
        self.min_elapsed_ms: int = 5_000
        self.min_percent: float = 5
        # frequency of reporting back updated remaining
        self.display_update_ms: int = 1_000
        # lower ratio == steadier updates of remaining time
        self.smoothing_ratio: float = 0.25

        # -- Tracked Outputs --
        self.records = deque()
        self.last_display_update_ms = 0
        self.smoothed_remaining_ms: float | None = None

    def update(self, percent: float) -> int | None:
        '''
        Returns remaining milliseconds ONLY when value has changed from last reported
        value and we have enough data to compute
        '''
        now_ms = QDateTime.currentMSecsSinceEpoch()

        self.records.append(ProgressRecord(now_ms, percent))

        # drop old records outside the rolling window
        while self.records and now_ms - self.records[0].time_ms > self.window_ms:
            self.records.popleft()

        # don't report back remaining ms too often
        if now_ms - self.last_display_update_ms < self.display_update_ms:
            return None

        if len(self.records) < 2:
            return None
        
        first = self.records[0]
        last = self.records[-1]

        elapsed_ms = last.time_ms - first.time_ms

        if elapsed_ms < self.min_elapsed_ms or last.percent < self.min_percent:
            return None

        if percent >= 100:
            return 0

        percent_delta = last.percent - first.percent
        percent_per_ms = percent_delta / elapsed_ms
        raw_remaining_ms = (100.0 - percent) / percent_per_ms

        # use a smoothing algorithm to calculate remaining ms
        if self.smoothed_remaining_ms is None:
            self.smoothed_remaining_ms = raw_remaining_ms
        else:
            self.smoothed_remaining_ms = (
                self.smoothed_remaining_ms * (1.0 - self.smoothing_ratio)
                + raw_remaining_ms * self.smoothing_ratio
            )

        self.last_display_update_ms = now_ms
        return int(self.smoothed_remaining_ms)