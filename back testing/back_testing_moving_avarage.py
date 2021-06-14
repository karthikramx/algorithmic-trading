import nsepy
import numpy as np
import pandas as pd
import datetime as dt
from statistics import mean

mahabank_data = nsepy.get_history(symbol="MAHABANK", start=dt.datetime.now() - dt.timedelta(365), end=dt.datetime.today())
print(mahabank_data.columns)
print(mahabank_data.info())
mahabank_data = mahabank_data[["Symbol", "Prev Close", "Open", "High", "Low", "Close", "Volume"]]
mahabank_data["MA"] = mahabank_data["Close"].ewm(span=9, min_periods=9).mean()

mahabank_data=mahabank_data[mahabank_data["MA"].notnull()]
print(mahabank_data)

mode = None
buy_price = 0
sell_price = 0
buy_date = mahabank_data.index[1]
sell_date = mahabank_data.index[0]

for tick in range(1, len(mahabank_data)):

    if mode == "buy" or mode is None:
        buy_date = mahabank_data.index[tick]
        if (buy_date - sell_date).days > 0:
            if mahabank_data["MA"][tick-1] > mahabank_data["High"][tick-1]:
                # assumption is that I will buy the the average value for the day
                o_c = [mahabank_data["Open"][tick], mahabank_data["Close"][tick], mahabank_data["High"][tick], mahabank_data["Low"][tick]]
                if mean(o_c) > mahabank_data["MA"][tick-1]:
                    buy_price = mean(o_c)
                    buy_date = mahabank_data.index[tick]
                    print("buy price on {}".format(buy_price))
                    mode = "sell"

    elif mode == "sell" or mode is None:
        if mahabank_data["MA"][tick-1] > mahabank_data["High"][tick-1]:
            o_c = [mahabank_data["Open"][tick], mahabank_data["Close"][tick]]
            if mean(o_c) > mahabank_data["MA"][tick-1]:
                sell_price = mean(o_c)
                print("buy price on {}".format(buy_price))
                mode = "buy"

