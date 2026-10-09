import yfinance as yf
import pandas as pd
import os

if not os.path.exists("data"):
    os.makedirs("data")

tickers=["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","HINDUNILVR.NS","ITC.NS",
        "SBIN.NS","LT.NS","BHARTIARTL.NS","AXISBANK.NS","KOTAKBANK.NS","ASIANPAINT.NS","BAJFINANCE.NS",
        "BAJAJFINSV.NS","MARUTI.NS","M&M.NS","BAJAJHLDNG.NS","TATASTEEL.NS","SUNPHARMA.NS",
        "ULTRACEMCO.NS","NESTLEIND.NS","POWERGRID.NS","NTPC.NS","ONGC.NS","COALINDIA.NS","ADANIPORTS.NS",
        "ADANIENT.NS","WIPRO.NS","TECHM.NS","HCLTECH.NS","CIPLA.NS","DRREDDY.NS",
        "EICHERMOT.NS","HEROMOTOCO.NS","INDUSINDBK.NS","BAJAJ-AUTO.NS","SHRIRAMFIN.NS","BEL.NS",
        "TRENT.NS","TITAN.NS","JSWSTEEL.NS","GRASIM.NS","HINDALCO.NS","BRITANNIA.NS","APOLLOHOSP.NS",
        "TATACONSUM.NS","SBILIFE.NS","HDFCLIFE.NS","ETERNAL.NS"]



for ticker in tickers:
    data=yf.download(ticker,start="2020-01-01",end="2026-01-01")
    if not data.empty:
      filename=f"data/{ticker}_data.csv"
      data.to_csv(filename)
      print("data downloaded and saved data for {ticker} to {filename}")
    else:
      print("No data downloaded for {ticker}")






