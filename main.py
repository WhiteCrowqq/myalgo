
# root='wss://ws.kite.trade'
import kiteapp as kt
import pandas as pd
import numpy as np
import time
import talib
from time import sleep
with open('enctoken.txt', 'r') as rd:
    token = rd.read()
kite = kt.KiteApp("kite", "DQD407", token)
kws = kite.kws()  # For Websocket


print("Start..")
stock = {13442818: 'NIFTY2510223700CE' }
# print(list(stock.keys()))

ltp_data = {}


def on_ticks(ws, ticks):
    for symbol in ticks:
        ltp_data[stock[symbol['instrument_token']]] = {
            "ltp": symbol["last_price"], "High": symbol["ohlc"]["high"], "Low": symbol["ohlc"]["low"]}


def on_connect(ws, response):
    ws.subscribe(list(stock.keys()))
    # MODE_FULL , MODE_QUOTE MODE_LTP
    ws.set_mode(ws.MODE_QUOTE, list(stock.keys()))


kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.connect(threaded=True)
while len(ltp_data.keys()) != len(list(stock.keys())):
    sleep(0.5)
    continue


import pandas as pd
import time
import talib

# Initialize variables
vb = {}  # To store stock data
positions = {}  # To track buy positions for each stock
capital = 10000  # Initial capital for simplicity (you can modify this)

while True:
    for i in list(stock.values()):  # Replace `stock` with your actual stock list
        ltp = ltp_data[i]['ltp']  # Latest traded price
        high = ltp_data[i]['High']  # High price (not used here but part of data)

        # Check if the key exists in vb, if not initialize with an empty list
        if i not in vb:
            vb[i] = []

        # Append the new record to the list associated with the stock
        vb[i].append({
            "Stock": i,
            "LTP": ltp
        })

        # Flatten vb into a single list of records for DataFrame conversion
        flat_data = [record for records in vb.values() for record in records]
        vb_df = pd.DataFrame(flat_data)

        # Ensure LTP is numeric
        vb_df["LTP"] = pd.to_numeric(vb_df["LTP"], errors="coerce")

        # Calculate RSI using TA-Lib
        vb_df["RSI"] = talib.RSI(vb_df["LTP"], timeperiod=14)

        # Calculate Bollinger Bands
        upper_band, middle_band, lower_band = talib.BBANDS(
            vb_df["LTP"], 
            timeperiod=20, 
            nbdevup=2, 
            nbdevdn=2, 
            matype=0
        )
        vb_df["Upper Band"] = upper_band
        vb_df["Lower Band"] = lower_band
        print(vb_df)
        # Generate Buy/Sell Signals
        buy_signal = (vb_df["RSI"].iloc[-1] < 30) and (vb_df["LTP"].iloc[-1] <= vb_df["Lower Band"].iloc[-1])
        sell_signal = (vb_df["RSI"].iloc[-1] > 70) and (vb_df["LTP"].iloc[-1] >= vb_df["Upper Band"].iloc[-1])

        # Handle Buy Signal
        if buy_signal and i not in positions:
            positions[i] = ltp  # Record the buy price for the stock
            print(f"Buy Signal for {i}: Bought at ₹{ltp:.2f}, RSI={vb_df['RSI'].iloc[-1]:.2f}, Lower Band={vb_df['Lower Band'].iloc[-1]:.2f}")

        # Handle Sell Signal
        elif sell_signal and i in positions:
            buy_price = positions.pop(i)  # Get the buy price and remove the position
            profit_loss = ltp - buy_price  # Absolute gain/loss
            percentage_change = (profit_loss / buy_price) * 100  # Percentage gain/loss
            print(f"Sell Signal for {i}: Sold at ₹{ltp:.2f}, Profit/Loss: ₹{profit_loss:.2f} ({percentage_change:.2f}%)")
        
        time.sleep(2)  # Delay for next iteration




            
