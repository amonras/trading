import pandas as pd
import numpy as np
import ctypes

from strategies.strategy import Strategy
from utils import get_library


class CppStrategy(Strategy):
    def __init__(self):
        super().__init__()

        self.obj = None

        self.lib = get_library()

        self.size_callback = self.lib.get_trades_size
        self.position_callback = self.lib.get_position
        self.entry_callback = self.lib.get_enter
        self.exit_callback = self.lib.get_exit
        self.open_callback = self.lib.get_open
        self.close_callback = self.lib.get_close

        self.signal_history_size_callback = self.lib.get_position_history_size
        self.signal_history_callback = self.lib.get_position_history

    def _execute(self):
        pass

    def _signal_history_size(self):
        return self.signal_history_size_callback(self.obj)

    def _signal_history(self, size):
        if size == 0:
            return []

        head_pointer = self.signal_history_callback(self.obj)
        array_pointer = ctypes.cast(head_pointer, ctypes.POINTER(ctypes.c_int * size))
        return np.frombuffer(array_pointer.contents, dtype=ctypes.c_int, count=size)

    def signal_history(self, df):
        self._execute()

        size = self._signal_history_size()

        signal_history = self._signal_history(size)

        df = pd.Series(
            signal_history,
            index=df.index,
            name='signal'
        )

        return df

    def _size(self):
        return self.size_callback(self.obj)

    def _positions(self, size):
        if size == 0:
            return []

        # ArrayType = ctypes.c_int * size
        head_pointer = self.position_callback(self.obj)
        # head_pointer = self.lib.Sma_get_position(self.obj)

        # SLOWER. SAFER
        # Copy data. No problem with deallocation
        # vals = np.fromiter(head_pointer, dtype=np.int, count=size)

        # FASTER. RISKIER
        # Do not copy data. May get corrupted if sma object is freed.
        array_pointer = ctypes.cast(head_pointer, ctypes.POINTER(ctypes.c_int * size))
        return np.frombuffer(array_pointer.contents, dtype=ctypes.c_int, count=size)

    def _enter_at(self, size):
        if size == 0:
            return []
        # ArrayType = ctypes.c_int * size
        head_pointer = self.entry_callback(self.obj)
        # head_pointer = self.lib.Sma_get_enter(self.obj)

        # SLOWER. SAFER
        # Copy data. No problem with deallocation
        # vals = np.fromiter(head_pointer, dtype=np.int, count=size)

        # FASTER. RISKIER
        # Do not copy data. May get corrupted if sma object is freed.
        array_pointer = ctypes.cast(head_pointer, ctypes.POINTER(ctypes.c_double * size))
        array = np.frombuffer(array_pointer.contents, dtype=ctypes.c_double, count=size)

        return array.astype('datetime64[ms]')

    def _exit_at(self, size):
        if size == 0:
            return []

        # ArrayType = ctypes.c_int * size
        head_pointer = self.exit_callback(self.obj)
        # head_pointer = self.lib.Sma_get_exit(self.obj)

        # SLOWER. SAFER
        # Copy data. No problem with deallocation
        # vals = np.fromiter(head_pointer, dtype=np.int, count=size)

        # FASTER. RISKIER
        # Do not copy data. May get corrupted if sma object is freed.
        array_pointer = ctypes.cast(head_pointer, ctypes.POINTER(ctypes.c_double * size))
        array = np.frombuffer(array_pointer.contents, dtype=ctypes.c_double, count=size)

        return array.astype('datetime64[ms]')

    def _open(self, size):
        if size == 0:
            return []

        # ArrayType = ctypes.c_int * size
        head_pointer = self.open_callback(self.obj)
        # head_pointer = self.lib.Sma_get_enter(self.obj)

        # SLOWER. SAFER
        # Copy data. No problem with deallocation
        # vals = np.fromiter(head_pointer, dtype=np.int, count=size)

        # FASTER. RISKIER
        # Do not copy data. May get corrupted if sma object is freed.
        array_pointer = ctypes.cast(head_pointer, ctypes.POINTER(ctypes.c_double * size))
        array = np.frombuffer(array_pointer.contents, dtype=ctypes.c_double, count=size)

        return array

    def _close(self, size):
        if size == 0:
            return []

        # ArrayType = ctypes.c_int * size
        head_pointer = self.close_callback(self.obj)
        # head_pointer = self.lib.Sma_get_enter(self.obj)

        # SLOWER. SAFER
        # Copy data. No problem with deallocation
        # vals = np.fromiter(head_pointer, dtype=np.int, count=size)

        # FASTER. RISKIER
        # Do not copy data. May get corrupted if sma object is freed.
        array_pointer = ctypes.cast(head_pointer, ctypes.POINTER(ctypes.c_double * size))
        array = np.frombuffer(array_pointer.contents, dtype=ctypes.c_double, count=size)

        return array

    def _trade_history(self, df):
        self._execute()

        size = self._size()

        positions = self._positions(size)
        enter_at = self._enter_at(size)
        exit_at = self._exit_at(size)
        open_value = self._open(size)
        close_value = self._close(size)

        df = pd.DataFrame({
            'position': positions,
            'enter_at': enter_at,
            'exit_at': exit_at,
            'open': open_value,
            'close': close_value
        })

        return df
