from typing import List

import pandas as pd
import numpy as np

from models import Trade
from strategies.strategy import NativeStrategy

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 150)
pd.set_option("display.width", 1000)


class Obv(NativeStrategy):
    def __init__(self, ma_period):
        super().__init__()
        self.ma_period: int = ma_period

    def name(self):
        return 'obv'

    # def _backtest(self, df):
    #     df["obv"] = (np.sign(df["close"].diff()) * df["volume"]).fillna(0).cumsum()
    #     df["obv_ma"] = round(df["obv"].rolling(window=self.ma_period).mean(), 2)
    #
    #     df["signal"] = np.where(df["obv"] > df["obv_ma"], 1, -1)
    #     df["close_change"] = df["close"].pct_change()
    #     df["signal_shift"] = df["signal"].shift(1)
    #     df["pnl"] = df["close"].pct_change() * df["signal"].shift(1)
    #
    #     df["cum_pnl"] = df["pnl"].cumsum()
    #     df["max_cum_pnl"] = df["cum_pnl"].cummax()
    #     df["drawdown"] = df["max_cum_pnl"] - df["cum_pnl"]
    #
    #     return df["pnl"].sum(), df["drawdown"].max()

    def _compute_history(self, df) -> pd.DataFrame:
        df["obv"] = (np.sign(df["close"].diff()) * df["volume"]).fillna(0).cumsum()
        df["obv_ma"] = round(df["obv"].rolling(window=self.ma_period).mean(), 2)

        df["signal"] = np.where(df["obv"] > df["obv_ma"], 1, -1)
        df["pct_close_change"] = df["close"].pct_change()
        df["signal_shift"] = df["signal"].shift(1)
        df["pnl"] = df["pct_close_change"] * df["signal_shift"]

        df["cum_pnl"] = df["pnl"].cumsum()
        df["max_cum_pnl"] = df["cum_pnl"].cummax()
        df["drawdown"] = df["max_cum_pnl"] - df["cum_pnl"]

        return df

    def _backtest(self, df):

        df = self._compute_history(df)

        return df["pnl"].sum(), df["drawdown"].max()

    def _trade_history(self, df) -> pd.DataFrame:
        raw_df = self._compute_history(df)

        mask = raw_df['pnl'].notna()

        # Crop first and last candle
        mask.iloc[0] = False
        mask.iloc[-1] = False

        trades = pd.DataFrame({
            # Signal is given at the end of last candle
            'position': raw_df[mask.shift(-1).fillna(False)]['signal'].values,
            # Position is entered at the current candle's start time
            'enter_at': raw_df[mask].index.values,
            # Position is exited at the next candle start time
            'exit_at': raw_df[mask.shift(1).fillna(False)].index.values,
            # Position is open at current candle's open value
            'open': raw_df[mask]['open'].values,
            # Position is closed at current candle's close value
            'close': raw_df[mask]['close'].values
        })

        return trades
