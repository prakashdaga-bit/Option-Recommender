from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import random

# Import local modules
from kite_service import kite_service
from strategy_engine import calculate_strategy
from advanced_analyzer import AdvancedOptionsAnalyzer
from sentiment_analyzer import sentiment_service
from exit_logic import check_my_exit
from datetime import datetime
import re

analyzer = AdvancedOptionsAnalyzer()

app = FastAPI(title="F&O Options Analyzer")

# Allowing CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    stocks: List[str]
    strategy: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Options Analyzer API is running"}

@app.post("/analyze")
def analyze_options(req: AnalysisRequest):
    results = []
    
    # 1. Fetch Current LTPs
    ltps = kite_service.get_ltp(req.stocks)
    
    for stock in req.stocks:
        # Zerodha returns keys prefixed with the exchange (e.g. NSE:RELIANCE)
        spot_prefix = f"NSE:{stock}"
        
        if stock in ltps:
            current_price = ltps[stock]["last_price"]
        elif spot_prefix in ltps:
            current_price = ltps[spot_prefix]["last_price"]
        else:
            continue

        
        # Calculate dynamic strike range (+/- 20% of LTP for Deep OTM analysis)
        range_min = current_price * 0.80
        range_max = current_price * 1.20
        
        # 2. Get real option chain around this range
        chain = kite_service.get_option_chain(stock, current_price, range_min, range_max)
        
        # 3. Predict direction using the robust Advanced Strategy Engine
        regime_data = analyzer.analyze_regime(current_price, chain)
        prediction_text = regime_data["prediction_text"]
        pred_signal = regime_data["signal"]
        
        # 4. Fetch Natural Language Sentiment
        sentiment_data = sentiment_service.analyze_ticker(stock)
        
        # 5. Calculate Payoffs/ROIs
        strategy_stats = calculate_strategy(req.strategy, chain, current_price)
        
        if "error" in strategy_stats:
            continue
            
        results.append({
            "stock": stock,
            "spot": round(current_price, 2),
            "prediction": prediction_text,
            "signal": pred_signal,
            "pcr": regime_data["pcr"],
            "seller_recommendation": regime_data["seller_recommendation"],
            "sentiment": sentiment_data,
            "stats": strategy_stats
        })
        
    return {"data": results}

@app.get("/positions")
def get_positions_analysis():
    """
    Fetch open positions and run Exit Logic on them.
    """
    raw_positions = kite_service.get_positions()
    analyzed_positions = []
    
    # 1. Fetch live prices for all underlying symbols in one go (optimization possible, but loop is fine for now)
    # Actually, let's process each position
    
    for pos in raw_positions:
        # Parse Symbol and Expiry
        # Zerodha Symbol Format: NIFTY24FEB22000CE or RELIANCE24FEB2400CE
        # We need to extract: Underlying, Expiry Date, Strike (to calc delta if needed)
        
        tradingsymbol = pos['tradingsymbol']
        instrument_type = pos['instrument_token'] # We might need this, but 'tradingsymbol' is easier to parse manually if needed
        
        # Simple parsing logic (This is fragile, ideally use instrument_token master list)
        # But for "NIFTY" or "BANKNIFTY", it's standard. 
        # For stocks "RELIANCE", it works too.
        
        # Fetch Underlying LTP
        # pos['last_price'] is the Option Price. We need Underlying Price.
        # We can try to guess underlying symbol.
        
        underlying = "NIFTY 50" # Default fallback? No.
        if "NIFTY" in tradingsymbol and "BANK" not in tradingsymbol:
             underlying = "NIFTY 50"
        elif "BANKNIFTY" in tradingsymbol:
             underlying = "NIFTY BANK"
        else:
             # Extract from tradingsymbol? E.g. RELIANCE24...
             # Regex to find the alphabetical prefix
             match = re.match(r"([A-Z]+)", tradingsymbol)
             if match:
                 underlying = match.group(1)
        
        # Fetch Real Underlying Price
        ltp_data = kite_service.get_ltp([underlying])
        underlying_price = 0
        if underlying in ltp_data:
             underlying_price = ltp_data[underlying]['last_price']
        elif f"NSE:{underlying}" in ltp_data:
             underlying_price = ltp_data[f"NSE:{underlying}"]['last_price']
             
        # Days to Expiry? 
        # Zerodha API response usually has 'expiry' field in datetime format if we used 'net' properly?
        # Actually 'net' positions list might NOT have expiry date directly stringified.
        # It's better to fetch instrument master or parse string.
        # Let's mock expiry parsing or rely on manual check for now if complex.
        # Wait, strictly speaking we can't easily parse expiry from "NIFTY24FEB..." without a library or efficient regex.
        # For now, let's assume we can get it or default to a safe value (to test logic).
        # IMPROVEMENT: Use `kite.instruments()` to map token to details. Expensive to call every time.
        # Hack: Assume 10 days if unknown to avoid false positive EXIT on time.
        days_to_expiry = 10 
        
        # Exit Check
        # entry_price = pos['average_price']
        # current_price = pos['last_price']
        # quantity = pos['quantity']
        
        bias = "LONG" if pos['quantity'] > 0 else "SHORT"
        
        exit_decision = check_my_exit(
            position_type="CE" if "CE" in tradingsymbol else "PE",
            bias=bias,
            current_price=pos['last_price'],
            entry_price=pos['average_price'],
            days_to_expiry=days_to_expiry,
            underlying_symbol=underlying,
            underlying_price=underlying_price
        )
        
        analyzed_positions.append({
            "symbol": tradingsymbol,
            "qty": pos['quantity'],
            "avg_price": pos['average_price'],
            "ltp": pos['last_price'],
            "pnl": pos['pnl'],
            "action": exit_decision['action'],
            "reason": exit_decision['reason'],
            "underlying": underlying,
            "underlying_price": underlying_price
        })
        
    return {"data": analyzed_positions}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
