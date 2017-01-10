"""
scheduleを確認して合致するものがあれば録画したりするcontrollerを定義したい
"""

import os.path
import json
import threading
from datetime import datetime, timedelta
from .recorder import Recorder

SCHEDULE = "schedule.json"

class Controller(object):
    wday = { k : i for i, k in enumerate("月火水木金土日") }

    def __init__(self, config_dir = ".", **kwargs):
        self.schedule_file = os.path.join(config_dir, SCHEDULE)
        with open(self.schedule_file, "r") as f:
            self.schedule = json.load(f)
        self.recorder = Recorder(config_dir, **kwargs)

    def check(self, debug = False):
        now = datetime(2017, 1, 11, 19, 59, 30) if debug else datetime.now()
        targets = []
        for _ in self.schedule:
            print(_)
            h, m = map(int, _["start"].split(":"))

            is_next_day = int(bool(h == 0 and m == 0))
            reserve_time = datetime(now.year, now.month, now.day, h, m) + timedelta(is_next_day)

            if (self.wday[_["wday"]] - now.weekday()) % len(self.wday) == is_next_day:
                if reserve_time - now < timedelta(seconds = 60):
                    targets.append(threading.Thread(target = self.recorder.record, kwargs = _))
        for _ in targets:
            _.start()
        return

    def debug(self, ):
        now = detetime(2017, 1, 11, 19, 59, 30)

if __name__ == '__main__':
    ctrl = Controller()
    ctrl.debug()
