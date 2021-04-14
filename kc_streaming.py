# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect - Streaming Data

@author: Karthik Ram (https://karthikramx.wordpress.com/)
"""
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
from paths import *
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)


# generate trading session
access_token = open(access_token_path, 'r').read()
key_secret = open(auth_details_path, 'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)

# Get dump of all NSE instruments in a pandas data frame
instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)


def tokenLookup(instrument_df, symbol_list):
    """Looks up instrument token for a given script from instrument dump"""
    token_list = []
    for symbol in symbol_list:
        token_list.append(int(instrument_df[instrument_df.tradingsymbol == symbol].instrument_token.values[0]))
    return token_list


#####################update ticker list######################################
tickers = ["INFY"]
#############################################################################

# Initialise
kws = KiteTicker(key_secret[0], kite.access_token)


def on_ticks(ws, ticks):
    # Callback to receive ticks.
    logging.debug("Ticks: {}".format(ticks))


def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    ws.subscribe([738561, 5633])

    # Set RELIANCE to tick in `full` mode.
    ws.set_mode(ws.MODE_FULL, [738561,5633])


def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()


# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.debug = True
try:
    print(kws.__version__)
except:
    print("Version not found")
kws.connect()


"""
# create KiteTicker object
kws = KiteTicker(key_secret[0], kite.access_token)
tokens = tokenLookup(instrument_df, tickers)


def on_ticks(ws, ticks):
    # Callback to receive ticks.
    # logging.debug("Ticks: {}".format(ticks))
    print(ticks)


def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    # logging.debug("on connect: {}".format(response))
    ws.subscribe(tokens)
    # ws.set_mode(ws.MODE_FULL, [tokens[0]])
    ws.set_mode(ws.MODE_LTP, tokens)  # Set all token tick in `full` mode.
    print(response)
    #   # Set one token tick in `full` mode.

def on_message(ws, payload, is_binary):
    print(payload)


def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    print("closing kite ticker connection")
    ws.stop()


kws.on_ticks = on_ticks
kws.on_message = on_message
kws.on_connect = on_connect
kws.on_close = on_close

kws.connect()
"""