import pandas as pd
import numpy as np
import ctypes

from strategies.strategy import Strategy
from utils import get_library


class CppStrategy(Strategy):
    def __init__(self):
        super().__init__()

        self.obj = None

        self.size_callback = None
        self.position_callback = None
        self.entry_callback = None
        self.exit_callback = None
        self.open_callback = None
        self.close_callback = None

    def _execute(self):
        pass

    def _size(self):
        return self.size_callback(self.obj)
        # return self.lib.Sma_get_trades_size(self.obj)

    def _positions(self, size):
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

    def _trades(self):
        self._execute()

        size = self._size()

        positions = self._positions(size)
        enter_at = self._enter_at(size)
        exit_at = self._exit_at(size)
        open_value = self._open(size)
        close_value = self._close(size)

        return pd.DataFrame({
            'position': positions,
            'enter_at': enter_at,
            'exit_at': exit_at,
            'open': open_value,
            'close': close_value
        })

