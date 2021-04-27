import requests
from bs4 import BeautifulSoup

page = requests.get("https://www.moneycontrol.com/stocks/marketinfo/marketcap/bse/travel-services.html")
soup = BeautifulSoup(page.content, 'html.parser')

# print the entire html document in a pretty format
# print(soup.prettify())

print(soup.title.parent.name)
x = soup.find_all("table")
print(x)

table = soup.table
table_rows = soup.find_all('tr')
number_of_rows = len(table_rows)
first_row = table_rows[3]
cell_in_row = first_row.find_all("th")

for j, cell in enumerate(cell_in_row):
    print(j, list(enumerate(cell))[0][1])

table_cell = first_row.td
print(table_cell)
children = table.children


print("A")