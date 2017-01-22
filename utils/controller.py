"""
scheduleを確認して合致するものがあれば録画したりするcontrollerを定義したい
"""

import os.path
import json
import threading
from datetime import datetime, timedelta
from logging import getLogger

from .recorder import Recorder

SCHEDULE = "schedule.json"

class Controller(object):
    wday = { k : i for i, k in enumerate("月火水木金土日") }

    def __init__(self, recorder, schedule_file):
        with open(schedule_file, "r") as f:
            self.schedule = json.load(f)
        self.recorder = recorder

    def check(self, ):
        now = datetime.now()
        targets = []
        for _ in self.schedule:
            h, m = map(int, _["start"].split(":"))

            is_next_day = int(bool(h == 0 and m == 0))
            reserve_time = datetime(now.year, now.month, now.day, h, m) + timedelta(is_next_day)

            if (self.wday[_["wday"]] - now.weekday()) % len(self.wday) == is_next_day:
                if abs(reserve_time - now) < timedelta(seconds = 60):
                    targets.append(threading.Thread(target = self.recorder.record, kwargs = _))
        for _ in targets:
            _.start()
        return
