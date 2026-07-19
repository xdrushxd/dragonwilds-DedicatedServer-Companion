import os
import pymysql
from datetime import datetime

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")


def db_enabled():
    return all([MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD])


def get_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def init_db():
    if not db_enabled():
        print("Database disabled: missing MySQL environment variables")
        return

    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS player_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            player_name VARCHAR(100) NOT NULL,
            account_id VARCHAR(100) NOT NULL,
            joined_at DATETIME NOT NULL,
            left_at DATETIME NULL,
            duration_seconds INT DEFAULT 0,
            INDEX(player_name),
            INDEX(account_id),
            INDEX(joined_at)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS server_metrics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            cpu_percent FLOAT NULL,
            memory_gib FLOAT NULL,
            players_online INT NOT NULL,
            INDEX(timestamp)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            message VARCHAR(255) NOT NULL,
            INDEX(timestamp)
        )
        """)

    conn.close()
    print("Database initialized")


def log_event(message):
    if not db_enabled():
        return

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO events (timestamp, message) VALUES (%s, %s)",
            (datetime.now(), message)
        )
    conn.close()


def player_join(account_id, player_name):
    if not db_enabled():
        return

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO player_sessions (player_name, account_id, joined_at)
            VALUES (%s, %s, %s)
        """, (player_name, account_id, datetime.now()))
    conn.close()


def player_leave(account_id):
    if not db_enabled():
        return

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, joined_at
            FROM player_sessions
            WHERE account_id = %s AND left_at IS NULL
            ORDER BY joined_at DESC
            LIMIT 1
        """, (account_id,))
        session = cur.fetchone()

        if session:
            duration = int((datetime.now() - session["joined_at"]).total_seconds())
            cur.execute("""
                UPDATE player_sessions
                SET left_at = %s, duration_seconds = %s
                WHERE id = %s
            """, (datetime.now(), duration, session["id"]))

    conn.close()


def log_metrics(cpu_percent, memory_gib, players_online):
    if not db_enabled():
        return

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO server_metrics
            (timestamp, cpu_percent, memory_gib, players_online)
            VALUES (%s, %s, %s, %s)
        """, (datetime.now(), cpu_percent, memory_gib, players_online))
    conn.close()

from utils import seconds_to_human


def get_leaderboard(limit=10):
    if not db_enabled():
        return []

    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                player_name,
                COUNT(*) AS sessions,
                SUM(duration_seconds) AS total_seconds,
                MAX(duration_seconds) AS longest_session
            FROM player_sessions
            WHERE duration_seconds > 0
            GROUP BY player_name
            ORDER BY total_seconds DESC
            LIMIT %s
        """, (limit,))

        rows = cur.fetchall()

    conn.close()

    leaderboard = []

    for row in rows:
        total = row["total_seconds"] or 0
        longest = row["longest_session"] or 0

        leaderboard.append({
            "player": row["player_name"],
            "sessions": row["sessions"],
            "total_seconds": int(total),
            "playtime": seconds_to_human(total),
            "longest_session": seconds_to_human(longest)
        })

    return leaderboard