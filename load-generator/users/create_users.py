#!/usr/bin/env python3
# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
import sys


def main():
    start = int(sys.argv[1])
    count = int(sys.argv[2])
    parameter_file = sys.argv[3]

    for n in range(start, start+count):
        cmd = ['./usergen.sh', str(n), parameter_file]
        proc = subprocess.Popen(cmd, shell=False)
        proc.communicate()


if __name__ == '__main__':
    main()
