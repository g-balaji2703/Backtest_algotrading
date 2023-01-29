# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 00:11:12 2021

@author: balaji
"""
import numpy as np
def ATR(data,time_period):
    df = data.copy()
    df['H-L'] = abs(df['High'] - df['Low'])
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L','H-PC','L-PC']].max(axis=1)
    df['ATR'] = np.zeros(len(df))
    df['ATR'].iloc[time_period-1] =df['TR'][0:time_period].mean()
    for i in range(time_period,len(df)):
        df['ATR'].iloc[i] = ((df['ATR'][i-1] * (time_period -1)) + df['TR'][i])/float(time_period)
    return df['ATR']
