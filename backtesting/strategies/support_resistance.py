import pandas as pd

import matplotlib.pyplot as plt
import mplfinance as mpf
import time
import numpy as np

from strategies.strategy import Strategy, NativeStrategy

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)


class SupportResistance(NativeStrategy):
    def __init__(self, min_points: int, min_diff_points: int, rounding_nb: float, take_profit: float, stop_loss: float):
        super().__init__()
        self.min_points: int = min_points
        self.min_diff_points: int = min_diff_points
        self.rounding_nb: float = rounding_nb
        self.take_profit: float = take_profit
        self.stop_loss: float = stop_loss        
        
    def backtest(self):
        df = self._get_data()

        candle_length = df.iloc[1].name - df.iloc[0].name
    
        pnl = 0
        max_pnl = 0
        trade_side = 0
        entry_price = None
        max_drawdown = 0
    
        df["rounded_high"] = round(df["high"] / self.rounding_nb) * self.rounding_nb
        df["rounded_low"] = round(df["low"] / self.rounding_nb) * self.rounding_nb
    
        price_groups = {"supports": dict(), "resistances": dict()}
        levels = {"supports": [], "resistances": []}
        last_h_l = {"supports": [], "resistances": []}
        resistances_supports = {"supports": [], "resistances": []}
    
        # Numpy Arrays
    
        highs = np.array(df["high"])
        lows = np.array(df["low"])
        rounded_highs = np.array(df["rounded_high"])
        rounded_lows = np.array(df["rounded_low"])
        closes = np.array(df["close"])
        times = np.array(df.index)
    
        row = {"high": highs, "low": lows, "rounded_high": rounded_highs, "rounded_low": rounded_lows, "close": closes}
    
        for i in range(len(highs)):
    
            index = times[i]
    
            for side in ["resistances", "supports"]:
    
                h_l = "high" if side == "resistances" else "low"
    
                if row["rounded_" + h_l][i] in price_groups[side]:
    
                    grp = price_groups[side][row["rounded_" + h_l][i]]
    
                    broken_in_last = 0
    
                    if grp["start_time"] is None:
    
                        for c in last_h_l[side]:
                            if c > row[h_l][i] and side == "resistances":
                                broken_in_last += 1
                            elif c < row[h_l][i] and side == "supports":
                                broken_in_last += 1
    
                        if broken_in_last < 3:
                            grp["start_time"] = index
    
                    if broken_in_last < 3 and (
                            grp["last"] is None or index >= grp["last"] + self.min_diff_points * candle_length):
                        grp["prices"].append(row[h_l][i])
    
                        if len(grp["prices"]) >= self.min_points:
                            extreme_price = max(grp["prices"]) if side == "resistances" else min(grp["prices"])
                            levels[side].append([(grp["start_time"], extreme_price), (index, extreme_price)])
                            resistances_supports[side].append({"price": extreme_price, "broken": False})
    
                        grp["last"] = index
    
                else:
                    broken_in_last = 0
    
                    for c in last_h_l[side]:
                        if c > row[h_l][i] and side == "resistances":
                            broken_in_last += 1
                        elif c < row[h_l][i] and side == "supports":
                            broken_in_last += 1
    
                    if broken_in_last < 3:
                        price_groups[side][row["rounded_" + h_l][i]] = {"prices": [row[h_l][i]], "start_time": index,
                                                                        "last": index}
    
                # Check whether price groups are still valid or not
    
                for key, value in price_groups[side].items():
                    if len(value["prices"]) > 0:
                        if side == "resistances" and row[h_l][i] > max(value["prices"]):
                            value["prices"].clear()
                            value["start_time"] = None
                            value["last"] = None
                        elif side == "supports" and row[h_l][i] < min(value["prices"]):
                            value["prices"].clear()
                            value["start_time"] = None
                            value["last"] = None
    
                last_h_l[side].append(row[h_l][i])
                if len(last_h_l[side]) > 10:
                    last_h_l[side].pop(0)
    
                # Check new trade
    
                for sup_res in resistances_supports[side]:
                    entry_condition = row["close"][i] > sup_res["price"] if side == "resistances" else row["close"][i] < \
                                                                                                       sup_res["price"]
    
                    if entry_condition and not sup_res["broken"]:
                        sup_res["broken"] = True
                        if trade_side == 0:
                            entry_price = row["close"][i]
                            trade_side = 1 if side == "resistances" else -1
    
                # Check PNL
    
                if trade_side == 1:
                    if row["close"][i] >= entry_price * (1 + self.take_profit / 100) or row["close"][i] <= entry_price * (
                            1 - self.stop_loss / 100):
                        pnl += (row["close"][i] / entry_price - 1) * 100
                        trade_side = 0
                        entry_price = None
                elif trade_side == -1:
                    if row["close"][i] <= entry_price * (1 - self.take_profit / 100) or row["close"][i] >= entry_price * (
                            1 + self.stop_loss / 100):
                        pnl += (entry_price / row["close"][i] - 1) * 100
                        trade_side = 0
                        entry_price = None
    
                max_pnl = max(max_pnl, pnl)
                max_drawdown = max(max_drawdown, max_pnl - pnl)
    
        # mpf.plot(df, type="candle", style="charles", alines=dict(alines=levels["resistances"] + levels["supports"]))
        # plt.show()
    
        return pnl, max_drawdown
