#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import sys
import json
import subprocess
from datetime import datetime

CHANNEL = "channels.json"

class Recorder():

    def __init__(self, config_dir, record_dir):
        self.record_dir = record_dir
        channel_file = os.path.join(config_dir, CHANNEL)
        with open(channel_file, "r") as f:
            self.channels = json.load(f)
        if not os.path.isdir(self.record_dir):
            os.mkdir(self.record_dir)

    def record(self, channel, title, length, **kwargs):

        now = datetime.now()
        length = length * 60

        record_file = title + "_" + now.strftime("%Y%m%d")

        for ch in self.channels:
            if ch["name"] == channel and os.path.exists(ch["cmd"].split()[0]):
                cmd = ch["cmd"].format(length = length, **ch)
                record_file_path = os.path.join(self.record_dir, record_file + "." + ch["fmt"])
                with open(record_file_path, "wb") as recf:
                    subprocess.run(cmd.split(), stdout = recf)
                break
        return
