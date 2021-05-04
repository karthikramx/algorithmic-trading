import pandas as pd

ltp = pd.read_csv('money_control_ltp.csv', index_col=[0])
# ltp.sort_index()
ltp = ltp[~ltp['Company Name'].str.contains("No Data Available")]
ltp.to_csv('money_control_ltpx.csv')

ltp['Last Price'] = ltp['Last Price'].apply(lambda x: float(x))
ltp['Market Cap(Rs. cr)'] = ltp['Market Cap(Rs. cr)'].apply(lambda x: float(x))
ltp['% Chg'] = ltp['% Chg'].apply(lambda x: float(x))
ltp['52 wkHigh'] = ltp['52 wkHigh'].apply(lambda x: float(x))
ltp['52 wkLow'] = ltp['52 wkLow'].apply(lambda x: float(x))


extract = ltp[ ltp["Last Price"] < 50]
extract = extract[ extract["Market Cap(Rs. cr)"] > 1000]
extract.to_csv('extract.csv')
ltp.to_csv('ltp.csv')
