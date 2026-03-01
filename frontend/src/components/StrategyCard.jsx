import React from 'react';
import { TrendingUp, TrendingDown, Minus, Info, Zap, AlertTriangle, IndianRupee } from 'lucide-react';

export default function StrategyCard({ result }) {
  const { stock, spot, prediction, signal, stats, seller_recommendation, sentiment } = result;

  const isBullish = signal === 'Bullish';
  const isBearish = signal === 'Bearish';

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

      {/* Header Profile */}
      <div className="flex justify-between items-center" style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1rem' }}>
        <div>
          <h3 style={{ fontSize: '1.5rem', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {stock}
            <span className={`badge ${isBullish ? 'success' : isBearish ? 'danger' : 'neutral'}`}>
              {signal}
            </span>
          </h3>
          <div className="text-muted" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem' }}>
            <IndianRupee size={16} />
            <span style={{ fontFamily: 'Space Grotesk', fontWeight: '600', color: 'white' }}>{spot.toLocaleString()}</span>
            <span>(LTP)</span>
            {result.pcr && (
              <>
                <span style={{ margin: '0 0.5rem', opacity: 0.3 }}>|</span>
                <span style={{ fontWeight: '600', color: result.pcr > 1.2 ? 'var(--success)' : result.pcr < 0.6 ? 'var(--danger)' : 'white' }}>PCR: {result.pcr}</span>
              </>
            )}
          </div>
        </div>

        {/* Signal Icon */}
        <div style={{
          background: isBullish ? 'var(--success-bg)' : isBearish ? 'var(--danger-bg)' : 'rgba(255,255,255,0.05)',
          padding: '1rem',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: isBullish ? 'var(--success)' : isBearish ? 'var(--danger)' : 'white'
        }}>
          {isBullish ? <TrendingUp size={28} /> : isBearish ? <TrendingDown size={28} /> : <Minus size={28} />}
        </div>
      </div>

      {/* Prediction Engine text */}
      <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '12px', borderLeft: `4px solid ${isBullish ? 'var(--success)' : isBearish ? 'var(--danger)' : 'var(--warning)'}` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', fontWeight: '600' }}>
          <Zap size={18} className="text-warning" />
          Prediction Engine
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', lineHeight: '1.5' }}>
          {prediction}
        </p>
      </div>

      {/* Option Seller Recommendation */}
      {seller_recommendation && (
        <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', fontWeight: '600', color: 'var(--text-main)' }}>
            <AlertTriangle size={18} className="text-warning" />
            Seller Recommendation: {seller_recommendation.strategy}
          </div>

          {seller_recommendation.options?.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1rem', maxHeight: '420px', overflowY: 'auto', paddingRight: '0.5rem', scrollbarWidth: 'thin' }}>
              {seller_recommendation.options.map((opt, idx) => (
                <div key={idx} style={{ background: 'rgba(0,0,0,0.2)', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                  <div className="flex justify-between items-center" style={{ marginBottom: '0.5rem' }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: 'bold', fontFamily: 'Space Grotesk' }}>
                      <span style={{ color: 'var(--text-muted)', marginRight: '6px' }}>#{idx + 1}</span>
                      {opt.strikes}
                    </div>
                    <div className="badge success" style={{ fontSize: '0.75rem', display: 'flex', gap: '6px', alignItems: 'center' }}>
                      <span>{opt.pop}% WIN RATE</span>
                    </div>
                  </div>
                  <div className="grid grid-cols-4 gap-3" style={{ fontFamily: 'Space Grotesk' }}>
                    <div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Net Credit</div>
                      <div className="text-success" style={{ fontSize: '0.9rem', fontWeight: '600' }}>₹{opt.net_credit?.toLocaleString()}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Max Loss</div>
                      <div className="text-danger" style={{ fontSize: '0.9rem', fontWeight: '600' }}>₹{opt.max_loss?.toLocaleString()}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Reward/Risk</div>
                      <div className="text-warning" style={{ fontSize: '0.9rem', fontWeight: '600' }}>{opt.rr_ratio}x</div>
                    </div>
                    <div style={{ background: 'rgba(255,255,255,0.05)', padding: '4px 8px', borderRadius: '4px', borderLeft: '2px solid var(--success)' }}>
                      <div style={{ fontSize: '0.7rem', color: 'white', textTransform: 'uppercase' }}>Exp. Value (EV)</div>
                      <div className="text-success" style={{ fontSize: '0.9rem', fontWeight: '600' }}>+₹{opt.ev?.toLocaleString()}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.5', margin: 0 }}>
            {seller_recommendation.rationale}
          </p>
        </div>
      )}

      {/* Sentiment & News Analysis */}
      {sentiment && (
        <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: '600', color: 'var(--text-main)' }}>
              <Info size={18} className="text-muted" />
              Live News Sentiment
            </div>
            <span className={`badge ${sentiment.score > 0.1 ? 'success' : sentiment.score < -0.1 ? 'danger' : 'neutral'}`} style={{ fontSize: '0.8rem' }}>
              {sentiment.mood} ({sentiment.score})
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {sentiment.headlines?.slice(0, 3).map((news, idx) => (
              <div key={idx} style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.7)', lineHeight: '1.4', display: 'flex', gap: '0.5rem' }}>
                <span style={{ color: news.sentiment === 'Positive' ? 'var(--success)' : news.sentiment === 'Negative' ? 'var(--danger)' : 'var(--text-muted)' }}>•</span>
                {news.title}
              </div>
            ))}
          </div>

          {sentiment.catalysts?.length > 0 && (
            <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginRight: '0.5rem' }}>Catalysts:</span>
              {sentiment.catalysts.map((cat, idx) => (
                <span key={idx} style={{ fontSize: '0.75rem', background: 'rgba(255,255,255,0.1)', padding: '2px 8px', borderRadius: '4px' }}>{cat}</span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Stats Grid */}
      <div>
        <h4 className="title-gradient" style={{ marginBottom: '1rem' }}>{stats.strategy_name} Parameters</h4>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="stat-box">
            <div className="stat-label">Net Premium Paid</div>
            <div className={`stat-value ${stats.premium_paid > stats.premium_received ? 'text-danger' : 'text-success'}`}>
              ₹{stats.premium_paid.toLocaleString()}
            </div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Net Premium Recv</div>
            <div className="stat-value text-success">
              ₹{stats.premium_received.toLocaleString()}
            </div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Max Profit</div>
            <div className="stat-value text-success">
              {stats.max_profit === 'Unlimited' ? 'Unlimited' : `₹${stats.max_profit.toLocaleString()}`}
            </div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Max Loss</div>
            <div className="stat-value text-danger">
              ₹{stats.max_loss.toLocaleString()}
            </div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Est Margin Req</div>
            <div className="stat-value">
              ₹{stats.margin.toLocaleString()}
            </div>
          </div>
          <div className="stat-box">
            <div className="stat-label">ROI (on Margin)</div>
            <div className={`stat-value ${stats.roi > 0 ? 'text-success' : 'text-warning'}`}>
              {stats.roi > 0 ? `${stats.roi}%` : 'N/A'}
            </div>
          </div>
        </div>
      </div>

      {/* Legs & Commentary */}
      <div className="grid grid-cols-2" style={{ marginTop: '0.5rem' }}>
        <div>
          <h5 style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Executions (Strikes)</h5>
          <div className="flex flex-col gap-2">
            {stats.strikes_involved.map((strike, idx) => (
              <div key={idx} style={{ background: 'rgba(255,255,255,0.05)', padding: '0.5rem 1rem', borderRadius: '8px', fontSize: '0.9rem', fontFamily: 'Space Grotesk' }}>
                {strike}
              </div>
            ))}
          </div>
        </div>
        <div>
          <h5 style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Trade Commentary</h5>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', lineHeight: '1.5' }}>
            {stats.commentary}
          </p>
        </div>
      </div>

    </div>
  );
}
