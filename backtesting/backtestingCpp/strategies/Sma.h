#include <string>
#include <vector>
#include "Strategy.h"

class Sma: public Strategy {
    public:
        Sma(char* exchange_c, char* symbol_c, char* timeframe_c, long long from_time, long long to_time, char* path_c);
        void execute_backtest(int slow_ma, int fast_ma);
        // void track_trade(int position, double enter_at, double exit_at, double open_price, double close_price);


        std::string exchange;
        std::string symbol;
        std::string timeframe;
        std::string path;

        std::vector<double> ts, open, high, low, close, volume;

};