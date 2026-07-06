from data.data_engine import DataEngine

engine = DataEngine()

def get_price_data(ticker, period="1y", interval="1d"):
    return engine.get_history(ticker, period=period, interval=interval)
