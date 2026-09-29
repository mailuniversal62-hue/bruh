cat > risk.py << 'EOF'
import datetime
import config

STATE = {
    "daily_loss": 0.0,
    "total_pnl": 0.0,
    "consecutive_losses": 0,
    "trades_this_hour": 0,
    "hour_started": datetime.datetime.utcnow(),
    "halted": False,
    "halt_reason": None,
}


def _reset_hourly():
    now = datetime.datetime.utcnow()
    if (now - STATE["hour_started"]).total_seconds() >= 3600:
        STATE["trades_this_hour"] = 0
        STATE["hour_started"] = now


def can_trade():
    if STATE["halted"]:
        return False, STATE["halt_reason"] or "halted"
    _reset_hourly()
    if STATE["daily_loss"] >= config.MAX_DAILY_LOSS:
        STATE["halted"] = True
        STATE["halt_reason"] = f"daily loss limit (${STATE['daily_loss']:.2f})"
        return False, STATE["halt_reason"]
    if -STATE["total_pnl"] >= config.MAX_DRAWDOWN:
        STATE["halted"] = True
        STATE["halt_reason"] = f"drawdown (${-STATE['total_pnl']:.2f})"
        return False, STATE["halt_reason"]
    if STATE["consecutive_losses"] >= config.STOP_AFTER_CONSECUTIVE_LOSSES:
        STATE["halted"] = True
        STATE["halt_reason"] = f"{STATE['consecutive_losses']} losses in a row"
        return False, STATE["halt_reason"]
    if STATE["trades_this_hour"] >= config.MAX_TRADES_PER_HOUR:
        return False, "hourly limit"
    return True, "ok"


def record_result(pnl):
    STATE["daily_loss"] += max(0.0, -pnl)
    STATE["total_pnl"] += pnl
    STATE["trades_this_hour"] += 1
    STATE["consecutive_losses"] = STATE["consecutive_losses"] + 1 if pnl < 0 else 0
EOF
