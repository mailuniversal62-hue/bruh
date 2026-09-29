cat > trader.py << 'EOF'
import os
import csv
import datetime
from colorama import Fore, Style

import config
import risk
import state as st
from indicators import evaluate
from pocket_client import PocketClient


class Trader:
    def __init__(self, client):
        self.client = client
        self.last_trade = None

    def _log(self, row):
        os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
        new = not os.path.exists(config.LOG_FILE)
        with open(config.LOG_FILE, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=row.keys())
            if new:
                w.writeheader()
            w.writerow(row)

    def _cooldown_ok(self):
        if not self.last_trade:
            return True
        return (datetime.datetime.utcnow() - self.last_trade).total_seconds() >= config.COOLDOWN_SECONDS

    async def tick(self):
        df = await self.client.get_candles(config.ASSET, config.TIMEFRAME, config.CANDLE_COUNT)
        if df.empty or len(df) < config.CANDLE_COUNT // 2:
            return

        sig = evaluate(df, config)
        st.update(
            last_signal=sig["final"],
            last_price=sig["price"],
            last_time=datetime.datetime.utcnow().isoformat(),
        )

        if sig["final"] == "NEUTRAL":
            return
        if not self._cooldown_ok():
            return

        ok, reason = risk.can_trade()
        if not ok:
            print(f"{Fore.YELLOW}[!] Skip — {reason}{Style.RESET_ALL}")
            st.update(halted=True, halt_reason=reason)
            return

        ts = datetime.datetime.utcnow().isoformat()
        price = sig["price"]
        direction = sig["final"]
        pnl = 0.0
        status = "paper"

        if config.PAPER_MODE:
            print(f"{Fore.CYAN}[PAPER] {direction} {config.ASSET} @ {price}{Style.RESET_ALL}")
        else:
            try:
                res = await self.client.place_trade(
                    config.ASSET, config.TRADE_AMOUNT, direction, config.TIMEFRAME
                )
                pnl = res.get("pnl", 0.0) if isinstance(res, dict) else 0.0
                status = "real"
                print(f"{Fore.GREEN}[REAL] {direction} pnl={pnl}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[!] Trade failed: {e}{Style.RESET_ALL}")
                return

        risk.record_result(pnl)
        self.last_trade = datetime.datetime.utcnow()

        st.update(
            total_pnl=risk.STATE["total_pnl"],
            today_pnl=-risk.STATE["daily_loss"],
            trades_today=risk.STATE["trades_this_hour"],
            halted=risk.STATE["halted"],
            halt_reason=risk.STATE["halt_reason"],
        )

        s = st.load()
        recent = s.get("recent", [])
        recent.insert(0, {
            "time": ts, "direction": direction, "price": price,
            "amount": config.TRADE_AMOUNT if not config.PAPER_MODE else 0,
            "pnl": pnl, "status": status,
        })
        st.save({**s, "recent": recent[:20]})

        self._log({
            "time": ts, "asset": config.ASSET, "direction": direction,
            "price": price, "amount": config.TRADE_AMOUNT if not config.PAPER_MODE else 0,
            "pnl": pnl, "status": status,
            "rsi": sig["rsi_value"], "macd_hist": sig["macd_hist"],
        })
EOF
