# -*- coding: utf-8 -*-
"""
Trading Robot - Zerodha Kite Connect Platform

@author: Karthik Ramx (https://karthikramx.wordpress.com/)
"""

from kiteconnect import KiteConnect
from selenium import webdriver
from config import *
import time
import os
import pandas as pd
import datetime as dt

credentials_path = os.environ["HOMEPATH"] + "\\Desktop" + "\\cred impt" + "\\zrdh_lgn_cred"
account_details_path = os.environ["HOMEPATH"] + "\\Desktop" + "\\cred impt" + "\\zrdh_acc_details"

auth_details_path = credentials_path + "\\auth_details.txt"
request_token_path = credentials_path + "\\request_token.txt"
access_token_path = credentials_path + "\\access_token.txt"

holdings_details_path = account_details_path + "\\holdings.txt"
orders_details_path = account_details_path + "\\orders.txt"


def autologin():

    key_secret = open(auth_details_path, 'r').read().split()
    kite = KiteConnect(api_key=key_secret[0])
    print("\t\tKite Object created")

    service = webdriver.chrome.service.Service('./chromedriver')
    service.start()
    options = webdriver.ChromeOptions()
    if HEADLESS_MODE:
        options.add_argument('--headless')
    options = options.to_capabilities()
    print("\t\tLaunching Chrome Driver")
    driver = webdriver.Remote(service.service_url, options)
    driver.set_window_position(BROWSER_X_POS, BROWSER_Y_POS)
    driver.set_window_size(BROWSER_X_SIZE, BROWSER_Y_SIZE)
    driver.get(kite.login_url())
    driver.implicitly_wait(10)
    print("\t\tEntering credentials. Please wait.")
    username = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[1]/input')
    password = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input')
    username.send_keys(key_secret[2])
    password.send_keys(key_secret[3])
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button').click()
    pin = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/div/input')
    print("\t\tEntering PIN. Please wait.")
    pin.send_keys(key_secret[4])
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[3]/button').click()
    time.sleep(4)
    print("\t\tCURRENT URL: {}".format(driver.current_url))

    request_token = driver.current_url.split('=')[1].split('&action')[0]  # fails the string operation sometimes
    print("\t\tREQUEST TOKEN: {}".format(request_token))

    driver.quit()

    with open(request_token_path, 'w') as the_file:
        the_file.write(request_token)
    print("\t\tREQUEST TOKEN: {} SAVED".format(request_token))



def generate_access_token():
    request_token = open(request_token_path, 'r').read()
    key_secret = open(auth_details_path, 'r').read().split()
    kite = KiteConnect(api_key=key_secret[0])
    data = kite.generate_session(request_token, api_secret=key_secret[1])
    print("\t\tACCESS  TOKEN: {}".format(data["access_token"]))
    with open(access_token_path, 'w') as file:
        file.write(data["access_token"])
        print("\t\tACCESS  TOKEN: {} SAVED".format(data["access_token"]))


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

for i in range(1,5):
    autologin()
    generate_access_token()
    print("\t\t TEST LOOP: {}".format(i))
exit()

access_token = open(access_token_path, "r").read()
key_secret = open(auth_details_path, 'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)

quote = kite.quote("NSE:IDFC")
print(kite.quote("NSE:IDFC"))
print(kite.ltp("NSE:IDFC"))

for i in range(10):
    print(kite.ltp("NSE:IDFC"))

# orders = kite.orders()
holdings = kite.holdings()
print(holdings)
print("here")
# instruments = kite.instruments()
# login_url = kite.login_url()
# duration = 2
# interval = "5minute"
