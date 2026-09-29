cat > indicators.py << 'EOF'
import pandas as pd
import numpy as np


def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(series, fast=12, slow=26, signal=9):
    ema_f = series.ewm(span=fast, adjust=False).mean()
    ema_s = series.ewm(span=slow, adjust=False).mean()
    line = ema_f - ema_s
    sig = line.ewm(span=signal, adjust=False).mean()
    hist = line - sig
    return line, sig, hist


def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def evaluate(df, cfg):
    close = df["close"]

    r = rsi(close, cfg.RSI_PERIOD).iloc[-1]
    if r < cfg.RSI_OVERSOLD:
        rsi_sig = "CALL"
    elif r > cfg.RSI_OVERBOUGHT:
        rsi_sig = "PUT"
    else:
        rsi_sig = "NEUTRAL"

    ml, sl, hist = macd(close, cfg.MACD_FAST, cfg.MACD_SLOW, cfg.MACD_SIGNAL)
    mn, sn, mp, sp = ml.iloc[-1], sl.iloc[-1], ml.iloc[-2], sl.iloc[-2]
    if mp < sp and mn > sn:
        macd_sig = "CALL"
    elif mp > sp and mn < sn:
        macd_sig = "PUT"
    else:
        macd_sig = "NEUTRAL"

    ef, es = ema(close, cfg.EMA_FAST), ema(close, cfg.EMA_SLOW)
    if ef.iloc[-2] < es.iloc[-2] and ef.iloc[-1] > es.iloc[-1]:
        ema_sig = "CALL"
    elif ef.iloc[-2] > es.iloc[-2] and ef.iloc[-1] < es.iloc[-1]:
        ema_sig = "PUT"
    else:
        ema_sig = "NEUTRAL"

    sigs = {"RSI": rsi_sig, "MACD": macd_sig, "EMA": ema_sig}
    calls = sum(1 for v in sigs.values() if v == "CALL")
    puts = sum(1 for v in sigs.values() if v == "PUT")

    if calls >= cfg.MIN_AGREEING and calls > puts:
        final = "CALL"
    elif puts >= cfg.MIN_AGREEING and puts > calls:
        final = "PUT"
    else:
        final = "NEUTRAL"

    return {
        "final": final,
        "per_indicator": sigs,
        "rsi_value": round(float(r), 2),
        "macd_hist": round(float(hist.iloc[-1]), 6),
        "price": float(close.iloc[-1]),
    }
EOF
