#!/usr/bin/env python3
# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import multiprocessing
import concurrent.futures
import subprocess
import sys
from functools import partial


def run(lock, parameter_file, n):
    cmd = ['./usergen.sh', str(n), parameter_file]
    print('executing', cmd)
    output = subprocess.run(cmd, shell=False, stdout=subprocess.PIPE).stdout
    print(output)

    with lock:
        with open('output.txt', 'a') as f:
            f.writelines(output)


def main():
    start = int(sys.argv[1])
    count = int(sys.argv[2])
    parameter_file = sys.argv[3]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        lock = multiprocessing.Manager().Lock()
        executor.map(partial(run, lock, parameter_file), range(start, start+count))


if __name__ == '__main__':
    main()
