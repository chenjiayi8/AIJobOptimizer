#!/usr/bin/env python3

import os
import re
import time
from datetime import datetime
import sys
import hashlib

def write_log(msg):
    time_prefix = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
    time_prefix = time_prefix[:-3] + '$ '
    print(time_prefix + msg)


def delete_conflicts(folder, conflict_marker):
    # iterate through all files in folder recursively
    for root, _, files in os.walk(folder):
        for file in files:
            if 'sync-conflict' in file and conflict_marker in file:
                conflict = os.path.join(root, file)
                write_log(f"Deleting {conflict}")
                os.remove(conflict)

def get_pidfile_path():
    hashed_path = hashlib.sha256(os.getcwd().encode('utf-8')).hexdigest()
    hashed_path = os.path.join('/tmp', 'watch-conflict-' + hashed_path[:6] + '.pid')
    return hashed_path


def watcher(targets):
    # create pid file
    pid = str(os.getpid())
    pidfile = get_pidfile_path()
    with open(pidfile, 'w') as f:
        f.write(pid)
    config_path = os.path.expanduser('~/.config/syncthing/config.xml')
    if not os.path.exists(config_path):
        write_log("Config file not found")
        return
    with open(config_path, 'r', encoding="utf-8") as f:
        config = f.read()

    # find content of  <defaults> tag
    defaults = re.search(r'<defaults>(.*)</defaults>', config, re.DOTALL)
    # find device id in <device> tag
    device_id = re.search(
        r'<device id="(.*)" introducedBy="">', defaults.group(1))
    device_id = device_id.group(1)
    conflict_marker = device_id[:7]
    root = os.getcwd()
    if len(targets) == 0:
        folders = [root]
    else:
        folders = [os.path.join(root, target) for target in targets if os.path.isdir(
            os.path.join(root, target))]

    if len(folders) == 0:
        write_log("No valid folder found")
        return
    for folder in folders:
        write_log(f"Watching folder {folder} with marker {conflict_marker}")
    write_log("Press Ctrl + C to exit")
    interval = 5  # unit: mins
    try:
        while True:
            # delete all files with conflict marker
            for folder in folders:
                delete_conflicts(folder, conflict_marker)
            # sleep for 5 mins
            time.sleep(interval * 60)
    except KeyboardInterrupt:
        write_log("Exiting...")

def only_intance():
    # check if another instance is running
    pidfile = get_pidfile_path()
    # pid = str(os.getpid())
    # pidfile = "/tmp/watch-conflict.pid"
    if os.path.isfile(pidfile):
        with open(pidfile, 'r') as f:
            pid = f.read()
        if os.path.exists(f"/proc/{pid}"):
            return True
        else:
            os.remove(pidfile)
            return False


if __name__ == "__main__":
    if only_intance():
        write_log("Only one instance allowed")
        sys.exit(1)
    targets = sys.argv[1:]
    watcher(targets)
