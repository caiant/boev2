# -*- coding: utf-8 -*-
"""Enhanced Market Report with BOE Rate and Professional Formatting"""

import yfinance as yf
import pandas as pd
import yagmail 
from datetime import datetime
import pytz
import time
import os
import requests
from bs4 import BeautifulSoup
import re


# Email credentials (use environment variables in production)
EMAIL_ADDRESS = "cailin.antonio@glccap.com"
EMAIL_PASSWORD = "ohdu zsxf lahi mpss"
TO_EMAILS = "lovelycailin@gmail.com"
BCC_EMAILS = "caiantonio2427@gmail.com"

# Updated and verified ticker symbols
tickers = {
    "Nikkei 225": "^N225",
    "Hang Seng": "^HSI",
    "SSE Composite": "000001.SS",
    "FTSE 100": "^FTSE",
    "DAX Index": "^GDAXI",
    "S&P 500 (prior day)": "^GSPC",
    "Dow Jones (prior day)": "^DJI",
    "Nasdaq Composite (prior day)": "^IXIC",
    "USD/JPY (Yen)": "JPY=X",
    "EUR/USD (Euro)": "EURUSD=X",
    "GBP/USD (Pound)": "GBPUSD=X",
    "Crude Oil (WTI)": "WTI",
    "S&P Futures": "ES=F",
    "Dow Jones Futures": "YM=F", 
    "Nasdaq Futures": "NQ=F", 
    "Gold Futures": "GC=F", 
    "US-10 Year Bond Futures": "ZN=F"
}

