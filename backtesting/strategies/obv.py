import pandas as pd
import numpy as np

from strategies.native_strategy import NativeStrategy

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
        raw_df = self._compute_history(df).dropna()

        # Compare a signal with the previous signal, assign distinct labels to each contiguous set of signals
        trade_groups = (raw_df['signal'] != raw_df['signal'].shift(1)).astype(int).cumsum()

        # Signal is given at the end of last candle
        position = raw_df['signal'].groupby(trade_groups).agg(lambda x: x[0])
        # Position is entered at the current candle's start time
        enter_at = raw_df['signal'].groupby(trade_groups.shift(1)).agg(lambda x: x.index.min())
        # Position is exited at the next candle's start time
        exit_at = raw_df['signal'].groupby(trade_groups.shift(2)).agg(lambda x: x.index.max())
        # Position is open at first candle's open value
        open_value = raw_df['open'].groupby(trade_groups.shift(1)).agg('first')
        # Position is closed at last candle's close value
        close_value = raw_df['close'].groupby(trade_groups.shift(1)).agg('last')

        trades = pd.DataFrame({
            'position': position,
            'enter_at': enter_at,
            'exit_at': exit_at,
            'open': open_value,
            'close': close_value
        }).reset_index(drop=True)

        return trades
