#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from utils import Controller

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record_dir", type = str, default = "./recorded")
    parser.add_argument("--config_dir", type = str, default = ".")

    return vars(parser.parse_args())

def main():
    args = parse()
    ctrl = Controller(**args)
    ctrl.check(debug = True)

if __name__ == '__main__':
    main()
