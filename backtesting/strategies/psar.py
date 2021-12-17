import pathlib
from typing import Tuple

from strategies.cpp_strategy import CppStrategy
from utils import get_library


class Psar(CppStrategy):
    def __init__(self, initial_acc: float, acc_increment: float, max_acc: float):
        super(Psar, self).__init__()
        self.initial_acc = initial_acc
        self.acc_increment = acc_increment
        self.max_acc = max_acc

        self.obj_creator = self.lib.Psar_new

    def name(self):
        return 'psar'

    def _execute(self):
        super()._execute()
        path = str((pathlib.Path(__file__).parent.parent / 'data').absolute())
        self.obj = self.lib.Psar_new(
            self.exchange.encode(),
            self.symbol.encode(),
            self.tf.encode(),
            self.from_time,
            self.to_time,
            path.encode()
        )
        self.lib.Psar_execute_backtest(self.obj, self.initial_acc, self.acc_increment, self.max_acc)

    def backtest(self) -> Tuple[float, float]:
        self._execute()

        pnl = self.lib.get_pnl(self.obj)
        max_drawdown = self.lib.get_max_dd(self.obj)

        return pnl, max_drawdown
