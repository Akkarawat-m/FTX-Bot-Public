"""
#Akkarawat Mansap

#Credit1 : Nattapon Soomtha (กองทุนความมั่งคั่งแห่งชาติ Training)
#Credit2 : b2 spetsnaz club
#Credit3 : TEERACHAI RATTANABUNDITSAKUL

#----------------------------------------------------------------

# 1.Install library ที่เราจำเป็นจะต้องใช้ในการส่งคำสั่งและการตรวจเช็คออเดอร์
# - ccxt library ที่เป็นที่นิยมในการเชื่อม API กับ Exchange ต่างๆได้ง่ายขึ้นมาก
# - pandas library จะช่วยในการแปลงข้อมูลที่เราดึงมาจาก Exchange แปลงให้
#   เป็นตารางเพื่อให้ง่ายต่อการตรวจสอบออเดอร์
# - json จะใช้สำหรับการดึงข้อมูลที่เราต้องการมาจาก Exchange

#!pip install ccxt
#!pip install pandas

"""

# Config Session

import ccxt
import json
import pandas as pd
import time

# api and secret

apiKey = ''         #input("Enter API Key:")      
secret = ''         #input("Enter Secret Key:")
subaccount = ''                                      #input("Enter Sub Account Name or 0 for Main:")


# Exchange Detail
exchange = ccxt.ftx({
    'apiKey' : apiKey ,'secret' : secret ,'enableRateLimit': True
})

# Sub Account Check

if subaccount == "0":
  print("This is Main Account")
else:
  exchange.headers = {
   'FTX-SUBACCOUNT': subaccount,
  }

# Global Variable Setting
pair = 'BTC-PERP'
tf = '5m'

# Get Price Hist Data

def priceHistdata():
  
  try:
    priceData = pd.DataFrame(exchange.fetch_ohlcv(pair,tf))
  except ccxt.NetworkError as e:
    print(exchange.id, 'fetch_ohlcv failed due to a network error:', str(e))
    priceData = pd.DataFrame(exchange.fetch_ohlcv(pair,tf))
  except ccxt.ExchangeError as e:  
    print(exchange.id, 'fetch_ohlcv failed due to exchange error:', str(e))
    priceData = pd.DataFrame(exchange.fetch_ohlcv(pair,tf))
  except Exception as e:
    print(exchange.id, 'fetch_ohlcv failed with:', str(e))
    priceData = pd.DataFrame(exchange.fetch_ohlcv(pair,tf))

  return priceData
  
# Variable setting for minimum Range and minimum Profit
buyRecord = []
minimumRange = 10
minimumProfit = 30
minOrder = min(buyRecord, default=0.0)
maxOrder = max(buyRecord, default=100000000.0)
priceData = priceHistdata()
buySignal = round((priceData.iloc[-31:-1,4].mean())*2) / 2
sellSignal = round((priceData.iloc[-11:-1,4].mean())*2) / 2

def getPrice():

  try:
    r1 = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r1)
    #print(exchange)
    #print(pair + '=',dataPrice['last'])
  except ccxt.NetworkError as e:
    r1 = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r1)
  except ccxt.ExchangeError as e:
    r1 = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r1)
  except Exception as e:
    r1 = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r1)
  
  return (dataPrice['last'])

def showPending():
    print("Your Pending Order")
    pendingOrder = pd.DataFrame(exchange.fetch_open_orders(pair),
                   columns=['id','datetime','status','symbol','type','side','price','amount','filled','average','remaining'])
    pendingOrder.head(5)
    return pendingOrder

def showMatched():
    print("Your Matched Order")
    matchedOrder = pd.DataFrame(exchange.fetchMyTrades(pair),
                       columns=['id','datetime', 'symbol','type','side','price','amount','cost'])
    print(matchedOrder.head(5))
    return matchedOrder

