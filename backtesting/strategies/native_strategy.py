from typing import Optional, Tuple

import pandas as pd

from storage.database import Hdf5Client
from strategies.strategy import Strategy
from utils import resample_timeframe


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