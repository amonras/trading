#include <string>
#include <vector>
#include "Strategy.h"

void Strategy::track_trade(int new_pos, double enter_ts, double exit_ts, double open_price, double close_price) {            
    position.push_back(new_pos);

    enter_at.push_back(enter_ts);
    exit_at.push_back(exit_ts);

    open_val.push_back(open_price);
    close_val.push_back(close_price);
};

extern "C" {
    double _get_pnl(Strategy* obj) { return obj->pnl; }
    double _get_max_dd(Strategy* obj) { return obj->max_dd; }

    int _get_trades_size(Strategy* obj) { return obj->position.size(); }
    int* _get_position(Strategy* obj) { return obj->position.data(); }
    double* _get_enter(Strategy* obj) { return obj->enter_at.data(); }
    double* _get_exit(Strategy* obj) { return obj->exit_at.data(); }
    double* _get_open(Strategy* obj) { return obj->open_val.data(); }
    double* _get_close(Strategy* obj) { return obj->close_val.data(); }
}