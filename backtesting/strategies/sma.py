import pathlib
from typing import Tuple

from strategies.cpp_strategy import CppStrategy
import plotly.graph_objects as go


class Sma(CppStrategy):
    def __init__(self, slow_ma: int, fast_ma: int):
        super(Sma, self).__init__()
        self.slow_ma = slow_ma
        self.fast_ma = fast_ma

        self.obj_creator = self.lib.Sma_new

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

    def get_indicators(self, df):
        slow_ma = df['close'].rolling(self.slow_ma).mean()
        fast_ma = df['close'].rolling(self.fast_ma).mean()

        return [go.Scatter(x=slow_ma.index, y=slow_ma.values, marker=dict(color='blue')),
                go.Scatter(x=fast_ma.index, y=fast_ma.values, marker=dict(color='orange'))]