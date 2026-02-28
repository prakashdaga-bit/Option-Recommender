import yfinance as yf
from textblob import TextBlob
import logging

class SentimentAnalyzer:
    """
    Fetches real-time news headlines using yfinance and scores them
    using Natural Language Processing (TextBlob) to determine market sentiment.
    """
    
    def __init__(self):
        pass
        
    def analyze_ticker(self, symbol):
        """
        Fetches the latest news for a ticker and calculates a blended sentiment score.
        Returns a dict with mood, score, top headlines, and keywords.
        """
        # Format for yfinance (e.g., RELIANCE.NS)
        yf_symbol = symbol
        if "NSE:" in symbol:
            yf_symbol = symbol.replace("NSE:", "") + ".NS"
        elif not symbol.endswith(".NS") and symbol != "NIFTY 50" and symbol != "BANKNIFTY":
            yf_symbol = f"{symbol}.NS"
            
        try:
            ticker = yf.Ticker(yf_symbol)
            news = ticker.news
            
            if not news:
                return self._default_neutral()
                
            headlines = []
            total_polarity = 0.0
            keywords = set()
            
            # Keywords to watch out for in options trading
            catalysts = ["earnings", "dividend", "acquisition", "merger", "lawsuit", "resigns", "guidance"]
            
            for item in news[:5]: # Analyze top 5 recent articles
                title = item.get('title', '')
                if not title:
                    continue
                    
                # NLP Sentiment Scoring
                blob = TextBlob(title)
                polarity = blob.sentiment.polarity
                total_polarity += polarity
                
                headlines.append({
                    "title": title,
                    "sentiment": "Positive" if polarity > 0.1 else "Negative" if polarity < -0.1 else "Neutral"
                })
                
                # Catalyst extraction
                lower_title = title.lower()
                for cat in catalysts:
                    if cat in lower_title:
                        keywords.add(cat.title())
                        
            
            avg_polarity = total_polarity / len(headlines) if headlines else 0
            
            # Determine Mood
            if avg_polarity > 0.15:
                mood = "Highly Positive"
            elif avg_polarity > 0.05:
                mood = "Slightly Positive"
            elif avg_polarity < -0.15:
                mood = "Highly Negative"
            elif avg_polarity < -0.05:
                mood = "Slightly Negative"
            else:
                mood = "Neutral"

            return {
                "score": round(avg_polarity, 2),
                "mood": mood,
                "headlines": headlines,
                "catalysts": list(keywords)
            }
            
        except Exception as e:
            logging.error(f"Failed to fetch sentiment for {yf_symbol}: {e}")
            return self._default_neutral()
            
    def _default_neutral(self):
        return {
            "score": 0.0,
            "mood": "Neutral",
            "headlines": [{"title": "No recent English news detected.", "sentiment": "Neutral"}],
            "catalysts": []
        }

sentiment_service = SentimentAnalyzer()
