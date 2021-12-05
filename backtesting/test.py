import time
import numpy as np

from database import Hdf5Client
from utils import *


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Import and format the data

h5_df = Hdf5Client('binance')
data = h5_df.get_data('BTCUSDT', from_time=0, to_time=int(time.time() * 1000))
data = resample_timeframe(data, '1h')

# Perform operations on the DataFrame

data['high_low_average'] = (data['high'] + data['low'])/2

data['signal'] = np.where(data['close'] > data['high_low_average'], 1, -1)
print(data)
