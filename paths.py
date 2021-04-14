import os

credentials_path = os.environ["HOMEPATH"] + "\\Desktop" + "\\cred impt" + "\\zrdh_lgn_cred"
account_details_path = os.environ["HOMEPATH"] + "\\Desktop" + "\\cred impt" + "\\zrdh_acc_details"

auth_details_path = credentials_path + "\\auth_details.txt"
request_token_path = credentials_path + "\\request_token.txt"
access_token_path = credentials_path + "\\access_token.txt"

holdings_details_path = account_details_path + "\\holdings.txt"
orders_details_path = account_details_path + "\\orders.txt"