#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import argparse
from logging import getLogger

from utils import Controller, Recorder

SCHEDULE = "schedule.json"
CHANNEL = "channels.json"

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record_dir", type = str, default = "./recorded")
    parser.add_argument("--config_dir", type = str, default = ".")
    parser.add_argument("--debug", action = 'store_true')

    return vars(parser.parse_args())

def main():
    args = parse()

    debug = args["debug"]
    del(args["debug"])

    recorder = Recorder(
            os.path.join(args["config_dir"], CHANNEL),
            args["record_dir"]
            )
    controller = Controller(
            recorder,
            os.path.join(args["config_dir"], SCHEDULE)
            )

    controller.check()

if __name__ == '__main__':
    main()
