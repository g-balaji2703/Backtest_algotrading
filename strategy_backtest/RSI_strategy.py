# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 17:30:03 2020

@author: balaji
"""

## Problem 3
## Strategy based on RSI indicator

import pandas as pd
import numpy as np
import pandas_datareader as pdr
import datetime
import matplotlib.pyplot as plt
import talib

start = datetime.datetime(2015,1,1)
end = datetime.datetime(2020,10,20)

df1 = pdr.get_data_yahoo('SPY',start,end)

#Making a copy to work with
#SPY = df1.copy()

#Data cleaning, dropping unnecessary columns
df1.drop(['High','Low','Open','Adj Close','Volume'],axis=1,inplace=True)

#Calculating RSI using talib
df1['RSI'] = talib.RSI(df1['Close'])

#Dropping NaN values and resetting the index (this will help in data manipulation)
df1.dropna(inplace=True,axis=0)
df1 = df1.reset_index()

df1.head()

## Defining a function for backtesting, based on the conditions mentioned in the question statement
def backtesting_RSI(df, TP_level, SL_level):
    # Initializing two new columns
    df['Entry_price'] = 0
    df['RSI_signal'] = 0
    #defining a few variables to generate signals using a for loop
    n = df.shape[0]
    cash=1
    stock=0
     
     # the for loop to create signals based on RSI only
    for i in range(0,n):
        if df['RSI'].loc[i] <= 30 and cash == 1:
            df['RSI_signal'].loc[i]=1
            df['entry_price'].loc[i]=df['Close'].loc[i]
            cash=0
            stock=1
             
        if stock == 1 and df['RSI'].loc[i] >= 70:
            df['RSI_signal'].loc[i] = -1
            cash = 1
            stock = 0
            
    # creating columns for take profit and stoploss price, based on the trade entry price
    df['take_proft_price'] = df['entry_price']*(1+TP_level)
    df['stop_loss_price'] = df['entry_price']*(1-SL_level)
    
    df['take_price_price'] = df['take_profit_price'].replace(to_replace=0, method='ffill')
    df['stop_loss_price'] = df['stop_loss_price'].replace(to_replace=0, method='ffill')
    
    #Updating the signal taking into account TP and SL
    for i in range(0,n):
        # if in a position based on previous conditions and if Close TP or SL, make the signal -1
        if df['Close'].loc[i] < df['stop_loss_price'].loc[i] or df['Close'].loc[i] > df['take_profit_price'].loc[i]:
            df['RSI_signal'].loc[i] = -1
            
    # forward filling the signals so that we can get the position column from it later
    df['RSI_signal'] = df['RSI_signal'].replace(to_replace=0, method='ffill')
    
    #For position column, replacing -1 with 0, as this is a long only strategy
    df['position'] = df['RSI_signal'].replace(to_replace=-1,value=0)
    
    #Visualizing the strategy with posotion overlaid on RSI
    y = df['RSI'].plot(figsize=(30,10))
    l1 = np.array([30 for i in range(n)])
    l2 = np.array([70 for i in range(n)])
    plt.plot(l1)
    plt.plot(l2)
    df['position'].plot(ax=y, secondary_y='position')
    plt.title('Visualizing the strategy with position overlaid on RSI')
    plt.show()
    
    # calculating and plotting strategy returns
    df['daily_log_returns'] = np.log(df['Close']/df['Close'].shift())
    df['strategy_returns'] = df['daily_log_returns'] * df['position'].shift()
    df['cumulative_strategy_returns'] = np.cumsum(df['strategy_returns'])
    print('total return from this strategy: ',df['strategy_returns'].sum())
    df['cumulative_strategy_returns'].plot()
    plt.title('Cumulative returns for this strategy')
    plt.show()
    
    return df

backtesting_RSI(df1, TP_level=0.05, SL_level=0.02)