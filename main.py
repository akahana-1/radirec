#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import argparse
import asyncio
import json
from string import Template
from datetime import datetime, timedelta
# from logging import getLogger

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# from utils import Controller, Recorder

SCHEDULE = "schedule.json"
CONFIG = "config.json"


def check_requirement(config):
    """
    tile_format, record_dir, channelsがそれぞれ定義されているか確認
    定義されていなければ適当に例外飛ばす
    """
    pass


def load_config(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
    return config


def assemble_record_command(config, program):
    ch = config["channels"].get(program["channel"], None)
    params = program
    params["length"] *= 60

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

    params.update(ch)

    opt = Template(opt).safe_substitute(params)
    return " ".join((cmd, opt))


def assemble_title(config, program, date):
    title = Template(config.get["title_format"])
    title.safe_substitute(program)
    title.safe_substitute(date=date.strftime("%Y%m%d"))
    return title


def record(config, program, now):
    cmd = assemble_record_command(config, program)
    if not cmd:
        """
        なんかエラー出力
        """
    title = assemble_title(config, program, now)
    pass


def is_matched_program(programs, interval=60):
    now = datetime.now()
    now = datetime(now.year, 4, 1, 18, 29, 30)
    wday = now.weekday()

    for program in programs:
        h, m = map(int, program["start"].split(":"))
        is_next_day = h == 0 and m == 0

        start_wday = ("月火水木金土日".find(program["wday"])) % 7
        start_time = datetime(now.year, now.month, now.day, h, m)
        if is_next_day:
            start_time += timedelta(days=1)

        appropriate_interval = timedelta(seconds=interval)

        is_appropriate_time = abs(start_time - now) < appropriate_interval
        is_appropriate_wday = (wday + is_next_day) % 7 == start_wday

        if is_appropriate_time and is_appropriate_wday:
            yield (start_time, program)


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", type=str, default=CONFIG)
    parser.add_argument("--schedule_file", type=str, default=SCHEDULE)

    return vars(parser.parse_args())


def main():
    args = parse()
    config = load_config(args["config_file"])
    with open(args["schedule_file"], "r") as f:
        programs = json.load(f)
    for a in is_matched_program(programs):
        print(a)
    # scheduler = AsyncIOScheduler()
    # scheduler.start()

    # try:
    #     asyncio.get_event_loop().run_forever()
    # except:
    #     pass


if __name__ == '__main__':
    main()
