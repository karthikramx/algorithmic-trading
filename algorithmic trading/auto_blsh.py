import time
from kiteconnect import KiteConnect
from paths import *
import pandas as pd
import datetime as dt
import numpy as np
import nsepy
import sys

"""
blsh - buy low sell high
"""

"""
        0. Schedule login.py at 9                                           - higher level task
        1. Execute only on trading days                                     - higher level task
        1. Auto launch at 9:15 *                                            - higher level task
        2. Automate Authorizing CDSL at 9:15                                - higher level task
(done)  3. sell previous days stock if price per share has increased > 0.05
(done)  4. buy stock after 3:29 
"""


class tradx_driver:

    def __init__(self):
        print("Initialized TradeX driver\n")

    def get_holdings_info(self):
        data = kite.holdings()
        holds = pd.DataFrame()
        for d in data:
            df = pd.DataFrame.from_records([d])
            holds = holds.append(df)
        holds.reset_index(inplace=True)
        holds.drop('index', axis=1, inplace=True)
        return holds

    def get_positions_info(self):
        data = kite.positions()
        net = pd.DataFrame(data['net'])
        day = pd.DataFrame(data['day'])
        positions = day[["tradingsymbol", "product", "quantity", "average_price", "last_price", "pnl"]]
        return positions

    def get_orders_info(self):
        data = kite.orders()
        order = pd.DataFrame(data)
        order = order[["tradingsymbol", "order_type", "status", "transaction_type", "product", "quantity", "price"]]
        return order

    def place_cnc_order(self, symbol, buy_sell, quantity):
        # Place an intraday market order on NSE
        if buy_sell == "buy":
            t_type = kite.TRANSACTION_TYPE_BUY
        elif buy_sell == "sell":
            t_type = kite.TRANSACTION_TYPE_SELL
        kite.place_order(tradingsymbol=symbol,
                         exchange=kite.EXCHANGE_NSE,
                         transaction_type=t_type,
                         quantity=quantity,
                         order_type=kite.ORDER_TYPE_MARKET,
                         product=kite.PRODUCT_CNC,
                         variety=kite.VARIETY_REGULAR)

    def place_limit_order(self, symbol, buy_sell, quantity, price):
        # Place an intraday market order on NSE
        if buy_sell == "buy":
            t_type = kite.TRANSACTION_TYPE_BUY
        elif buy_sell == "sell":
            t_type = kite.TRANSACTION_TYPE_SELL
        kite.place_order(tradingsymbol=symbol,
                         exchange=kite.EXCHANGE_NSE,
                         transaction_type=t_type,
                         quantity=quantity,
                         order_type=kite.ORDER_TYPE_LIMIT,
                         product=kite.PRODUCT_CNC,
                         variety=kite.VARIETY_REGULAR,
                         price=price)

    def print_strategyx1_status(self):
        sys.stdout.write('\r' + "First 30 min holding price checks.")
        time.sleep(0.25)
        sys.stdout.write('\r' + "First 30 min holding price checks..")
        time.sleep(0.25)
        sys.stdout.write('\r' + "First 30 min holding price checks...")
        time.sleep(0.25)
        sys.stdout.write('\r' + "First 30 min holding price checks....")
        time.sleep(0.25)

    def idle(self):
        time.sleep(1)
        sys.stdout.write('\r' + str(dt.datetime.now()))


tradable_instruments = ["PNB", "UNIONBANK", "YESBANK", "IDEA", "GMRINFRA", "IDBI", "IDFCFIRSTB", "SUZLON", "ONGC",
                        "BANKBARODA", "MMTC", "MAHABANK"]
print("Tradx will be using: {} for blsh algo\n".format(tradable_instruments))

access_token = open(access_token_path, "r").read()
key_secret = open(auth_details_path, 'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)
print("kite object initialized\n")

tx = tradx_driver()

year = dt.datetime.now().year
month = dt.datetime.now().month
day = dt.datetime.now().day

start_time = dt.datetime(year=year, month=month, day=day, hour=9, minute=15, second=30)
end_time = dt.datetime(year=year, month=month, day=day, hour=15, minute=30, second=00)
buy_time = dt.datetime(year=year, month=month, day=day, hour=15, minute=29, second=00)
sell_time = dt.datetime(year=year, month=month, day=day, hour=9, minute=45, second=00)

buy_pending = True

# Authorize CDSL TO SELL SHARES

print("\nStart time: {} | end time:{}\n".format(start_time, end_time))
holdings = tx.get_holdings_info()
to_sell = holdings["tradingsymbol"].tolist()
to_buy = list(np.setdiff1d(tradable_instruments, to_sell))
sold = []
no_profit = []
print("\nHOLDINDS\n{}\n".format(holdings))
print("\nEOD BUY: {}\n".format(to_buy))

while start_time < dt.datetime.now() < end_time:

    # SELL
    while dt.datetime.now() <= sell_time and len(to_sell) > 0:
        tx.print_strategyx1_status()
        holdings = tx.get_holdings_info()
        time.sleep(1)
        if dt.datetime.now() == sell_time:
            print("\nEnd of 30 minute check. Exiting at 9:45\n")
            break

        for inst in to_sell:
            pnl = holdings[holdings["tradingsymbol"] == inst]["pnl"].values[0]
            if pnl > 0:
                quantity = holdings[holdings["tradingsymbol"] == inst]["t1_quantity"].values[0]
                if quantity > 0:
                    tx.place_cnc_order(inst, "sell", quantity)
                    sold.append(inst)
                    print("\nSOLD {} | quantity:{} | with pnl:{}".format(inst, quantity, round(pnl, 2)))
            else:
                no_profit.append(inst)

        to_sell = list(np.setdiff1d(to_sell, sold))
        if not to_sell:
            print("Nothing to sell")
            break


    # BUY
    if buy_time <= dt.datetime.now() and buy_pending:
        for inst in to_buy:
            tx.place_cnc_order(inst, "buy", 5)
            print("Order placed - {}".format(inst))
            time.sleep(0.5)
        buy_pending = False

    tx.idle()
