import pandas as pd
import sys
import time
import datetime as dt
from kiteconnect import KiteConnect
from paths import *


class tradex_driver:

    def __init__(self, kite):
        print("INITIALIZED TRADEX DRIVER\n")
        access_token = open(access_token_path, "r").read()
        key_secret = open(auth_details_path, 'r').read().split()
        self.kite = KiteConnect(api_key=key_secret[0])
        print("KITE OBJECT CREATED")
        self.kite.set_access_token(access_token)
        print("KITE ACCESS TOKEN SET")

    def get_holdings_info(self):
        data = self.kite.holdings()
        holds = pd.DataFrame()
        for d in data:
            df = pd.DataFrame.from_records([d])
            holds = holds.append(df)
        holds.reset_index(inplace=True)
        holds.drop('index', axis=1, inplace=True)
        return holds

    def get_positions_info(self):
        data = self.kite.positions()
        net = pd.DataFrame(data['net'])
        day = pd.DataFrame(data['day'])
        positions = day[["tradingsymbol", "product", "quantity", "average_price", "last_price", "pnl"]]
        return positions

    def get_orders_info(self):
        data = self.kite.orders()
        order = pd.DataFrame(data)
        order = order[["tradingsymbol", "order_type", "status", "transaction_type", "product", "quantity", "price"]]
        return order

    def place_cnc_order(self, symbol, buy_sell, quantity):
        # Place an intraday market order on NSE
        t_type = None
        if buy_sell == "buy":
            t_type = self.kite.TRANSACTION_TYPE_BUY
        elif buy_sell == "sell":
            t_type = self.kite.TRANSACTION_TYPE_SELL
        self.kite.place_order(tradingsymbol=symbol,
                              exchange=self.kite.EXCHANGE_NSE,
                              transaction_type=t_type,
                              quantity=quantity,
                              order_type=self.kite.ORDER_TYPE_MARKET,
                              product=self.kite.PRODUCT_CNC,
                              variety=self.kite.VARIETY_REGULAR)

    def place_limit_order(self, symbol, buy_sell, quantity, price):
        # Place an intraday market order on NSE
        if buy_sell == "buy":
            t_type = self.kite.TRANSACTION_TYPE_BUY
        elif buy_sell == "sell":
            t_type = self.kite.TRANSACTION_TYPE_SELL
        self.kite.place_order(tradingsymbol=symbol,
                              exchange=self.kite.EXCHANGE_NSE,
                              transaction_type=t_type,
                              quantity=quantity,
                              order_type=self.kite.ORDER_TYPE_LIMIT,
                              product=self.kite.PRODUCT_CNC,
                              variety=self.kite.VARIETY_REGULAR,
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
