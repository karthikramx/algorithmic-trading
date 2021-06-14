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

    def get_minute_data(self, month, days_of_month=None, instrument_name=None):
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
        DF["MACD"] = df["MA_Fast"] - df["MA_Slow"]
        DF["Signal"] = DF["MACD"].ewm(span=c, min_periods=c).mean()
        DF.dropna(inplace=True)

    def RSI(self, DF, n=14):
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
        DF['RSI'] = 100 - 100 / (1 + rs)

    def MA(self, DF, n=9):
        """Moving Average Calculations"""
        DF["MA"] = DF["close"].ewm(span=n, min_periods=n).mean()


class backtest_simulation:
    def __init__(self, df):
        self.ti = technical_indicators()
        self.buy_price = 0
        self.sell_price = 0
        self.action = "RTB"
        self.gains = []
        self.df = df

        self.ti.RSI(self.df)
        self.ti.MACD(self.df)
        self.ti.MA(self.df)

        self.df.dropna(axis=0, inplace=True)
        self.df = self.df.reset_index()
        self.df.drop("index", inplace=True, axis=1)

    def check_buy_conditions(self, close, ma, rsi, macd, signal, macd_slope, rsi_slope):
        # check if ma is below close by certain percentage

        return True


    def buy_sell(self):

        for tick in range(len(self.df)):

            ma_value = self.df.loc[tick, 'MA']
            rsi_value = self.df.loc[tick, 'RSI']
            macd_value = self.df.loc[tick, 'MACD']
            signal_value = self.df.loc[tick, 'Signal']
            close = self.df.loc[tick, 'close']
            date = self.df.loc[tick,'date - time']

            if self.action == "RTB":
                if self.check_buy_conditions():
                    self.buy_price = close
                    self.action = "RTS"
                    buy_day = self.df['date - time'][tick]
                    print("BUY DAY: {}".format(self.df['date - time'][tick]))

            elif self.action == "RTS":
                current_price = self.df.loc[self.df['date - time'] == self.df['date - time'][tick]]['open'].to_list()[0]
                days = self.df['date - time'][tick] - buy_day
                if (macd_mean > signal_mean) and (current_price > self.buy_price) and days.days > 2:
                    self.sell_price = self.df.loc[self.df['date - time'] == df['date - time'][tick]]['close'].to_list()[
                        0]
                    print("SELL DAY: {}".format(self.df['date - time'][tick]))
                    print("Days: {}".format(days.days))
                    print("bought at: {}".format(self.buy_price))
                    print("sold at: {}".format(self.sell_price))
                    print("gains: {} % \n".format(((self.sell_price / self.buy_price) - 1) * 100))
                    self.gains.append(((self.sell_price / self.buy_price) - 1) * 1200000)
                    self.action = "RTB"

        print("Gains aggregate: {}".format(sum(self.gains)))


month_days = ['03', '04', '05', '06', '07', '10', '11', '12', '14', '17', '18', '19', '20',
              '21', '24', '25', '26', '27', '28', '31']

dh = data_handler()
may_acc_data = dh.get_minute_data(month='MAY', days_of_month=month_days, instrument_name="ITC")

ti = technical_indicators()
bs = backtest_simulation(may_acc_data)
bs.buy_sell()
