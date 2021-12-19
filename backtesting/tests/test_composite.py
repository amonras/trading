from datetime import datetime
import pandas as pd

import pytest

from backtesting.strategies import *
from backtesting.strategies.strategy import Strategy
from storage.database import Hdf5Client
from strategies.composite import Composite
from strategies.cpp_strategy import CppStrategy
from utils import resample_timeframe

from_time = int(datetime(2021, 1, 1).timestamp() * 1000)
to_time = int(datetime(2021, 2, 1).timestamp() * 1000)

exchange = 'binance'
symbol = 'BTCUSDT'

tf = '1h'

db_client = Hdf5Client(exchange, path="tests/resources")


@pytest.fixture(
    params=[
        Composite([Sma(20, 10)]),
        Composite([Sma(10, 5), Sma(20, 10)])
    ]
)
def strategy(request) -> Composite:
    strtgy = request.param
    strtgy.set_target(exchange=exchange, symbol=symbol, tf=tf, from_time=from_time, to_time=to_time,
                      path="tests/resources")
    strtgy._execute()
    yield strtgy


@pytest.fixture
def data():
    df = db_client.get_data(symbol=symbol, from_time=from_time, to_time=to_time)
    df = resample_timeframe(df, tf)
    yield df


def test_signal_history(strategy: Composite, data: pd.DataFrame):
    signal_history = strategy.signal_history(data)
    assert len(signal_history) == len(data)


def test_trades(strategy: Composite, data: pd.DataFrame):
    trades = strategy.trade_history(data)
    print(trades)
    assert len(trades) > 0


def test_position_history(strategy: Composite, data: pd.DataFrame):
    position_history = strategy.signal_history(data)
    assert len(data) == len(position_history)


def test_trades_from_signal_match(strategy: Composite, data: pd.DataFrame):
    # Trades computed according to trade signal from C++
    python_calculation = strategy.trade_history_from_signal(data)

    # Trades computed according to trade records from C++
    cpp_calculation = strategy._trade_history(data)

    assert python_calculation.equals(cpp_calculation)


def test_real_case():
    from_date = int(datetime(2021, 1, 1).timestamp() * 1000)
    to_date = int(datetime(2021, 7, 1).timestamp() * 1000)
    today = int(datetime(2021, 12, 31).timestamp() * 1000)

    models = [{'slow_ma': 96, 'fast_ma': 3},
              {'slow_ma': 95, 'fast_ma': 3},
              {'slow_ma': 97, 'fast_ma': 4},
              {'slow_ma': 95, 'fast_ma': 4},
              {'slow_ma': 96, 'fast_ma': 4},
              {'slow_ma': 95, 'fast_ma': 5},
              {'slow_ma': 95, 'fast_ma': 2},
              {'slow_ma': 96, 'fast_ma': 2},
              {'slow_ma': 95, 'fast_ma': 10},
              {'slow_ma': 99, 'fast_ma': 3}]

    strategy = Composite([Sma(**model) for model in models])
    strategy.set_target('binance', 'BTCUSDT', '1h', from_date, to_date)
    strategy._execute()

    db = Hdf5Client('binance')
    data = db.get_data('BTCUSDT', from_date, to_date).sort_index()
    db.hf.close()
    df = resample_timeframe(data, '1h')

    trades = strategy.trade_history(df)