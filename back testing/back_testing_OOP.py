"""
Author: Karthik Ram
Email: karthikram570@gmail.com
Topic: Backtesting strategies using Object Oriented Programming
About: Implementing basic momentum based technical indicators on yfinance data, optimizing strategy paramenters and
        generating pyfolio performance reports
"""

import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
from itertools import product
import matplotlib.pyplot as plt
import warnings
import pyfolio as pf
warnings.filterwarnings("ignore")


class FinancialData:
    def __init__(self, symbol='TSLA', end=dt.datetime.today(), days=168):
        self.symbol = symbol
        self.start = end - pd.Timedelta(days=days)
        self.end = end
        self.retrieve_data(self.symbol, self.start, self.end)
        self.prepare_data()

    def retrieve_data(self, symbol, start, end):
        self.data = yf.download(symbol, start=start, end=end)

    def prepare_data(self):
        self.data['daily_returns'] = np.log(self.data['Adj Close'] / self.data['Adj Close'].shift(1))
        self.data['bnh_returns'] = self.data['daily_returns'].cumsum()
        self.data.dropna(inplace=True)

    def plot_data(self, attribute_list):
        self.data[attribute_list].plot()
        plt.show()

    def plot_strategy_returns(self):
        self.plot_data(['bnh_returns', 'strategy_returns'])

    def create_simple_tear_sheet(self):
        pf.display(pf.create_simple_tear_sheet(self.data['strategy_returns']))



class SMABacktester(FinancialData):

    def prepare_indicators(self, SMA1, SMA2):
        self.data['SMA1'] = self.data['Adj Close'].rolling(window=SMA1).mean()
        self.data['SMA2'] = self.data['Adj Close'].rolling(window=SMA2).mean()

    def backtest_strategy(self, SMA1, SMA2, start=None):
        if start is None:
            start = SMA2
        self.prepare_indicators(SMA1, SMA2)
        self.data['position'] = np.where(self.data['SMA1'] > self.data['SMA2'], 1, -1)
        self.data['position'] = self.data['position'].shift(1)
        self.data['strategy_returns'] = self.data['position'] * self.data['daily_returns']
        performance = self.data[['daily_returns', 'strategy_returns']].iloc[start:].sum()
        self.data['strategy_returns'] = self.data['strategy_returns'].cumsum()
        return performance

    def plot_optimized_sma_strategy_returns(self):
        if (len(self.results)) > 0:
            self.optimized_sma1 = self.results.loc[0, 'SMA1']
            self.optimized_sma2 = self.results.loc[1, 'SMA2']
            self.backtest_strategy(self.optimized_sma1, self.optimized_sma2)
            self.plot_strategy_returns()

    def optimize_parameters(self, sma1_range, sma2_range):
        self.results = pd.DataFrame()
        print(len(self.results))
        start = max(sma2_range)
        for sma1, sma2 in product(sma1_range, sma2_range):
            perf = self.backtest_strategy(sma1, sma2, start=start)
            self.result = pd.DataFrame({'SMA1': sma1,
                                        'SMA2': sma2,
                                        'bnh returns': perf['daily_returns'],
                                        'strategy retunrs': perf['strategy_returns']}, index=[0, ])
            self.results = self.results.append(self.result, ignore_index=True)
        self.results.sort_values(by='strategy retunrs')
        print(self.results)


class BollingerBandBacktester(FinancialData):
    def prepare_indicators(self, window):
        self.data['moving_avg'] = self.data['Adj Close'].rolling(window=window).mean()
        self.data['moving_std'] = self.data['Adj Close'].rolling(window=window).std()

    def backtest_strategy(self, window, start=None):
        self.prepare_indicators(window)
        self.data['upper_band'] = self.data['moving_avg'] + 2 * self.data['moving_std']
        self.data['lower_band'] = self.data['moving_avg'] - 2 * self.data['moving_std']

        if start is None:
            start = window

        # BUY condition
        self.data['signal'] = np.where((self.data['Adj Close'] < self.data['lower_band']) &
                                       (self.data['Adj Close'].shift(1) >= self.data['lower_band']), 1, 0)

        # SELL condition
        self.data['signal'] = np.where((self.data['Adj Close'] > self.data['upper_band']) &
                                       (self.data['Adj Close'].shift(1) <= self.data['upper_band']), -1,
                                       self.data['signal'])

        self.data['position'] = self.data['signal'].replace(to_replace=0, method='ffill')
        self.data['position'] = self.data['position'].shift()

        self.data['strategy_returns'] = self.data['position'] * self.data['daily_returns']

        performance = self.data[['daily_returns', 'strategy_returns']].iloc[start:].sum()

        self.data['strategy_returns'] = self.data['strategy_returns'].cumsum()
        return performance

    def optimize_bollinger_band_parameters(self, windows):
        start = max(windows)
        self.results = pd.DataFrame()
        for window in windows:
            perf = self.backtest_strategy(window=window, start=start)
            self.result = pd.DataFrame({'Window': window,
                                        'bnh returns': perf['daily_returns'],
                                        'strategy returns': perf['strategy_returns']}, index=[0, ])
            self.results = self.results.append(self.result, ignore_index=True)
        self.results.sort_values(by='strategy returns', inplace=True, ascending=False)
        self.results = self.results.reset_index()
        self.results = self.results.drop("index", axis=1)
        print(self.results)

    def plot_optimized_bollinger_strategy_returns(self):
        if (len(self.results)) > 0:
            window = self.results.loc[0, 'Window']
            print("Window:", window)
            self.backtest_strategy(window=window)
            self.plot_strategy_returns()


Bollinger = BollingerBandBacktester(symbol="MSFT")
Bollinger.optimize_bollinger_band_parameters(range(1, 50, 1))
Bollinger.plot_optimized_bollinger_strategy_returns()
Bollinger.create_simple_tear_sheet()

