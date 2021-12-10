#include <string>
#include <vector>

class Strategy
 {
   protected:
        void track_trade(int new_pos, double enter_ts, double exit_ts, double open_price, double close_price);

        std::string exchange;
        std::string symbol;
        std::string timeframe;
        std::string path;

        std::vector<double> ts, open, high, low, close, volume;

    public:

        std::vector<int> position = {};
        std::vector<double> enter_at = {};
        std::vector<double> exit_at = {};
        std::vector<double> open_val = {};
        std::vector<double> close_val = {};

        double pnl = 0.0;
        double max_dd = 0.0;
};