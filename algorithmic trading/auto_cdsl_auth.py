import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import datetime as dt
from paths import *
from config import *
import time


# automate browser to login into kite
# navigate to holdings
# click authorization
# Click on continue on pop-up
# Click on continue-to-CDSL on pop-up
# Submit tpin
# check for otp on email from edis@cdslindia.co.in
# extract 6 digit otp | https://www.geeksforgeeks.org/python-fetch-your-gmail-emails-from-a-particular-user/
# enter otp to authorize selling shares
# confirm authorization
# exit browser


class auto_authorize_cdsl:
    def __init__(self):
        handles = None
        print("Auto CDSL authorization initialized at: {}".format(dt.datetime.now()))
        key_secret = open(auth_details_path, 'r').read().split()
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
        driver.get("https://kite.zerodha.com/")
        driver.implicitly_wait(10)


        username = driver.find_element_by_id("userid")
        password = driver.find_element_by_id("password")
        username.send_keys(key_secret[2])
        password.send_keys(key_secret[3])
        driver.find_element_by_class_name("button-orange.wide").click()
        pin = driver.find_element_by_id("pin")
        pin.send_keys(key_secret[4])
        driver.find_element_by_class_name("button-orange.wide").click()
        driver.find_element_by_class_name("icon.icon-briefcase").click()
        driver.find_element_by_class_name("icon.icon-lock").click()
        driver.find_element_by_class_name("button.button-blue").click()

        time.sleep(0.5)
        pop_up = driver.window_handles[1]
        driver.switch_to.window(pop_up)
        driver.find_element_by_class_name("button.button-blue").click()
        time.sleep(0.5)
        actions = ActionChains(driver)
        actions.send_keys('******')
        actions.perform()
        all_elements = driver.find_elements_by_tag_name("button")
        actions.click(all_elements[0])
        actions.perform()
        print("x")
        time.sleep(5)
        driver.quit()


aac = auto_authorize_cdsl()
