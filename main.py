#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import argparse
import shlex
import asyncio
import json
import re
import subprocess
import time
import threading
from string import Template
from datetime import datetime, timedelta

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


def assemble_record_command(config, program, date):
    ch = config["channels"].get(program["channel"], None)
    fname = assemble_filename(config, program, date)

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

    opt = rsubstitute(opt, ch, {
        "length": program["length"] * 60,
        "file": fname
        })
    print(opt)
    return " ".join((cmd, opt))


def assemble_filename(config, program, date):
    title_ptr = config["title_format"]
    ext = config["channels"][program["channel"]]["ext"]
    title = rsubstitute(title_ptr, program, {"date": date.strftime("%Y%m%d")})
    return title + "." + ext


def is_matched_program(programs, interval=60):
    now = datetime.now()
#    now = datetime(now.year, 5, 2, 23, 59, 30)
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
    threads = []

    # このタイミングで録画するタスクの生成
    for (st, p) in is_matched_program(programs):
        cmd = assemble_record_command(config, p)
        # fname = assemble_filename(config, p, st)
        # print(cmd, fname)
        if cmd:
            threads.append(threading.Thread(subprocess.Popen, shlex.split(cmd)))

    for _ in threads:
        _.start()

    while any(_.is_alive() for _ in threads):
        pass

    # 録画ファイルへのファイルポインタをすべて削除
    for fp in fps:
        fp.close()


def generate_debug_task(n=20):
    """
    ファイルポインタを持ったままで並列化した時にブロッキングされるか確かめる
    => そんなことはない?
    """
    cmd = "/usr/bin/rtmpdump -r rtmp://fms-base1.mitene.ad.jp/agqr/aandg22 -B 10 --live"
    fps = []
    ths = []
    for i in range(n):
        t = 10
        fp = open("{}.flv".format(i), "wb")
        ths.append(
                threading.Thread(
                    target=delay_execute,
                    args=(t, cmd),
                    kwargs={"stderr": subprocess.DEVNULL, "stdout": fp}
                )
            )
        fps.append(fp)

    for _ in ths:
        _.start()

    while any(_.is_alive() for _ in ths):
        pass

    for _ in fps:
        _.close()


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", type=str, default=CONFIG)
    parser.add_argument("--schedule_file", type=str, default=SCHEDULE)

    return vars(parser.parse_args())


def delay_execute(seconds, cmd, *args, **kwargs):
    time.sleep(seconds)
    subprocess.Popen(shlex.split(cmd), *args, **kwargs)


def main():
    args = parse()
    config = load_json(args["config_file"])
    programs = load_json(args["schedule_file"])
    generate_task(config, programs)
    scheduler = AsyncIOScheduler()
    scheduler.start()
    cronopt = {
            'year': '*',
            'month': '*',
            'day': '*',
            'week': '*',
            'hour': '*',
            'minute': '29/59',
            'second': '30'
            }
    scheduler.add_job(generate_task, 'cron', args=(config, programs), kwargs=cronopt)

    try:
        asyncio.get_event_loop().run_forever()
    except:
        pass


if __name__ == '__main__':
    # main()
    scheduler = AsyncIOScheduler()
    scheduler.start()
    scheduler.add_job(generate_debug_task, 'interval', args=(2,), seconds=10)

    try:
        asyncio.get_event_loop().run_forever()
    except:
        pass
