import argparse
from pathlib import Path
import yfinance as yf


DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

btc = yf.download(
    "BTC-USD",
    period="max",
    interval="5m",
    progress=False,
)

btc.to_parquet(DATA_DIR / "btc_usd_5m.parquet")

print(f"Downloaded {len(btc):,} rows")
