#include <numeric>
#include "Psar.h"
#include "../Database.h"
#include "../Utils.h"

using namespace std;

Psar::Psar(char* exchange_c, char* symbol_c, char* timeframe_c, long long from_time, long long to_time, char* path_c)
{
    exchange = exchange_c;
    symbol = symbol_c;
    timeframe = timeframe_c;
    path = path_c;

    Database db(exchange, path);
    int array_size = 0;
    double** res = db.get_data(symbol, exchange, array_size);
    db.close_file();

    std::tie(ts, open, high, low, close, volume) = rearrange_candles(res, timeframe, from_time, to_time, array_size);
    // printf("%lu, %lu. %lu. %lu. %lu, %lu", ts.size(), open.size(), high.size(), low.size(), close.size(), volume.size());
}

void Psar::execute_backtest(double initial_acc, double accel_increment, double max_acc) {
    double pnl = 0.0;
    double max_dd = 0.0;

    double max_pnl = 0.0;
    int current_position = 0;
    double entry_price;

    double open_price;
    double close_price;
    double entry_time;
    double exit_time;

    int trend[2] = { 0, 0 };
    double sar[2] = { 0.0, 0.0 };
    double ep[2] = { 0.0, 0.0 };
    double af[2] = { 0.0, 0.0 };

    double temp_sar = 0.0;

    // Initialize values

    trend[0] = close[1] > close[0] ? 1 : -1;
    sar[0] = trend[0] > 0 ? high[0] : low[0];
    ep[0] = trend[0] > 0 ? high[1] : low[1];
    af[0] = initial_acc;

    track_signal(0);
    track_signal(0);

    for (int i = 2; i < ts.size(); i++) {
        // Trend

        temp_sar = sar[0] + af[0] * (ep[0] - sar[0]);

        if(trend[0] < 0) {
            if(trend[0] <= -2) {
                temp_sar = max(temp_sar, max(high[i - 1], high[i - 2]));
            }
            trend[1] = temp_sar < high[i] ? 1 : trend[0] - 1;
        }
        else {
            if(trend[0] >= 2) {
                temp_sar = min(temp_sar, min(low[i - 1], low[i-2]));
            }
            trend[1] = temp_sar > low[i] ? -1 : trend[0] + 1;
        }

        // EP

        if (trend[1] <0) {
            ep[1] = trend[1] != -1 ? min(low[i], ep[0]) : low[i];
        }
        else {
            ep[1] = trend[1] != 1 ? max(high[i], ep[0]) : high[i];
        }

        // AF / SAR

        if (abs(trend[1]) == 1) { // If the trend has just changed
            sar[1] = ep[0];
            af[1] = initial_acc;
        }
        else {
            sar[1] = temp_sar;
            if(ep[1] == ep[0]) {
                af[1] = af[0];
            }
            else {
                af[1] = min(max_acc, af[0] + accel_increment);
            }
        }

        // Long signal

        if (trend[1] == 1 && trend[0] < 0) {
            if (current_position == -1) {
                exit_time = ts[i + 1];
                close_price = open[i + 1];

                this->track_trade(-1, entry_time, exit_time, open_price, close_price);

                double pnl_temp = (entry_price / close[i] -1) * 100;
                pnl += pnl_temp;
                max_pnl = max(max_pnl, pnl);
                max_dd = max(max_dd, max_pnl - pnl);
            }
            
            current_position = 1;
            entry_price = close[i];
            
            open_price = open[i + 1];
            entry_time = ts[i + 1];
        }

        // Short signal
        else if (trend[1] == -1 && trend[0] > 0) {
            if (current_position == 1) {
                exit_time = ts[i + 1];
                close_price = open[i + 1];

                this->track_trade(1, entry_time, exit_time, open_price, close_price);

                double pnl_temp = (close[i]/entry_price -1) * 100;
                pnl += pnl_temp;
                max_pnl = max(max_pnl, pnl);
                max_dd = max(max_dd, max_pnl - pnl);
            }
            
            current_position = -1;
            entry_price = close[i];

            open_price = open[i + 1];
            entry_time = ts[i + 1];
        }

        trend[0] = trend[1];
        sar[0] = sar[1];
        ep[0] = ep[1];
        af[0] = af[1];

        track_signal(current_position);
    }

    this->pnl = pnl;
    this->max_dd = max_dd;
}

extern "C" {
    Psar* Psar_new(char* exchange, char* symbol, char* timeframe, long long from_time, long long to_time, char* path) {
        return new Psar(exchange,  symbol, timeframe, from_time, to_time, path);
    }
    void Psar_execute_backtest(Psar* psar, double initial_acc, double acc_increment, double max_acc) {
        return psar->execute_backtest(initial_acc, acc_increment, max_acc);
    }
    // double Psar_get_pnl(Psar* psar) { return psar->pnl; }
    // double Psar_get_max_dd(Psar* psar) { return psar->max_dd; }
}
