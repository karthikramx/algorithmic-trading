# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect - Streaming Data

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import os

cwd = os.chdir("D:\\Udemy\\Zerodha KiteConnect API\\1_account_authorization")


#generate trading session
access_token = open("access_token.txt",'r').read()
key_secret = open("api_key.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)

#get dump of all NSE instruments
instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)

def tokenLookup(instrument_df,symbol_list):
    """Looks up instrument token for a given script from instrument dump"""
    token_list = []
    for symbol in symbol_list:
        token_list.append(int(instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]))
    return token_list

#####################update ticker list######################################
tickers = ["INFY", "ACC", "ICICIBANK"]
#############################################################################

#create KiteTicker object
kws = KiteTicker(key_secret[0], kite.access_token)
tokens = tokenLookup(instrument_df, tickers)

def on_ticks(ws,ticks):
    # Callback to receive ticks.
    #logging.debug("Ticks: {}".format(ticks))
    print(ticks)

def on_connect(ws,response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    #logging.debug("on connect: {}".format(response))
    ws.subscribe(tokens)
    ws.set_mode(ws.MODE_FULL, tokens) # Set all token tick in `full` mode.
    #ws.set_mode(ws.MODE_FULL,[tokens[0]])  # Set one token tick in `full` mode.
 

kws.on_ticks=on_ticks
kws.on_connect=on_connect
kws.connect()
