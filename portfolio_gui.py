import yfinance as yf
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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

    def get_portfolio_data(self):
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
                "Buy Price": round(buy_price,2),
                "Current Price": round(current_price,2),
                "Position Value ($)": round(position_value,2),
                "Gain/Loss ($)": round(gain_loss,2),
                "Return (%)": round(return_pct,2)
            })
        df = pd.DataFrame(rows)
        return df, total_value

class PortfolioGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Portfolio Dashboard")
        self.portfolio = Portfolio()
        self.portfolio_history = []  # Track portfolio value over time
        
        # Treeview
        self.tree = ttk.Treeview(root)
        self.tree.pack(fill="both", expand=True)
        self.tree["columns"] = ("Shares", "Buy Price", "Current Price", "Position Value ($)", "Gain/Loss ($)", "Return (%)")
        self.tree.heading("#0", text="Ticker")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)

        # Total value label
        self.total_label = tk.Label(root, text="")
        self.total_label.pack(pady=5)


        # Refresh button
        self.refresh_btn = tk.Button(root, text="Refresh Portfolio", command=self.update_portfolio)
        self.refresh_btn.pack(pady=5)
        self.root.after(10000, self.auto_refresh)  # 10000ms = 10 seconds


        # --- Add Stock Inputs ---
        self.new_ticker_label = tk.Label(root, text="Enter Ticker:")
        self.new_ticker_label.pack()
        self.new_ticker_entry = tk.Entry(root)
        self.new_ticker_entry.pack()

        self.new_shares_label = tk.Label(root, text="Shares:")
        self.new_shares_label.pack()
        self.new_shares_entry = tk.Entry(root)
        self.new_shares_entry.pack()

        self.add_btn = tk.Button(root, text="Add Stock", command=self.add_stock)
        self.add_btn.pack(pady=5)

        # Remove Stock button
        self.remove_btn = tk.Button(root, text="Remove Selected Stock", command=self.remove_stock)
        self.remove_btn.pack(pady=5)

        # --- Matplotlib Figure ---
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Initial load
        self.update_portfolio()
        
    def auto_refresh(self):
          self.update_portfolio()
          self.root.after(10000, self.auto_refresh)

    # ------------------- Update Portfolio Table -------------------
    def update_portfolio(self):
        df, total_value = self.portfolio.get_portfolio_data()
        self.portfolio_history.append(total_value)

        # Clear old treeview
        for row in self.tree.get_children():
            self.tree.delete(row)
        for index, row in df.iterrows():
            self.tree.insert("", "end", text=row["Ticker"], values=(
                row["Shares"], row["Buy Price"], row["Current Price"],
                row["Position Value ($)"], row["Gain/Loss ($)"], row["Return (%)"]
            ))
        self.total_label.config(text=f"TOTAL PORTFOLIO VALUE: ${round(total_value,2)}")

        # Update charts
        self.update_charts(df)

    # ------------------- Add Stock -------------------
    def add_stock(self):
        ticker = self.new_ticker_entry.get().upper()
        try:
            shares = int(self.new_shares_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Shares must be a number")
            return

        if ticker and shares > 0:
            try:
                buy_price = float(simpledialog.askstring("Buy Price", f"Enter buy price for {ticker}:"))
            except TypeError:
                return  # user pressed cancel
            self.portfolio.positions.append({"ticker": ticker, "shares": shares, "buy_price": buy_price})
            self.update_portfolio()
            self.new_ticker_entry.delete(0, tk.END)
            self.new_shares_entry.delete(0, tk.END)

    # ------------------- Remove Stock -------------------
    def remove_stock(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select a stock to remove")
            return
        ticker = self.tree.item(selected_item)["text"]
        self.portfolio.positions = [p for p in self.portfolio.positions if p["ticker"] != ticker]
        self.update_portfolio()

    # ------------------- Update Charts -------------------
    def update_charts(self, df):
        self.ax1.clear()
        self.ax2.clear()

        # Pie chart - allocation
        if not df.empty:
            self.ax1.pie(df["Position Value ($)"], labels=df["Ticker"], autopct="%1.1f%%")
            self.ax1.set_title("Portfolio Allocation")

        # Line chart - portfolio value over time
        self.ax2.plot(self.portfolio_history, marker='o')
        self.ax2.set_title("Portfolio Value Over Time")
        self.ax2.set_xlabel("Refresh Count")
        self.ax2.set_ylabel("Total Value ($)")
        self.ax2.grid(True)

        self.fig.tight_layout()
        self.canvas.draw()

# ------------------- Run the GUI -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = PortfolioGUI(root)
    root.mainloop()
