import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# === CONFIGURABLE PARAMETERS ===
STOP_LOSS = 50
TAKE_PROFIT = 100
TRAILING_STOP = 30
BREAKEVEN_TRIGGER = 30
MARTINGALE_FACTOR = 1.5
ALLOWED_SYMBOLS = ["XAUUSD", "US30", "NASDAQ", "GBPJPY", "BTCUSD"]
MAGIC = 222222

# === INDICATOR FUNCTIONS ===
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def is_bullish_pinbar(row):
    open_, close, high, low = row['open'], row['close'], row['high'], row['low']
    body = abs(close - open_)
    return close > open_ and (high - close) < body * 0.25 and (open_ - low) > body * 1.5

def is_bearish_pinbar(row):
    open_, close, high, low = row['open'], row['close'], row['high'], row['low']
    body = abs(close - open_)
    return open_ > close and (close - low) < body * 0.25 and (high - open_) > body * 1.5

def is_trading_time(dt):
    hour = dt.hour
    return 7 <= hour < 23

# === SIGNAL LOGIC ===
def is_buy_signal(df, i):
    if i < 50: return False
    rsi_val = df['rsi'].iloc[i]
    ema_val = df['ema'].iloc[i]
    price_now = df['close'].iloc[i]
    price_prev = df['close'].iloc[i-1]
    pinbar = is_bullish_pinbar(df.iloc[i-1])
    return rsi_val < 30 and price_prev < ema_val and price_now > ema_val and pinbar

def is_sell_signal(df, i):
    if i < 50: return False
    rsi_val = df['rsi'].iloc[i]
    ema_val = df['ema'].iloc[i]
    price_now = df['close'].iloc[i]
    price_prev = df['close'].iloc[i-1]
    pinbar = is_bearish_pinbar(df.iloc[i-1])
    return rsi_val > 70 and price_prev > ema_val and price_now < ema_val and pinbar

# === TRADE MANAGEMENT ===
def calculate_lot_size(symbol):
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"Symbol info not found for {symbol}")
        return 0.01
    tick_value = info.trade_tick_value
    lot_step = info.volume_step
    min_lot = info.volume_min
    max_lot = info.volume_max
    free_margin = mt5.account_info().margin_free
    lot = (free_margin / tick_value) * 0.01 if tick_value > 0 else min_lot
    lot = np.floor(lot / lot_step) * lot_step
    lot = max(min_lot, min(lot, max_lot))
    return round(lot, 2)

def execute_trade(symbol, is_buy, price):
    lot = calculate_lot_size(symbol)
    sl = price - STOP_LOSS * mt5.symbol_info(symbol).point if is_buy else price + STOP_LOSS * mt5.symbol_info(symbol).point
    tp = price + TAKE_PROFIT * mt5.symbol_info(symbol).point if is_buy else price - TAKE_PROFIT * mt5.symbol_info(symbol).point
    order_type = mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": MAGIC,
        "comment": "MetatraAutoPilot"
    }
    result = mt5.order_send(request)
    print(f"Trade executed: {'BUY' if is_buy else 'SELL'} {symbol} @ {price} Lot: {lot} Result: {result.retcode}")

def recover_losing_trades(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions is None: return
    for pos in positions:
        profit = pos.profit
        lot = pos.volume
        direction = pos.type
        if profit < 0:
            new_lot = round(lot * MARTINGALE_FACTOR, 2)
            execute_recovery_trade(symbol, direction, new_lot)

def execute_recovery_trade(symbol, direction, lot):
    price = mt5.symbol_info_tick(symbol).ask if direction == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
    sl = price - STOP_LOSS * mt5.symbol_info(symbol).point if direction == mt5.POSITION_TYPE_BUY else price + STOP_LOSS * mt5.symbol_info(symbol).point
    tp = price + TAKE_PROFIT * mt5.symbol_info(symbol).point if direction == mt5.POSITION_TYPE_BUY else price - TAKE_PROFIT * mt5.symbol_info(symbol).point
    order_type = mt5.ORDER_TYPE_BUY if direction == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_SELL
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": MAGIC,
        "comment": "MetatraRecovery"
    }
    result = mt5.order_send(request)
    print(f"Recovery trade: {'BUY' if direction == mt5.POSITION_TYPE_BUY else 'SELL'} {symbol} @ {price} Lot: {lot} Result: {result.retcode}")

