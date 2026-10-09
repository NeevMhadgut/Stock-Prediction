import os
import pandas as pd
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator

os.makedirs("charts/RSI", exist_ok=True)
files = os.listdir("data")

for filename in files:

    try:

        df = pd.read_csv(f"data/{filename}", skiprows=[1,2])
        stock_name = filename.replace("_data.csv","")
        df.rename(columns={"Price":"Date"}, inplace=True)
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)

        weekly = df.resample("W").agg({
            "Open":"first",
            "High":"max",
            "Low":"min",
            "Close":"last",
            "Volume":"sum"
        })

        weekly["RSI"] = RSIIndicator(
            close=weekly["Close"],
            window=14
        ).rsi()
        weekly.dropna(inplace=True)

        weekly["Swing_High"] = False
        weekly["Swing_Low"] = False

        for i in range(1, len(weekly)-1):

           
            if (
               weekly["High"].iloc[i] > weekly["High"].iloc[i-1]
               and
               weekly["High"].iloc[i] > weekly["High"].iloc[i+1]
            ):
               weekly.loc[weekly.index[i], "Swing_High"] = True

            
            if (
                weekly["Low"].iloc[i] < weekly["Low"].iloc[i-1]
                and
                weekly["Low"].iloc[i] < weekly["Low"].iloc[i+1]
            ):
                weekly.loc[weekly.index[i], "Swing_Low"] = True

        plt.figure(figsize=(14,6))

        plt.plot(
            weekly.index,
            weekly["RSI"],
            label="RSI"
        )

        plt.axhline(70, linestyle="--")
        plt.axhline(30, linestyle="--")

        highs = weekly[weekly["Swing_High"]]
        plt.scatter(
            highs.index,
            highs["RSI"],
            marker="^",
            s=80,
            label="Swing High"
        )

        lows = weekly[weekly["Swing_Low"]]
        plt.scatter(
            lows.index,
            lows["RSI"],
            marker="v",
            s=80,
            label="Swing Low"
        )

        plt.title(f"{stock_name} - Weekly RSI")
        plt.xlabel("Date")
        plt.ylabel("RSI")
        plt.grid(True)
        plt.legend()

        plt.savefig(
            f"charts/RSI/{stock_name}_RSI.png",
            dpi=300,
            bbox_inches="tight"
        )
        plt.close()
        print(f"{stock_name} RSI Chart Created")

    except Exception as e:

        print(f"Error in {filename}: {e}")