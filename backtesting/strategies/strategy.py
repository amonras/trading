from typing import Tuple, Optional
import numpy as np
import pandas as pd

from storage.database import Hdf5Client
from utils import resample_timeframe

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

    def backtest(self, df: Optional[pd.DataFrame] = None) -> Tuple[float, float]:
        pass

    def _trade_history(self, df) -> pd.DataFrame:
        pass

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


class NativeStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.db_client: Hdf5Client = None

    def set_target(self, exchange, symbol, tf, from_time, to_time, **kwargs):
        super().set_target(exchange, symbol, tf, from_time, to_time)
        self.db_client = Hdf5Client(exchange, kwargs.get('path'))

    def _get_data(self) -> pd.DataFrame:
        data = self.db_client.get_data(self.symbol, self.from_time, self.to_time)
        data = resample_timeframe(data, self.tf)
        return data

    def backtest(self, df: Optional[pd.DataFrame] = None) -> Tuple[float, float]:
        if df is None:
            df = self._get_data()

        return self._backtest(df)

    def _backtest(self, df: pd.DataFrame) -> Tuple[float, float]:
        pass

