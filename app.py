from flask import Flask, jsonify
import config
from state import get_state
from monitor import start_monitor
from dockerstats import start_dockerstats
from savewatcher import start_savewatcher

app = Flask(__name__)


@app.route("/status")
def status():
    return jsonify(get_state())


@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>Dragonwilds Companion</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { background:#0f1117; color:#e5e7eb; font-family:Arial,sans-serif; margin:0; padding:30px; }
    .card { max-width:900px; margin:auto; background:#171a23; border-radius:18px; padding:28px; box-shadow:0 10px 30px #0006; }
    h1 { margin-top:0; color:#f59e0b; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:16px; margin-top:20px; }
    .box { background:#222633; padding:18px; border-radius:14px; }
    .label { color:#9ca3af; font-size:13px; }
    .value { font-size:24px; font-weight:bold; margin-top:6px; }
    ul { padding-left:20px; }
    .online { color:#22c55e; }
  </style>
</head>
<body>
  <div class="card">
    <h1> Dragonwilds Companion</h1>
    <p class="online"> Server Online</p>

    <div class="grid">
      <div class="box"><div class="label">Players</div><div class="value" id="players">...</div></div>
      <div class="box"><div class="label">Names</div><div class="value" id="names">...</div></div>
      <div class="box"><div class="label">World</div><div class="value" id="world">...</div></div>
      <div class="box"><div class="label">Uptime</div><div class="value" id="uptime">...</div></div>
      <div class="box"><div class="label">Last Save</div><div class="value" id="save">...</div></div>
      <div class="box"><div class="label">CPU</div><div class="value" id="cpu">...</div></div>
      <div class="box"><div class="label">RAM</div><div class="value" id="ram">...</div></div>
      <div class="box"><div class="label">Version</div><div class="value" id="version">...</div></div>
    </div>

    <h2>Recent Events</h2>
    <ul id="events"></ul>
  </div>

<script>
async function loadStatus() {
  const res = await fetch('/status');
  const s = await res.json();

  document.getElementById('players').innerText = `${s.players_online} / ${s.max_players}`;
  document.getElementById('names').innerText = s.players_text;
  document.getElementById('world').innerText = s.world;
  document.getElementById('uptime').innerText = s.uptime;
  document.getElementById('save').innerText = s.last_save;
  document.getElementById('cpu').innerText = s.cpu;
  document.getElementById('ram').innerText = s.memory;
  document.getElementById('version').innerText = s.version;

  const events = document.getElementById('events');
  events.innerHTML = '';
  (s.events || []).forEach(e => {
    const li = document.createElement('li');
    li.innerHTML =
        `<span style="color:#9ca3af;">[${e.timestamp}]</span> ${e.message}`;
    events.appendChild(li);
});
}

loadStatus();
setInterval(loadStatus, 5000);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    start_monitor()
    start_dockerstats()
    start_savewatcher()

    app.run(
        host="0.0.0.0",
        port=config.PORT
    )