from typing import Tuple, Optional
import numpy as np
import pandas as pd

import plotly.graph_objects as go


class Strategy:
    def __init__(self, **kwargs):
        self.exchange = None
        self.symbol = None
        self.tf = None
        self.from_time = None
        self.to_time = None

        self.trades = None

    def set_target(self, exchange, symbol, tf, from_time, to_time, **kwargs):
        self.exchange: str = exchange
        self.symbol: str = symbol
        self.tf: str = tf
        self.from_time: int = from_time
        self.to_time: int = to_time

        self.trades = None

    def name(self):
        pass

    def signal_history(self, df):
        pass

    def trade_history_from_signal(self, df):
        signal = self.signal_history(df)
        # Compare a signal with the previous signal, assign distinct labels to each contiguous set of signals
        trade_groups = (signal != signal.shift(1)).astype(int).cumsum()

        # Signal is given at the end of last candle
        position = signal.groupby(trade_groups).agg(lambda x: x[0])
        # Position is entered at the current candle's start time
        enter_at = signal.groupby(trade_groups.shift(1)).agg(lambda x: x.index.min())
        # Position is exited at the next candle's start time
        exit_at = signal.groupby(trade_groups.shift(2)).agg(lambda x: x.index.max())
        # Position is open at first candle's open value
        open_value = df['open'].groupby(trade_groups.shift(1)).agg('first')
        # Position is closed at last candle's close value
        close_value = df['open'].groupby(trade_groups.shift(2)).agg('last')

        trades = pd.DataFrame({
            'position': position,
            'enter_at': enter_at,
            'exit_at': exit_at,
            'open': open_value,
            'close': close_value
        })

        trades = trades[trades['position'] != 0].reset_index(drop=True)[:-1]

        return trades

    def backtest(self, df: Optional[pd.DataFrame] = None) -> Tuple[float, float]:
        pass

    def _trade_history(self, df) -> pd.DataFrame:
        return self.trade_history_from_signal(df)

    def trade_history(self, df) -> pd.DataFrame:

        trades = self._trade_history(df)
        try:
            assert 'position' in trades.columns
        except AssertionError as e:
            print(trades.head())
            raise e

        trades['pnl'] = trades['position'] * (trades['close'] - trades['open']) / trades['open']
        trades['log-returns'] = np.log(1 + trades['pnl'])
        trades['log-cum-returns'] = trades['log-returns'].cumsum()
        trades['cum-returns'] = np.exp(trades['log-cum-returns'])

        self.trades = trades

        return trades

    def get_trades(self):
        lines = []

        for i, trade in self.trades.iterrows():
            x = [trade['enter_at'], trade['exit_at']]
            y = [trade['open'], trade['close']]
            if (trade['close'] - trade['open'])*trade['position'] > 0:
                color = 'green'
            else:
                color = 'red'

            lines.append(
                go.Scatter(x=x, y=y, marker=dict(color=color), name=f'trade {i}', mode='lines')
            )

        return lines

    def get_indicators(self, df):
        pass
