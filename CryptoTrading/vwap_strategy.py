import pandas_ta as ta
import pandas as pd
import threading
import datetime
import time
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException,BinanceOrderException
import csv

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

def cal_vwap(data):
    df_vwap = ta.vwap(high=data['highPrice'], low=data['lowPrice'], close=data['closePrice'], volume=data['baseAssetVolume'])
    return df_vwap

def vwap_strategy(symbol,crypto_filename,depth_filename):
    position = 0
    entry_price = 0
    exit_price = 0
    PL = 0
    per_return = 0
    cancel_order = None
    trade_log_fieldname = ['eventTime','symbol','interval',
                                  'openPrice','closePrice','highPrice','lowPrice',
                                  'entry_price','orderId']   
    while True:
        dt = datetime.datetime.now()
        data = read_data(crypto_filename)
        depth = read_data(depth_filename)
        data['vwap'] = cal_vwap(data)
        closePrice = data['closePrice'][-1]
        eventTime = data.index[-1]
        isKline = bool(data['isKline'][-1])
        symbol = data['symbol'][-1]
        interval = data['interval'][-1]
        openPrice = data['openPrice'][-1]
        highPrice = data['highPrice'][-1]
        lowPrice = data['lowPrice'][-1]
        closePrice = data['closePrice'][-1]
        vwap = data['vwap'][-1]
        bestAsk = depth['bestAskPrice'][-1]
        bestBid = depth['bestBidPrice'][-1]
        print(f"{dt} | {eventTime} |Crypto : {symbol} |kline: {isKline} |close: {closePrice} |vwap: {vwap} |Ask: {bestAsk} |Bid: {bestBid}")
            
        if isKline:
            print("\n")
            print(f"No trade : {dt} | {eventTime} |Crypto : {symbol} |kline: {isKline} |close: {closePrice} |vwap: {vwap} |Ask: {bestAsk} |Bid: {bestBid}")
            #sell order
            if closePrice > vwap:
                entryPrice = bestAsk
                #comment out if want to go live 
                # try:
                #     entry_order = client.create_test_order(symbol=symbol, side='SELL', type='MARKET', quantity=1)
                # except BinanceAPIException as e:
                #     # error handling goes here
                #     print(e)
                # except BinanceOrderException as e:
                #     # error handling goes here
                #     print(e)
                print(f"Long : {dt} | {eventTime} |Crypto : {symbol} | entryPrice: {entryPrice}")
                time.sleep(2)
                # try:
                #     cancel_order = client.cancel_order(symbol=symbol, orderId=entry_order['orderId'])
                # except BinanceAPIException as e:
                #     # error handling goes here
                #     print(e)
                # except BinanceOrderException as e:
                #     # error handling goes here
                #     print(e)
                
            
            #buy order
            if closePrice < vwap:
                entryPrice = bestBid
                # try:
                #     entry_order = client.create_test_order(symbol=symbol, side='BUY', type='MARKET', quantity=1)
                # except BinanceAPIException as e:
                #     # error handling goes here
                #     print(e)
                # except BinanceOrderException as e:
                #     # error handling goes here
                #     print(e)
                print(f"short : {dt} | {eventTime} |Crypto : {symbol} | entryPrice: {entryPrice}")
                time.sleep(2)
                # try:
                #     cancel_order = client.cancel_order(symbol=symbol, orderId=entry_order['orderId'])
                # except BinanceAPIException as e:
                #     # error handling goes here
                #     print(e)
                # except BinanceOrderException as e:
                #     # error handling goes here
                #     print(e)
                
            
            with open(symbol+"_trade_log.csv",'a',newline='') as f:
                csv_writer = csv.DictWriter(f,fieldnames=trade_log_fieldname)
                info = {
                        'eventTime': eventTime ,
                        'symbol': symbol ,
                        'interval': interval,
                        'openPrice': openPrice ,
                        'closePrice': closePrice ,
                        'highPrice': highPrice ,
                        'lowPrice': lowPrice ,
                        'entry_price':entry_price,
                        'orderId':entryPrice
                        }
                if f.tell() == 0:
                    csv_writer.writeheader()
                csv_writer.writerow(info)
        time.sleep(1)

btc_thread = threading.Thread(target=vwap_strategy,name='btc_trade',args=('BTCUSDT','BTCUSDT.csv','btcusdt@depth5.csv',))
eth_thread = threading.Thread(target=vwap_strategy,name='eth_trade',args=('ETHUSDT','ETHUSDT.csv','ethusdt@depth5.csv',))
btc_thread.start()
eth_thread.start()
btc_thread.join()
eth_thread.join()