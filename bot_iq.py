from iqoptionapi.stable_api import IQ_Option
import time
import numpy as np
import pandas as pd
from ta.volatility import AverageTrueRange

# Konfigurasi Akun
IQ_EMAIL = "your_email@example.com"
IQ_PASSWORD = "your_password"
iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
iq.connect()

# Pastikan koneksi berhasil
if iq.check_connect():
    print("Login Berhasil!")
else:
    print("Login Gagal!")
    exit()

# Parameter Trading
PAIR = "EURUSD"
TIMEFRAME = 1  # Timeframe M1
BALANCE = iq.get_balance()
RISK_PER_TRADE = 0.02  # 2% dari modal
STOP_LOSS_MULTIPLIER = 1.5  # ATR x 1.5
TAKE_PROFIT_MULTIPLIER = 2  # ATR x 2

# Fungsi mendapatkan data historis
def get_candles(pair, timeframe, count):
    candles = iq.get_candles(pair, (timeframe * 60), count, time.time())
    df = pd.DataFrame(candles)[['open', 'high', 'low', 'close']]
    return df

# Fungsi mendeteksi Order Block (OB)
def detect_order_block(df):
    recent_high = df['high'].iloc[-5:].max()
    recent_low = df['low'].iloc[-5:].min()

    # Order Block Bullish (Buy Entry)
    if df['close'].iloc[-1] > recent_high:
        return "BUY", recent_high

    # Order Block Bearish (Sell Entry)
    elif df['close'].iloc[-1] < recent_low:
        return "SELL", recent_low

    return None, None

# Fungsi menghitung ATR untuk SL & TP
def calculate_atr(df):
    df['ATR'] = AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
    return df['ATR'].iloc[-1]

# Fungsi untuk eksekusi trade
def place_trade(direction, entry_price, sl, tp):
    amount = BALANCE * RISK_PER_TRADE
    status, order_id = iq.buy(amount, PAIR, direction.lower(), TIMEFRAME)
    if status:
        print(f"Trade {direction} Placed @ {entry_price}, SL: {sl}, TP: {tp}")
    else:
        print("Trade Gagal!")

# Main Loop
while True:
    df = get_candles(PAIR, TIMEFRAME, 20)
    direction, order_block = detect_order_block(df)

    if direction:
        atr = calculate_atr(df)
        if direction == "BUY":
            sl = order_block - (STOP_LOSS_MULTIPLIER * atr)
            tp = order_block + (TAKE_PROFIT_MULTIPLIER * atr)
        else:
            sl = order_block + (STOP_LOSS_MULTIPLIER * atr)
            tp = order_block - (TAKE_PROFIT_MULTIPLIER * atr)

        place_trade(direction, order_block, sl, tp)

    time.sleep(5)  # Tunggu sebelum cek lagi
  
