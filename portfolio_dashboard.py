import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import time
import os

class Portfolio:
    def __init__(self):
        self.positions = [
            {"ticker": "AAPL", "shares": 5, "buy_price": 150},
            {"ticker": "MSFT", "shares": 3, "buy_price": 310},
            {"ticker": "TSLA", "shares": 2, "buy_price": 180}
        ]

    def fetch_current_price(self, ticker):
        data = yf.Ticker(ticker).history(period="1d")
        return data["Close"].iloc[-1]

    def calculate_portfolio(self):
        rows = []
        total_value = 0

        for pos in self.positions:
            ticker = pos["ticker"]
            shares = pos["shares"]
            buy_price = pos["buy_price"]
            current_price = self.fetch_current_price(ticker)

            position_value = shares * current_price
            total_value += position_value

            gain_loss = (current_price - buy_price) * shares
            return_pct = (current_price - buy_price) / buy_price * 100

            rows.append({
                "Ticker": ticker,
                "Shares": shares,
                "Buy Price": buy_price,
                "Current Price": round(current_price, 2),
                "Position Value ($)": round(position_value, 2),
                "Gain/Loss ($)": round(gain_loss, 2),
                "Return (%)": round(return_pct, 2)
            })

        df = pd.DataFrame(rows)
        return df, total_value

    def pie_chart(self, df):
        plt.figure(figsize=(7, 7))
        plt.pie(df["Position Value ($)"], labels=df["Ticker"], autopct="%1.1f%%")
        plt.title("Portfolio Allocation")
        plt.show()

    def value_chart(self, values):
        plt.figure(figsize=(10, 5))
        plt.plot(values)
        plt.title("Portfolio Value Over Time")
        plt.xlabel("Refresh Count")
        plt.ylabel("Portfolio Value ($)")
        plt.grid(True)
        plt.show()

# -------------------- LIVE DASHBOARD --------------------

def run_live_dashboard(refresh_interval=10, refresh_count=10):
    portfolio = Portfolio()
    portfolio_values = []

    for i in range(refresh_count):
        os.system("cls" if os.name == "nt" else "clear")

        df, total_value = portfolio.calculate_portfolio()
        portfolio_values.append(total_value)

        print("\n===== LIVE PORTFOLIO DASHBOARD =====")
        print(df)
        print(f"\nTOTAL VALUE: ${round(total_value, 2)}")
        print(f"REFRESH {i + 1}/{refresh_count} (every {refresh_interval} sec)")

        time.sleep(refresh_interval)

    # After last refresh — show graphs
    portfolio.pie_chart(df)
    portfolio.value_chart(portfolio_values)


# -------------------- RUN --------------------
run_live_dashboard(refresh_interval=10, refresh_count=8)
