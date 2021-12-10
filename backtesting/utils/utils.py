import datetime
import pathlib
from ctypes import c_void_p, c_char_p, c_longlong, c_int, c_double, CDLL, POINTER

import pandas as pd

TF_EQUIV = {'1m': '1Min', '5m': '5Min', '15m': '15Min', '30m': '30Min', '1h': '1H', '4h': '4H', '12h': '12H',
            '1d': '1D'}

STRAT_PARAMS = {
    'obv': {
        'ma_period': {'name': 'MA Period', 'type': int, 'min': 2, 'max': 200}
    },
    'ichimoku': {
        'kijun': {'name': 'Kijun Period', 'type': int, 'min': 2, 'max': 200},
        'tenkan': {'name': 'Tenkan Period', 'type': int, 'min': 2, 'max': 200}
    },
    'sup_res': {
        'min_points': {'name': 'Min. Points', 'type': int, 'min': 2, 'max': 20},
        'min_diff_points': {'name': 'Min. Diffenence between Points', 'type': int, 'min': 2, 'max': 100},
        'rounding_nb': {'name': 'Rounding Number', 'type': float, 'min': 1, 'max': 500, "decimals": 2},
        'take_profit': {'name': 'Take Profit %', 'type': float, 'min': 1, 'max': 40, "decimals": 2},
        'stop_loss': {'name': 'Stop Loss %', 'type': float, 'min': 1, 'max': 40, 'decimals': 2}
    },
    'sma': {
        'slow_ma': {'name': 'Slow MA Period', 'type': int, 'min': 2, 'max': 200},
        'fast_ma': {'name': 'Fast MA Period', 'type': int, 'min': 2, 'max': 200}
    },
    'psar': {
        'initial_acc': {'name': 'Initial Acceleration', 'type': float, 'min': 0.01, 'max': 0.2, "decimals": 2},
        'acc_increment': {'name': 'Acceleration Increment', 'type': float, 'min': 0.01, 'max': 0.3, "decimals": 2},
        'max_acc': {'name': 'Max. Acceleration', 'type': float, 'min': 0.05, 'max': 1, "decimals": 2},
    },
}


def ms_to_dt(ms: int) -> datetime.datetime:
    return datetime.datetime.utcfromtimestamp(ms / 1000)


def resample_timeframe(data: pd.DataFrame, tf: str) -> pd.DataFrame:
    return data.resample(TF_EQUIV[tf]).agg(
        {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }
    )


def get_library():
    lib = CDLL(pathlib.Path(__file__).parent.parent / "backtestingCpp/build/libbacktestingCpp.dylib", winmode=0)

    # SMA
    lib.Sma_new.restype = c_void_p
    lib.Sma_new.argtypes = [c_char_p, c_char_p, c_char_p, c_longlong, c_longlong, c_char_p]
    lib.Sma_execute_backtest.restype = c_void_p
    lib.Sma_execute_backtest.argtypes = [c_void_p, c_int, c_int]

    # lib.Sma_get_pnl.restype = c_double
    # lib.Sma_get_pnl.argtypes = [c_void_p]
    # lib.Sma_get_max_dd.restype = c_double
    # lib.Sma_get_max_dd.argtypes = [c_void_p]
    # lib.Sma_get_trades_size.restype = c_int
    # lib.Sma_get_trades_size.argtypes = [c_void_p]
    # lib.Sma_get_position.restype = POINTER(c_int)
    # lib.Sma_get_position.argtypes = [c_void_p]
    # lib.Sma_get_enter.restype = POINTER(c_double)
    # lib.Sma_get_enter.argtypes = [c_void_p]
    # lib.Sma_get_exit.restype = POINTER(c_double)
    # lib.Sma_get_exit.argtypes = [c_void_p]
    # lib.Sma_get_open.restype = POINTER(c_double)
    # lib.Sma_get_open.argtypes = [c_void_p]
    # lib.Sma_get_close.restype = POINTER(c_double)
    # lib.Sma_get_close.argtypes = [c_void_p]

    # PSAR
    lib.Psar_new.restype = c_void_p
    lib.Psar_new.argtypes = [c_char_p, c_char_p, c_char_p, c_longlong, c_longlong]
    lib.Psar_execute_backtest.restype = c_void_p
    lib.Psar_execute_backtest.argtypes = [c_void_p, c_double, c_double, c_double]

    lib.Psar_get_pnl.restype = c_double
    lib.Psar_get_pnl.argtypes = [c_void_p]
    lib.Psar_get_max_dd.restype = c_double
    lib.Psar_get_max_dd.argtypes = [c_void_p]

    # Generic

    lib._get_pnl.restype = c_double
    lib._get_pnl.argtypes = [c_void_p]
    lib._get_max_dd.restype = c_double
    lib._get_max_dd.argtypes = [c_void_p]
    lib._get_trades_size.restype = c_int
    lib._get_trades_size.argtypes = [c_void_p]
    lib._get_position.restype = POINTER(c_int)
    lib._get_position.argtypes = [c_void_p]
    lib._get_enter.restype = POINTER(c_double)
    lib._get_enter.argtypes = [c_void_p]
    lib._get_exit.restype = POINTER(c_double)
    lib._get_exit.argtypes = [c_void_p]
    lib._get_open.restype = POINTER(c_double)
    lib._get_open.argtypes = [c_void_p]
    lib._get_close.restype = POINTER(c_double)
    lib._get_close.argtypes = [c_void_p]

    return lib
