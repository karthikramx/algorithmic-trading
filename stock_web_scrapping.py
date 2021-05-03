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
    # x=li.find('a')
    # href = x.attrs
    # link = href["href"]
    # print(type(li))
    sector_list.append(li.string)

print(sector_list)


def scrap_moneycontrol_sectors_ltp():
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
            time.sleep(2)
            driver.find_element_by_link_text(sector).click()

            #Driver.findElement(By.xpath( // a[ @ href = '/docs/configuration']")).click();

            time.sleep(2)
            WebDriverWait(driver, 30)

        except Exception as e:
            print("Failed to retrieve:{}".format(sector))
            print("Exception:{}".format(e))

    """
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button').click()

    pin = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/div/input')
    print("\t\tEntering PIN. Please wait.")
    pin.send_keys(key_secret[4])
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[3]/button').click()
    time.sleep(4)
    print("\t\tCURRENT URL: {}".format(driver.current_url))

    request_token = driver.current_url.split('=')[1].split('&action')[0]  # fails the string operation sometimes
    print("\t\tREQUEST TOKEN: {}".format(request_token))

    driver.quit()

    with open(request_token_path, 'w') as the_file:
        the_file.write(request_token)
    print("\t\tREQUEST TOKEN: {} SAVED".format(request_token))
    """
    driver.quit()


scrap_moneycontrol_sectors_ltp()


page_df = pd.read_html(url)
table_df = page_df[1]
table_df["Company Name"] = table_df["Company Name"].apply(lambda x: x.split(" Add to Watchlist")[0])
print(table_df)
