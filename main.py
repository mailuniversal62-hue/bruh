cat > main.py << 'EOF'
#!/usr/bin/env python3
"""AceTrader — Pocket Broker auto-trader."""

import asyncio
from colorama import Fore, Style, init

import config
import state as st
from pocket_client import PocketClient
from trader import Trader

init(autoreset=True)


async def run():
    print(f"{Fore.CYAN}AceTrader{Style.RESET_ALL} — Pocket Broker auto-trader")
    print(f"Asset      : {config.ASSET}")
    print(f"Timeframe  : {config.TIMEFRAME}s")
    print(f"Paper mode : {Fore.YELLOW}{config.PAPER_MODE}{Style.RESET_ALL}")
    print(f"Bet size   : ${config.TRADE_AMOUNT}")
    print(f"Daily cap  : ${config.MAX_DAILY_LOSS}")
    print(f"Drawdown   : ${config.MAX_DRAWDOWN}\n")

    if not config.PAPER_MODE:
        print(f"{Fore.RED}[!] LIVE MODE — real money at risk.{Style.RESET_ALL}\n")

    client = PocketClient(config.POCKET_SSID)
    await client.connect()
    print(f"{Fore.GREEN}[+] Connected.{Style.RESET_ALL}\n")

    st.update(running=True, paper_mode=config.PAPER_MODE, asset=config.ASSET)
    trader = Trader(client)

    try:
        while True:
            try:
                await trader.tick()
            except Exception as e:
                print(f"{Fore.RED}[!] tick error: {e}{Style.RESET_ALL}")
            await asyncio.sleep(config.LOOP_INTERVAL)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Stopping.{Style.RESET_ALL}")
    finally:
        st.update(running=False)
        await client.close()


if __name__ == "__main__":
    asyncio.run(run())
EOF
