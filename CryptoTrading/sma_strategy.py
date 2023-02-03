import json
import pandas as pd
import datetime
import time
import csv
from binance.client import Client
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('api_key')
api_secret = os.getenv('api_secret')
client = Client(api_key, api_secret)
api_url = os.getenv('api_url')
client.API_URL = api_url


btc_filename = 'BTCUSDT.csv'
btc_depth_filename = 'btcusdt@depth5.csv'
eth_filename = 'ETHUSDT.csv'
eth_filename = 'ethusdt@depth5.csv'

def read_data(filename):
    data = pd.read_csv(filename)
    data.set_index('eventTime',inplace=True)
    data.index = pd.to_datetime(data.index,unit='ms')
    return data


position = 0
entry_price = 0
exit_price = 0
PL = 0
per_return = 0
while True:
    dt = datetime.datetime.now()
    data = read_data(btc_filename)
    data['sma_23'] = data['closePrice'].rolling(23).mean()
    data['sma_52'] = data['closePrice'].rolling(52).mean()
    eventTime = data.index[-1]
    isKline = bool(data['isKline'][-1])
    symbol = data['symbol'][-1]
    interval = data['interval'][-1]
    openPrice = data['openPrice'][-1]
    highPrice = data['highPrice'][-1]
    lowPrice = data['lowPrice'][-1]
    closePrice = data['closePrice'][-1]
    sma_23 = round(data['sma_23'][-1],2)
    prev_sma_23 = round(data['sma_23'][-2],2)
    sma_52 = round(data['sma_52'][-1],2)
    prev_sma_52 = round(data['sma_52'][-2],2) 
    print(f"{dt} | {eventTime} | {isKline} | {closePrice} | {sma_23} | {prev_sma_23} | {sma_52} | {prev_sma_52}")
    if isKline:
       
        if position == 0:
            print(f"No trade : {dt} | {eventTime} | {isKline} | {closePrice} | {sma_23} | {prev_sma_23} | {sma_52} | {prev_sma_52}")
            if (sma_23 > sma_52) and (prev_sma_23 < prev_sma_52):
                
                position = 1
                entry_price = closePrice
                buy_order = client.create_test_order(symbol='BTCUSDT', side='BUY', type='MARKET', quantity=1)
                print(f"Enter long | {eventTime} | {symbol} | {entry_price}")
            
            if (sma_23 < sma_52) and (prev_sma_23 > prev_sma_52):
                position = -1
                entry_price = closePrice
                buy_order = client.create_test_order(symbol='BTCUSDT', side='SELL', type='MARKET', quantity=1)
                print(f"Enter short | {eventTime} | {symbol} | {entry_price}")
        
        if position == 1:
            carry_price = closePrice
            print(f"carry | {eventTime} | {symbol} | {carry_price}")
            if (sma_23 <= sma_52) and (prev_sma_23 >= prev_sma_52):
                buy_order = client.create_test_order(symbol='BTCUSDT', side='SELL', type='MARKET', quantity=1)
                exit_price = closePrice
                PL = exit_price - entry_price
                per_return = (PL/entry_price)*100
                position = 0
                print(f"EXIT long | {eventTime} | {symbol} | {exit_price}")

        
        if position == -1:
            carry_price = closePrice
            if (sma_23 >= sma_52) and (prev_sma_23 <= prev_sma_52):
                buy_order = client.create_test_order(symbol='BTCUSDT', side='BUY', type='MARKET', quantity=1)
                exit_price = closePrice
                PL = entry_price - exit_price
                per_return = (PL/entry_price)*100
                position = 0
                print(f"EXIT short | {eventTime} | {symbol} | {exit_price}")
                
                
        trade_log_fieldname = ['eventTime','symbol',
                              'interval','openPrice','closePrice','highPrice','lowPrice',
                              'position','entry_price','carry_price','exit_price','PL','per_return']
        with open("BTCUSDT_trade_log.csv",'a',newline='') as f:
            csv_writer = csv.DictWriter(f,fieldnames=trade_log_fieldname)
            info = {
                    'eventTime': eventTime ,
                    'symbol': symbol ,
                    'interval': interval,
                    'openPrice': openPrice ,
                    'closePrice': closePrice ,
                    'highPrice': highPrice ,
                    'lowPrice': lowPrice ,
                    'position':position,
                    'entry_price':entry_price,
                    'exit_price':exit_price,
                    'PL':PL,
                    'per_return':per_return
                    }
            if f.tell() == 0:
                csv_writer.writeheader()
            csv_writer.writerow(info)
        if position == 0:
            per_return = 0
            entry_price = 0
            exit_price = 0
            carry_price = 0
    time.sleep(1)