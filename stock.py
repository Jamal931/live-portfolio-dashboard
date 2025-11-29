import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

class StockDashboard:
    def __init__(self, ticker, period="1y"):
        """Initialize dashboard with stock ticker and period."""
        self.ticker = ticker.upper()
        self.period = period
        self.data = self.fetch_data()
        
    def fetch_data(self):
        """Fetch stock data from Yahoo Finance."""
        try:
            stock = yf.Ticker(self.ticker)
            hist = stock.history(period=self.period)
            return hist
        except Exception as e:
            print(f"Error fetching data for {self.ticker}: {e}")
            return None
    
    def calculate_indicators(self):
        """Calculate key technical indicators."""
        if self.data is None or self.data.empty:
            return None
        
        df = self.data.copy()
        
        # Moving averages
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Volatility (20-day standard deviation of returns)
        df['Daily_Return'] = df['Close'].pct_change()
        df['Volatility'] = df['Daily_Return'].rolling(window=20).std() * np.sqrt(252)
        
        return df
    
    def get_summary_stats(self):
        """Get key statistics for the stock."""
        if self.data is None or self.data.empty:
            return None
        
        current_price = self.data['Close'].iloc[-1]
        start_price = self.data['Close'].iloc[0]
        period_return = ((current_price - start_price) / start_price) * 100
        max_price = self.data['Close'].max()
        min_price = self.data['Close'].min()
        avg_volume = self.data['Volume'].mean()
        
        return {
            'Current Price': f"${current_price:.2f}",
            'Period Return': f"{period_return:.2f}%",
            '52-Week High': f"${max_price:.2f}",
            '52-Week Low': f"${min_price:.2f}",
            'Avg Volume': f"{avg_volume:,.0f}",
        }
    
    def plot_dashboard(self):
        """Create a comprehensive dashboard visualization."""
        indicators = self.calculate_indicators()
        
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        fig.suptitle(f'{self.ticker} - Stock Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # Plot 1: Price with Moving Averages
        axes[0].plot(indicators.index, indicators['Close'], label='Close Price', linewidth=2, color='blue')
        axes[0].plot(indicators.index, indicators['SMA_50'], label='SMA 50', alpha=0.7, linestyle='--')
        axes[0].plot(indicators.index, indicators['SMA_200'], label='SMA 200', alpha=0.7, linestyle='--')
        axes[0].set_ylabel('Price ($)', fontweight='bold')
        axes[0].set_title('Price Movement & Moving Averages')
        axes[0].legend(loc='best')
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: RSI
        axes[1].plot(indicators.index, indicators['RSI'], label='RSI (14)', color='orange', linewidth=2)
        axes[1].axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Overbought (70)')
        axes[1].axhline(y=30, color='g', linestyle='--', alpha=0.5, label='Oversold (30)')
        axes[1].fill_between(indicators.index, 70, 100, alpha=0.1, color='red')
        axes[1].fill_between(indicators.index, 0, 30, alpha=0.1, color='green')
        axes[1].set_ylabel('RSI', fontweight='bold')
        axes[1].set_title('Relative Strength Index')
        axes[1].set_ylim(0, 100)
        axes[1].legend(loc='best')
        axes[1].grid(True, alpha=0.3)
        
        # Plot 3: Volume
        colors = ['green' if indicators['Close'].iloc[i] >= indicators['Close'].iloc[i-1] else 'red' 
                  for i in range(1, len(indicators))]
        axes[2].bar(indicators.index[1:], indicators['Volume'].iloc[1:], color=colors, alpha=0.6)
        axes[2].set_ylabel('Volume', fontweight='bold')
        axes[2].set_xlabel('Date', fontweight='bold')
        axes[2].set_title('Trading Volume')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def print_summary(self):
        """Print summary statistics."""
        print(f"\n{'='*50}")
        print(f"STOCK DASHBOARD - {self.ticker}")
        print(f"{'='*50}\n")
        
        stats = self.get_summary_stats()
        for key, value in stats.items():
            print(f"{key:.<30} {value}")
        
        print(f"\n{'='*50}\n")

# Usage Example
if __name__ == "__main__":
    # Create dashboard for Apple stock
    dashboard = StockDashboard(ticker="AAPL", period="1y")
    
    # Print summary statistics
    dashboard.print_summary()
    
    # Display visualization
    dashboard.plot_dashboard()
    
    # You can also use other tickers:
    # dashboard = StockDashboard(ticker="MSFT", period="6mo")
    # dashboard = StockDashboard(ticker="TSLA", period="3mo")