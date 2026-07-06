import yfinance as yf
import pandas as pd

def get_price_data(ticker, period="1y", interval="1d"):
    try:
        data = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
            group_by="column"
        )

        if data is None or data.empty:
            return pd.DataFrame()

        # Arregla columnas tipo MultiIndex si yfinance las devuelve así
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        required_cols = ["Open", "High", "Low", "Close", "Volume"]

        for col in required_cols:
            if col not in data.columns:
                return pd.DataFrame()

        data = data[required_cols].dropna()

        return data

    except Exception:
        return pd.DataFrame()
