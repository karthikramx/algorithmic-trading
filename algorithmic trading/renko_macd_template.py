# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect - real time renko based strategy template

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""


from kiteconnect import KiteTicker, KiteConnect
import pandas as pd
import datetime as dt
import os
import sys

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

def tickerLookup(token):
    global instrument_df
    return instrument_df[instrument_df.instrument_token==token].tradingsymbol.values[0] 

def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1
        
def fetchOHLC(ticker,interval,duration):
    """extracts historical data and outputs in the form of dataframe"""
    instrument = instrumentLookup(instrument_df,ticker)
    data = pd.DataFrame(kite.historical_data(instrument,dt.date.today()-dt.timedelta(duration), dt.date.today(),interval))
    data.set_index("date",inplace=True)
    return data

def atr(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['high']-df['low'])
    df['H-PC']=abs(df['high']-df['close'].shift(1))
    df['L-PC']=abs(df['low']-df['close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].ewm(com=n,min_periods=n).mean()
    return df['ATR'][-1]

def MACD(DF,a,b,c):
    """function to calculate MACD
       typical values a(fast moving average) = 12; 
                      b(slow moving average) =26; 
                      c(signal line ma window) =9"""
    df = DF.copy()
    df["MA_Fast"]=df["close"].ewm(span=a,min_periods=a).mean()
    df["MA_Slow"]=df["close"].ewm(span=b,min_periods=b).mean()
    df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
    df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
    df.dropna(inplace=True)
    return df

def macd_xover_refresh(macd,ticker):
    global macd_xover
    if macd["MACD"][-1]>macd["Signal"][-1]:
        macd_xover[ticker]="bullish"
    elif macd["MACD"][-1]<macd["Signal"][-1]:
        macd_xover[ticker]="bearish"
        
def renkoOperation(ticks):
    for tick in ticks:
        try:
            ticker = tickerLookup(int(tick['instrument_token']))
            if renko_param[ticker]["upper_limit"] == None:
                renko_param[ticker]["upper_limit"] = float(tick['last_price']) + renko_param[ticker]["brick_size"]
                renko_param[ticker]["lower_limit"] = float(tick['last_price']) - renko_param[ticker]["brick_size"]
            if float(tick['last_price']) > renko_param[ticker]["upper_limit"]:
                gap = (float(tick['last_price'] - renko_param[ticker]["upper_limit"]))//renko_param[ticker]["brick_size"]
                renko_param[ticker]["lower_limit"] = renko_param[ticker]["upper_limit"] + (gap*renko_param[ticker]["brick_size"]) - renko_param[ticker]["brick_size"]
                renko_param[ticker]["upper_limit"] = renko_param[ticker]["upper_limit"] + ((1+gap)*renko_param[ticker]["brick_size"])
                renko_param[ticker]["brick"] = max(1,renko_param[ticker]["brick"]+(1+gap))
            if float(tick['last_price']) < renko_param[ticker]["lower_limit"]:
                gap = (renko_param[ticker]["lower_limit"] - float(tick['last_price']))//renko_param[ticker]["brick_size"]
                renko_param[ticker]["upper_limit"] = renko_param[ticker]["lower_limit"] - (gap*renko_param[ticker]["brick_size"]) + renko_param[ticker]["brick_size"]
                renko_param[ticker]["lower_limit"] = renko_param[ticker]["lower_limit"] - ((1+gap)*renko_param[ticker]["brick_size"])
                renko_param[ticker]["brick"] = min(-1,renko_param[ticker]["brick"]-(1+gap))
            print("{}: brick number = {},last price ={}, upper bound ={}, lower bound ={}"\
                  .format(ticker,renko_param[ticker]["brick"],tick['last_price'],renko_param[ticker]["upper_limit"],renko_param[ticker]["lower_limit"]))
        except Exception as e:
            print(e)
            pass 
        
    
def main(capital):
    global renko_param
    a,b = 0,0
    while a < 10:
        try:
            pos_df = pd.DataFrame(kite.positions()["day"])
            break
        except:
            print("can't extract position data..retrying")
            a+=1
    while b < 10:
        try:
            ord_df = pd.DataFrame(kite.orders())
            break
        except:
            print("can't extract order data..retrying")
            b+=1
    
    for ticker in tickers:
        print("starting passthrough for.....",ticker)
        try:
            ohlc = fetchOHLC(ticker,"minute",4)
            macd = MACD(ohlc,12,26,9)
            macd_xover_refresh(macd,ticker)
            quantity = int(capital/ohlc["close"][-1])
            if len(pos_df.columns)==0:
                if macd_xover[ticker] == "bullish" and renko_param[ticker]["brick"] >=2:
                    print("buy order placed for {}".format(ticker))
                if macd_xover[ticker] == "bearish" and renko_param[ticker]["brick"] <=-2:
                    print("sell order placed for {}".format(ticker))
            if len(pos_df.columns)!=0 and ticker not in pos_df["tradingsymbol"].tolist():
                if macd_xover[ticker] == "bullish" and renko_param[ticker]["brick"] >=2:
                    print("buy order placed for {}".format(ticker))
                if macd_xover[ticker] == "bearish" and renko_param[ticker]["brick"] <=-2:
                    print("sell order placed for {}".format(ticker))
            if len(pos_df.columns)!=0 and ticker in pos_df["tradingsymbol"].tolist():
                if pos_df[pos_df["tradingsymbol"]==ticker]["quantity"].values[0] == 0:
                    if macd_xover[ticker] == "bullish" and renko_param[ticker]["brick"] >=2:
                        print("buy order placed for {}".format(ticker))
                    if macd_xover[ticker] == "bearish" and renko_param[ticker]["brick"] <=-2:
                        print("sell order placed for {}".format(ticker))
                if pos_df[pos_df["tradingsymbol"]==ticker]["quantity"].values[0] > 0:
                    print("buy order modified for {}".format(ticker))
                if pos_df[pos_df["tradingsymbol"]==ticker]["quantity"].values[0] < 0:
                    print("sell order modified for {}".format(ticker))
        except Exception as e:
            print("API error for ticker :",ticker)
            print(e)
    
    
#####################update ticker list######################################
tickers = ["ZEEL","WIPRO","VEDL","ULTRACEMCO","UPL","TITAN","TECHM","TATASTEEL",
           "TATAMOTORS","TCS","SUNPHARMA","SBIN","SHREECEM","RELIANCE","POWERGRID",
           "ONGC","NESTLEIND","NTPC","MARUTI","M&M","LT","KOTAKBANK","JSWSTEEL","INFY",
           "INDUSINDBK","IOC","ITC","ICICIBANK","HDFC","HINDUNILVR","HINDALCO",
           "HEROMOTOCO","HDFCBANK","HCLTECH","GRASIM","GAIL","EICHERMOT","DRREDDY",
           "COALINDIA","CIPLA","BRITANNIA","BHARTIARTL","BPCL","BAJAJFINSV",
           "BAJFINANCE","BAJAJ-AUTO","AXISBANK","ASIANPAINT","ADANIPORTS"]
#############################################################################
capital = 3000 #position size
macd_xover = {}
renko_param = {}
for ticker in tickers:
    renko_param[ticker] = {"brick_size":round(0.2*atr(fetchOHLC(ticker,"5minute",15),200),2),"upper_limit":None, "lower_limit":None,"brick":0}
    macd_xover[ticker] = None
    
#create KiteTicker object
kws = KiteTicker(key_secret[0],kite.access_token)
tokens = tokenLookup(instrument_df,tickers)

start_minute = dt.datetime.now().minute
def on_ticks(ws,ticks):
    global start_minute
    renkoOperation(ticks)
    now_minute = dt.datetime.now().minute
    if abs(now_minute - start_minute) >= 1:
        start_minute = now_minute
        main(capital)

def on_connect(ws,response):
    ws.subscribe(tokens)
    ws.set_mode(ws.MODE_LTP,tokens)

while True:
    now = dt.datetime.now()
    if (now.hour >= 9 and now.minute >= 15 ):
        kws.on_ticks=on_ticks
        kws.on_connect=on_connect
        kws.connect()
    if (now.hour >= 14 and now.minute >= 30):
        sys.exit()