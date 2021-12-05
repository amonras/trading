import pandas as pd
import numpy as np

from strategies.strategy import NativeStrategy

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 150)
pd.set_option("display.width", 1000)


class Obv(NativeStrategy):
    def __init__(self, ma_period):
        super().__init__()
        self.ma_period: int = ma_period

    def _backtest(self, df):
        df["obv"] = (np.sign(df["close"].diff()) * df["volume"]).fillna(0).cumsum()
        df["obv_ma"] = round(df["obv"].rolling(window=self.ma_period).mean(), 2)

        df["signal"] = np.where(df["obv"] > df["obv_ma"], 1, -1)
        df["close_change"] = df["close"].pct_change()
        df["signal_shift"] = df["signal"].shift(1)
        df["pnl"] = df["close"].pct_change() * df["signal"].shift(1)

        df["cum_pnl"] = df["pnl"].cumsum()
        df["max_cum_pnl"] = df["cum_pnl"].cummax()
        df["drawdown"] = df["max_cum_pnl"] - df["cum_pnl"]

        return df["pnl"].sum(), df["drawdown"].max()
