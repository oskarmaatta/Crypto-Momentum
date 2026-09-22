import pandas as pd

def backtest_sma(df: pd.DataFrame,
                 window: int) -> pd.DataFrame:

    return_df = df[['time', 'close']].copy()
    return_df['sma'] = return_df['close'].rolling(window).mean()
    return_df['close_diff'] = return_df['close'].diff()
    return_df['position'] = (return_df['close'] > return_df['sma']).shift(1).fillna(False)
    return_df['pl'] = return_df['position'] * return_df['close_diff']
    return_df['cumulative_pl'] = return_df['pl'].cumsum()

    return return_df