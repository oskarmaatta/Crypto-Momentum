import pandas as pd
import math
from numbers import Integral

def backtest_sma(df: pd.DataFrame,
                 window: int,
                 stop_loss_atr: float | None = None,
                 take_profit_atr: float | None = None,
                 atr_window: int = 14) -> pd.DataFrame:

    for name, value in (("window", window), ("atr_window", atr_window)):
        if not isinstance(value, Integral) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    for name, value in (("stop_loss_atr", stop_loss_atr),
                        ("take_profit_atr", take_profit_atr)):
        if value is not None and (not math.isfinite(value) or value <= 0):
            raise ValueError(f"{name} must be a finite positive number or None")

    return_df = df[['time', 'open', 'high', 'low', 'close', 'Volume', 'RSI']].copy()
    return_df['sma'] = return_df['close'].rolling(window).mean()
    return_df['close_diff'] = return_df['close'].diff()
    return_df['position'] = (return_df['close'] > return_df['sma']).shift(1).fillna(False)
    return_df['pl'] = return_df['position'] * return_df['close_diff']

    if stop_loss_atr is not None or take_profit_atr is not None:
        previous_close = df['close'].shift(1)
        true_range = pd.concat([
            df['high'] - df['low'],
            (df['high'] - previous_close).abs(),
            (df['low'] - previous_close).abs(),
        ], axis=1).max(axis=1)
        return_df['atr'] = true_range.rolling(atr_window).mean()

        holding = False
        stop = target = None
        positions, profits, reasons = [], [], []
        bars = zip(df['open'], df['high'], df['low'], df['close'],
                   return_df['sma'], return_df['atr'])
        for i, (open_price, high, low, close, sma, atr) in enumerate(bars):
            positions.append(holding)
            profit = 0.0
            reason = None
            if holding:
                exit_price = close
                if stop is not None and open_price <= stop:
                    exit_price, reason = open_price, 'stop_loss'
                elif target is not None and open_price >= target:
                    exit_price, reason = open_price, 'take_profit'
                elif stop is not None and low <= stop:
                    exit_price, reason = stop, 'stop_loss'
                elif target is not None and high >= target:
                    exit_price, reason = target, 'take_profit'
                elif close <= sma:
                    reason = 'sma'
                profit = exit_price - return_df['close'].iloc[i - 1]
                if reason is not None:
                    holding = False

            if not holding and close > sma and pd.notna(atr) and atr > 0:
                holding = True
                stop = close - stop_loss_atr * atr if stop_loss_atr is not None else None
                target = close + take_profit_atr * atr if take_profit_atr is not None else None
            profits.append(profit)
            reasons.append(reason)

        return_df['position'] = positions
        return_df['pl'] = profits
        return_df['exit_reason'] = reasons

    return_df['cumulative_pl'] = return_df['pl'].cumsum()

    return return_df
