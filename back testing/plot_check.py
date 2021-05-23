import pandas as pd
from matplotlib import pyplot as plt
import os

acc_path = os.environ["HOMEPATH"] + "\\Desktop" + "\\algorithmic-trading" + "\\data" + "\\21MAY" + "\\ACC.txt"

acc_data = pd.read_csv(acc_path, header=None, parse_dates=[2])

a = acc_data.columns
print(acc_data.columns)

rename_index = {0: "instrument", 1: "date", 2: "date - time", 3: "open", 4: "high", 5: "low", 6: "close",
                7: "volume", 8: "x"}


acc_data = acc_data.rename(columns=rename_index)
acc_data.drop("date", axis=1, inplace=True)
acc_data = acc_data[~(acc_data['date - time'] > '2021-05-23 15:30')]
acc_data = acc_data[~(acc_data['date - time'] < '2021-05-23 09:15')]

# make and plot macd
# make and plot rsi
# make and plot supertrend
# make and plot renko
# clear all tax/zerodha charges/intra day and cnc based questions/ -- know the game
# feed time series data into the decision maker and calculate returns based on decisions



# test placing trades - all about buy/sell/intraday/stop-loss/trailing stop loss/
# placing cnc orders inorder to get continuiing returns no matter what - sell when you get a 2000 return
# but you will have a stop loss in place and check if

acc_data.plot(x="date - time", y="close")
plt.show()

acc_data.info()
print("debug")
