import websocket
import datetime
import csv
import sys
import json
kline_fieldnames = ['eventType','stream','eventTime','symbol','klineStartTime','klineClosetime','klineSymbol',
          'interval','firstTradeId','lastTradeId','openPrice','closePrice','highPrice','lowPrice',
          'baseAssetVolume','numberOfTrades','isKline','quoteAssetVolume','takerBuyBaseAssetVolume','takerBuyQuoteAssetVolume','ignore']
depth_fieldnames = ['eventType','stream','eventTime','transactionTime','bestBidPrice','bestAskPrice']

def on_message(ws, msg):
    try:
        print(str(datetime.datetime.now()) + ": ")
        print(msg)
        print(type(msg))
        try:
            # data = ws.recv()
            # if data != "":
            msg = json.loads(msg)
            # else:
            #     msg = {}
        except ValueError as e:
            print(e)
            print("{} - data: {}".format(e, msg))
        except Exception as e:
            print(e)
            print("{} - data: {}".format(e, msg))
        else:
            if "result" not in msg:
                print("result",msg)

                stream = msg['stream']
                eventType = msg['data']['e']
                if eventType == 'kline':
                    eventTime = msg['data']['E']
                    symbol = msg['data']['s']
                    klineStartTime = msg['data']['k']['t']
                    klineClosetime = msg['data']['k']['T']
                    klineSymbol = msg['data']['k']['s']
                    interval = msg['data']['k']['i']
                    firstTradeId = msg['data']['k']['f']
                    lastTradeId = msg['data']['k']['L']
                    openPrice = float(msg['data']['k']['o'])
                    closePrice = float(msg['data']['k']['c'])
                    highPrice = float(msg['data']['k']['h'])
                    lowPrice = float(msg['data']['k']['l'])
                    baseAssetVolume = float(msg['data']['k']['v'])
                    numberOfTrades = msg['data']['k']['n']
                    isKline = msg['data']['k']['x']
                    quoteAssetVolume = float(msg['data']['k']['q'])
                    takerBuyBaseAssetVolume = float(msg['data']['k']['V'])
                    takerBuyQuoteAssetVolume = float(msg['data']['k']['Q'])
                    ignore = msg['data']['k']['B']


                    kline_filename = symbol+'.csv'    
                    with open(kline_filename,'a',newline='') as f:
                        csv_writer = csv.DictWriter(f,fieldnames=kline_fieldnames)
                        info = {
                                'stream':stream,
                                'eventType': eventType ,
                                'eventTime': eventTime ,
                                'symbol': symbol ,
                                'klineStartTime': klineStartTime ,
                                'klineClosetime': klineClosetime ,
                                'klineSymbol': klineSymbol ,
                                'interval': interval ,
                                'firstTradeId': firstTradeId ,
                                'lastTradeId': lastTradeId ,
                                'openPrice': openPrice ,
                                'closePrice': closePrice ,
                                'highPrice': highPrice ,
                                'lowPrice': lowPrice ,
                                'baseAssetVolume': baseAssetVolume ,
                                'numberOfTrades': numberOfTrades ,
                                'isKline': isKline ,
                                'quoteAssetVolume': quoteAssetVolume ,
                                'takerBuyBaseAssetVolume': takerBuyBaseAssetVolume ,
                                'takerBuyQuoteAssetVolume': takerBuyQuoteAssetVolume ,
                                'ignore': ignore
                                }
                        if f.tell() == 0:
                            csv_writer.writeheader()
                        csv_writer.writerow(info)

                if eventType == 'depthUpdate':
                    stream = msg['stream']
                    eventType = msg['data']['e']
                    eventTime = msg['data']['E']
                    transactionTime = msg['data']['T']
                    bestBidPrice = msg['data']['b'][0][0]
                    bestAskPrice = msg['data']['a'][0][0]
                    depth_filename = stream+'.csv'
                    with open(depth_filename,'a',newline='') as f:
                        csv_writer = csv.DictWriter(f,fieldnames=depth_fieldnames)
                        info = {
                                'stream':stream,
                                'eventType':eventType,
                                'eventTime':eventTime,
                                'transactionTime':transactionTime,
                                'bestBidPrice':bestBidPrice,
                                'bestAskPrice':bestAskPrice}
                        if f.tell() == 0:
                            csv_writer.writeheader()
                        csv_writer.writerow(info)
    except Exception as err:
        print("ERROR type : ",type(err).__name__)
        print("Look:",type(err))
       


    

def on_error(ws, error):
    print(error)

def on_close(ws,close_msg):
    print("### closed ###", close_msg)

def stream():
    # global ws
    websocket.enableTrace(False)
    # socket = f'wss://stream.binance.com:9443/ws/{currency}@kline_{interval}'
    socket = "wss://fstream.binance.com/stream?streams=btcusdt@depth5/ethusdt@depth5/btcusdt@kline_1m/ethusdt@kline_1m"
    # socket = f'wss://stream.binance.com:9443/ws'
    ws = websocket.WebSocketApp(socket,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever()

stream()