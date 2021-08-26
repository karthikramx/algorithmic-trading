# gui global config variables
HEADLESS_MODE = False
BROWSER_X_POS = 750
BROWSER_Y_POS = 0
BROWSER_X_SIZE = 800
BROWSER_Y_SIZE = 900

# algo global config variables
MAX_TRIES = 10

# stock market varaibles
# can add API to fetch NIFTY FIFTY STOCKS
nifty_tickers = ["ZEEL", "WIPRO", "VEDL", "ULTRACEMCO", "UPL", "TITAN", "TECHM", "TATASTEEL",
                 "TATAMOTORS", "TCS", "SUNPHARMA", "SBIN", "SHREECEM", "RELIANCE", "POWERGRID",
                 "ONGC", "NESTLEIND", "NTPC", "MARUTI", "M&M", "LT", "KOTAKBANK", "JSWSTEEL", "INFY",
                 "INDUSINDBK", "IOC", "ITC", "ICICIBANK", "HDFC", "HINDUNILVR", "HINDALCO",
                 "HEROMOTOCO", "HDFCBANK", "HCLTECH", "GRASIM", "GAIL", "EICHERMOT", "DRREDDY",
                 "COALINDIA", "CIPLA", "BRITANNIA", "BHARTIARTL", "BPCL", "BAJAJFINSV",
                 "BAJFINANCE", "BAJAJ-AUTO", "AXISBANK", "ASIANPAINT", "ADANIPORTS"]

trading_holidays = ['26-Jan-2021', '11-Mar-2021', '29-Mar-2021', '02-Apr-2021', '14-Apr-2021', '21-Apr-2021',
                    '13-May-2021', '21-Jul-2021', '19-Aug-2021', '10-Sep-2021', '15-Oct-2021', '05-Nov-2021',
                    '19-Nov-2021']

# tradable_instruments = ["PNB", "UNIONBANK", "GMRINFRA", "IDBI", "IDFCFIRSTB", "ONGC",
#                        "BANKBARODA", "MMTC", "MAHABANK"]

tradable_instruments = []

risk_factor = 0.5

# CHARGES --------------------------------------------------------------------------------------------------------------
GST = [1.18]

# CDSL
depository_participant_charge = 13.5 * GST[0]

# BROKER


# STOCK EXCHANGE

my_tickers = []
