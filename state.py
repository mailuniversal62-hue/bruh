cat > state.py << 'EOF'
import os
import json
import tempfile
import config

DEFAULTS = {
    "running": False,
    "paper_mode": True,
    "asset": "EURUSD_otc",
    "last_signal": None,
    "last_price": None,
    "last_time": None,
    "total_pnl": 0.0,
    "today_pnl": 0.0,
    "trades_today": 0,
    "halted": False,
    "halt_reason": None,
    "recent": [],
}


def load():
    path = config.STATE_FILE
    if not os.path.exists(path):
        return dict(DEFAULTS)
    try:
        with open(path) as f:
            data = json.load(f)
        out = dict(DEFAULTS)
        out.update(data)
        return out
    except Exception:
        return dict(DEFAULTS)


def save(s):
    path = config.STATE_FILE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(s, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)


def update(**kwargs):
    s = load()
    s.update(kwargs)
    save(s)
EOF
