import numpy as np
from tradex_driver import tradex_driver
from auto_cdsl_auth import *
from auto_login import *
import pyttsx3

engine = pyttsx3.init()

"""
blsh - buy low sell high
"""

"""
(done)  1. Execute only on trading days                                     - higher level task
        2. Auto launch at 9:15 *                                            - higher level task
(done)  3. Automate Authorizing CDSL at 9:15                                - higher level task
(done)  4. sell previous days stock if price per share has increased > 0.05
(done)  5. buy stock after 3:29 
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
sell_time = dt.datetime(year=year, month=month, day=day, hour=9, minute=45, second=00)

engine.say("TRADEX INITIALIZED")
engine.runAndWait()

# AUTO LOGIN KITE AND GENERATE ACCESS TOKEN
autologin()
generate_access_token()

engine.say("AUTO LOGIN COMPLETE AND ACCESS TOKEN UPDATED")
engine.runAndWait()

# AUTHORIZE CDSL TO SELL SHARES
engine.say("C D S L AUTO AUTHORIZATION INITIALIZED")
engine.runAndWait()

aac = auto_authorize_cdsl()

engine.say("C D S L AUTO AUTHORIZATION COMPLETE")
engine.runAndWait()

print("Tradx will be using: {} for blsh algo\n".format(tradable_instruments))

tx = tradex_driver()
buy_pending = True

print("\nStart time: {} | end time:{}\n".format(start_time, end_time))
holdings = tx.get_holdings_info()
to_sell = holdings["tradingsymbol"].tolist()
to_buy = list(np.setdiff1d(tradable_instruments, to_sell))
sold = []
no_profit = []
print("\nHOLDINDS\n{}\n".format(holdings))
print("\nEOD BUY: {}\n".format(to_buy))

engine.say("GOING LIVE")
engine.runAndWait()


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
            tx.place_cnc_order(inst, "buy", 10)
            print("\nOrder placed - {}".format(inst))
            time.sleep(0.5)

        engine.say("BUY COMPLETE")
        engine.runAndWait()
        buy_pending = False

    tx.idle()

engine.say("TRADEX SHUTTING DOWN")
engine.runAndWait()
