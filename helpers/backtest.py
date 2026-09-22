import pandas as pd

def backtest_sma(df: pd.DataFrame, window: int) -> pd.DataFrame:
    close = df["Close"].squeeze()

    sma = close.rolling(window).mean()
    returns = close.pct_change()

    position = (close > sma).shift(1).fillna(False)

    strategy_returns = returns * position
    cumulative_returns = (1 + strategy_returns).cumprod() - 1

    cumulative_buys = (position & ~position.shift(1).fillna(False)).cumsum()
    cumulative_sells = (~position & position.shift(1).fillna(False)).cumsum()

    return pd.DataFrame({
        "close": close,
        "sma": sma,
        "position": position,
        "returns": strategy_returns,
        "cumulative_returns": cumulative_returns,
        "cumulative_buys": cumulative_buys,
        "cumulative_sells": cumulative_sells
    })