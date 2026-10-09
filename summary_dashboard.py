import pandas as pd

ath = pd.read_excel("output/ATH_Report.xlsx")
rsi = pd.read_excel("output/RSI_Divergence_Report.xlsx")
swing = pd.read_excel("output/Weekly_Swing_Report.xlsx")

ath.rename(columns={"Stock Name": "Stock"}, inplace=True)



divergence_counts = (
    rsi.groupby(["Stock", "Divergence"])
       .size()
       .unstack(fill_value=0)
       .reset_index()
)




swing_counts = (
    swing.groupby(["Stock", "Swing Type"])
         .size()
         .unstack(fill_value=0)
         .reset_index()
)



dashboard = ath.merge(divergence_counts, on="Stock", how="left")

dashboard = dashboard.merge(
    swing_counts,
    on="Stock",
    how="left"
)

dashboard.fillna(0, inplace=True)


dashboard.rename(
    columns={
        "Bullish": "Bullish Divergences",
        "Bearish": "Bearish Divergences",
        "Swing High": "Weekly Swing Highs",
        "Swing Low": "Weekly Swing Lows"
    },
    inplace=True
)


dashboard["ATH Date"] = pd.to_datetime(
    dashboard["ATH Date"]
).dt.strftime("%d-%m-%Y")


dashboard.sort_values("Stock", inplace=True)

dashboard.to_excel(
    "output/Summary_Dashboard.xlsx",
    index=False
)

print(dashboard.head())

print("Summary Dashboard Created Successfully!")