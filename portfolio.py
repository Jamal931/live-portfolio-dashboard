import yfinance as yf
import pandas as pd

class Portfolio:
    def __init__(self):
        # You can add or remove positions here
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
                "Buy Price": round(buy_price, 2),
                "Current Price": round(current_price, 2),
                "Position Value ($)": round(position_value, 2),
                "Gain/Loss ($)": round(gain_loss, 2),
                "Return (%)": round(return_pct, 2)
            })

        df = pd.DataFrame(rows)
        return df, total_value


# -------- RUN THE TRACKER --------

portfolio = Portfolio()
df, total_value = portfolio.calculate_portfolio()

print("\nPORTFOLIO SUMMARY")
print(df)
print(f"\nTOTAL PORTFOLIO VALUE: ${round(total_value, 2)}")
