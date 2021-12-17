#include <numeric>
#include "Sma.h"
#include "../Database.h"
#include "../Utils.h"

using namespace std;

Sma::Sma(char* exchange_c, char* symbol_c, char* timeframe_c, long long from_time, long long to_time, char* path_c) {
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
};

void Sma::execute_backtest(int slow_ma, int fast_ma) {
    double pnl = 0.0;
    double max_dd = 0.0;

    double max_pnl = 0.0;
    int current_position = 0;
    double open_price;
    double close_price;
    double entry_time;
    double exit_time;

    vector<double> slow_ma_closes = {};
    vector<double> fast_ma_closes = {};

    // Avoid looping till the very last candle because we need to reference i+1
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
            track_signal(0);
            // printf("Tracking position at i=%d\n", i);
            continue;
        }

        double sum_slow = accumulate(slow_ma_closes.begin(), slow_ma_closes.end(), 0.0);
        double sum_fast = accumulate(fast_ma_closes.begin(), fast_ma_closes.end(), 0.0);

        double mean_slow = sum_slow / slow_ma;
        double mean_fast = sum_fast / fast_ma;

        // Long signal

        if (mean_fast > mean_slow && current_position <= 0 ) {
            if (current_position == -1) {
                exit_time = ts[i + 1];
                close_price = open[i + 1];

                track_trade(-1, entry_time, exit_time, open_price, close_price);

                double pnl_temp = (open_price / close[i] -1 ) * 100;
                pnl += pnl_temp;
                max_pnl = max(max_pnl, pnl);
                max_dd = max(max_dd, max_pnl - pnl);
                
            }
            
            current_position = 1;
            open_price = open[i + 1];
            entry_time = ts[i + 1];
        }

        // Short signal
        
        if (mean_fast < mean_slow && current_position >= 0 ) {
            if (current_position == 1) {
                exit_time = ts[i + 1];
                close_price = open[i + 1];

                track_trade(1 , entry_time, exit_time, open_price, close_price);

                double pnl_temp = (close[i] / open_price -1 ) * 100;
                pnl += pnl_temp;
                max_pnl = max(max_pnl, pnl);
                max_dd = max(max_dd, max_pnl - pnl);
            }
            
            current_position = -1;
            open_price = open[i + 1];
            entry_time = ts[i + 1];
        }
        track_signal(current_position);
        // printf("Tracking position at i=%d\n", i);
    }
    // track_position(0);
    // printf("Tracking position at i=final\n");

    this->pnl = pnl;
    this->max_dd = max_dd;
    
};


extern "C" {
    Sma* Sma_new(char* exchange, char* symbol, char* timeframe, long long from_time, long long to_time, char* path) {
        return new Sma(exchange,  symbol, timeframe, from_time, to_time, path);
    }

    void Sma_execute_backtest(Sma* sma, int slow_ma, int fast_ma) {
        return sma->execute_backtest(slow_ma, fast_ma);
    }
}