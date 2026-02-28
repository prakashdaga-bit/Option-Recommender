import React, { useState } from 'react';
import { Activity, Search, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';

export default function TradeForm({ onAnalyze, loading }) {
  const [stocks, setStocks] = useState("RELIANCE, TCS, HDFCBANK");
  const [strategy, setStrategy] = useState("Bull Call");
  const handleSubmit = (e) => {
    e.preventDefault();
    const stockList = stocks.split(',').map(s => s.trim()).filter(s => s);
    if (!stockList.length) return;

    onAnalyze({
      stocks: stockList,
      strategy
    });
  };

  return (
    <div className="glass-panel" style={{ marginBottom: "2rem" }}>
      <div className="flex items-center gap-2 mb-6">
        <Activity size={24} className="text-success" />
        <h2>Analysis Parameters</h2>
      </div>

      <form onSubmit={handleSubmit} className="grid grid-cols-2">
        <div style={{ gridColumn: "1 / -1" }}>
          <label>Stock Tickers (comma separated)</label>
          <div className="flex gap-2">
            <Search size={20} className="text-muted" style={{ position: 'absolute', margin: '14px' }} />
            <input
              type="text"
              value={stocks}
              onChange={(e) => setStocks(e.target.value)}
              placeholder="e.g. RELIANCE, TCS, INFY"
              style={{ paddingLeft: '44px' }}
              required
            />
          </div>
        </div>

        <div>
          <label>Options Strategy</label>
          <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
            <option value="Bull Call">Bull Call Spread</option>
            <option value="Bear Call">Bear Call Spread</option>
            <option value="Bull Put">Bull Put Spread</option>
            <option value="Bear Put">Bear Put Spread</option>
            <option value="Long Straddle">Long Straddle</option>
          </select>
        </div>


        <div style={{ gridColumn: "1 / -1", display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
          <button type="submit" className="primary flex items-center gap-2" disabled={loading}>
            {loading ? <span className="spinner" style={{ width: '20px', height: '20px', margin: 0, borderWidth: '2px' }}></span> : <Activity size={20} />}
            {loading ? 'Analyzing...' : 'Generate Analysis'}
          </button>
        </div>
      </form>
    </div>
  );
}
