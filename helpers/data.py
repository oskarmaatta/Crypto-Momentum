from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw")

def load_bitcoin_prices(interval='5m') -> pd.DataFrame:
    return pd.read_parquet(DATA_DIR / f"btc_usd_{interval}.parquet")

def resample_ohlcv(df, interval):
    return df.resample(interval).agg({
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum"}).dropna()