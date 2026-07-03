from flask import Flask, jsonify
import subprocess
import re
import time
import os
from datetime import datetime, timezone

app = Flask(__name__)

CONTAINER = "runescape-dragonwilds"
MAX_PLAYERS = 6
LOG_LINES = "15000"

# Change to the location where your wolrd save is.
SAVE_PATH = "/opt/dragonwilds/server-files/RSDragonwilds/Saved/SaveGames"


def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def get_logs():
    return run_cmd([
        "docker",
        "logs",
        "--tail",
        LOG_LINES,
        CONTAINER
    ])


def seconds_to_human(seconds):
    seconds = max(0, int(seconds))

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if days:
        return f"{days}d {hours}h {minutes}m"

    if hours:
        return f"{hours}h {minutes}m"

    if minutes:
        return f"{minutes}m"

    return f"{secs}s"


def get_last_save():
    newest = None

    for root, dirs, files in os.walk(SAVE_PATH):
        for file in files:
            path = os.path.join(root, file)

            try:
                mtime = os.path.getmtime(path)
            except:
                continue

            if newest is None or mtime > newest:
                newest = mtime

    if newest is None:
        return "Unknown"

    return seconds_to_human(time.time() - newest) + " ago"


def get_players():
    logs = get_logs()

    online = {}

    for line in logs.splitlines():

        added = re.search(
            r"Player ADDED to session \[(.*?)\]-\[(.*?)\]",
            line
        )

        if added:
            account = added.group(1)
            name = added.group(2)

            online[account] = name
            continue

        removed = re.search(
            r"Player Removed from session \[(.*?)\]-\[(.*?)\]",
            line
        )

        if removed:
            account = removed.group(1)
            online.pop(account, None)

    return list(online.values())


def get_world():
    logs = get_logs()

    match = re.search(
        r"Save completed SUCCESSFULLY \(slot:\s*(.*?)\)",
        logs
    )

    if match:
        return match.group(1)

    return "Unknown"


def get_version():
    logs = get_logs()

    patterns = [
        r"version[:= ]+([0-9A-Za-z\.\-_]+)",
        r"build[:= ]+([0-9A-Za-z\.\-_]+)",
        r"server version[:= ]+([0-9A-Za-z\.\-_]+)"
    ]

    for pattern in patterns:
        m = re.search(pattern, logs, re.IGNORECASE)

        if m:
            return m.group(1)

    return "Unknown"


def get_uptime():

    started = run_cmd([
        "docker",
        "inspect",
        "-f",
        "{{.State.StartedAt}}",
        CONTAINER
    ])

    try:
        started_dt = datetime.fromisoformat(
            started.replace("Z", "+00:00")
        )

        now = datetime.now(timezone.utc)

        return seconds_to_human(
            (now - started_dt).total_seconds()
        )

    except:
        return "Unknown"


def get_stats():

    output = run_cmd([
        "docker",
        "stats",
        "--no-stream",
        "--format",
        "{{.CPUPerc}}|{{.MemUsage}}",
        CONTAINER
    ])

    if "|" not in output:
        return {
            "cpu": "Unknown",
            "memory": "Unknown"
        }

    cpu, memory = output.split("|", 1)

    # Alleen gebruikt RAM tonen
    memory = memory.split("/")[0].strip()

    return {
        "cpu": cpu,
        "memory": memory
    }


@app.route("/status")
def status():

    players = get_players()
    stats = get_stats()

    return jsonify({

        "status": "online",

        "server": "Dragonwilds",

        "world": get_world(),

        "version": get_version(),

        "players_online": len(players),

        "max_players": MAX_PLAYERS,

        "players": players,

        "players_text": ", ".join(players) if players else "None",

        "memory": stats["memory"],

        "cpu": stats["cpu"],

        "uptime": get_uptime(),

        "last_save": get_last_save(),

        "updated": int(time.time())

    })


@app.route("/")
def index():

    return jsonify({

        "message": "Dragonwilds Companion",

        "endpoint": "/status"

    })


if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=9876

    )
