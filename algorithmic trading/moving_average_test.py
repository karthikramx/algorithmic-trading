import time
from kiteconnect import KiteConnect
from paths import *
import pandas as pd
import datetime as dt
import nsepy

access_token = open(access_token_path, "r").read()
key_secret = open(auth_details_path, 'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)

my_instruments = ["PNB", "MAHABANK", "UNIONBANK", "MMTC"]

year = dt.datetime.now().year
month = dt.datetime.now().month
day = dt.datetime.now().day

start_time = dt.datetime(year=year, month=month, day=day, hour=9, minute=15, second=00)
end_time = dt.datetime(year=year, month=month, day=day, hour=15, minute=15, second=00)


def get_holdings_info():
    data = kite.holdings()
    try:
        holds = pd.DataFrame(data[0], index=[0])
    except:
        holds = pd.DataFrame(data[0])
    holdings = holds[["tradingsymbol", "product", "quantity", "average_price", "last_price", "pnl"]]
    return holdings


def get_positions_info():
    data = kite.positions()
    net = pd.DataFrame(data['net'])
    day = pd.DataFrame(data['day'])
    positions = day[["tradingsymbol", "product", "quantity", "average_price", "last_price", "pnl"]]
    return positions


def get_orders_info():
    data = kite.orders()
    orders = pd.DataFrame(data)
    return orders


def instrument_lookup(instrument_df, symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol == symbol].instrument_token.values[0]
    except:
        return -1


def tokenLookup(instrument_df, symbol_list):
    """Looks up instrument token for a given script from instrument dump"""
    token_list = []
    for symbol in symbol_list:
        token_list.append(int(instrument_df[instrument_df.tradingsymbol == symbol].instrument_token.values[0]))
    return token_list


def place_cnc_order(symbol, buy_sell, quantity):
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



instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)
tickers = my_instruments
tokens = tokenLookup(instrument_df, tickers)

# print("ORDERS \n {}".format(get_orders_info()))
# print("HOLDINGS \n {}".format(get_holdings_info()))
# print("POSITIONS \n {}".format(get_positions_info()))

#mahabank_data = nsepy.get_history(symbol="MAHABANK", start=dt.datetime.now() - dt.timedelta(365), end=dt.datetime.today())
#mahabank = mahabank_data[["Date", "Symbol", "Prev Close", "Open", "High", "Low", "Close", "Volume"]]

"""
while start_time < dt.datetime.now() < end_time:
    time.sleep(5)
    print(kite.ltp(["NSE:GMRINFRA"])[0][1])

# place_market_order("IDEA", "buy", 1)
"""

close_time = dt.datetime(year=year, month=month, day=day, hour=15, minute=29, second=00)

while True:
    if close_time <= dt.datetime.now():
        place_cnc_order("MAHABANK", "buy", 50)
        print("Order placed")
        break
    else:
        print("waiting for 3:29")
        time.sleep(1)
