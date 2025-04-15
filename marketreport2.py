# -*- coding: utf-8 -*-
"""Enhanced Market Report with BOE Rate and Professional Formatting"""

import yfinance as yf
import pandas as pd
import yagmail
from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

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
    "Gold Futures": "GC=F"
}

def get_boe_rate():
    """Fetch current Bank of England Bank Rate from homepage"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Use webdriver_manager to handle ChromeDriver automatically
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get("https://www.bankofengland.co.uk")
        
        # Wait for the Bank Rate component to load
        rate_container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.bank-rate"))
        
        # Extract the rate and decision date
        current_rate = WebDriverWait(rate_container, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.bank-rate__rate"))
        ).text.strip()
        
        decision_date = WebDriverWait(rate_container, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.bank-rate__date"))
        ).text.strip()
        
        # Take verification screenshot
        os.makedirs("boe_screenshots", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rate_container.screenshot(f"boe_screenshots/boe_rate_{timestamp}.png")
        
        driver.quit()
        
        return {
            "Asset": "BOE Bank Rate",
            "Last Price": current_rate,
            "Change": "N/A",
            "Change %": "N/A",
            "Decision Date": decision_date
        }
        
    except Exception as e:
        print(f"Error fetching BOE rate: {e}")
        return {
            "Asset": "BOE Bank Rate",
            "Last Price": "Error",
            "Change": "N/A",
            "Change %": "N/A",
            "Decision Date": "N/A"
        }

def get_market_data():
    """Fetch market data with enhanced error handling"""
    data = []
    
    # Get BOE rate first (most important)
    boe_data = get_boe_rate()
    data.append([
        boe_data["Asset"],
        boe_data["Last Price"],
        boe_data["Change"],
        boe_data["Change %"]
    ])
    
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
                if "Yield" in name:
                    data.append([name, f"{last_close:.2f}%", f"{change:.2f}", f"{percent_change:.2f}%"])
                elif any(x in name for x in ["Nikkei", "Hang Seng", "FTSE", "DAX", "S&P", "Dow","Nasdaq", "Gold"]):
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
    
    return pd.DataFrame(data, columns=["Asset", "Last Price", "Change", "Change %"])

def format_html_report(df, boe_decision_date):
    """Generate professional HTML report with proper styling"""
    current_time = datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M %Z')
    
    # Add BOE decision date to header if available
    boe_note = ""
    if boe_decision_date and boe_decision_date != "N/A":
        boe_note = f"<div style='margin-bottom:15px;'><strong>BOE Rate Decision:</strong> {boe_decision_date}</div>"
    
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
        {boe_note}
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
        
        # Get BOE decision date separately
        boe_data = get_boe_rate()
        decision_date = boe_data.get("Decision Date", "N/A")
        
        # Format report
        report_html = format_html_report(market_data, decision_date)
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
