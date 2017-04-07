#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import argparse
import asyncio
from string import Template
from datetime import datetime, timedelta
# from logging import getLogger

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils import Controller, Recorder

SCHEDULE = "schedule.json"
CONFIG = "config.json"


def check_requirement(config):
    """
    tile_format, record_dir, channelsがそれぞれ定義されているか確認
    定義されていなければ適当に例外飛ばす
    """


def assemble_record_command(config, program):
    ch = config["channels"].get(program["channel"], None)

    # 録画すべきチャンネルの設定が存在していないときは何もしない
    if ch is None:
        """
        エラー送出でなくログ書き出しが望ましい
        """
        return

    cmd, opt = ch["cmd"]
    # 録画コマンドが存在していないときは何もしない
    if not os.path.exists(cmd):
        """
        エラー送出でなくログ書き出しが望ましい
        """
        return

    opt = Template(opt).safe_substitute(ch).safe_substitute(program)
    return " ".join((cmd, opt))


def assemble_title(config, program, start_time):
    title = Template(config.get["title_format"])
    """
    ここに置き換え処理が入る
    """
    return title


def generate(programs, interval=60):
    now = datetime.now()
    wday = now.weekday()

    for program in programs:
        h, m = map(int, program["time"].split(":"))
        is_next_day = int(h == 0 and m == 0)

        start_wday = ("月火水木金土日".find(program["wday"])) % 7
        start_time = datetime(now.year, now.month, now.day, h, m) + timedelta(days=is_next_day)

        is_appropriate_time = abs(start_time - now) < timedelta(seconds=interval)
        is_appropriate_wday = (wday + is_next_day) % 7 == start_wday

        if is_appropriate_time and is_appropriate_wday:
            pass



def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", type=str, default=CONFIG)
    parser.add_argument("--schedule_file", type=str, default=SCHEDULE)
    parser.add_argument("--debug", action='store_true')

    return vars(parser.parse_args())


def main():
    args = parse()

    scheduler = AsyncIOScheduler()

    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except:
        pass