def check_group_profit(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions is None: return
    total_profit = sum([pos.profit for pos in positions])
    if total_profit > 0:
        for pos in positions:
            close_position(pos)

def close_position(pos):
    symbol = pos.symbol
    ticket = pos.ticket
    volume = pos.volume
    price = mt5.symbol_info_tick(symbol).bid if pos.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(symbol).ask
    order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": ticket,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 10,
        "magic": MAGIC,
        "comment": "MetatraClose"
    }
    result = mt5.order_send(request)
    print(f"Position closed: {symbol} Ticket: {ticket} Result: {result.retcode}")

def apply_breakeven(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions is None: return
    for pos in positions:
        open_price = pos.price_open
        sl = pos.sl
        price = mt5.symbol_info_tick(symbol).bid if pos.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(symbol).ask
        profit_pts = (price - open_price) / mt5.symbol_info(symbol).point if pos.type == mt5.POSITION_TYPE_BUY else (open_price - price) / mt5.symbol_info(symbol).point
        if profit_pts >= BREAKEVEN_TRIGGER:
            new_sl = open_price + 10 * mt5.symbol_info(symbol).point if pos.type == mt5.POSITION_TYPE_BUY else open_price - 10 * mt5.symbol_info(symbol).point
            if (pos.type == mt5.POSITION_TYPE_BUY and new_sl > sl) or (pos.type == mt5.POSITION_TYPE_SELL and new_sl < sl):
                modify_sl(pos, new_sl)

def modify_sl(pos, new_sl):
    symbol = pos.symbol
    ticket = pos.ticket
    tp = pos.tp
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": ticket,
        "symbol": symbol,
        "sl": new_sl,
        "tp": tp,
        "magic": MAGIC,
        "comment": "MetatraSL"
    }
    result = mt5.order_send(request)
    print(f"SL modified: {symbol} Ticket: {ticket} New SL: {new_sl} Result: {result.retcode}")

def manage_trailing_stop(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions is None: return
    for pos in positions:
        sl = pos.sl
        price = mt5.symbol_info_tick(symbol).bid if pos.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(symbol).ask
        new_sl = price - TRAILING_STOP * mt5.symbol_info(symbol).point if pos.type == mt5.POSITION_TYPE_BUY else price + TRAILING_STOP * mt5.symbol_info(symbol).point
        if (pos.type == mt5.POSITION_TYPE_BUY and new_sl > sl) or (pos.type == mt5.POSITION_TYPE_SELL and new_sl < sl):
            modify_sl(pos, new_sl)

# === MAIN LOOP ===
def run_strategy(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 200)
    if rates is None or len(rates) < 60:
        print(f"Not enough data for {symbol}")
        return
    df = pd.DataFrame(rates)
    df['datetime'] = pd.to_datetime(df['time'], unit='s')
    df['ema'] = ema(df['close'], 50)
    df['rsi'] = rsi(df['close'], 14)
    for i in range(51, len(df)):
        row = df.iloc[i]
        dt = row['datetime']
        price = row['close']
        if not is_trading_time(dt):
            continue
        if is_buy_signal(df, i):
            execute_trade(symbol, True, mt5.symbol_info_tick(symbol).ask)
        elif is_sell_signal(df, i):
            execute_trade(symbol, False, mt5.symbol_info_tick(symbol).bid)
        recover_losing_trades(symbol)
        check_group_profit(symbol)
        manage_trailing_stop(symbol)
        apply_breakeven(symbol)

if __name__ == "__main__":
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        quit()
    for symbol in ALLOWED_SYMBOLS:
        print(f"Running strategy for {symbol}")
        run_strategy(symbol)
    mt5.shutdown() 