import os
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


sns.set_theme()
sns.set_context("paper")


class technical_indicators:
    def __init__(self):
        print("technical indicators class initialized")

    def MACD(self, DF, a=12, b=26, c=9):
        """function to calculate MACD
           typical values a(fast moving average) = 12;
                          b(slow moving average) =26;
                          c(signal line ma window) =9"""
        df = DF.copy()
        df["MA_Fast"] = df["close"].ewm(span=a, min_periods=a).mean()
        df["MA_Slow"] = df["close"].ewm(span=b, min_periods=b).mean()
        df["MACD"] = df["MA_Fast"] - df["MA_Slow"]
        df["Signal"] = df["MACD"].ewm(span=c, min_periods=c).mean()
        df.dropna(inplace=True)
        return df

    def rsi(self, df, n):
        """function to calculate RSI"""

        delta = df["close"].diff().dropna()
        u = delta * 0
        d = u.copy()
        u[delta > 0] = delta[delta > 0]
        d[delta < 0] = -delta[delta < 0]
        u[u.index[n - 1]] = np.mean(u[:n])  # first value is average of gains
        u = u.drop(u.index[:(n - 1)])
        d[d.index[n - 1]] = np.mean(d[:n])  # first value is average of losses
        d = d.drop(d.index[:(n - 1)])
        rs = u.ewm(com=n, min_periods=n).mean() / d.ewm(com=n, min_periods=n).mean()
        return 100 - 100 / (1 + rs)

    def supertrend(self, DF, n, m):
        """function to calculate Supertrend given historical candle data
            n = n day ATR - usually 7 day ATR is used
            m = multiplier - usually 2 or 3 is used"""
        df = DF.copy()
        df['ATR'] = self.atr(df, n)
        df["B-U"] = ((df['high'] + df['low']) / 2) + m * df['ATR']
        df["B-L"] = ((df['high'] + df['low']) / 2) - m * df['ATR']
        df["U-B"] = df["B-U"]
        df["L-B"] = df["B-L"]
        ind = df.index
        for i in range(n, len(df)):
            if df['close'][i - 1] <= df['U-B'][i - 1]:
                df.loc[ind[i], 'U-B'] = min(df['B-U'][i], df['U-B'][i - 1])
            else:
                df.loc[ind[i], 'U-B'] = df['B-U'][i]
        for i in range(n, len(df)):
            if df['close'][i - 1] >= df['L-B'][i - 1]:
                df.loc[ind[i], 'L-B'] = max(df['B-L'][i], df['L-B'][i - 1])
            else:
                df.loc[ind[i], 'L-B'] = df['B-L'][i]
        df['Strend'] = np.nan
        for test in range(n, len(df)):
            if df['close'][test - 1] <= df['U-B'][test - 1] and df['close'][test] > df['U-B'][test]:
                df.loc[ind[test], 'Strend'] = df['L-B'][test]
                break
            if df['close'][test - 1] >= df['L-B'][test - 1] and df['close'][test] < df['L-B'][test]:
                df.loc[ind[test], 'Strend'] = df['U-B'][test]
                break
        for i in range(test + 1, len(df)):
            if df['Strend'][i - 1] == df['U-B'][i - 1] and df['close'][i] <= df['U-B'][i]:
                df.loc[ind[i], 'Strend'] = df['U-B'][i]
            elif df['Strend'][i - 1] == df['U-B'][i - 1] and df['close'][i] >= df['U-B'][i]:
                df.loc[ind[i], 'Strend'] = df['L-B'][i]
            elif df['Strend'][i - 1] == df['L-B'][i - 1] and df['close'][i] >= df['L-B'][i]:
                df.loc[ind[i], 'Strend'] = df['L-B'][i]
            elif df['Strend'][i - 1] == df['L-B'][i - 1] and df['close'][i] <= df['L-B'][i]:
                df.loc[ind[i], 'Strend'] = df['U-B'][i]
        return df['Strend']

    def atr(self, DF, n):
        """function to calculate True Range and Average True Range"""
        df = DF.copy()
        df['H-L'] = abs(df['high'] - df['low'])
        df['H-PC'] = abs(df['high'] - df['close'].shift(1))
        df['L-PC'] = abs(df['low'] - df['close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
        df['ATR'] = df['TR'].ewm(com=n, min_periods=n).mean()
        return df['ATR']


acc_path = os.environ["HOMEPATH"] + "\\Desktop" + "\\algorithmic-trading" + "\\data" + "\\21MAY" + "\\ACC.txt"

acc_data = pd.read_csv(acc_path, header=None, parse_dates=[2])

a = acc_data.columns
print(acc_data.columns)

rename_index = {0: "instrument", 1: "date", 2: "date - time", 3: "open", 4: "high", 5: "low", 6: "close",
                7: "volume", 8: "x"}

acc_data = acc_data.rename(columns=rename_index)
acc_data.drop("date", axis=1, inplace=True)
acc_data = acc_data[~(acc_data['date - time'] > '2021-05-24 15:30')]
acc_data = acc_data[~(acc_data['date - time'] < '2021-05-24 09:15')]

ti = technical_indicators()

acc_data_macd = ti.MACD(acc_data)

sns.lineplot(x=acc_data_macd["date - time"], y=acc_data_macd["MACD"], color="g")
ax2 = plt.twinx()
sns.lineplot(x=acc_data_macd["date - time"], y=acc_data_macd["Signal"], color="b", ax=ax2)
plt.show()

acc_data.info()
print("debug")


