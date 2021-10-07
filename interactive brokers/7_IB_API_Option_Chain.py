# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 16:12:01 2020

@author: Jay Parmar

@doc: https://interactivebrokers.github.io/tws-api/basic_contracts.html

@goal: Fetch options chain 

@output_details: https://interactivebrokers.github.io/tws-api/classIBApi_1_1ContractDetails.html
"""

# Import necessary libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Thread
import time

class strategy(EClient, EWrapper):
    
    def __init__(self):
        EClient.__init__(self, self)
        
    def contractDetails(self, reqId, contractDetails):
        cont = contractDetails.contract
        symbol = cont.symbol
        strike = cont.strike
        right = cont.right
        multiplier = cont.multiplier
        exp_date = contractDetails.realExpirationDate
        exchange = cont.exchange
        
        print(symbol, strike, right, multiplier, exp_date, exchange)
        # print('\nReqId: ', reqId, '\nContract Details: ', contractDetails )
        
    def contractDetailsEnd(self, reqId):
        print('\nReqId: ', reqId, 'Contract Details Ended.')
        
# -------------------------x-----------------------x---------------------------

# Create object of the strategy class
app = strategy()

# Connect strategy to IB TWS
app.connect(host='127.0.0.1', port=7496, clientId=1)

# Wait for sometime to connect to the server
time.sleep(1)

# Start a separate thread that will receive all responses from the TWS
Thread(target=app.run, daemon=True).start()

print('Is application connected to IB TWS:', app.isConnected())

# Create object for contract
eurusd_contract = Contract()

contract = Contract()
contract.symbol = "MSFT"
contract.secType = "OPT"
contract.currency = "USD"
contract.exchange = "SMART"
# contract.strike = 250
contract.lastTradeDateOrContractMonth = '202106'
# contract.right = 'P'

# Request contract details
app.reqContractDetails(reqId=38, contract=contract)

# Sleep for few seconds
time.sleep(15)

# Disconnect the strategy
app.disconnect()