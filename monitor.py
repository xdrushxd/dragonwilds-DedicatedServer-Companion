import subprocess
import re
import threading
import config
from state import set_player, remove_player, update_field, add_event


def parse_line(line):
    added = re.search(r"Player ADDED to session \[(.*?)\]-\[(.*?)\]", line)
    if added:
        set_player(added.group(1), added.group(2))
        return

    removed = re.search(r"Player Removed from session \[(.*?)\]-\[(.*?)\]", line)
    if removed:
        remove_player(removed.group(1), removed.group(2))
        return

    world = re.search(r"Save completed SUCCESSFULLY \(slot:\s*(.*?)\)", line)
    if world:
        update_field("world", world.group(1))
        return

    version_patterns = [
        r"version[:= ]+([0-9A-Za-z\.\-_]+)",
        r"build[:= ]+([0-9A-Za-z\.\-_]+)",
        r"server version[:= ]+([0-9A-Za-z\.\-_]+)"
    ]

    for pattern in version_patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            update_field("version", match.group(1))
            return


def load_recent_logs():
    cmd = ["docker", "logs", "--tail", config.LOG_LINES_ON_START, config.CONTAINER]
    result = subprocess.run(cmd, capture_output=True, text=True)

    logs = result.stdout + "\n" + result.stderr
    for line in logs.splitlines():
        parse_line(line)


def follow_logs():
    cmd = ["docker", "logs", "-f", "--tail", "0", config.CONTAINER]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in process.stdout:
        parse_line(line)


def start_monitor():
    load_recent_logs()

    thread = threading.Thread(target=follow_logs, daemon=True)
    thread.start()