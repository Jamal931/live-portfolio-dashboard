import pandas as pd
import numpy as np
from datetime import datetime

class DCFValuation:
    def __init__(self, company_name, fcf_base, fcf_growth_years=5):
        """
        Initialize DCF model.
        
        Args:
            company_name: Name of the company
            fcf_base: Base year free cash flow (in millions)
            fcf_growth_years: Number of years to project (default 5)
        """
        self.company_name = company_name
        self.fcf_base = fcf_base
        self.fcf_growth_years = fcf_growth_years
        self.projections = []
    
    def project_fcf(self, growth_rates):
        """
        Project free cash flows.
        
        Args:
            growth_rates: List of growth rates (as decimals) for each year
        """
        if len(growth_rates) != self.fcf_growth_years:
            raise ValueError(f"Provide {self.fcf_growth_years} growth rates")
        
        fcf = self.fcf_base
        self.projections = []
        
        for year in range(1, self.fcf_growth_years + 1):
            fcf = fcf * (1 + growth_rates[year - 1])
            self.projections.append({
                'Year': year,
                'FCF': fcf,
                'Growth Rate': growth_rates[year - 1]
            })
        
        return self.projections
    
    def calculate_terminal_value(self, terminal_growth_rate, wacc):
        """
        Calculate terminal value using perpetuity growth method.
        
        Args:
            terminal_growth_rate: Long-term growth rate (as decimal, typically 2-3%)
            wacc: Weighted average cost of capital (as decimal)
        """
        if not self.projections:
            raise ValueError("Run project_fcf() first")
        
        final_fcf = self.projections[-1]['FCF']
        terminal_fcf = final_fcf * (1 + terminal_growth_rate)
        terminal_value = terminal_fcf / (wacc - terminal_growth_rate)
        
        return terminal_value
    
    def calculate_pv(self, discount_rate):
        """Calculate present value of projected FCFs."""
        pv_fcfs = []
        
        for projection in self.projections:
            year = projection['Year']
            fcf = projection['FCF']
            pv = fcf / ((1 + discount_rate) ** year)
            pv_fcfs.append(pv)
        
        return pv_fcfs
    
    def calculate_enterprise_value(self, growth_rates, terminal_growth_rate, wacc):
        """
        Calculate enterprise value.
        
        Args:
            growth_rates: List of growth rates for projection period
            terminal_growth_rate: Perpetual growth rate
            wacc: Discount rate / weighted average cost of capital
        """
        # Project FCF
        self.project_fcf(growth_rates)
        
        # Calculate PV of projected FCFs
        pv_fcfs = self.calculate_pv(wacc)
        pv_fcf_sum = sum(pv_fcfs)
        
        # Calculate terminal value and its PV
        terminal_value = self.calculate_terminal_value(terminal_growth_rate, wacc)
        pv_terminal_value = terminal_value / ((1 + wacc) ** self.fcf_growth_years)
        
        # Enterprise value
        enterprise_value = pv_fcf_sum + pv_terminal_value
        
        return {
            'PV of Projected FCFs': pv_fcf_sum,
            'Terminal Value': terminal_value,
            'PV of Terminal Value': pv_terminal_value,
            'Enterprise Value': enterprise_value
        }
    
    def calculate_equity_value(self, enterprise_value, net_debt, shares_outstanding):
        """
        Calculate equity value and price per share.
        
        Args:
            enterprise_value: Enterprise value from DCF
            net_debt: Total debt minus cash (in millions)
            shares_outstanding: Number of shares outstanding (in millions)
        """
        equity_value = enterprise_value - net_debt
        price_per_share = equity_value / shares_outstanding
        
        return {
            'Equity Value': equity_value,
            'Price Per Share': price_per_share
        }
    
    def run_valuation(self, fcf_growth, terminal_growth, wacc, net_debt, shares):
        """
        Run complete DCF valuation.
        
        Args:
            fcf_growth: List of growth rates for projection period
            terminal_growth: Perpetual growth rate
            wacc: Weighted average cost of capital (discount rate)
            net_debt: Net debt in millions
            shares: Shares outstanding in millions
        """
        print(f"\n{'='*70}")
        print(f"DCF VALUATION MODEL - {self.company_name.upper()}")
        print(f"{'='*70}\n")
        
        # Calculate enterprise value
        ev_results = self.calculate_enterprise_value(fcf_growth, terminal_growth, wacc)
        
        # Calculate equity value
        equity_results = self.calculate_equity_value(
            ev_results['Enterprise Value'],
            net_debt,
            shares
        )
        
        # Print results
        print("INPUT ASSUMPTIONS:")
        print(f"  Base Year FCF ..................... ${self.fcf_base:,.1f}M")
        print(f"  Projection Period ................ {self.fcf_growth_years} years")
        print(f"  Terminal Growth Rate ............. {terminal_growth*100:.1f}%")
        print(f"  WACC (Discount Rate) ............. {wacc*100:.1f}%")
        print(f"  Net Debt .......................... ${net_debt:,.1f}M")
        print(f"  Shares Outstanding ............... {shares:.1f}M")
        
        print("\nFCF PROJECTIONS:")
        df_projections = pd.DataFrame(self.projections)
        df_projections['Growth Rate'] = df_projections['Growth Rate'].apply(lambda x: f"{x*100:.1f}%")
        df_projections['FCF'] = df_projections['FCF'].apply(lambda x: f"${x:,.1f}M")
        print(df_projections.to_string(index=False))
        
        print("\nVALUATION RESULTS:")
        print(f"  PV of Projected FCFs ............. ${ev_results['PV of Projected FCFs']:,.1f}M")
        print(f"  Terminal Value ................... ${ev_results['Terminal Value']:,.1f}M")
        print(f"  PV of Terminal Value ............. ${ev_results['PV of Terminal Value']:,.1f}M")
        print(f"  Enterprise Value ................. ${ev_results['Enterprise Value']:,.1f}M")
        print(f"\n  Less: Net Debt .................... ${net_debt:,.1f}M")
        print(f"  Equity Value ...................... ${equity_results['Equity Value']:,.1f}M")
        print(f"  ÷ Shares Outstanding ............. {shares:.1f}M")
        print(f"\n  {'─'*50}")
        print(f"  INTRINSIC VALUE PER SHARE ........ ${equity_results['Price Per Share']:.2f}")
        print(f"  {'─'*50}\n")
        
        return {
            'enterprise_value': ev_results['Enterprise Value'],
            'equity_value': equity_results['Equity Value'],
            'price_per_share': equity_results['Price Per Share']
        }


# EXAMPLE: Microsoft DCF Valuation
if __name__ == "__main__":
    # Create valuation model
    msft = DCFValuation(
        company_name="Microsoft",
        fcf_base=45000,  # Base year FCF in millions
        fcf_growth_years=5
    )
    
    # Define assumptions
    fcf_growth_rates = [0.08, 0.08, 0.07, 0.07, 0.06]  # 8%, 8%, 7%, 7%, 6%
    terminal_growth = 0.025  # 2.5% perpetual growth
    wacc = 0.07  # 7% weighted average cost of capital
    net_debt = 0  # Millions (negative = net cash)
    shares_outstanding = 8400  # Millions
    
    # Run valuation
    results = msft.run_valuation(
        fcf_growth=fcf_growth_rates,
        terminal_growth=terminal_growth,
        wacc=wacc,
        net_debt=net_debt,
        shares=shares_outstanding
    )
    
    # You can also value other companies by adjusting inputs:
    # apple = DCFValuation(company_name="Apple", fcf_base=110000)
    # tesla = DCFValuation(company_name="Tesla", fcf_base=13000)