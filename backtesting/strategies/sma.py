import pathlib
from typing import Tuple

from strategies.cpp_strategy import CppStrategy
from utils import get_library


class Sma(CppStrategy):
    def __init__(self, slow_ma: int, fast_ma: int):
        super(Sma, self).__init__()
        self.slow_ma = slow_ma
        self.fast_ma = fast_ma

    def name(self):
        return 'sma'

    def _execute(self):

        path = str((pathlib.Path(__file__).parent.parent / 'data').absolute())
        self.obj = self.lib.Sma_new(
            self.exchange.encode(),
            self.symbol.encode(),
            self.tf.encode(),
            self.from_time,
            self.to_time,
            path.encode()
        )
        self.lib.Sma_execute_backtest(self.obj, self.slow_ma, self.fast_ma)

    def backtest(self) -> Tuple[float, float]:
        self._execute()

        pnl = self.lib.get_pnl(self.obj)
        max_drawdown = self.lib.get_max_dd(self.obj)

        return pnl, max_drawdown
