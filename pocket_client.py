cat > pocket_client.py << 'EOF'
import asyncio
import pandas as pd
from BinaryOptionsToolsV2.pocketoption import PocketOptionAsync


class PocketClient:
    def __init__(self, ssid):
        self.ssid = ssid
        self.api = None

    async def connect(self):
        self.api = PocketOptionAsync(self.ssid)
        await self.api.wait_for_assets()
        return self.api

    async def get_candles(self, asset, timeframe, count):
        raw = await self.api.get_candles(asset, timeframe, count)
        rows = [{
            "time": c.get("time") or c.get("timestamp"),
            "open": float(c["open"]),
            "high": float(c["high"]),
            "low": float(c["low"]),
            "close": float(c["close"]),
        } for c in raw]
        return pd.DataFrame(rows).sort_values("time").reset_index(drop=True)

    async def place_trade(self, asset, amount, direction, duration):
        if direction == "CALL":
            return await self.api.buy(asset, amount, duration)
        return await self.api.sell(asset, amount, duration)

    async def close(self):
        if self.api:
            try:
                await self.api.close()
            except Exception:
                pass
EOF
