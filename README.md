# Dragonwilds Dedicated Server Companion

A lightweight companion API for RuneScape: Dragonwilds Dedicated Servers.

Designed for Homepage dashboards, homelabs and self-hosted game servers.

## Features

- Live player count
- Live player names
- Server uptime
- Last save detection using save-file modification time
- World name detection
- CPU and RAM usage
- Homepage dashboard integration
- REST API endpoint

## API Output

```json
{
  "status": "online",
  "server": "Dragonwilds",
  "players_online": 1,
  "max_players": 6,
  "players_text": "xdrushxd",
  "uptime": "16h 15m",
  "last_save": "4m ago",
  "memory": "1.7GiB",
  "cpu": "6.5%"
}
