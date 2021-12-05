from typing import Tuple

from strategies.strategy import Strategy
from utils import get_library


class Sma(Strategy):
    def __init__(self, slow_ma: int, fast_ma: int):
        super(Sma, self).__init__()
        self.slow_ma = slow_ma
        self.fast_ma = fast_ma

    def backtest(self) -> Tuple[float, float]:
        lib = get_library()

        obj = lib.Sma_new(self.exchange.encode(), self.symbol.encode(), self.tf.encode(), self.from_time, self.to_time)
        lib.Sma_execute_backtest(obj, self.slow_ma, self.fast_ma)
        pnl = lib.Sma_get_pnl(obj)
        max_drawdown = lib.Sma_get_max_dd(obj)

        return pnl, max_drawdown
