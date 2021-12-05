import datetime
import logging

import backtester
from optimization.genetic import optimize
from data_collector import collect_all
from exchanges.binance import BinanceClient
from exchanges.ftx import FtxClient
from strategies.ichimoku import Ichimoku
from strategies.obv import Obv
from strategies.psar import Psar
from strategies.sma import Sma
from strategies.support_resistance import SupportResistance
from utils import TF_EQUIV, STRAT_PARAMS

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s %(levelname)s :: %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("info.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

if __name__ == '__main__':

    mode = input("Chose program mode (data / backtest / optimize)").lower()

    while True:
        exchange = input("Chose an exchange: ").lower()
        if exchange in ['binance', 'ftx']:
            break

    if exchange == 'binance':
        client = BinanceClient(True)
    elif exchange == 'ftx':
        client = FtxClient()

    print("Available symbols:")
    print(client.symbols)

    while True:
        symbol = input("Choose a symbol: ").upper()
        if symbol in client.symbols:
            break

    if mode == 'data':
        collect_all(client, exchange, symbol)
    elif mode in ['backtest', 'optimize']:

        # Strategy

        available_strategies = ['obv', 'ichimoku', "sup_res", "sma", "psar"]

        while True:
            strategy = input(f"Choose a strategy ({', '.join(available_strategies)})").lower()
            if strategy in available_strategies:
                break

        # Timeframe
        while True:
            tf = input(f"Choose a timeframe ({', '.join(TF_EQUIV.keys())})").lower()
            if tf in TF_EQUIV.keys():
                break

        # From
        while True:
            from_time = input(f"Backtest from (yyyy-mm-dd or press ENTER): ").lower()
            if from_time == "":
                from_time = 0
                break

            try:
                from_time = int(datetime.datetime.strptime(from_time, "%Y-%m-%d").timestamp() * 1000)
                break
            except ValueError:
                continue

        # To
        while True:
            to_time = input(f"Backtest to (yyyy-mm-dd or press ENTER): ").lower()
            if to_time == "":
                to_time = int(datetime.datetime.now().timestamp() * 1000)
                break

            try:
                to_time = int(datetime.datetime.strptime(to_time, "%Y-%m-%d").timestamp() * 1000)
                break
            except ValueError:
                continue

        if mode == 'backtest':
            strategy_mapping = {
                'obj': Obv,
                'ichimoku': Ichimoku,
                'sup_res': SupportResistance,
                'sma': Sma,
                'psar': Psar,
            }

            params_des = STRAT_PARAMS[strategy]

            params = dict()

            for p_code, p in params_des.items():
                while True:
                    try:
                        params[p_code] = p['type'](input(p['name'] + ': '))
                        break
                    except ValueError:
                        continue

            obj = strategy_mapping[strategy](**params)
            obj.set_target(exchange, symbol, tf, from_time, to_time)
            print(obj.backtest())
            # print(backtester.run(exchange, symbol, strategy, tf, from_time, to_time))

        elif mode == 'optimize':
            # Population size
            while True:
                try:
                    pop_size = int(input(f'Choose a population size: '))
                    break
                except ValueError:
                    continue
            # Iterations
            while True:
                try:
                    generations = int(input(f'Choose a number of generations: '))
                    break
                except ValueError:
                    continue

            optimize(exchange, symbol, strategy, tf, from_time, to_time, pop_size, generations)
