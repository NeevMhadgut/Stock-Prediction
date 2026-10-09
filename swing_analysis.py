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

        
        swing_highs = weekly[
            (weekly["Swing_High"]) 
        ]

        swing_lows = weekly[
            (weekly["Swing_Low"]) 
        ]

        
        for index, row in swing_highs.iterrows():

           results.append([
           stock_name,
           index.date(),
           "Swing High",
           round(float(row["High"]),2)
           ])

        
        for index, row in swing_lows.iterrows():

          results.append([
          stock_name,
          index.date(),
          "Swing Low",
          round(float(row["Low"]),2)
          ])

        

    except Exception as e:
        print(f"Error in {filename}: {e}")


report = pd.DataFrame(
    results,
    columns=[
        "Stock",
        "Date",
        "Swing Type",
        "Price"
    ]
)
report["Date"] = pd.to_datetime(report["Date"]).dt.strftime("%d-%m-%Y")
report = report.sort_values(["Stock", "Date"])


os.makedirs("output", exist_ok=True)

report.to_excel(
    "output/Weekly_Swing_Report.xlsx",
    index=False
)

print("\nDone!")
print(report.head())
print(f"\nTotal Swing Points Found: {len(report)}")