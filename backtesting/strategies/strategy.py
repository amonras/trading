from typing import Tuple

import pandas as pd

from database import Hdf5Client
from utils import resample_timeframe


class Strategy:
    def __init__(self, **kwargs):
        self.exchange = None
        self.symbol = None
        self.tf = None
        self.from_time = None
        self.to_time = None

    def set_target(self, exchange, symbol, tf, from_time, to_time, **kwargs):
        self.exchange: str = exchange
        self.symbol: str = symbol
        self.tf: str = tf
        self.from_time: int = from_time
        self.to_time: int = to_time

    def backtest(self) -> Tuple[float, float]:
        pass


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

    def backtest(self):
        pass
