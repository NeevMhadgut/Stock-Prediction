import os
import pandas as pd
import matplotlib.pyplot as plt

files = os.listdir("data")

os.makedirs("charts/ATH", exist_ok=True)

for filename in files:

    try:

        df = pd.read_csv(f"data/{filename}", skiprows=[1,2])
        stock_name = filename.replace("_data.csv","")
        df.rename(columns={"Price":"Date"}, inplace=True)
        df["Date"] = pd.to_datetime(df["Date"])

        ath = df["High"].max()
        ath_row = df[df["High"] == ath]
        ath_date = ath_row.iloc[0]["Date"]

        plt.figure(figsize=(12,6))
        plt.plot(
            df["Date"],
            df["Close"],
            label="Closing Price"
        )

        plt.scatter(
            ath_date,
            ath,
            color="red",
            s=120,
            marker="*",
            label="ATH"
        )

        plt.annotate(
            f"{ath:.2f}",
            (ath_date, ath),
            textcoords="offset points",
            xytext=(10,10)
        )

        plt.title(f"{stock_name} - All Time High")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.grid(True)
        plt.legend()

        plt.savefig(
            f"charts/ATH/{stock_name}_ATH.png",
            dpi=300,
            bbox_inches="tight"
        )
        plt.close()
        print(f"{stock_name} chart created")

    except Exception as e:

        print(f"Error in {filename}: {e}")

    