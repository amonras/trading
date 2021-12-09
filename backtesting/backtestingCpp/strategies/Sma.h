#include <string>
#include <vector>

class Sma {
    public:
        Sma(char* exchange_c, char* symbol_c, char* timeframe_c, long long from_time, long long to_time, char* path_c);
        void execute_backtest(int slow_ma, int fast_ma);
        void track_trade(int position, double enter_at, double exit_at, double open_price, double close_price);


        std::string exchange;
        std::string symbol;
        std::string timeframe;
        std::string path;

        std::vector<double> ts, open, high, low, close, volume;

        std::vector<int> position = {};
        std::vector<double> enter_at = {};
        std::vector<double> exit_at = {};
        std::vector<double> open_val = {};
        std::vector<double> close_val = {};

        double pnl = 0.0;
        double max_dd = 0.0;

};