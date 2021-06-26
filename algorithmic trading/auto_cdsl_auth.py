import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import datetime as dt
from config import *
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
import os.path
from paths import *
import sys


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
        tpin = open(cdsl_tpin_path, 'r').read().split()[0]
        self.service = None
        self.auth_gmail()
        self.delete_edis_email()
        self.auto_auth(tpin)
        self.delete_edis_email()


    def auto_auth(self, tpin):
        key_secret = open(auth_details_path, 'r').read().split()
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

        # Working on the POP window from CDSL
        pop_up = driver.window_handles[1]
        driver.switch_to.window(pop_up)
        driver.find_element_by_class_name("button.button-blue").click()
        time.sleep(0.5)
        actions = ActionChains(driver)
        actions.send_keys(tpin)
        actions.perform()
        all_elements = driver.find_elements_by_tag_name("button")
        actions.click(all_elements[0])
        actions.perform()

        # Waiting for GMAIL API to receive OTP
        OTP = self.get_OTP()
        print("\nReceived OTP:{}".format(OTP))

        # entering OTP for CDSL authorization
        pop_up = driver.window_handles[1]
        driver.switch_to.window(pop_up)
        actions = ActionChains(driver)

        actions.send_keys(OTP)
        actions.perform()
        all_elements = driver.find_elements_by_tag_name("button")
        actions.click(all_elements[0])
        actions.perform()
        time.sleep(2)
        driver.quit()
        print("CDSL AUTO AUTHORIZATION COMPLETE")

    def auth_gmail(self):
        # Variable creds will store the user access token.
        # If no valid token found, we will create one.
        creds = None
        OTP = None
        SCOPES = ['https://mail.google.com/']

        # The file token.pickle contains the user access token.
        # Check if it exists
        if os.path.exists(gmail_token_path):
            # Read the token from the file and store it in the variable creds
            with open(gmail_token_path, 'rb') as token:
                creds = pickle.load(token)

        # If credentials are not available or are invalid, ask the user to log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(gmail_credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the access token in token.pickle file for the next run
            with open(gmail_token_path, 'wb') as token:
                pickle.dump(creds, token)

        # Connect to the Gmail API
        self.service = build('gmail', 'v1', credentials=creds)

    def get_OTP(self):
        messages = None
        # We can also pass maxResults to get any number of emails. Like this:
        while messages is None:
            result = self.service.users().messages().list(maxResults=5, userId='me', q="edis@cdslindia.co.in").execute()
            messages = result.get('messages')
            time.sleep(1)
            self.print_OTP_wait_msg()

        # iterate through all the messages
        for msg in messages:
            # Get the message from its id
            txt = self.service.users().messages().get(userId='me', id=msg['id']).execute()
            ad = txt.get('snippet')
            OTP = [x for x in ad.split(' ') if len(x) == 6 and x.isdigit()][0]
            print(OTP)

        return OTP

    def delete_edis_email(self):

        messages = None
        result = None

        result = self.service.users().messages().list(maxResults=5, userId='me', q="edis@cdslindia.co.in").execute()
        messages = result.get('messages')

        if messages is None:
            print("NO EMAILS FROM edis@cdslindia.co.in FOUND")
            return

        print("\nResult:{}".format(result))

        for msg in messages:
            # delete the message from its id
            self.service.users().messages().delete(userId="me", id=msg['id']).execute()

        print("DELETED PREVIOUS EMAIL(S) from: edis@cdslindia.co.in with ID:")

    def print_OTP_wait_msg(self):
        sys.stdout.write('\r' + "Waiting for OTP.")
        time.sleep(0.25)
        sys.stdout.write('\r' + "Waiting for OTP..")
        time.sleep(0.25)
        sys.stdout.write('\r' + "Waiting for OTP...")
        time.sleep(0.25)
        sys.stdout.write('\r' + "Waiting for OTP....")
        time.sleep(0.25)


