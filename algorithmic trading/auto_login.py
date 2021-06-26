# -*- coding: utf-8 -*-
"""
Trading Robot - Zerodha Kite Connect Platform

@developer: Karthik Ramx (https://karthikramx.wordpress.com/)
"""

from kiteconnect import KiteConnect
from selenium import webdriver
from config import *
from paths import *
import time


def autologin():
    key_secret = open(auth_details_path, 'r').read().split()
    kite = KiteConnect(api_key=key_secret[0])
    print("Kite Object created")

    service = webdriver.chrome.service.Service('./chromedriver')
    service.start()
    options = webdriver.ChromeOptions()
    if HEADLESS_MODE:
        options.add_argument('--headless')
    print("Launching Chrome Driver")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Remote(service.service_url, options=options)

    driver.set_window_position(BROWSER_X_POS, BROWSER_Y_POS)
    driver.set_window_size(BROWSER_X_SIZE, BROWSER_Y_SIZE)
    driver.get(kite.login_url())
    driver.implicitly_wait(10)
    print("Entering credentials. Please wait.")
    username = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[1]/input')
    password = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input')
    username.send_keys(key_secret[2])
    password.send_keys(key_secret[3])
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button').click()
    pin = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/div/input')
    print("Entering PIN. Please wait.")
    pin.send_keys(key_secret[4])
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[3]/button').click()
    time.sleep(4)
    print("CURRENT URL: {}".format(driver.current_url))

    url_split = driver.current_url.split('=')
    request_token = max(url_split, key=len)
    request_token = request_token.split('&action')[0]
    print("REQUEST TOKEN: {}, len:{}".format(request_token, len(request_token)))

    driver.quit()

    if request_token == "login&status":
        print("FAILED TO ACCESS REQUEST TOKEN... TRYING AGAIN")
        autologin()

    with open(request_token_path, 'w') as the_file:
        the_file.write(request_token)
    print("REQUEST TOKEN: {} SAVED".format(request_token))


def generate_access_token():
    request_token = open(request_token_path, 'r').read()
    key_secret = open(auth_details_path, 'r').read().split()
    kite = KiteConnect(api_key=key_secret[0])
    data = kite.generate_session(request_token, api_secret=key_secret[1])
    print("ACCESS  TOKEN: {}".format(data["access_token"]))
    with open(access_token_path, 'w') as file:
        file.write(data["access_token"])
        print("ACCESS  TOKEN: {} SAVED".format(data["access_token"]))
