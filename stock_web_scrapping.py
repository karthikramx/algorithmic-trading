import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.moneycontrol.com/stocks/marketinfo/marketcap/bse/travel-services.html"
page = requests.get(url)
page_content = page.content

soup = BeautifulSoup(page.content, 'html.parser')
mydivs = soup.find('div', {"class": 'lftmenu'})
list_options = mydivs.findAll('li')

sector_list = []

for li in list_options:
    sector_list.append(li.string)


print(soup.prettify())
all_li = soup.find_all('ul')


table_rows = soup.find_all('tr')

page_df = pd.read_html(url)
table_df = page_df[1]
table_df["Company Name"] = table_df["Company Name"].apply(lambda x: x.split(" Add to Watchlist")[0])
print(table_df)
