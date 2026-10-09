import pandas as pd
import os

files = os.listdir("data")

results = []

for filename in files:

    df = pd.read_csv(f"data/{filename}", skiprows=[1, 2])

    df.rename(columns={"Price": "Date"}, inplace=True)

    stock_name = filename.replace("_data.csv", "")

    ath = df["High"].max()

    ath_row = df[df["High"] == ath]

    ath_date = ath_row.iloc[0]["Date"]

    results.append([stock_name, round(float(ath), 2), ath_date])



report = pd.DataFrame(
    results,
    columns=["Stock Name", "ATH", "ATH Date"]
)

print(report)

if not os.path.exists("output"):
    os.makedirs("output")

report.to_excel("output/ATH_Report.xlsx", index=False)

print("ATH Report saved successfully!")
    
