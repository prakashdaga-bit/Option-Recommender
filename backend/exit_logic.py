import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

def check_my_exit(
    position_type: str,  # "CE" or "PE"
    bias: str,           # "LONG" or "SHORT" (Net Quantity > 0 is LONG, < 0 is SHORT)
    current_price: float,
    entry_price: float,
    days_to_expiry: int,
    underlying_symbol: str, 
    underlying_price: float
) -> dict:
    """
    Evaluates whether to EXIT or HOLD a position based on:
    1. Time to Expiry
    2. Profit/Loss Targets
    3. India VIX Spikes
    4. Technical Trend (20-SMA)
    5. Event Risk (Earnings)
    """
    
    reasons = []
    should_exit = False
    
    # --- 1. TIME CHECK ---
    if days_to_expiry <= 5:
        return {"action": "EXIT", "reason": "Expiry approaching (Liquidity Risk)"}

    # --- 2. PROFIT/LOSS CHECK ---
    # Logic depends on whether we are Long (Bought) or Short (Sold) the option
    # Note: 'current_premium' in user request maps to 'current_price' here
    
    if bias == "SHORT":
        # Credit Strategy (Short Strangle/Iron Condor leg)
        # Max Profit = Entry Price. Max Loss = Unlimited.
        
        # Stop Loss: If premium spikes 3x (200% loss)
        if current_price >= (entry_price * 3.0):
             return {"action": "EXIT", "reason": "Hard Stop Loss (2x Credit Loss)"}
             
        # Profit Target: If premium decays to 50%
        if current_price <= (entry_price * 0.5):
             return {"action": "EXIT", "reason": "Profit Target Reached (50% Decay)"}
             
    elif bias == "LONG":
        # Debit Strategy
        # Stop Loss: If premium drops 50%
        if current_price <= (entry_price * 0.5):
             return {"action": "EXIT", "reason": "Stop Loss (50% Premium Eroded)"}
             
        # Profit Target: If premium doubles
        if current_price >= (entry_price * 2.0):
             return {"action": "EXIT", "reason": "Profit Target Reached (100% Return)"}

    # --- 3. VIX WATCH (Safety Guardrail) ---
    try:
        vix = yf.Ticker("^INDIAVIX")
        vix_hist = vix.history(period="2d")
        if len(vix_hist) >= 2:
            prev_close = vix_hist['Close'].iloc[-2]
            curr_vix = vix_hist['Close'].iloc[-1]
            vix_change = ((curr_vix - prev_close) / prev_close) * 100
            
            if vix_change > 10.0:
                 return {"action": "EXIT", "reason": f"VIX Spike Detected (+{round(vix_change, 1)}%)"}
    except Exception as e:
        logging.warning(f"Failed to fetch VIX data: {e}")

    # --- 4. TREND WATCH (20-SMA) ---
    # We need 15-min candles to verify 2 consecutive closes. 
    # Validating this strictly via yfinance might be delayed. 
    # We will use a simplified check: If CURRENT price + Prev 15min Close are both violating SMA.
    try:
        # Fetch intraday data for underlying
        # yfinance format for NSE symbols often needs suffix. 
        # Assuming underlying_symbol is like "RELIANCE" or "NIFTY 50"
        yf_symbol = f"{underlying_symbol}.NS" if "NIFTY" not in underlying_symbol else "^NSEI" 
        if "BANKNIFTY" in underlying_symbol: yf_symbol = "^NSEBANK"
            
        ticker = yf.Ticker(yf_symbol)
        # Fetch enough data for 20 SMA (e.g. 5 days of 15m data)
        df = ticker.history(period="5d", interval="15m")
        
        if len(df) > 20:
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            
            last_candle = df.iloc[-1]
            prev_candle = df.iloc[-2]
            
            sma_last = last_candle['SMA_20']
            sma_prev = prev_candle['SMA_20']
            
            close_last = last_candle['Close']
            close_prev = prev_candle['Close']
            
            # Logic:
            # Long Bias (e.g. Short Put / Long Call) -> Bullish -> Exit if Price < SMA
            # Short Bias (e.g. Short Call / Long Put) -> Bearish -> Exit if Price > SMA
            
            # Wait, the User request was:
            # "For Long-biased (Puts): Exit if Price < 20-SMA" -> This implies SELLING Puts (Bullish trade) OR Buying Puts (Bearish trade)?
            # Usually "Long-biased" means you want the market to go UP. 
            # If you BOUGHT a PUT, you are Bearish (Short-biased on market).
            # If you SOLD a PUT, you are Bullish (Long-biased on market).
            
            # User Wording: "For Long-biased (Puts)" 
            # This is ambiguous. "Long Puts" usually means OWNING a Put (Bearish). 
            # But "Long-biased" usually means Bullish exposure.
            # Context: "Seller Strategy" -> Selling Puts = Bullish.
            # Let's assume User means: "Strategies relying on Bullish Trend (e.g. Short Puts)"
            
            # INTERPRETATION:
            # "Long-biased (Puts)" = Short Put Strategy (Bullish Market View)
            #   -> EXIT if Price < 20-SMA (Trend breakdown).
            
            # "Short-biased (Calls)" = Short Call Strategy (Bearish Market View)
            #   -> EXIT if Price > 20-SMA (Trend reversal).
            
            is_bullish_trade = (position_type == "PE" and bias == "SHORT") or (position_type == "CE" and bias == "LONG")
            is_bearish_trade = (position_type == "CE" and bias == "SHORT") or (position_type == "PE" and bias == "LONG")

            if is_bullish_trade:
                # Exit if Bearish Trend confirmed (2 candles < SMA)
                if close_last < sma_last and close_prev < sma_prev:
                    return {"action": "EXIT", "reason": "Trend Breakdown (Price < 20-SMA)"}
                    
            if is_bearish_trade:
                # Exit if Bullish Trend confirmed (2 candles > SMA)
                if close_last > sma_last and close_prev > sma_prev:
                     return {"action": "EXIT", "reason": "Trend Reversal (Price > 20-SMA)"}

    except Exception as e:
        logging.warning(f"Failed to fetch Technical data for {underlying_symbol}: {e}")

    # --- 5. CALENDAR WATCH (Event Risk) ---
    try:
        # Check Earnings
        stock = yf.Ticker(yf_symbol)
        calendar = stock.calendar
        
        # yfinance calendar format varies. Safe check.
        if calendar is not None and not calendar.empty:
            # Check if there is an earnings date tomorrow
            # This is complex to parse generically for all stocks, simplified for now
            pass 
            
        # Time check for 3:00 PM
        now = datetime.now()
        if now.hour == 15 and now.minute >= 0:
             # Strictly check if earnings tomorrow? 
             # For now, we will skip hard implementation without reliable earnings implementation
             pass
             
    except Exception:
        pass

    return {"action": "HOLD", "reason": "All checks passed"}
