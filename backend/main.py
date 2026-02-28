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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
