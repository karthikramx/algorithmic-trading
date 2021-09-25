import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
from itertools import product
import matplotlib.pyplot as plt


np.random.standard_normal()

# Data Retrieval
class Financial_Data:
    def __init__(self, symbol='TSLA', end=dt.datetime.today(), days=168):
        self.symbol = symbol
        start = end - pd.Timedelta(days=days)
        self.download_daily_data(start=start, end=end)
        self.prepare_data()

    def download_daily_data(self, start, end):
        self.df = yf.download(self.symbol, start=start, end=end)

    def prepare_data(self):
        self.df['daily_returns'] = np.log(self.df['Adj Close'] / self.df['Adj Close'].shift(1))
        self.df['bnh_returns'] = self.df['daily_returns'].cumsum()
        self.df.dropna(inplace=True)

    def plot_returns(self, list_of_columns):
        self.df[list_of_columns].plot()
        plt.show()


class SMA_Back_tester(Financial_Data):

    def prepare_indicators(self, SMA1, SMA2):
        self.df['SMA1'] = self.df['Close'].rolling(window=SMA1).mean()
        self.df['SMA2'] = self.df['Close'].rolling(window=SMA2).mean()
        self.df.dropna(inplace=True)

    def backtest_strategy(self, SMA1, SMA2):
        self.prepare_indicators(SMA1, SMA2)
        self.df['position'] = np.where(self.df['SMA1'] > self.df['SMA2'], 1, 0)
        self.df['position'] = self.df['position'].shift(1)
        self.df['strategy_returns'] = self.df['position'] * self.df['daily_returns']
        self.df['strategy_returns'] = self.df['strategy_returns'].cumsum()
        start = SMA2
        perf = self.df[['strategy_returns', 'bnh_returns']]  # .iloc[start:].sum().apply(np.exp)
        return perf

    def plot_strategy_returns(self):
        self.plot_returns(['bnh_returns', 'strategy_returns'])

    def optimize_paramters(self, SMA1_Range, SMA2_Range):
        self.results = pd.DataFrame()
        for sma1, sma2 in product(SMA1_Range, SMA2_Range):
            perf = sma.backtest_strategy(sma1, sma2)
            self.result = pd.DataFrame({'SMA1': sma1,
                                        'SMA2': sma2,
                                        'bnh returns': perf['bnh_returns'],
                                        'strategy retunrs': perf['strategy_returns']})
            self.results = self.results.append(self.result, ignore_index=True)

        print(self.results)


sma = SMA_Back_tester()
sma.optimize_paramters(range(1, 7, 1), range(5, 15, 1))

# https://gist.github.com/yhilpisch/a2048d54fea8d35b253ea6ab8ed7bba5

