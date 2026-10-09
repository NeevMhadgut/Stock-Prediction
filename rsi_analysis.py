import os
import pandas as pd
from ta.momentum import RSIIndicator


files = os.listdir("data")

results = []


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

            # Swing High
            if (
                weekly["High"].iloc[i] > weekly["High"].iloc[i-1]
                and
                weekly["High"].iloc[i] > weekly["High"].iloc[i+1]
            ):
                weekly.loc[weekly.index[i], "Swing_High"] = True

            # Swing Low
            if (
                weekly["Low"].iloc[i] < weekly["Low"].iloc[i-1]
                and
                weekly["Low"].iloc[i] < weekly["Low"].iloc[i+1]
            ):
                weekly.loc[weekly.index[i], "Swing_Low"] = True

        
        swing_highs = weekly[
            (weekly["Swing_High"]) &
            (weekly["RSI"].notna())
        ]

        swing_lows = weekly[
            (weekly["Swing_Low"]) &
            (weekly["RSI"].notna())
        ]

       
        for i in range(1, len(swing_lows)):

            previous = swing_lows.iloc[i-1]
            current = swing_lows.iloc[i]

            if (
                current["Low"] < previous["Low"]
                and
                current["RSI"] > previous["RSI"]
                and
                current["RSI"] < 50
            ):

                results.append([
                    stock_name,
                    current.name.date(),
                    "Bullish",
                    round(float(current["Low"]),2),
                    round(float(current["RSI"]),2)
                ])

        
        for i in range(1, len(swing_highs)):

            previous = swing_highs.iloc[i-1]
            current = swing_highs.iloc[i]

            if (
                current["High"] > previous["High"]
                and
                current["RSI"] < previous["RSI"]
                and
                current["RSI"] > 50
            ):

                results.append([
                    stock_name,
                    current.name.date(),
                    "Bearish",
                    round(float(current["High"]),2),
                    round(float(current["RSI"]),2)
                ])

        print(f"Finished: {stock_name}")

    except Exception as e:
        print(f"Error in {filename}: {e}")


report = pd.DataFrame(
    results,
    columns=[
        "Stock",
        "Date",
        "Divergence",
        "Price",
        "RSI"
    ]
)
report["Date"] = pd.to_datetime(report["Date"]).dt.strftime("%d-%m-%Y")
report = report.sort_values(["Stock", "Date"])


os.makedirs("output", exist_ok=True)

report.to_excel(
    "output/RSI_Divergence_Report.xlsx",
    index=False
)

print("\nDone!")
print(report.head())
print(f"\nTotal Divergences Found: {len(report)}")