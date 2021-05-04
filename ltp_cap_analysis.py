import pandas as pd

ltp = pd.read_csv('money_control_ltp.csv')

ltp = ltp[~ltp['Company Name'].str.contains("No Data Available")]

ltp.to_csv('money_control_ltpx.csv')

#extract = ltp[ float(ltp["Last Price"]) < 50 ]

#extract.to_csv('extract.csv')

print(ltp)