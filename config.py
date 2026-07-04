import os

CONTAINER = os.getenv("CONTAINER", "runescape-dragonwilds")
SAVE_PATH = os.getenv("SAVE_PATH", "/savegames")
MAX_PLAYERS = int(os.getenv("MAX_PLAYERS", "6"))
PORT = int(os.getenv("PORT", "9876"))

LOG_LINES_ON_START = os.getenv("LOG_LINES_ON_START", "3000")