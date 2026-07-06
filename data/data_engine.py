import yfinance as yf
import pandas as pd


class DataEngine:
    def __init__(self):
        pass

    def get_history(self, ticker, period="1y", interval="1d"):
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

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            required = ["Open", "High", "Low", "Close", "Volume"]

            for col in required:
                if col not in data.columns:
                    return pd.DataFrame()

            return data[required].dropna()

        except Exception:
            return pd.DataFrame()

    def get_current_price(self, ticker):
        data = self.get_history(ticker, period="5d", interval="1d")

        if data.empty:
            return None

        return float(data["Close"].iloc[-1])

    def get_options_expirations(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            return list(stock.options)
        except Exception:
            return []

    def get_option_chain(self, ticker, expiration):
        try:
            stock = yf.Ticker(ticker)
            chain = stock.option_chain(expiration)

            calls = chain.calls.copy()
            puts = chain.puts.copy()

            calls["type"] = "CALL"
            puts["type"] = "PUT"

            return calls, puts

        except Exception:
            return pd.DataFrame(), pd.DataFrame()

    def get_basic_info(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                "symbol": ticker,
                "name": info.get("shortName", ticker),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap", None),
                "beta": info.get("beta", None),
            }

        except Exception:
            return {
                "symbol": ticker,
                "name": ticker,
                "sector": "N/A",
                "industry": "N/A",
                "market_cap": None,
                "beta": None,
            }
