#include <string>
#include <vector>
#include "Strategy.h"

class Psar : public Strategy {
    public:
        Psar(char* exchange_c, char* symbol_c, char* timeframe_c, long long from_time, long long to_time, char* path_c);
        void execute_backtest(double initial_acc, double accel_increment, double max_acc);

        std::string exchange;
        std::string symbol;
        std::string timeframe;
        std::string path;

        std::vector<double> ts, open, high, low, close, volume;

};