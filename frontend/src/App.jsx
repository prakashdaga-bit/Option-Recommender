import React, { useState } from 'react';
import axios from 'axios';
import TradeForm from './components/TradeForm';
import StrategyCard from './components/StrategyCard';
import { Target } from 'lucide-react';

function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  const handleAnalyze = async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('http://localhost:8000/analyze', payload);
      setResults(response.data.data);
    } catch (err) {
      setError(err.message || 'Failed to fetch analysis');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header style={{ textAlign: 'center', marginBottom: '3rem', marginTop: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }}>
          <div style={{
            background: 'var(--glass-bg)',
            padding: '1rem',
            borderRadius: '20px',
            border: '1px solid var(--glass-border)',
            boxShadow: '0 0 30px var(--primary-glow)'
          }}>
            <Target size={48} className="text-primary" />
          </div>
        </div>
        <h1 style={{ fontSize: '3.5rem', letterSpacing: '-1px' }}>
          F&O <span className="title-gradient">Options Analyzer</span>
        </h1>
        <p className="text-muted" style={{ fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto' }}>
          Advanced strategy generation, predictive analytics, and risk management for the Indian Stock Market.
        </p>
      </header>

      <TradeForm onAnalyze={handleAnalyze} loading={loading} />

      {error && (
        <div style={{ background: 'var(--danger-bg)', border: '1px solid var(--danger)', padding: '1rem', borderRadius: '12px', color: 'var(--danger)', marginBottom: '2rem' }}>
          <strong>Error:</strong> {error}. Make sure the FastAPI backend is running on port 8000.
        </div>
      )}

      {loading && <div className="spinner"></div>}

      {!loading && results.length > 0 && (
        <div className="grid flex-col gap-6">
          <h2 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ width: '8px', height: '32px', background: 'var(--primary)', borderRadius: '4px', display: 'inline-block' }}></span>
            Analysis Results
          </h2>
          {results.map((result, index) => (
            <StrategyCard key={index} result={result} />
          ))}
        </div>
      )}

      {!loading && results.length === 0 && !error && (
        <div style={{ textAlign: 'center', opacity: 0.5, marginTop: '4rem' }}>
          <div className="glass-panel" style={{ display: 'inline-block', borderStyle: 'dashed' }}>
            No analysis generated yet. Enter parameters above.
          </div>
        </div>
      )}

    </div>
  );
}

export default App;
