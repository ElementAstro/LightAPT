# coding=utf-8

"""

Copyright(c) 2022-2023 Max Qian  <lightapt.com>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License version 3 as published by the Free Software Foundation.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.
You should have received a copy of the GNU Library General Public License
along with this library; see the file COPYING.LIB.  If not, write to
the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.

"""

import time
import subprocess

def set_ntp(enabled : bool) -> int:
    return subprocess.run(['sudo', 'timedatectl', 'set-ntp', 'true' if enabled else 'false']).returncode == 0

def get_timestamp() -> dict:
    return { 'utc_timestamp': time.time() }

def set_timestamp(timestamp) -> dict | None:
    timestamp = int(timestamp)
    if not __set_timestamp_timedatectl(timestamp) or not __set_timestamp_date(timestamp):
            return
    return get_timestamp()

def __set_timestamp_timedatectl(timestamp):
    return set_ntp(False) and subprocess.run(['sudo', 'timedatectl', 'set-time', '@{}'.format(timestamp)]).returncode == 0


def __set_timestamp_date(timestamp):
    return subprocess.run(['sudo', 'date', '-s', '@{}'.format(timestamp)]).returncode == 0