#!/usr/bin/env python3

from sys import argv
from sys import exit as sys_exit
from json import loads as json_loads

# the alert-payload was saved to a file - we get the path to it as argument #1
file_in = argv[1]
with open(file_in, 'r', encoding='utf-8') as _f:
    data = json_loads(_f.read())

# implement alerting

if data['execution']['failed']:
    # failure action

    for host, stats in data['stats'].items():
        # print(f"STATS: {host} => {stats}")

        if stats['unreachable'] or stats['tasks_failed'] > 0:
            # hosts that failed
            # print(f"FAILED: {host}")
            pass

sys_exit(0)