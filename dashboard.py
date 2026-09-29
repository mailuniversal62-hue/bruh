cat > dashboard.py << 'EOF'
#!/usr/bin/env python3
"""AceTrader dashboard."""

import subprocess
from flask import Flask, jsonify, render_template

import config
import state as st

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/state")
def api_state():
    return jsonify(st.load())


@app.route("/api/start", methods=["POST"])
def api_start():
    subprocess.run(["sudo", "systemctl", "start", "acetrader"], check=False)
    st.update(running=True)
    return jsonify({"ok": True})


@app.route("/api/stop", methods=["POST"])
def api_stop():
    subprocess.run(["sudo", "systemctl", "stop", "acetrader"], check=False)
    st.update(running=False)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host=config.DASHBOARD_HOST, port=config.DASHBOARD_PORT)
EOF
