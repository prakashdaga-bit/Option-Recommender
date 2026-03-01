import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { AlertTriangle, CheckCircle, RefreshCcw, TrendingUp, TrendingDown, Clock } from 'lucide-react';

import { API_URL } from '../config';

const PositionsDashboard = () => {
    const [positions, setPositions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchPositions = async () => {
        setLoading(true);
        setError(null);
        try {
            // Use environment variable or default to localhost for dev
            const response = await axios.get(`${API_URL}/positions`);
            setPositions(response.data.data);
        } catch (err) {
            setError(err.message || "Failed to load positions.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPositions();
    }, []);

    // Helper to determine row style based on action
    const getRowStyle = (action) => {
        if (action === "EXIT") return { background: "rgba(255, 69, 58, 0.15)", borderLeft: "4px solid var(--danger)" };
        return { background: "rgba(48, 209, 88, 0.1)", borderLeft: "4px solid var(--success)" };
    };

    return (
        <div className="section-container" style={{ marginTop: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2>
                    <span style={{ color: 'var(--primary)' }}>Live </span>
                    Positions Monitor
                </h2>
                <button
                    onClick={fetchPositions}
                    className="button-primary"
                    style={{ padding: '0.6rem 1.2rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}
                >
                    <RefreshCcw size={18} /> Refresh
                </button>
            </div>

            {loading && <div className="spinner" style={{ margin: '3rem auto' }}></div>}

            {error && (
                <div style={{ padding: '1rem', background: 'var(--danger-bg)', borderRadius: '8px', color: 'var(--danger)', marginBottom: '1rem', display: 'flex', gap: '0.5rem' }}>
                    <AlertTriangle size={20} />
                    {error}
                </div>
            )}

            {!loading && !error && positions.length === 0 && (
                <div style={{ textAlign: 'center', padding: '3rem', opacity: 0.6 }}>
                    No open positions found in Zerodha.
                </div>
            )}

            {!loading && positions.length > 0 && (
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {positions.map((pos, idx) => (
                        <div key={idx} className="glass-panel" style={{
                            ...getRowStyle(pos.action),
                            padding: '1.25rem',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.5rem',
                            transition: 'all 0.2s ease'
                        }}>
                            {/* Header: Symbol & PnL */}
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div>
                                    <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: '600' }}>{pos.symbol}</h3>
                                    <div style={{ fontSize: '0.9rem', opacity: 0.8, marginTop: '0.25rem' }}>
                                        {pos.qty} qty @ {pos.avg_price.toFixed(2)}
                                    </div>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{
                                        fontWeight: 'bold',
                                        fontSize: '1.2rem',
                                        color: pos.pnl >= 0 ? 'var(--success)' : 'var(--danger)'
                                    }}>
                                        {pos.pnl >= 0 ? '+' : ''}{pos.pnl.toFixed(2)}
                                    </div>
                                    <div style={{ fontSize: '0.8rem', opacity: 0.6 }}>PnL</div>
                                </div>
                            </div>

                            <hr style={{ borderColor: 'rgba(255,255,255,0.1)', margin: '0.5rem 0' }} />

                            {/* Details Grid */}
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.9rem' }}>
                                <div>
                                    <span style={{ opacity: 0.6 }}>LTP: </span>
                                    <strong>{pos.ltp.toFixed(2)}</strong>
                                </div>
                                <div>
                                    <span style={{ opacity: 0.6 }}>Und. Price: </span>
                                    <strong>{pos.underlying_price.toFixed(2)}</strong>
                                </div>
                            </div>

                            {/* Action Banner */}
                            <div style={{
                                marginTop: '0.75rem',
                                padding: '0.75rem',
                                borderRadius: '8px',
                                background: pos.action === "EXIT" ? 'rgba(255, 69, 58, 0.2)' : 'rgba(48, 209, 88, 0.2)',
                                color: pos.action === "EXIT" ? '#ff6b6b' : '#69db7c',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.75rem',
                                fontWeight: '600'
                            }}>
                                {pos.action === "EXIT" ? <AlertTriangle size={20} /> : <CheckCircle size={20} />}

                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <span style={{ textTransform: 'uppercase', letterSpacing: '0.5px' }}>{pos.action}</span>
                                    <span style={{ fontSize: '0.85rem', fontWeight: 'normal', opacity: 0.9 }}>
                                        {pos.reason}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default PositionsDashboard;
