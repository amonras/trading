from typing import Tuple

from strategies.strategy import Strategy
from utils import get_library


class Psar(Strategy):
    def __init__(self, initial_acc: float, acc_increment: float, max_acc: float):
        super(Psar, self).__init__()
        self.initial_acc = initial_acc
        self.acc_increment = acc_increment
        self.max_acc = max_acc

    def backtest(self) -> Tuple[float, float]:
        lib = get_library()

        obj = lib.Psar_new(self.exchange.encode(), self.symbol.encode(), self.tf.encode(), self.from_time, self.to_time)
        lib.Psar_execute_backtest(obj, self.initial_acc, self.acc_increment, self.max_acc)
        pnl = lib.Psar_get_pnl(obj)
        max_drawdown = lib.Psar_get_max_dd(obj)

        return pnl, max_drawdown
