#include <numeric>
#include "Sma.h"
#include "../Database.h"
#include "../Utils.h"

using namespace std;

Sma::Sma(char* exchange_c, char* symbol_c, char* timeframe_c, long long from_time, long long to_time, char* path_c)
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

void Sma::execute_backtest(int slow_ma, int fast_ma) {
    pnl = 0.0;
    max_dd = 0.0;

    double max_pnl = 0.0;
    int current_position = 0;
    double entry_price;

    vector<double> slow_ma_closes = {};
    vector<double> fast_ma_closes = {};

    for (int i = 0; i < ts.size(); i++) {
        slow_ma_closes.push_back(close[i]);
        fast_ma_closes.push_back(close[i]);

        if(slow_ma_closes.size() > slow_ma) {
            slow_ma_closes.erase(slow_ma_closes.begin());
        }
        if(fast_ma_closes.size() > fast_ma) {
            fast_ma_closes.erase(fast_ma_closes.begin());
        }

        if(slow_ma_closes.size() < slow_ma) {
            continue;
        }

        double sum_slow = accumulate(slow_ma_closes.begin(), slow_ma_closes.end(), 0.0);
        double sum_fast = accumulate(fast_ma_closes.begin(), fast_ma_closes.end(), 0.0);

        double mean_slow = sum_slow / slow_ma;
        double mean_fast = sum_fast / fast_ma;

        // Long signal

        if (mean_fast > mean_slow && current_position <= 0 ) {
            if (current_position == -1) {
                double pnl_temp = (entry_price / close[i] -1) * 100;
                pnl += pnl_temp;
                max_pnl = max(max_pnl, pnl);
                max_dd = max(max_dd, max_pnl - pnl);

                exit_at.push_back(ts[i + 1]);
                close_val.push_back(close[i]);
            }
            
            current_position = 1;
            entry_price = close[i];

            position.push_back(current_position);
            // printf("%f\n", ts[i+1]);
            enter_at.push_back(ts[i + 1]);
            open_val.push_back(entry_price);
        }

        // Short signal
        
        if (mean_fast < mean_slow && current_position >= 0 ) {
            if (current_position == 1) {
                double pnl_temp = (close[i]/entry_price -1) * 100;
                pnl += pnl_temp;
                max_pnl = max(max_pnl, pnl);
                max_dd = max(max_dd, max_pnl - pnl);

                exit_at.push_back(ts[i + 1]);
                close_val.push_back(close[i]);
            }
            
            current_position = -1;
            entry_price = close[i];

            position.push_back(current_position);
            // printf("%f\n", ts[i+1]);
            enter_at.push_back(ts[i+1]);
            open_val.push_back(entry_price);

        }
    }
}

extern "C" {
    Sma* Sma_new(char* exchange, char* symbol, char* timeframe, long long from_time, long long to_time, char* path) {
        return new Sma(exchange,  symbol, timeframe, from_time, to_time, path);
    }

    void Sma_execute_backtest(Sma* sma, int slow_ma, int fast_ma) {
        return sma->execute_backtest(slow_ma, fast_ma);
    }
    double Sma_get_pnl(Sma* sma) { return sma->pnl; }
    double Sma_get_max_dd(Sma* sma) { return sma->max_dd; }

    int Sma_get_trades_size(Sma* sma) { return sma->position.size(); }
    int* Sma_get_position(Sma* sma) { return sma->position.data(); }
    double* Sma_get_enter(Sma* sma) { return sma->enter_at.data(); }
    double* Sma_get_exit(Sma* sma) { return sma->exit_at.data(); }
    double* Sma_get_open(Sma* sma) { return sma->open.data(); }
    double* Sma_get_close(Sma* sma) { return sma->close.data(); }
}