# -*- coding: utf-8 -*-
"""
Created on Mon May 25 16:52:32 2020

Modified on Fri Jun 18 16:44:59 2021

@author: Jay Parmar

@doc: http://interactivebrokers.github.io/tws-api/connection.html

@goal: Connect Python script to TWS
"""

# Import necessary libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from threading import Thread
from datetime import datetime
import time

# Define strategy class - inherits from EClient and EWrapper
class Strategy(EClient, EWrapper):
    
    # Initialize the class - and inherited classes
    def __init__(self):
        EClient.__init__(self, self)
        
    # This Callback method is available from the EWrapper class
    def currentTime(self, time): # Method to handle response
        t = datetime.fromtimestamp(time)
        print('Current time on server:', t)
        
# -------------------------x-----------------------x---------------------------

# Create object of the strategy class
app = Strategy()

# Connect strategy to IB TWS
app.connect(host='127.0.0.1', port=7496, clientId=1)

# Wait for sometime to connect to the server
time.sleep(1)

# Start a separate thread that will receive all responses from the TWS
Thread(target=app.run, daemon=True).start()

print('\nIs application connected to IB TWS:', app.isConnected())

# This method comes from EClient class
# Example of sending a request to TWS
app.reqCurrentTime() # Requesting

time.sleep(5)

print('\nDisconnecting from application')

# Disconnect the app
app.disconnect()


