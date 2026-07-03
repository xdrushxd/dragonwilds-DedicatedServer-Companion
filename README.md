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
```
# Docker Installation (Recommended)

Clone the repository:

```bash
git clone https://github.com/xdrushxd/dragonwilds-DedicatedServer-Companion.git
cd dragonwilds-DedicatedServer-Companion
```

Edit `docker-compose.yml` and configure the following values:

```yaml
services:
  dragonwilds-companion:
    build: .
    container_name: dragonwilds-companion
    restart: unless-stopped

    ports:
      - "9876:9876"

    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /opt/dragonwilds/server-files/RSDragonwilds/Saved/SaveGames:/savegames:ro

    environment:
      CONTAINER: runescape-dragonwilds
      SAVE_PATH: /savegames
      MAX_PLAYERS: 6
```

Start the companion:

```bash
docker compose up -d
```

Verify that it is running:

```bash
docker ps
```

Open:

```text
http://YOUR_DOCKER_HOST_IP:9876/status
```

---


## Manual Installation

```bash
cd /opt
git clone https://github.com/xdrushxd/dragonwilds-DedicatedServer-Companion.git
cd dragonwilds-DedicatedServer-Companion
apt update
apt install -y python3-flask
```

## Configuration

Edit `app.py` and set your paths:

```python
CONTAINER = "runescape-dragonwilds"
SAVE_PATH = "/opt/dragonwilds/server-files/RSDragonwilds/Saved/SaveGames"
MAX_PLAYERS = 6
```

## Run manually

```bash
python3 app.py
```

Open:

```text
http://YOUR_DOCKER_HOST_IP:9876/status
```

## Run as a service

```bash
cp systemd/dragonwilds-companion.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now dragonwilds-companion
systemctl status dragonwilds-companion
```

## Homepage Integration

Example widget:

```yaml
- Dragonwilds:
    icon: runescape
    description: RuneScape Dragonwilds
    server: docker
    container: runescape-dragonwilds
    showstats: true
    widget:
      type: customapi
      url: http://YOUR_DOCKER_HOST_IP:9876/status
      mappings:
        - field: players_online
          label: Players
        - field: players_text
          label: Names
        - field: uptime
          label: Uptime
        - field: last_save
          label: Save
```

## Requirements

- Python 3
- Flask
- Docker
- RuneScape: Dragonwilds dedicated server running in Docker

## Roadmap

- [x] Player monitoring
- [x] Homepage widget
- [x] Save detection
- [x] Docker stats
- [ ] Discord webhook
- [ ] Web dashboard
- [ ] Docker image
- [ ] Backup monitoring
- [ ] Steam update checker

## License

MIT
