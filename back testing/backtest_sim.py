import numpy as np
import pandas as pd
from statistics import mean
import os


# use TA LIB


class data_handler:
    def __init__(self):
        self.rename_index = {0: "instrument",
                             1: "date",
                             2: "time",
                             3: "open",
                             4: "high",
                             5: "low",
                             6: "close",
                             7: "volume",
                             8: "x"}

    def get_minute_data(self, month="MAY", days_of_month=None, instrument_name=None):
        hist_data = pd.DataFrame()
        if all(1 <= int(ele) <= 31 for ele in days_of_month):
            try:
                for i in range(len(days_of_month)):
                    folder_name = str(days_of_month[i]) + str(month)
                    data_path = os.environ["HOMEPATH"] + "\\Desktop\\algorithmic-trading\\data\\{}\\{}.txt".format(
                        folder_name, instrument_name)
                    print("Extracting from: {}".format(data_path))
                    minute_data = pd.read_csv(data_path, header=None)

                    minute_data = minute_data.rename(columns=self.rename_index)
                    minute_data["date"] = minute_data["date"].astype(str)
                    minute_data["time"] = minute_data["time"].astype(str)
                    date = minute_data.iloc[[0], [1]]['date'][0]
                    minute_data["time"] = pd.to_datetime((minute_data['date']) + ' ' + (minute_data['time']))
                    minute_data.drop("date", axis=1, inplace=True)
                    minute_data = minute_data.rename(columns={"time": "date - time"})
                    minute_data = minute_data[~(minute_data['date - time'] > '{} 15:30'.format(date))]
                    minute_data = minute_data[~(minute_data['date - time'] < '{} 09:15'.format(date))]
                    hist_data = hist_data.append(minute_data)
                    hist_data = hist_data.reset_index(drop=True)
                    print(hist_data.dtypes)


            except Exception as e:
                print("Data not found: {}".format(e))
        return hist_data


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

    def rsi(self, DF, n):
        """function to calculate RSI"""
        df = DF.copy()
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
        # return
        df['rsi'] = 100 - 100 / (1 + rs)
        return df

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
        return df

    def atr(self, DF, n):
        """function to calculate True Range and Average True Range"""
        df = DF.copy()
        df['H-L'] = abs(df['high'] - df['low'])
        df['H-PC'] = abs(df['high'] - df['close'].shift(1))
        df['L-PC'] = abs(df['low'] - df['close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
        df['ATR'] = df['TR'].ewm(com=n, min_periods=n).mean()
        return df['ATR']


class backtest_simulation:
    def __init__(self, df):
        self.ti = technical_indicators()
        self.buy_price = 0
        self.sell_price = 0
        self.action = "RTB"
        self.gains = []
        self.df = df
        self.df_rsi = self.ti.rsi(df, 14)
        self.df_macd = self.ti.MACD(df)
        self.dt_supertrend = self.ti.supertrend(df, n=7, m=2)

    def checks(self, df):
        print("Length of df:{}".format(len(df)))
        print("Length of df_rsi:{}".format(len(self.df_rsi)))
        print("Length of df_macd:{}".format(len(self.df_macd)))

    def buy_sell(self, df):
        macd_buffer = [0 * 5]
        signal_buffer = [0 * 5]
        rsi_buffer = [0 * 5]

        for tick in range(len(df)):
            try:
                rsi_value = self.df_rsi.loc[self.df['date - time'] == self.df['date - time'][tick]]['rsi'].to_list()[0]
                macd_value = self.df_macd.loc[self.df['date - time'] == self.df['date - time'][tick]]['MACD'].to_list()[
                    0]
                signal_value = \
                self.df_macd.loc[self.df['date - time'] == self.df['date - time'][tick]]['Signal'].to_list()[0]
            except IndexError as e:
                signal_value = np.NAN
                macd_value = np.NAN
                rsi_value = np.NAN

            macd_buffer.pop(0)
            macd_buffer.append(macd_value)
            rsi_buffer.pop(0)
            rsi_buffer.append(rsi_value)
            signal_buffer.pop(0)
            signal_buffer.append(signal_value)
            macd_mean = mean(macd_buffer)
            signal_mean = mean(signal_buffer)
            rsi_mean = mean(rsi_buffer)

            if self.action == "RTB":
                if macd_mean > signal_mean:
                    self.buy_price = self.df.loc[self.df['date - time'] == self.df['date - time'][tick]]['close'].to_list()[0]
                    self.action = "RTS"
                    buy_day = df['date - time'][tick]
                    print("BUY DAY: {}".format(self.df['date - time'][tick]))

            elif self.action == "RTS":
                current_price = self.df.loc[self.df['date - time'] == self.df['date - time'][tick]]['open'].to_list()[0]
                days = self.df['date - time'][tick] - buy_day
                if (macd_mean > signal_mean) and (current_price > self.buy_price) and days.days > 2:
                    self.sell_price = self.df.loc[self.df['date - time'] == df['date - time'][tick]]['close'].to_list()[0]
                    print("SELL DAY: {}".format(self.df['date - time'][tick]))
                    print("Days: {}".format(days.days))
                    print("bought at: {}".format(self.buy_price))
                    print("sold at: {}".format(self.sell_price))
                    print("gains: {} % \n".format(((self.sell_price / self.buy_price) - 1) * 100))
                    self.gains.append(((self.sell_price / self.buy_price) - 1) * 1200000)
                    self.action = "RTB"

        print("Gains aggregate: {}".format(sum(self.gains)))


dh = data_handler()

month_days = ['03', '04', '05', '06', '07', '10', '11', '12', '14', '17', '18', '19', '20',
              '21', '24', '25', '26', '27', '28', '31']
may_acc_data = dh.get_minute_data(days_of_month=month_days, instrument_name="ITC")
bs = backtest_simulation(may_acc_data)
bs.buy_sell()
