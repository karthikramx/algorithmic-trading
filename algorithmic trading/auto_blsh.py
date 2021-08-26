import time

import numpy as np
from tradex_driver import tradex_driver
from auto_cdsl_auth import *
from auto_login import *
import pyttsx3
import logging

logs_path = logs_path + "\\{}".format('tradex-logs-' + str(dt.datetime.now().date()) + ".log")
logging.basicConfig(filename=logs_path,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

# Inistializing tts engine
engine = pyttsx3.init()

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

"""
blsh - buy low sell high
"""

"""
(done)  1. Execute only on trading days                                       - higher level task
(done)  2. Auto launch at 9:15 *                                              - higher level task
(done)  3. Automate Authorizing CDSL at 9:15                                  - higher level task
(done)  4. sell previous days stock if price per share has increased > 0.05
(done)  5. buy stock after 3:29 
(done)  6. Invest half your Margins available
(done)  7. divide capital available by number of tradable instruments and buy
(done)  8. Holdings is not updating frequently - need to stream values or get pnl values
()      9. Check for LTP and place a limit order during sell
()     10. Basic stoploss, with gain GTTs and stop loss limits - fucntions
()     11. Check frequency of calls
(done) 12. Add logging
()     13. Implement actual charges and take positions with stop loss 
()     14. Brokerage Calculator

"""

# INIT TIME
year = dt.datetime.now().year
month = dt.datetime.now().month
day = dt.datetime.now().day

# CHECK IF TRADIND DAY IS TRUE
holiday_list = [dt.datetime.strptime(date, '%d-%b-%Y').date() for date in trading_holidays]
trading_date = dt.datetime.today()

if trading_date.date() in holiday_list or trading_date.weekday() in [5, 6]:
    print("HOLIDAY :/")
    exit()

# INIT TRADEX ACTION TIME
start_time = dt.datetime(year=year, month=month, day=day, hour=9, minute=15, second=30)
end_time = dt.datetime(year=year, month=month, day=day, hour=15, minute=30, second=00)
buy_time = dt.datetime(year=year, month=month, day=day, hour=15, minute=29, second=00)
sell_time = dt.datetime(year=year, month=month, day=day, hour=15, minute=27, second=00)

engine.say("TRADEX INITIALIZED")
engine.runAndWait()
logging.info('-------------------------------------------------------------------------')
logging.info('TRADEX INITIALIZED')


# AUTO LOGIN KITE AND GENERATE ACCESS TOKEN

logging.info('TRADEX INITIALIZED')
autologin()
generate_access_token()

logging.info('AUTO LOGIN COMPLETE AND ACCESS TOKEN UPDATED')
engine.say("AUTO LOGIN COMPLETE AND ACCESS TOKEN UPDATED")
engine.runAndWait()


# AUTHORIZE CDSL TO SELL SHARES
engine.say("C D S L AUTO AUTHORIZATION INITIALIZED")
logging.info('C D S L AUTO AUTHORIZATION INITIALIZED')

engine.runAndWait()

aac = auto_authorize_cdsl()

logging.info('C D S L AUTO AUTHORIZATION COMPLETE')
engine.say("C D S L AUTO AUTHORIZATION COMPLETE")
engine.runAndWait()


print("Tradx will be using: {} for blsh algo\n".format(tradable_instruments))

tx = tradex_driver()
buy_pending = True

print("\nStart time: {} | end time:{}\n".format(start_time, end_time))
holdings = tx.get_holdings_info()
to_sell = holdings["tradingsymbol"].tolist()
print(to_sell)
to_buy = list(np.setdiff1d(tradable_instruments, to_sell))
sold = []
no_profit = []
print("\nHOLDINDS\n{}\n".format(holdings))
print("\nEOD BUY: {}\n".format(to_buy))

engine.say("GOING LIVE")
logging.info('GOING LIVE')
engine.runAndWait()

"""

while start_time < dt.datetime.now() < end_time:

    # SELL
    while dt.datetime.now() <= sell_time and len(to_sell) > 0:
        tx.print_status("Executing Strategy X1")
        holdings = tx.get_holdings_info()
        ltp_data = tx.kite.ltp(['NSE:' + symbol for symbol in to_sell])

        if dt.datetime.now() == sell_time:
            print("\nEnd of SELL TIME\n")
            logging.info('END OF SELL TIME')
            break

        for inst in to_sell:
            quantity = holdings[holdings["tradingsymbol"] == inst]["quantity"].values[0]
            t1_quantity = holdings[holdings["tradingsymbol"] == inst]["t1_quantity"].values[0]
            quantity = quantity + t1_quantity
            average_price = holdings[holdings["tradingsymbol"] == inst]["average_price"].values[0]
            last_price = ltp_data.get('NSE:' + inst).get('last_price')
            pnl = holdings[holdings["tradingsymbol"] == inst]["pnl"].values[0]

            if quantity == 0:
                sold.append(inst)

            if last_price - average_price >= 0.10 and quantity > 0:
                time.sleep(0.34)
                tx.place_cnc_market_order(inst, "sell", quantity)
                sold.append(inst)
                print("\nSOLD {} | quantity:{}".format(inst, quantity))
                logging.info("SOLD {} | quantity:{}".format(inst, quantity))

            # check if its < -0.5 % , if thats the case, sell immediately
            # (((last_price) * quantity / (average_price * quantity)) - 1) * 100

            else:
                no_profit.append(inst)

        to_sell = list(np.setdiff1d(to_sell, sold))

        if not to_sell:
            print("Nothing to sell")
            logging.info("NOTHING TO SELL. IDLE MODE.")
            break

    tx.update_daily_margin(to_sell)

    # BUY
    if buy_time <= dt.datetime.now() and buy_pending:
        margin = tx.get_equity_margins()
        risk_capital = int(margin * risk_factor)
        max_cap_per_stock = int(risk_capital / len(to_buy))

        print("MARGIN:{}".format(margin))
        print("RISK CAPITAL AMOUNT:{}".format(risk_capital))
        print("MAX CAP PER STOCK:{}".format(max_cap_per_stock))

        for inst in to_buy:
            ltp = tx.kite.ltp('NSE:' + str(inst))['NSE:' + str(inst)]['last_price']
            quantity = 200
            # int(max_cap_per_stock / ltp)
            if ltp * quantity < 8000:
                tx.place_cnc_order(inst, "buy", quantity)
                print("\nOrder placed - {} | @ {} | quantity: {}".format(inst, ltp, quantity))
                time.sleep(0.5)

                engine.say("BUY COMPLETE")
                logging.info("BUY COMPLETE")
                engine.runAndWait()
                buy_pending = False
                break

    tx.idle()

engine.say("TRADEX SHUTTING DOWN")
logging.info("TRADEX SHUTTING DOWN")

engine.runAndWait()

"""