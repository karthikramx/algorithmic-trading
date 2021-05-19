# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect - Fetching Historical Data over extended duration

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
from kiteconnect import KiteConnect
import os
import datetime as dt
import pandas as pd

cwd = os.chdir("D:\\Udemy\\Zerodha KiteConnect API\\1_account_authorization")

#generate trading session
access_token = open("access_token.txt",'r').read()
key_secret = open("api_key.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)


#get dump of all NSE instruments
instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)
#instrument_df.to_csv("NSE_Instruments_31122019.csv",index=False)


def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1





ohlc = fetchOHLCExtended("INFY","20-08-2019","5minute")