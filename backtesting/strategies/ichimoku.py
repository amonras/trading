import pandas as pd
import numpy as np

from strategies.strategy import Strategy, NativeStrategy

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)


class Ichimoku(NativeStrategy):
    def __init__(self, tenkan: int, kijun: int):
        super().__init__()
        self.tenkan_period: int = tenkan
        self.kijun_period: int = kijun

    def name(self):
        return 'ichimoku'

    def _compute_history(self, df):
        # Tenkan Sen : Short-term signal line

        df["rolling_min_tenkan"] = df["low"].rolling(window=self.tenkan_period).min()
        df["rolling_max_tenkan"] = df["high"].rolling(window=self.tenkan_period).max()

        df["tenkan_sen"] = (df["rolling_max_tenkan"] + df["rolling_min_tenkan"]) / 2

        df.drop(["rolling_min_tenkan", "rolling_max_tenkan"], axis=1, inplace=True)

        # Kijun Sen : Long-term signal line

        df["rolling_min_kijun"] = df["low"].rolling(window=self.kijun_period).min()
        df["rolling_max_kijun"] = df["high"].rolling(window=self.kijun_period).max()

        df["kijun_sen"] = (df["rolling_max_kijun"] + df["rolling_min_kijun"]) / 2

        df.drop(["rolling_min_kijun", "rolling_max_kijun"], axis=1, inplace=True)

        # Senkou Span A

        df["senkou_span_a"] = ((df["tenkan_sen"] + df["kijun_sen"]) / 2).shift(self.kijun_period)

        # Senkou Span B

        df["rolling_min_senkou"] = df["low"].rolling(window=self.kijun_period * 2).min()
        df["rolling_max_senkou"] = df["high"].rolling(window=self.kijun_period * 2).max()

        df["senkou_span_b"] = ((df["rolling_max_senkou"] + df["rolling_min_senkou"]) / 2).shift(self.kijun_period)

        df.drop(["rolling_min_senkou", "rolling_max_senkou"], axis=1, inplace=True)

        # Chikou Span : Confirmation line

        df["chikou_span"] = df["close"].shift(self.kijun_period)

        df.dropna(inplace=True)

        # Signal

        df["tenkan_minus_kijun"] = df["tenkan_sen"] - df["kijun_sen"]
        df["prev_tenkan_minus_kijun"] = df["tenkan_minus_kijun"].shift(1)

        df["signal"] = np.where((df["tenkan_minus_kijun"] > 0) &
                                (df["prev_tenkan_minus_kijun"] < 0) &
                                (df["close"] > df["senkou_span_a"]) &
                                (df["close"] > df["senkou_span_b"]) &
                                (df["close"] > df["chikou_span"]), 1,

                                np.where((df["tenkan_minus_kijun"] < 0) &
                                         (df["prev_tenkan_minus_kijun"] > 0) &
                                         (df["close"] < df["senkou_span_a"]) &
                                         (df["close"] < df["senkou_span_b"]) &
                                         (df["close"] < df["chikou_span"]), -1, np.NaN))

        df = df[df["signal"] != 0].copy()

        df['close_pct_change'] = df["close"].pct_change()

        df["pnl"] = df["close"].pct_change() * df["signal"].shift(1)

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

        trades = pd.DataFrame({
            'position': raw_df[mask.shift(-1).fillna(False)]['signal'].values,
            'enter_at': raw_df[mask].index.values,
            'exit_at': raw_df[mask.shift(1).fillna(False)].index.values,
            'open': raw_df[mask]['open'].values,
            'close': raw_df[mask]['close'].values
        })

        return trades