def get_trading_economics_yields_with_changes():
    yields_data = {}
    urls = {
        "UK 10Y Gilt": "https://tradingeconomics.com/united-kingdom/government-bond-yield",
        "Germany 10Y Bund": "https://tradingeconomics.com/germany/government-bond-yield"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for name, url in urls.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Find the main table containing the bond data
            table = soup.find('table', {'id': 'te-bond-table'})
            if not table:
                yields_data[name] = {"error": "Data table not found"}
                continue
                
            # Find the row for 10Y bond
            rows = table.find_all('tr')
            for row in rows:
                cols = [col.get_text(strip=True) for col in row.find_all('td')]
                if len(cols) >= 5 and '10Y' in cols[0]:
                    # Extract all relevant data points
                    current_yield = cols[1]
                    change_abs = cols[2]  # Absolute change
                    change_pct = cols[3]  # Percentage change
                    
                    # Validate and store the data
                    if all([current_yield, change_abs, change_pct]):
                        yields_data[name] = {
                            "yield": f"{current_yield}%",
                            "change": change_abs,
                            "change%": change_pct,
                            "time": cols[4] if len(cols) > 4 else "N/A"  # Time of last update
                        }
                    else:
                        yields_data[name] = {"error": "Incomplete data found"}
                    break
            else:
                yields_data[name] = {"error": "10Y bond data not found"}
                
        except requests.exceptions.RequestException as e:
            yields_data[name] = {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            yields_data[name] = {"error": f"Processing error: {str(e)}"}
            
    return yields_data
    
    
def get_market_data(): 
    """Fetch market data with enhanced error handling"""
    data = []
    
    # Get other market data
    for name, symbol in tickers.items():
        try:
            asset = yf.Ticker(symbol)
            info = asset.history(period="2d")
            
            if not info.empty and len(info) >= 2:
                last_close = info["Close"].iloc[-1]
                prev_close = info["Close"].iloc[-2]
                change = last_close - prev_close
                percent_change = (change / prev_close) * 100
                
                # Format numbers based on asset type      
                if any(x in name for x in ["Nikkei", "Hang Seng", "FTSE", "DAX", "S&P", "Dow","Nasdaq", "Gold", "10 Year"]):
                    data.append([name, f"{last_close:,.2f}", f"{change:,.2f}", f"{percent_change:.2f}%"])
                elif any(x in name for x in ["USD/JPY", "EUR/USD", "GBP/USD"]):
                    data.append([name, f"{last_close:.4f}", f"{change:.4f}", f"{percent_change:.2f}%"])
                else:  # Commodities
                    data.append([name, f"{last_close:.2f}", f"{change:.2f}", f"{percent_change:.2f}%"])
            else:
                data.append([name, "No Data", "N/A", "N/A"])

        except Exception as e:
            print(f"Error fetching {name}: {str(e)}")
            data.append([name, "Error", "Error", "Error"])

# Get yields with change data
yield_data = get_trading_economics_yields_with_changes()

for name, metrics in yield_data.items():
    if 'error' in metrics:
        # Handle error case - maybe log it or use default values
        data.append([name, "Error", "N/A", "N/A"])
    else:
        # Append all available metrics
        data.append([
            name,
            metrics.get('yield', 'N/A'),
            metrics.get('change', 'N/A'),
            metrics.get('change_percent', 'N/A')
        ])

    
return pd.DataFrame(data, columns=["Asset", "Last Price", "Change", "Change %"])


def format_html_report(df):
    """Generate professional HTML report with proper styling"""
    current_time = datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M %Z')
    
    
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
            }}
            h2 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                box-shadow: 0 2px 3px rgba(0,0,0,0.1);
            }}
            th {{
                background-color: #3498db;
                color: white;
                text-align: center;
                padding: 12px;
                font-weight: bold;
            }}
            td {{
                padding: 10px;
                text-align: center;
                border-bottom: 1px solid #ddd;
            }}
            tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            tr:hover {{
                background-color: #e9f7fe;
            }}
            .positive {{
                color: #27ae60;
                font-weight: bold;
            }}
            .negative {{
                color: #e74c3c;
                font-weight: bold;
            }}
            .footer {{
                font-size: 12px;
                color: #7f8c8d;
                text-align: center;
                margin-top: 20px;
            }}
            .boe-highlight {{
                background-color: #e3f2fd;
                font-weight: bold;
                border-left: 4px solid #1976d2;
            }}
            .info-note {{
                background-color: #e8f5e9;
                padding: 8px;
                border-radius: 4px;
                margin-bottom: 15px;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <h2>📈 Daily Market Report - {current_time}</h2>
        <table>
            <thead>
                <tr>
                    <th>Asset</th>
                    <th>Last Price</th>
                    <th>Change</th>
                    <th>Change %</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for _, row in df.iterrows():
        # Special formatting for BOE rate
        row_class = "boe-highlight" if "BOE Bank Rate" in row['Asset'] else ""
        
        # Color coding for changes (except BOE rate)
        change_class = ""
        if "BOE Bank Rate" not in row['Asset']:
            try:
                change_value = float(row['Change'].replace(',','').replace('%',''))
                if change_value > 0:
                    change_class = "positive"
                elif change_value < 0:
                    change_class = "negative"
            except:
                pass
        
        html += f"""
                <tr class="{row_class}">
                    <td>{row['Asset']}</td>
                    <td>{row['Last Price']}</td>
                    <td class="{change_class}">{row['Change']}</td>
                    <td class="{change_class}">{row['Change %']}</td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
        <div class="footer">
            <p>Data sources: Yahoo Finance & Bank of England | Report generated at {current_time}</p>
        </div>
    </body>
    </html>
    """
    return html

def send_email():
    """Send formatted market report via email"""
    try:
        # Get market data including BOE rate
        market_data = get_market_data()
        
        # Format report - you'll need to define decision_date or pass None
        report_html = format_html_report(market_data)  # or get this from somewhere
        subject = f"Daily Market Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Initialize yagmail
        yag = yagmail.SMTP(EMAIL_ADDRESS, EMAIL_PASSWORD)
        yag.send(
            to=TO_EMAILS,
            subject=subject,
            contents=report_html, 
            bcc=BCC_EMAILS
        )
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")

if __name__ == "__main__":
    send_email()
