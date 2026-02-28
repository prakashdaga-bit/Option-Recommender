import os
import logging
from kiteconnect import KiteConnect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class KiteService:
    """
    Live service to interact with the Zerodha Kite Connect API.
    """
    def __init__(self):
        self.api_key = os.getenv("KITE_API_KEY")
        self.api_secret = os.getenv("KITE_API_SECRET")
        self.access_token = os.getenv("KITE_ACCESS_TOKEN")
        self.kite = None
        
        if self.api_key and self.access_token:
            try:
                self.kite = KiteConnect(api_key=self.api_key)
                self.kite.set_access_token(self.access_token)
                logging.info("KiteConnect initialized successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize KiteConnect: {e}")
        else:
            logging.warning("Kite API credentials not found in environment.")

    def get_ltp(self, instruments):
        """
        Fetch real Last Traded Price from Zerodha.
        instruments should be structured like ["NSE:RELIANCE", "NSE:TCS"]
        """
        if not self.kite:
            raise Exception("Kite API not initialized")
            
        # Ensure correct formatting for NSE Equities/Indices
        formatted_instruments = []
        for inst in instruments:
            if not ":" in inst:
                formatted_instruments.append(f"NSE:{inst}")
            else:
                formatted_instruments.append(inst)
                
        try:
            return self.kite.quote(formatted_instruments)
        except Exception as e:
            logging.error(f"Error fetching LTP: {e}")
            return {}

    def get_option_chain(self, symbol, current_price, range_min, range_max):
        """
        Fetch real active option chain data from Zerodha within a specific range.
        Note: This requires querying the NFO instruments dump and then fetching live quotes.
        """
        if not self.kite:
            raise Exception("Kite API not initialized")
            
        options_data = []
        try:
            # 1. Fetch all NFO instruments
            # In a production app, this should be cached daily rather than fetched per request
            instruments = self.kite.instruments("NFO")
            
            # 2. Filter for our specific underlying symbol, and only Options (CE/PE)
            # Find closest expiry first
            symbol_instruments = [inst for inst in instruments 
                                if inst['name'] == symbol 
                                and inst['instrument_type'] in ['CE', 'PE'] 
                                and range_min <= inst['strike'] <= range_max]
            
            if not symbol_instruments:
                return []
                
            # Group by expiry date, then map strikes
            expiries = sorted(list(set([inst['expiry'] for inst in symbol_instruments])))
            current_expiry = expiries[0] # Just look at the nearest expiry
            
            active_options = [inst for inst in symbol_instruments if inst['expiry'] == current_expiry]
            
            # 3. Create a map of Trading Symbols to fetch bulk quotes
            trading_symbols = [f"NFO:{inst['tradingsymbol']}" for inst in active_options]
            
            # Fetch real-time prices for these specific strikes
            quotes = self.kite.quote(trading_symbols)
            
            # 4. Parse response into our expected format
            strike_map = {}
            for inst in active_options:
                strike = inst['strike']
                target = f"NFO:{inst['tradingsymbol']}"
                price = quotes.get(target, {}).get("last_price", 0)
                
                if strike not in strike_map:
                    strike_map[strike] = {"strike": strike, "ce_price": 0, "pe_price": 0}
                    
                if inst['instrument_type'] == 'CE':
                    strike_map[strike]['ce_price'] = price
                else:
                    strike_map[strike]['pe_price'] = price
                    
            options_data = list(strike_map.values())
            options_data.sort(key=lambda x: x['strike'])
            
        except Exception as e:
            logging.error(f"Error fetching option chain: {e}")
            
        return options_data

# Initialize singleton
kite_service = KiteService()
