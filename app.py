from flask import Flask, render_template,send_from_directory
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from ta.momentum import RSIIndicator

app = Flask(__name__)

company_df = pd.read_csv("company_names.csv")

dashboard = pd.read_excel("output/Summary_Dashboard.xlsx")

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/stock/<path:stock_name>")
def stock(stock_name):

    stocks = dashboard["Stock"].tolist()

    
    if stock_name not in stocks:
        return "Stock not found", 404

    
    current_index = stocks.index(stock_name)

   
    stock_data = dashboard.iloc[current_index]

    
    previous_stock = stocks[current_index - 1] if current_index > 0 else None
    next_stock = stocks[current_index + 1] if current_index < len(stocks) - 1 else None

    
    company_match = company_df.loc[
        company_df["Stock"] == stock_name,
        "Company"
    ]

    company_name = company_match.values[0] if not company_match.empty else stock_name

    
    df = pd.read_csv(
      f"data/{stock_name}_data.csv",
      skiprows=[1, 2]
    )

    df.rename(columns={"Price": "Date"}, inplace=True)

    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    
    ath_price = df["High"].max()
    ath_date = df["High"].idxmax()

    weekly = df.resample("W").agg({
       "Open": "first",
       "High": "max",
       "Low": "min",
       "Close": "last",
       "Volume": "sum"
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

       # Swing Low
       if (
          weekly["Low"].iloc[i] < weekly["Low"].iloc[i-1]
          and
          weekly["Low"].iloc[i] < weekly["Low"].iloc[i+1]
        ):
        weekly.loc[weekly.index[i], "Swing_Low"] = True
    
    highs = weekly[weekly["Swing_High"]]
    lows = weekly[weekly["Swing_Low"]]

    bullish_divergence = []

    for i in range(1, len(lows)):

       previous = lows.iloc[i-1]
       current = lows.iloc[i]

       if (
          current["Low"] < previous["Low"]
          and
          current["RSI"] > previous["RSI"]
          and
          current["RSI"] < 50
        ):

          bullish_divergence.append({
            "Date": current.name,
            "RSI": current["RSI"]
          })

    bearish_divergence = []

    for i in range(1, len(highs)):

      previous = highs.iloc[i-1]
      current = highs.iloc[i]

      if (
        current["High"] > previous["High"]
        and
        current["RSI"] < previous["RSI"]
        and
        current["RSI"] > 50
        ):

          bearish_divergence.append({
            "Date": current.name,
            "RSI": current["RSI"]
          })

    rsi_fig = go.Figure()

    rsi_fig.add_trace(
    go.Scatter(
        x=weekly.index,
        y=weekly["RSI"],
        mode="lines",
        name="RSI"
       )
    )

    rsi_fig.add_trace(
      go.Scatter(
        x=highs.index,
        y=highs["RSI"],
        mode="markers",
        marker=dict(
            color="red",
            size=10,
            symbol="triangle-up"
        ),
        name="Swing High"
      )
    )

    rsi_fig.add_trace(
      go.Scatter(
        x=lows.index,
        y=lows["RSI"],
        mode="markers",
        marker=dict(
            color="green",
            size=10,
            symbol="triangle-down"
        ),
        name="Swing Low"
      )
    )

    bullish_df = pd.DataFrame(bullish_divergence)

    if not bullish_df.empty:

       rsi_fig.add_trace(
          go.Scatter(
            x=bullish_df["Date"],
            y=bullish_df["RSI"],
            mode="markers",
            marker=dict(
                color="green",
                size=16,
                symbol="star"
            ),
            name="Bullish Divergence"
          )
        )
    

    bearish_df = pd.DataFrame(bearish_divergence)

    if not bearish_df.empty:

      rsi_fig.add_trace(
        go.Scatter(
            x=bearish_df["Date"],
            y=bearish_df["RSI"],
            mode="markers",
            marker=dict(
                color="red",
                size=16,
                symbol="star"
            ),
            name="Bearish Divergence"
        )
      )
    

    rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")

    rsi_fig.update_layout(
      title=f"{company_name} Weekly RSI",
      xaxis_title="Date",
      yaxis_title="RSI",
      template="plotly_white"
    )

    rsi_chart = pio.to_html(
      rsi_fig,
      full_html=False
    )
    
    fig = go.Figure()

    
    fig.add_trace(
       go.Scatter(
         x=df.index,
         y=df["Close"],
         mode="lines",
         name="Closing Price",
         line=dict(width=2)
        )
    )

   
    fig.add_trace(
      go.Scatter(
        x=[ath_date],
        y=[ath_price],
        mode="markers+text",
        text=["🏆 ATH"],
        textposition="top center",
        marker=dict(
            size=16,
            color="gold",
            symbol="star"
        ),
        name="All-Time High"
      )
    )

    fig.update_layout(

      title=f"{company_name} - All-Time High",
      xaxis_title="Date",
      yaxis_title="Price (₹)",
      template="plotly_white",
      hovermode="x unified",
      height=500
    )

    price_chart = pio.to_html(
      fig,
      full_html=False
    )

    return render_template(
        "stock.html",
        stock=stock_data,
        previous_stock=previous_stock,
        next_stock=next_stock,
        company_name=company_name,
        price_chart=price_chart,
        rsi_chart=rsi_chart
    )

@app.route("/dashboard")
def show_dashboard():

    total_stocks = len(dashboard)

    total_bullish = dashboard["Bullish Divergences"].sum()
    total_bearish = dashboard["Bearish Divergences"].sum()
    total_swing_highs = dashboard["Weekly Swing Highs"].sum()
    total_swing_lows = dashboard["Weekly Swing Lows"].sum()

    
    highest_ath = dashboard.loc[
        dashboard["ATH"].idxmax()
    ]

    
    most_bullish = dashboard.loc[
        dashboard["Bullish Divergences"].idxmax()
    ]

    
    most_bearish = dashboard.loc[
        dashboard["Bearish Divergences"].idxmax()
    ]

    
    most_swing_high = dashboard.loc[
        dashboard["Weekly Swing Highs"].idxmax()
    ]

    
    most_swing_low = dashboard.loc[
        dashboard["Weekly Swing Lows"].idxmax()
    ]

    stocks = dashboard.to_dict(orient="records")

    return render_template(
        "dashboard.html",
        total_stocks=total_stocks,
        total_bullish=total_bullish,
        total_bearish=total_bearish,
        total_swing_highs=total_swing_highs,
        total_swing_lows=total_swing_lows,
        stocks=stocks,

        # Pass new values to HTML
        highest_ath=highest_ath,
        most_bullish=most_bullish,
        most_bearish=most_bearish,
        most_swing_high=most_swing_high,
        most_swing_low=most_swing_low
    )

@app.route("/download/<filename>")
def download_report(filename):
    return send_from_directory(
        "output",
        filename,
        as_attachment=True
    )

@app.route("/reports")
def reports():
    return render_template("reports.html")

if __name__ == "__main__":
    app.run(debug=True)