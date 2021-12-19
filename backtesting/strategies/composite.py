from typing import List, Optional, Tuple
import pandas as pd
import numpy as np

from strategies.cpp_strategy import CppStrategy
from strategies.strategy import Strategy
from tqdm import tqdm


class Composite(Strategy):
    def __init__(self, models: List[CppStrategy], threshold: float = 0, **kwargs):
        super().__init__(**kwargs)
        self.models = {i: model for i, model in enumerate(models)}
        self.threshold = threshold

    def name(self):
        return "composite"

    def backtest(self, df: Optional[pd.DataFrame] = None) -> Tuple[float, float]:
        pass

    def _execute(self):
        for _, model in self.models.items():
            model._execute()

    def set_target(self, exchange, symbol, tf, from_time, to_time, **kwargs):
        for _, model in self.models.items():
            model.set_target(exchange, symbol, tf, from_time, to_time, **kwargs)

    def signal_history(self, df):
        signals = {}
        for k, model in tqdm(self.models.items()):
            cpp_model: CppStrategy = model
            signals[k] = cpp_model.signal_history(df)

        vote: pd.Series = pd.DataFrame(signals).apply(np.mean, axis=1)

        signals_df = pd.Series(
            np.where(vote > self.threshold, 1,
                     np.where(vote < -self.threshold, -1, 0)
                     ),
            index=vote.index
        )

        return signals_df

    # def _trade_history(self, df) -> pd.DataFrame:
    #     pass
