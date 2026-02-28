def calculate_strategy(strategy, options, spot_price):
    """
    Calculates payoffs for various options strategies based on mock/real option chain data.
    """
    if not options or len(options) < 2:
        return {"error": "Not enough option strikes available for strategy"}
        
    # Sort options by strike price
    options.sort(key=lambda x: x['strike'])
    
    # Simple logic to find ATM strike
    atm_option = min(options, key=lambda x: abs(x['strike'] - spot_price))
    atm_index = options.index(atm_option)
    
    result = {
        "strategy_name": strategy,
        "spot": spot_price,
        "margin": 0,
        "roi": 0.0,
        "premium_paid": 0,
        "premium_received": 0,
        "max_profit": 0,
        "max_loss": 0,
        "strikes_involved": [],
        "commentary": ""
    }
    
    # Common strategies logic
    # Lot size is usually 50 or 25 for indices, keeping 50 for simplicity for all mock calculations
    lot_size = 50
    
    if strategy == "Bull Call":
        # Buy ATM Call, Sell OTM Call
        if atm_index + 1 < len(options):
            buy_leg = options[atm_index]
            sell_leg = options[atm_index + 1]
            
            result["premium_paid"] = buy_leg['ce_price'] * lot_size
            result["premium_received"] = sell_leg['ce_price'] * lot_size
            net_premium = result["premium_paid"] - result["premium_received"]
            
            strike_diff = sell_leg['strike'] - buy_leg['strike']
            result["max_profit"] = (strike_diff * lot_size) - net_premium
            result["max_loss"] = net_premium
            result["margin"] = net_premium + 10000 # Margin approximation
            result["roi"] = (result["max_profit"] / result["margin"]) * 100 if result["margin"] > 0 else 0
            
            result["strikes_involved"] = [f"Buy {buy_leg['strike']} CE", f"Sell {sell_leg['strike']} CE"]
            result["commentary"] = f"Bullish strategy with capped risk and capped reward. Max loss is net premium {net_premium:.2f}."
            
    elif strategy == "Bear Put":
        # Buy ATM Put, Sell OTM Put (lower strike)
        if atm_index - 1 >= 0:
            buy_leg = options[atm_index]
            sell_leg = options[atm_index - 1]
            
            result["premium_paid"] = buy_leg['pe_price'] * lot_size
            result["premium_received"] = sell_leg['pe_price'] * lot_size
            net_premium = result["premium_paid"] - result["premium_received"]
            
            strike_diff = buy_leg['strike'] - sell_leg['strike']
            result["max_profit"] = (strike_diff * lot_size) - net_premium
            result["max_loss"] = net_premium
            result["margin"] = net_premium + 10000 
            result["roi"] = (result["max_profit"] / result["margin"]) * 100 if result["margin"] > 0 else 0
            
            result["strikes_involved"] = [f"Buy {buy_leg['strike']} PE", f"Sell {sell_leg['strike']} PE"]
            result["commentary"] = f"Bearish strategy limiting risk to the net premium {net_premium:.2f}."
            
    elif strategy == "Bear Call":
        # Sell ATM Call, Buy OTM Call (Credit spread)
        if atm_index + 1 < len(options):
            sell_leg = options[atm_index]
            buy_leg = options[atm_index + 1]
            
            result["premium_paid"] = buy_leg['ce_price'] * lot_size
            result["premium_received"] = sell_leg['ce_price'] * lot_size
            net_credit = result["premium_received"] - result["premium_paid"]
            
            strike_diff = buy_leg['strike'] - sell_leg['strike']
            result["max_profit"] = net_credit
            result["max_loss"] = (strike_diff * lot_size) - net_credit
            result["margin"] = 35000 # Higher margin for credit spreads
            result["roi"] = (result["max_profit"] / result["margin"]) * 100 if result["margin"] > 0 else 0
            
            result["strikes_involved"] = [f"Sell {sell_leg['strike']} CE", f"Buy {buy_leg['strike']} CE"]
            result["commentary"] = f"Bearish to neutral strategy collecting credit. Max profit is net credit {net_credit:.2f}."

    elif strategy == "Bull Put":
        # Sell ATM Put, Buy OTM Put (lower strike, Credit spread)
        if atm_index - 1 >= 0:
            sell_leg = options[atm_index]
            buy_leg = options[atm_index - 1]
            
            result["premium_paid"] = buy_leg['pe_price'] * lot_size
            result["premium_received"] = sell_leg['pe_price'] * lot_size
            net_credit = result["premium_received"] - result["premium_paid"]
            
            strike_diff = sell_leg['strike'] - buy_leg['strike']
            result["max_profit"] = net_credit
            result["max_loss"] = (strike_diff * lot_size) - net_credit
            result["margin"] = 35000 
            result["roi"] = (result["max_profit"] / result["margin"]) * 100 if result["margin"] > 0 else 0
            
            result["strikes_involved"] = [f"Sell {sell_leg['strike']} PE", f"Buy {buy_leg['strike']} PE"]
            result["commentary"] = f"Bullish to neutral strategy collecting credit. Max profit is net credit {net_credit:.2f}."

    elif strategy == "Long Straddle":
        # Buy ATM Call and ATM Put
        buy_call = options[atm_index]
        buy_put = options[atm_index]
        
        result["premium_paid"] = (buy_call['ce_price'] + buy_put['pe_price']) * lot_size
        result["premium_received"] = 0
        
        result["max_profit"] = float('inf') # Theoretically unlimited
        result["max_loss"] = result["premium_paid"]
        result["margin"] = result["premium_paid"]
        result["roi"] = 0 # Cannot calculate fixed ROI for unlimited profit
        
        result["strikes_involved"] = [f"Buy {buy_call['strike']} CE", f"Buy {buy_put['strike']} PE"]
        result["commentary"] = f"Highly volatile directional strategy. Requires strong movement in either direction to overcome net premium paid {result['premium_paid']:.2f}."
            
    else:
        return {"error": "Unsupported strategy"}
        
    # Format numerical values for UI
    result["premium_paid"] = round(result["premium_paid"], 2)
    result["premium_received"] = round(result["premium_received"], 2)
    result["max_profit"] = round(result["max_profit"], 2) if result["max_profit"] != float('inf') else "Unlimited"
    result["max_loss"] = round(result["max_loss"], 2)
    result["roi"] = round(result["roi"], 2)
    
    return result
