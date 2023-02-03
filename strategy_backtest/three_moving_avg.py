# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 12:54:57 2020

@author: balaji
"""
#Backtesting a strategy using three moving averages on any indices such as 
#Nifty 50, SPY, HSI and so on.
import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def download_data(stock, start, end):
    data = yf.download(stock, start, end)
    return data

def generate_returns(stock):
    data['p_returns'] = data['Close'].pct_change()
    return data

def backtesting_strategy(df, sma, mma, lma, print_chart):
    data = df.copy()
    
    data['sma'] = data['Close'].rolling(window=sma).mean()
    data['mma'] = data['Close'].rolling(window=mma).mean()
    data['lma'] = data['Close'].rolling(window=lma).mean()
    
    ## Generating long entry signals
    data['signal'] = np.where((data['Close'] > data['sma']) & 
        (data['Close'] > data['mma']) & 
        (data['Close'] > data['lma']),1,0)
    
    ## Generating long exit signals
    data['signal'] = np.where((data['Close'] < data['sma']) & 
        (data['Close'] > data['lma']),0,data['signal'])
    
    ## Generating short entry signals
    data['signal'] = np.where((data['Close'] < data['sma']) & 
        (data['Close'] < data['mma']) & 
        (data['Close'] < data['lma']),-1, data['signal'])
    
    ## Generating short exit signals
    data['signal'] = np.where((data['Close'] > data['sma']) & 
        (data['Close'] < data['lma']),0, data['signal'])
    
    if print_chart == True:
        data[['signal','sma','lma','Close']].plot(figsize=(10,6), secondary_y='signal')
        
    data['strategy_returns'] = data['p_returns'] * data['signal'].shift(1)
    
    return data 

def calculate_returns(data):
    bnh = (data['p_returns'] + 1).cumprod()[-1]
    s_returns = (data['strategy_returns'] + 1).cumprod()[-1]
    return bnh, s_returns

data = download_data('^NSEI','2015-1-1','2020-10-20')
data = generate_returns(data)
data = backtesting_strategy(data,10,20,30,True)

bnh, s_returns = calculate_returns(data)
print('Buy and hold returns:', np.round(bnh,2))
print('Strategy returns:', np.round(s_returns,2))

for sma in range(30,40,5):
    for mma in range(60,75,5):
        for lma in range(100,115,5):
            print(f'\nChecking for SMA: {sma}, MMA: {mma}, LMA: {lma}')
            df = data.copy()
            df = data = generate_returns(df)
            df = backtesting_strategy(df, sma, mma, lma, False)
            bnh, s_returns = calculate_returns(df)
            print('Buy and Hold returns:', np.round(bnh,2))
            print('Strategy returns:',np.round(s_returns,2))
else:
    print('\nComputation Completed.')
