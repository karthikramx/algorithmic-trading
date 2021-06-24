import pandas as pd

df = pd.read_csv('money_control_ltp.csv')

df['Last Price'] =  pd.to_numeric(df['Last Price'], errors='coerce')
df['Market Cap(Rs. cr)'] =  pd.to_numeric(df['Market Cap(Rs. cr)'], errors='coerce')

tradable = df[(df['Last Price'] < 50) & (df['Market Cap(Rs. cr)'] > 100)]
print(list(tradable['Company Name']))