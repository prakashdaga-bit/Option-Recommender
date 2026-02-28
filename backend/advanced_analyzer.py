import math

class AdvancedOptionsAnalyzer:
    """
    Analyzes historical data and options chains to provide robust, data-driven
    recommendations for options trading.
    """
    
    def __init__(self):
        # We'd typically initialize indicators or database connections here
        pass

    def calculate_pcr(self, chain):
        """
        Calculates Put-Call Ratio (PCR) from the option chain's implied OI or Volume.
        Since we only have mock premiums right now, we estimate PCR using premium decay 
        differences as a stand-in for demand.
        """
        total_pe_val = sum([opt['pe_price'] for opt in chain])
        total_ce_val = sum([opt['ce_price'] for opt in chain])
        
        if total_ce_val == 0:
            return 1.0
            
        return total_pe_val / total_ce_val

    def analyze_technicals(self, spot_price):
        """
        Analyzes technical indicators.
        In a real scenario, this would compute moving averages, RSI, and MACD 
        from historical OHLCV data using pandas and the `ta` library.
        For now, we derive a deterministic technical score based on spot price thresholds
        to simulate a predictable engine instead of random values.
        """
        # A deterministic way to simulate indicators for testing
        base_value = spot_price % 100
        
        rsi = 30 + (base_value * 0.4) # Range 30 to 70
        macd = (base_value - 50) / 25.0 # Range -2.0 to 2.0
        
        # Determine Trend
        trend = "Neutral"
        score = 0
        
        if rsi > 60 and macd > 0.5:
            trend = "Bullish"
            score += 2
        elif rsi < 40 and macd < -0.5:
            trend = "Bearish"
            score -= 2
            
        return {"rsi": round(rsi, 2), "macd": round(macd, 2), "trend": trend, "score": score}
        

    def analyze_regime(self, spot_price, chain):
        """
        Combines options data and technical analysis to determine the market regime.
        """
        technicals = self.analyze_technicals(spot_price)
        pcr = self.calculate_pcr(chain)
        
        regime_score = technicals['score']
        
        # Adjust score based on PCR (Contrarian Indicator)
        # PCR > 1.2 is considered oversold (Bullish reversal)
        # PCR < 0.6 is considered overbought (Bearish reversal)
        pcr_signal = "Neutral"
        if pcr > 1.2:
            regime_score += 1
            pcr_signal = "Oversold (Bullish Reversal Potential)"
        elif pcr < 0.6:
            regime_score -= 1
            pcr_signal = "Overbought (Bearish Reversal Potential)"
            
        # Determine final regime
        regime = "Neutral Consolidation"
        signal = "Neutral"
        
        if regime_score >= 2:
            regime = "Strong Bullish Trend"
            signal = "Bullish"
        elif regime_score == 1:
            regime = "Mildly Bullish"
            signal = "Mild Bullish"
        elif regime_score <= -2:
            regime = "Strong Bearish Trend"
            signal = "Bearish"
        elif regime_score == -1:
            regime = "Mildly Bearish"
            signal = "Mild Bearish"
            
        return {
            "prediction_text": f"Regime: {regime}. Technicals indicate {technicals['trend']} (RSI: {technicals['rsi']}, MACD: {technicals['macd']}). Options PCR is {round(pcr, 2)} indicating {pcr_signal}.",
            "signal": signal,
            "regime_score": regime_score,
            "pcr": round(pcr, 2),
            "seller_recommendation": self.recommend_seller_strategy(regime_score, spot_price, chain)
        }
        
    def recommend_seller_strategy(self, regime_score, spot_price, chain):
        """
        Calculates every possible option seller combination within the available chain
        to find options that have a Probability of Profit (POP) > 70% based on Delta
        and a positive Expected Value (EV).
        """
        def get_bs_delta(spot, strike, opt_type):
            # Standard assumptions for Delta calc: 7 days to expiry, 20% IV, 7% risk-free rate
            t = 7 / 365.0
            vol = 0.20
            r = 0.07
            if spot <= 0 or strike <= 0:
                return 0.5
            
            d1 = (math.log(spot / strike) + (r + 0.5 * vol**2) * t) / (vol * math.sqrt(t))
            cdf_d1 = (1.0 + math.erf(d1 / math.sqrt(2.0))) / 2.0
            
            if opt_type == 'CE':
                return cdf_d1
            else:
                return cdf_d1 - 1.0

        def calculate_delta_pop(spot, short_strike, opt_type):
            delta = get_bs_delta(spot, short_strike, opt_type)
            return 100 * (1 - abs(delta))

        sorted_chain = sorted(chain, key=lambda x: x['strike'])
        valid_trades = []
        lot_size = 50 
        
        if regime_score >= 1: 
            strategy_name = "Bull Put Spread"
            rationale = "Bullish trend detected. Selling Puts below the spot price to collect premium."
            valid_strikes = [opt for opt in sorted_chain if opt['strike'] < spot_price]
            
            for i in range(len(valid_strikes)):
                for j in range(i): 
                    sell_leg = valid_strikes[i]
                    buy_leg = valid_strikes[j]
                    
                    credit_per_share = sell_leg['pe_price'] - buy_leg['pe_price']
                    if credit_per_share <= 0: continue
                        
                    strike_width = sell_leg['strike'] - buy_leg['strike']
                    net_credit = credit_per_share * lot_size
                    max_loss = (strike_width * lot_size) - net_credit
                    if max_loss <= 0: continue
                        
                    # Calculate Delta POP
                    pop_pct = calculate_delta_pop(spot_price, sell_leg['strike'], 'PE')
                    pop_decimal = pop_pct / 100.0
                    
                    # Calculate Expected Value (EV)
                    ev = (pop_decimal * net_credit) - ((1.0 - pop_decimal) * max_loss)
                    
                    if 75 <= pop_pct <= 90 and max_loss <= 4 * net_credit and ev > 0:
                        rr_ratio = net_credit / max_loss
                        valid_trades.append({
                            "strikes": f"Sell {sell_leg['strike']} PE, Buy {buy_leg['strike']} PE",
                            "net_credit": round(net_credit, 2),
                            "max_loss": round(max_loss, 2),
                            "rr_ratio": round(rr_ratio, 2),
                            "pop": round(pop_pct, 1),
                            "ev": round(ev, 2)
                        })
                        
        elif regime_score <= -1: 
            strategy_name = "Bear Call Spread"
            rationale = "Bearish trend detected. Selling Calls above the spot price to collect premium safely."
            valid_strikes = [opt for opt in sorted_chain if opt['strike'] > spot_price]
            
            for i in range(len(valid_strikes)):
                for j in range(i+1, len(valid_strikes)): 
                    sell_leg = valid_strikes[i]
                    buy_leg = valid_strikes[j]
                    
                    credit_per_share = sell_leg['ce_price'] - buy_leg['ce_price']
                    if credit_per_share <= 0: continue
                        
                    strike_width = buy_leg['strike'] - sell_leg['strike']
                    net_credit = credit_per_share * lot_size
                    max_loss = (strike_width * lot_size) - net_credit
                    if max_loss <= 0: continue
                        
                    # Calculate Delta POP
                    pop_pct = calculate_delta_pop(spot_price, sell_leg['strike'], 'CE')
                    pop_decimal = pop_pct / 100.0
                    
                    # Calculate Expected Value (EV)
                    ev = (pop_decimal * net_credit) - ((1.0 - pop_decimal) * max_loss)
                    
                    if 75 <= pop_pct <= 90 and max_loss <= 4 * net_credit and ev > 0:
                        rr_ratio = net_credit / max_loss
                        valid_trades.append({
                            "strikes": f"Sell {sell_leg['strike']} CE, Buy {buy_leg['strike']} CE",
                            "net_credit": round(net_credit, 2),
                            "max_loss": round(max_loss, 2),
                            "rr_ratio": round(rr_ratio, 2),
                            "pop": round(pop_pct, 1),
                            "ev": round(ev, 2)
                        })
                        
        else: 
            strategy_name = "Iron Condor"
            rationale = "Neutral consolidation detected. Selling an OTM Call Spread and OTM Put Spread."
            puts = [opt for opt in sorted_chain if opt['strike'] < spot_price]
            calls = [opt for opt in sorted_chain if opt['strike'] > spot_price]
            
            valid_put_spreads = []
            for i in range(len(puts)):
                for j in range(i):
                    cps = puts[i]['pe_price'] - puts[j]['pe_price']
                    if cps <= 0: continue
                    width = puts[i]['strike'] - puts[j]['strike']
                    pop = calculate_delta_pop(spot_price, puts[i]['strike'], 'PE')
                    if pop >= 75:
                        valid_put_spreads.append((puts[i], puts[j], cps, width, pop))
            
            valid_call_spreads = []
            for i in range(len(calls)):
                for j in range(i+1, len(calls)):
                    cps = calls[i]['ce_price'] - calls[j]['ce_price']
                    if cps <= 0: continue
                    width = calls[j]['strike'] - calls[i]['strike']
                    pop = calculate_delta_pop(spot_price, calls[i]['strike'], 'CE')
                    if pop >= 75:
                        valid_call_spreads.append((calls[i], calls[j], cps, width, pop))
            
            for ps in valid_put_spreads:
                for cs in valid_call_spreads:
                    total_credit_per_share = ps[2] + cs[2]
                    max_width = max(ps[3], cs[3])
                    net_credit = total_credit_per_share * lot_size
                    max_loss = (max_width * lot_size) - net_credit
                    if max_loss <= 0: continue
                    
                    # For Iron Condor, approximate POP as the product of both sides succeeding
                    # or conservatively take the lowest probability side. We'll take the lowest.
                    pop_pct = min(ps[4], cs[4])
                    pop_decimal = pop_pct / 100.0
                    
                    ev = (pop_decimal * net_credit) - ((1.0 - pop_decimal) * max_loss)
                    
                    if 75 <= pop_pct <= 90 and max_loss <= 4 * net_credit and ev > 0:
                        rr_ratio = net_credit / max_loss
                        valid_trades.append({
                            "strikes": f"Puts: Sell {ps[0]['strike']}/Buy {ps[1]['strike']} | Calls: Sell {cs[0]['strike']}/Buy {cs[1]['strike']}",
                            "net_credit": round(net_credit, 2),
                            "max_loss": round(max_loss, 2),
                            "rr_ratio": round(rr_ratio, 2),
                            "pop": round(pop_pct, 1),
                            "ev": round(ev, 2)
                        })

        if not valid_trades:
            return {
                "strategy": "No Optimal Strategy Found",
                "rationale": "Could not find any strategies with 75-90% PoP, positive EV, and Max Loss under 4x.",
                "options": []
            }
            
        # Sort entirely by highest Expected Value (EV) first
        valid_trades.sort(key=lambda x: x['ev'], reverse=True)
        top_10 = valid_trades[:10]
            
        return {
            "strategy": strategy_name,
            "rationale": rationale + " Showing top 10 combinations strictly sorted by Highest Positive Expected Value (EV).",
            "options": top_10
        }
