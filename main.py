#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import argparse
import shlex
import asyncio
import json
import re
from string import Template
from datetime import datetime, timedelta
# from logging import getLogger

from apscheduler.schedulers.asyncio import AsyncIOScheduler

SCHEDULE = "schedule.json"
CONFIG = "config.json"


def rsubstitute(template, *params):
    temp = Template(template)
    substitute_pattern = "\\" + Template.delimiter + r"\{?" + Template.idpattern + r"\}?"
    ptr = re.compile(substitute_pattern)
    for param in params:
        temp = temp.safe_substitute(param)
        if ptr.findall(temp):
            temp = Template(temp)
        else:
            return temp


def is_valid_config(config):
    pass

def is_valid_schedule(schedule):
    pass

def load_json(json_file):
    with open(json_file, "r", encoding="UTF-8") as f:
        data = json.load(f)
    return data


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

    opt = rsubstitute(opt, ch, { "length":program["length"] * 60 })
    return " ".join((cmd, opt))


def assemble_title(config, program, date):
    title_format = config["title_format"]
    return rsubstitute(title_format, program, {"date" : date.strftime("%Y%m%d")})


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

def generate_task(config, programs):
    fps = []

    # このタイミングで録画するタスクの生成
    for (now, p) in is_matched_program(programs):
        cmd = assemble_record_command(config, p)
        fname = assemble_title(config, p, now) + ".{}".format(config["channels"][p["channel"]]["ext"])
        print(cmd, fname)
        if cmd and fname:
            fps.append(open(fname, 'wb'))
            asyncio.create_subprocess_exec(shlex.split(cmd), stdout=fps[-1])

    # 録画ファイルへのファイルポインタをすべて削除
    for fp in fps:
        fp.close()

def generate_debug_task(n=20):
    """
    ファイルポインタを持ったままで並列化した時にブロッキングされるか確かめる
    """
    cmd = ""
    for i in range(n):
        pass


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", type=str, default=CONFIG)
    parser.add_argument("--schedule_file", type=str, default=SCHEDULE)

    return vars(parser.parse_args())


def main():
    args = parse()
    config = load_json(args["config_file"])
    programs = load_json(args["schedule_file"])
    generate_task(config, programs)
    scheduler = AsyncIOScheduler()
    scheduler.start()

    scheduler.add_job(generate_task, 'interval', args=(config, programs), seconds=10)

    try:
        asyncio.get_event_loop().run_forever()
    except:
        pass


if __name__ == '__main__':
    main()
