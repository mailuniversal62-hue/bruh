cat > launcher.py << 'EOF'
#!/usr/bin/env python3
"""AceTrader launcher."""

import os
import re
import sys
import subprocess

CONFIG = "config.py"


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def banner():
    print(r"""
    ___                 _____              _
   / _ \               |_   _| _ __ _  __| | ___ _ __
  / /_\ \  ___ ___ ___   | || '__/ _` |/ _` |/ _ \ '__|
 / /   \ \|___|___|___|  | || | | (_| | (_| |  __/ |
 \/     \/               |_||_|  \__,_|\__,_|\___|_|
""")
    print("  AceTrader — Pocket Broker auto-trader\n")


def read_config():
    if not os.path.exists(CONFIG):
        print(f"[!] {CONFIG} not found. Run from the acetrader folder.")
        sys.exit(1)
    with open(CONFIG) as f:
        return f.read()


def get_value(key):
    txt = read_config()
    m = re.search(rf"^{key}\s*=\s*(.+)$", txt, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")


def set_value(key, value):
    txt = read_config()
    new_line = f"{key} = {value}"
    if re.search(rf"^{key}\s*=", txt, re.MULTILINE):
        txt = re.sub(rf"^{key}\s*=.*$", new_line, txt, flags=re.MULTILINE)
    else:
        txt += "\n" + new_line + "\n"
    with open(CONFIG, "w") as f:
        f.write(txt)


def current_status():
    paper = get_value("PAPER_MODE")
    mode = "DEMO / PRACTICE" if paper == "True" else "REAL MONEY"
    return (mode, get_value("TRADE_AMOUNT"), get_value("MAX_DAILY_LOSS"), get_value("MAX_DRAWDOWN"))


def menu():
    clear(); banner()
    mode, bet, loss, dd = current_status()
    print(f"  Current mode      : {mode}")
    print(f"  Bet per trade     : ${bet}")
    print(f"  Max daily loss    : ${loss}")
    print(f"  Max drawdown      : ${dd}")
    print()
    print("  [1]  Start — Real money")
    print("  [2]  Start — Demo / practice")
    print()
    print("  [3]  Change bet per trade")
    print("  [4]  Change max daily loss")
    print("  [5]  Change max drawdown")
    print()
    print("  [6]  Open dashboard in new window")
    print("  [0]  Exit")
    print()
    try:
        return input("  Your choice >> ").strip()
    except (EOFError, KeyboardInterrupt):
        return "0"


def ask_number(prompt):
    try:
        n = float(input(prompt).strip())
        if n <= 0:
            print("  [!] Must be > 0."); input("  Enter..."); return None
        return n
    except Exception:
        print("  [!] Enter a number."); input("  Enter..."); return None


def change_bet():
    clear(); banner()
    cur = get_value("TRADE_AMOUNT")
    print(f"  Bet per trade (current: ${cur})\n")
    n = ask_number("  New bet amount $ >> ")
    if n: set_value("TRADE_AMOUNT", f"{n:.2f}")


def change_daily_loss():
    clear(); banner()
    cur = get_value("MAX_DAILY_LOSS")
    print(f"  Max daily loss (current: ${cur})\n")
    n = ask_number("  New daily loss cap $ >> ")
    if n: set_value("MAX_DAILY_LOSS", f"{n:.2f}")


def change_drawdown():
    clear(); banner()
    cur = get_value("MAX_DRAWDOWN")
    print(f"  Max drawdown (current: ${cur})\n")
    n = ask_number("  New max drawdown $ >> ")
    if n: set_value("MAX_DRAWDOWN", f"{n:.2f}")


def confirm_real():
    clear(); banner()
    bet, loss, dd = get_value("TRADE_AMOUNT"), get_value("MAX_DAILY_LOSS"), get_value("MAX_DRAWDOWN")
    print("  !  REAL MONEY MODE\n")
    print(f"    Bet per trade    : ${bet}")
    print(f"    Max daily loss   : ${loss}")
    print(f"    Max drawdown     : ${dd}")
    print(f"\n  Worst-case loss today: ${loss}")
    print(f"  Worst-case loss ever : ${dd}\n")
    return input("  Type YES to continue >> ").strip() == "YES"


def launch():
    print("\n  [*] Starting AceTrader...\n")
    try:
        subprocess.run([sys.executable, "main.py"], check=False)
    except KeyboardInterrupt:
        print("\n  [*] Stopped.")


def open_dashboard():
    print("\n  [*] Starting dashboard...")
    subprocess.Popen(
        ["x-terminal-emulator", "-e", f"bash -c '{sys.executable} dashboard.py; exec bash'"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print("  [+] http://0.0.0.0:5000")
    input("\n  Enter...")


def main():
    read_config()
    while True:
        c = menu()
        if c == "0":
            print("  Bye."); break
        elif c == "1":
            if confirm_real():
                set_value("PAPER_MODE", "False"); launch()
                input("\n  Enter...")
            else:
                print("  Cancelled."); input("  Enter...")
        elif c == "2":
            set_value("PAPER_MODE", "True"); launch()
            input("\n  Enter...")
        elif c == "3": change_bet()
        elif c == "4": change_daily_loss()
        elif c == "5": change_drawdown()
        elif c == "6": open_dashboard()
        else:
            print("  [!] 0-6."); input("  Enter...")


if __name__ == "__main__":
    main()
EOF