def sendBuy():
  types = 'limit'                         # ประเภทของคำสั่ง
  side = 'buy'                            # กำหนดฝั่ง BUY/SELL
  usd = 1                                 # กรณี Rebalance และต้องกรอกเป็น USD
  price = buySignal + 20                  # ระดับราคาที่ต้องการ
  size_order = usd/price                  # ใส่ขนาดเป็น BTC, ถ้า Rebalance ให้ใส่เป็น usd/price # แล้วไปกรอกในตัวแปร usd แทน
  reduceOnly = False                      # ปิดโพซิชั่นเท่าจำนวนที่มีเท่านั้น (CREDIT : TY)
  postOnly =  False                       # วางโพซิชั่นเป็น MAKER เท่านั้น
  ioc = False                             # immidate or cancel เช่น ส่งคำสั่งไป Long 1000 market 
                                          # ถ้าไม่ได้ 1000 ก็ไม่เอา เช่นอาจจะเป็น 500 สองตัวก็ไม่เอา
  ## Send Order ##
  exchange.create_order(pair, types , side, size_order, price)

  ## Show Order Status##
  print("     ")
  showPending()
  print("     ")
  showMatched()

def sendSell():
  types = 'limit'                         # ประเภทของคำสั่ง
  side = 'sell'                           # กำหนดฝั่ง BUY/SELL
  usd = 1                                 # กรณี Rebalance และต้องกรอกเป็น USD
  price = sellSignal - 20                 # ระดับราคาที่ต้องการ
  size_order = usd/price                  # ใส่ขนาดเป็น BTC, ถ้า Rebalance ให้ใส่เป็น usd/price # แล้วไปกรอกในตัวแปร usd แทน
  reduceOnly = True                       # ปิดโพซิชั่นเท่าจำนวนที่มีเท่านั้น (CREDIT : TY)
  postOnly =  False                       # วางโพซิชั่นเป็น MAKER เท่านั้น
  ioc = False                             # immidate or cancel เช่น ส่งคำสั่งไป Long 1000 market 

  ## Send Order ##
  exchange.create_order(pair, types , side, size_order, price)

  ## Show Order Status##
  print("     ")
  showPending()
  print("     ")
  showMatched()

def readOrder():
  #Read Order To file
  with open("list.txt", "r") as f:
    for line in f:
      buyRecord.append(float(line.strip()))
  print(buyRecord)

def writeOrder():
  with open("list.txt", "w") as f:      #Write Order To file 
    for ord in buyRecord:
      f.write(str(ord) +"\n")

# LOGIC SESSION

def checkBuycondition():

  # Buy Condition
  if getPrice() == buySignal and len(buyRecord) <= 30 and buyRecord.count(buySignal) < 1:
    if (minOrder - getPrice()) > minimumRange or (getPrice() - maxOrder) > 10 or len(buyRecord) < 1 :
      sendBuy()
      print('Buy 1 USD at' + str(buySignal))
      buyRecord.append(buySignal)
      writeOrder()

    else:
      print('Not enough minimum Range = ' + str(minimumRange))
  else:
    print(getPrice())
    print('waiting for buy signal ' + 'at ' + str(buySignal))


def checkSellcondition():

  # Sell Signal function
  if len(buyRecord) > 0:
    if getPrice() <= sellSignal :
      print('sell signal triggered at ' + str(sellSignal)) 
      for ord in buyRecord:
        if getPrice() - ord > minimumProfit:
          sendSell()
          buyRecord.remove(ord)
          print(buyRecord)
          writeOrder()
        else:
          print('Not Enough Profit ' + 'Minimum = ' + str(ord + minimumProfit))
          
    else:
      print('Waiting for sell signal ' + 'at ' + str(sellSignal))
  else: print('No Buy Order Record')
  print("  ")



# Execute Session

while True:
  buyRecord = []
  print(time.ctime())
  readOrder()
  getPrice()
  checkBuycondition()
  checkSellcondition()
  time.sleep(1)

  