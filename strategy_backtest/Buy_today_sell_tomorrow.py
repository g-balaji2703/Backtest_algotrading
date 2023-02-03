# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 14:47:29 2020

@author: balaji
"""

## Problem-2
#Buy and sell the next day

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt

df = yf.download('^NSEI', start='2015-1-1', end='2020-10-20')

data = df.copy()

# create open to open returns
data['oo_returns'] = np.log(data['Open'] / data['Open'].shift(1))

#create close to close returns
data['cc_returns'] = np.log(data['Close'] / data['Close'].shift(1))

# Generating trading signals
# Day 1 = Down day
# Day 2 = Down day
# Day 3 = Down day
# Day 4 = Buy at open
data['signals'] = np.where((data['cc_returns'].shift(1) < 0) & 
    (data['cc_returns'].shift(2) < 0) & 
    (data['cc_returns'].shift(3) < 0), 1, 0)

# To give the effect of buying on the next day open
data['signals'] = data['signals'].shift(1)

# Compute strategy returns
data['strategy_return'] = data['signals'].shift(1) * data['oo_returns']

# Print returns
print('Buy and hold returns: ', np.round(data['cc_returns'].cumsum()[-1], 2))
print('Strategy returns: ',np.round(data['strategy_return'].cumsum()[-1], 2))

# Plotting 
bnh = data['cc_returns'].cumsum()
s_returns = data['strategy_return'].cumsum()

plt.figure(figsize=(10,6))
plt.plot(bnh)
plt.plot(s_returns)
plt.ylabel('Cumulative Returns')
plt.xlabel('Date')
plt.title('Returns comparison')
#plt.legend()
plt.show()
