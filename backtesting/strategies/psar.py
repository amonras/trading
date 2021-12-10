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

    def name(self):
        return 'psar'

    # def backtest(self) -> Tuple[float, float]:
    #     lib = get_library()
    #
    #     path = str((pathlib.Path(__file__).parent.parent / 'data').absolute())
    #
    #     obj = lib.Psar_new(
    #         self.exchange.encode(),
    #         self.symbol.encode(),
    #         self.tf.encode(),
    #         self.from_time,
    #         self.to_time,
    #         path.encode()
    #     )
    #     lib.Psar_execute_backtest(obj, self.initial_acc, self.acc_increment, self.max_acc)
    #     pnl = lib.Psar_get_pnl(obj)
    #     max_drawdown = lib.Psar_get_max_dd(obj)
    #
    #     return pnl, max_drawdown

    def _execute(self):

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
