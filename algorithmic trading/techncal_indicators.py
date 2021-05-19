import pandas as pd
import numpy as np


def MACD(DF, a, b, c):
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


def bollBnd(DF, n):
    "function to calculate Bollinger Band"
    df = DF.copy()
    # df["MA"] = df['close'].rolling(n).mean()
    df["MA"] = df['close'].ewm(span=n, min_periods=n).mean()
    df["BB_up"] = df["MA"] + 2 * df['close'].rolling(n).std(
        ddof=0)  # ddof=0 is required since we want to take the standard deviation of the population and not sample
    df["BB_dn"] = df["MA"] - 2 * df['close'].rolling(n).std(
        ddof=0)  # ddof=0 is required since we want to take the standard deviation of the population and not sample
    df["BB_width"] = df["BB_up"] - df["BB_dn"]
    df.dropna(inplace=True)
    return df


def atr(DF, n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L'] = abs(df['high'] - df['low'])
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].ewm(com=n, min_periods=n).mean()
    return df['ATR']


def rsi(df, n):
    "function to calculate RSI"

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


def adx(DF, n):
    "function to calculate ADX"
    df2 = DF.copy()
    df2['H-L'] = abs(df2['high'] - df2['low'])
    df2['H-PC'] = abs(df2['high'] - df2['close'].shift(1))
    df2['L-PC'] = abs(df2['low'] - df2['close'].shift(1))
    df2['TR'] = df2[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    df2['DMplus'] = np.where((df2['high'] - df2['high'].shift(1)) > (df2['low'].shift(1) - df2['low']),
                             df2['high'] - df2['high'].shift(1), 0)
    df2['DMplus'] = np.where(df2['DMplus'] < 0, 0, df2['DMplus'])
    df2['DMminus'] = np.where((df2['low'].shift(1) - df2['low']) > (df2['high'] - df2['high'].shift(1)),
                              df2['low'].shift(1) - df2['low'], 0)
    df2['DMminus'] = np.where(df2['DMminus'] < 0, 0, df2['DMminus'])
    TRn = []
    DMplusN = []
    DMminusN = []
    TR = df2['TR'].tolist()
    DMplus = df2['DMplus'].tolist()
    DMminus = df2['DMminus'].tolist()
    for i in range(len(df2)):
        if i < n:
            TRn.append(np.NaN)
            DMplusN.append(np.NaN)
            DMminusN.append(np.NaN)
        elif i == n:
            TRn.append(df2['TR'].rolling(n).sum().tolist()[n])
            DMplusN.append(df2['DMplus'].rolling(n).sum().tolist()[n])
            DMminusN.append(df2['DMminus'].rolling(n).sum().tolist()[n])
        elif i > n:
            TRn.append(TRn[i - 1] - (TRn[i - 1] / n) + TR[i])
            DMplusN.append(DMplusN[i - 1] - (DMplusN[i - 1] / n) + DMplus[i])
            DMminusN.append(DMminusN[i - 1] - (DMminusN[i - 1] / n) + DMminus[i])
    df2['TRn'] = np.array(TRn)
    df2['DMplusN'] = np.array(DMplusN)
    df2['DMminusN'] = np.array(DMminusN)
    df2['DIplusN'] = 100 * (df2['DMplusN'] / df2['TRn'])
    df2['DIminusN'] = 100 * (df2['DMminusN'] / df2['TRn'])
    df2['DIdiff'] = abs(df2['DIplusN'] - df2['DIminusN'])
    df2['DIsum'] = df2['DIplusN'] + df2['DIminusN']
    df2['DX'] = 100 * (df2['DIdiff'] / df2['DIsum'])
    ADX = []
    DX = df2['DX'].tolist()
    for j in range(len(df2)):
        if j < 2 * n - 1:
            ADX.append(np.NaN)
        elif j == 2 * n - 1:
            ADX.append(df2['DX'][j - n + 1:j + 1].mean())
        elif j > 2 * n - 1:
            ADX.append(((n - 1) * ADX[j - 1] + DX[j]) / n)
    df2['ADX'] = np.array(ADX)
    return df2['ADX']


def supertrend(DF, n, m):
    """function to calculate Supertrend given historical candle data
        n = n day ATR - usually 7 day ATR is used
        m = multiplier - usually 2 or 3 is used"""
    df = DF.copy()
    df['ATR'] = atr(df, n)
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


def hammer(ohlc_df):
    """returns dataframe with hammer candle column"""
    df = ohlc_df.copy()
    df["hammer"] = (((df["high"] - df["low"]) > 3 * (df["open"] - df["close"])) & \
                    ((df["close"] - df["low"]) / (.001 + df["high"] - df["low"]) > 0.6) & \
                    ((df["open"] - df["low"]) / (.001 + df["high"] - df["low"]) > 0.6)) & \
                   (abs(df["close"] - df["open"]) > 0.1 * (df["high"] - df["low"]))
    return df


def maru_bozu(ohlc_df):
    """returns dataframe with maru bozu candle column"""
    df = ohlc_df.copy()
    avg_candle_size = abs(df["close"] - df["open"]).median()
    df["h-c"] = df["high"] - df["close"]
    df["l-o"] = df["low"] - df["open"]
    df["h-o"] = df["high"] - df["open"]
    df["l-c"] = df["low"] - df["close"]
    df["maru_bozu"] = np.where((df["close"] - df["open"] > 2 * avg_candle_size) & \
                               (df[["h-c", "l-o"]].max(axis=1) < 0.005 * avg_candle_size), "maru_bozu_green",
                               np.where((df["open"] - df["close"] > 2 * avg_candle_size) & \
                                        (abs(df[["h-o", "l-c"]]).max(axis=1) < 0.005 * avg_candle_size),
                                        "maru_bozu_red", False))
    df.drop(["h-c", "l-o", "h-o", "l-c"], axis=1, inplace=True)
    return df


def shooting_star(ohlc_df):
    """returns dataframe with shooting star candle column"""
    df = ohlc_df.copy()
    df["sstar"] = (((df["high"] - df["low"]) > 3 * (df["open"] - df["close"])) & \
                   ((df["high"] - df["close"]) / (.001 + df["high"] - df["low"]) > 0.6) & \
                   ((df["high"] - df["open"]) / (.001 + df["high"] - df["low"]) > 0.6)) & \
                  (abs(df["close"] - df["open"]) > 0.1 * (df["high"] - df["low"]))
    return df


def slope(ohlc_df, n):
    "function to calculate the slope of regression line for n consecutive points on a plot"
    df = ohlc_df.iloc[-1 * n:, :]
    y = ((df["open"] + df["close"]) / 2).values
    x = np.array(range(n))
    y_scaled = (y - y.min()) / (y.max() - y.min())
    x_scaled = (x - x.min()) / (x.max() - x.min())
    x_scaled = sm.add_constant(x_scaled)
    model = sm.OLS(y_scaled, x_scaled)
    results = model.fit()
    slope = np.rad2deg(np.arctan(results.params[-1]))
    return slope


def trend(ohlc_df, n):
    "function to assess the trend by analyzing each candle"
    df = ohlc_df.copy()
    df["up"] = np.where(df["low"] >= df["low"].shift(1), 1, 0)
    df["dn"] = np.where(df["high"] <= df["high"].shift(1), 1, 0)
    if df["close"][-1] > df["open"][-1]:
        if df["up"][-1 * n:].sum() >= 0.7 * n:
            return "uptrend"
    elif df["open"][-1] > df["close"][-1]:
        if df["dn"][-1 * n:].sum() >= 0.7 * n:
            return "downtrend"
    else:
        return None
