#include <iostream>
#include <cstring>

#include "Database.h"
#include "Utils.h"
#include "strategies/Psar.h"
#include "Utils.h"


int main(int, char**) {
    // Database db("binance");
    // int array_size = 0;
    // double** res = db.get_data("BTCUSDT", "binance", array_size);
    
    // std::vector<double> ts, open, high, low, close, volume;
    // std::tie(ts, open, high, low, close, volume) = rearrange_candles(res, "5m", 1609344600000, 1609354600000, array_size);
    // for (int i =0; i < 100; i++) {
    //     printf("%f %f %f %f %f %f\n", ts[i], open[i], high[i], low[i], close[i], volume[i]);
    // }
    // printf("%lu\n", ts.size());
    // db.close_file();

    std::string symbol = "BTCUSDT";
    std::string exchange = "binance";
    std::string timeframe = "30m";

    char* symbol_char =  strcpy((char*)malloc(symbol.length() + 1), symbol.c_str());
    char* exchange_char = strcpy((char*)malloc(exchange.length() + 1), exchange.c_str());
    char* tf_char = strcpy((char*)malloc(timeframe.length() + 1), timeframe.c_str());
    char* path = "";

    Psar psar(exchange_char, symbol_char, tf_char, 1609344600000.0, 1609354200000.0, path);
    psar.execute_backtest(0.02, 0.02, 0.2);
    printf("%f | %f\n", psar.pnl, psar.max_dd);
}
