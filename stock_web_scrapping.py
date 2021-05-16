import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from config import *
import time


url = "https://www.moneycontrol.com/stocks/marketinfo/marketcap/bse/index.html"
page = requests.get(url)
page_content = page.content
soup = BeautifulSoup(page.content, 'html.parser')

mydivs = soup.find('div', {"class": 'lftmenu'})
list_options = mydivs.findAll('li')
sector_list = []

for li in list_options:
    sector_list.append(li.string)

print(sector_list)

ltp_data = pd.DataFrame()


def scrap_moneycontrol_sectors_ltp():
    global ltp_data
    service = webdriver.chrome.service.Service('./chromedriver')
    service.start()
    options = webdriver.ChromeOptions()
    if HEADLESS_MODE:
        options.add_argument('--headless')
    options = options.to_capabilities()
    print("\t\tLaunching Chrome Driver")
    driver = webdriver.Remote(service.service_url, options)
    driver.set_window_position(BROWSER_X_POS, BROWSER_Y_POS)
    driver.set_window_size(BROWSER_X_SIZE, BROWSER_Y_SIZE)
    driver.get(url)
    driver.implicitly_wait(10)
    time.sleep(1)

    for sector in sector_list:
        try:
            print("Clicking on: {}".format(sector))
            element = driver.find_element_by_link_text(sector)
            driver.execute_script("arguments[0].scrollIntoView();", element)
            driver.find_element_by_link_text(sector).click()
            WebDriverWait(driver, 30)

            page_df = pd.read_html(driver.current_url)
            table_df = page_df[1]
            table_df["Company Name"] = table_df["Company Name"].apply(lambda x: x.split(" Add to Watchlist")[0])
            print(table_df)
            ltp_data = ltp_data.append(table_df)
            print("---------------------------------------------------------------------------------------------------")
            print(ltp_data)
            print("---------------------------------------------------------------------------------------------------")


        except Exception as e:
            print("Failed to retrieve:{}".format(sector))
            print("Exception:{}".format(e))

    driver.quit()


scrap_moneycontrol_sectors_ltp()
ltp_data.to_csv('money_control_ltp.csv')


print(ltp_data)
