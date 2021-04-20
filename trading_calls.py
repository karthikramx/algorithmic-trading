from kiteconnect import KiteConnect
from paths import *
import pandas as pd
import datetime as dt
from config import *
import time

access_token = open(access_token_path, "r").read()
key_secret = open(auth_details_path, 'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)


def get_all_instruments():
    instrument_dump = kite.instruments()
    instrument_DataFrame = pd.DataFrame(instrument_dump)
    instrument_DataFrame.to_csv("Instruments.csv", index=False)


def get_all_NSE_instruments():
    instrument_dump = kite.instruments("NSE")
    nse_instrument_DataFrame = pd.DataFrame(instrument_dump)
    nse_instrument_DataFrame.to_csv("NSE_Instruments.csv", index=False)


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


def fetch_historical_data(instrument_df, ticker, interval, duration):
    """extracts historical data and outputs in the form of dataframe"""
    instrument = instrument_lookup(instrument_df, ticker)
    data = pd.DataFrame(
        kite.historical_data(instrument, dt.date.today() - dt.timedelta(duration), dt.date.today(), interval))
    data.set_index("date", inplace=True)
    return data


def place_market_order(symbol, buy_sell, quantity):
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
                     product=kite.PRODUCT_MIS,
                     variety=kite.VARIETY_REGULAR)


def place_bracket_order(symbol, buy_sell, quantity, atr, price):
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
                     price=price,  # BO has to be a limit order, set a low price threshold
                     product=kite.PRODUCT_MIS,
                     variety=kite.VARIETY_BO,
                     squareoff=int(6 * atr),
                     stoploss=int(3 * atr),
                     trailing_stoploss=2)


# instrument_dump = kite.instruments("NSE")
# instrument_df = pd.DataFrame(instrument_dump)
# tickers = ["INFY", "ITC", "BIOCON"]
# tokens = tokenLookup(instrument_df, tickers)

# for i in range(100):
#    print(kite.ltp(["NSE:ITC"]))
#    time.sleep(30)

while True:
    holding_tries = position_tries = 0
    begin_scan_time = time.time()
    while holding_tries < MAX_TRIES:
        try:
            holdings_dataframe = pd.DataFrame(kite.holdings())
            print(holdings_dataframe)
            break
        except:
            print("\t\tFailed to retrieve holdings data, trying again")

    while position_tries < MAX_TRIES:
        try:
            positions_dataframe = pd.DataFrame(kite.positions())
            print(positions_dataframe)
            break
        except:
            print("\t\tFailed to retrieve holdings data, trying again")

    stop_scan_time = time.time()
    time.sleep(10-(stop_scan_time - begin_scan_time))
    print(dt.datetime.now())
