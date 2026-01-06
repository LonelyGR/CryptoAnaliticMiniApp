import React, { useMemo } from 'react';

export default function CryptoCard({ crypto }) {
    const formatPrice = (price) => {
        if (price >= 1) {
            return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        } else {
            return price.toFixed(6);
        }
    };

    const formatChange = (change) => {
        const sign = change >= 0 ? '+' : '';
        return `${sign}${change.toFixed(2)}%`;
    };

    const isPositive = crypto.price_change_percentage_24h >= 0;

    // Use real sparkline data from API or generate fallback
    const sparklineData = useMemo(() => {
        // Try to use real sparkline data from CoinGecko API
        if (crypto.sparkline_in_7d?.price && Array.isArray(crypto.sparkline_in_7d.price)) {
            // Use last 24 hours of data (or all if less than 24)
            const data = crypto.sparkline_in_7d.price;
            // Take last 24 points for better visualization
            return data.slice(-24);
        }
        
        // Fallback: generate data based on current price and change
        const points = 24;
        const data = [];
        const basePrice = crypto.current_price;
        const change = crypto.price_change_percentage_24h / 100;
        
        for (let i = 0; i < points; i++) {
            // Simulate price movement over time
            const progress = i / (points - 1);
            const variation = change * progress * 0.5 + (Math.random() - 0.5) * Math.abs(change) * 0.2;
            const price = basePrice * (1 - variation);
            data.push(Math.max(price, basePrice * 0.5)); // Ensure price doesn't go too low
        }
        return data;
    }, [crypto.sparkline_in_7d, crypto.current_price, crypto.price_change_percentage_24h]);

    // Calculate normalized path for SVG
    const { normalizedData, pathData } = useMemo(() => {
        if (!sparklineData || sparklineData.length === 0) {
            return { normalizedData: [], pathData: '' };
        }

        const minPrice = Math.min(...sparklineData);
        const maxPrice = Math.max(...sparklineData);
        const priceRange = maxPrice - minPrice || 1;

        // Normalize data for SVG path
        const normalized = sparklineData.map((price, index) => {
            const x = (index / (sparklineData.length - 1)) * 100;
            const y = 100 - ((price - minPrice) / priceRange) * 100;
            return { x, y, price };
        });

        const path = normalized.map((point, index) => 
            index === 0 ? `M ${point.x},${point.y}` : `L ${point.x},${point.y}`
        ).join(' ');

        return { 
            normalizedData: normalized, 
            pathData: path 
        };
    }, [sparklineData]);

    return (
        <div className="crypto-card">
            <div className="crypto-header">
                <div className="crypto-info">
                    <div className="crypto-icon">
                        {crypto.image ? (
                            <img 
                                src={crypto.image} 
                                alt={crypto.name}
                                onError={(e) => {
                                    e.target.style.display = 'none';
                                    const fallback = e.target.parentElement.querySelector('.crypto-icon-fallback');
                                    if (fallback) {
                                        fallback.style.display = 'flex';
                                    }
                                }}
                            />
                        ) : null}
                        <div className="crypto-icon-fallback" style={{ display: crypto.image ? 'none' : 'flex' }}>
                            {crypto.symbol?.toUpperCase().charAt(0) || '?'}
                        </div>
                    </div>
                    <div className="crypto-name-section">
                        <h3 className="crypto-name">{crypto.name}</h3>
                        <span className="crypto-symbol">{crypto.symbol?.toUpperCase()}</span>
                    </div>
                </div>
                <div className={`crypto-change ${isPositive ? 'positive' : 'negative'}`}>
                    {formatChange(crypto.price_change_percentage_24h)}
                </div>
            </div>

            <div className="crypto-price-section">
                <div className="crypto-price">
                    ${formatPrice(crypto.current_price)}
                </div>
                <div className="crypto-market-cap">
                    MCap: ${(crypto.market_cap / 1e9).toFixed(2)}B
                </div>
            </div>

            <div className="crypto-chart">
                {normalizedData.length > 0 ? (
                    <svg viewBox="0 0 100 40" className="sparkline-svg" preserveAspectRatio="none">
                        <defs>
                            <linearGradient id={`gradient-${crypto.id}`} x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stopColor={isPositive ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'} />
                                <stop offset="100%" stopColor={isPositive ? 'rgba(34, 197, 94, 0)' : 'rgba(239, 68, 68, 0)'} />
                            </linearGradient>
                        </defs>
                        {/* Area under the line */}
                        <path
                            d={`${pathData} L 100,100 L 0,100 Z`}
                            fill={`url(#gradient-${crypto.id})`}
                            className="sparkline-area"
                        />
                        {/* Line */}
                        <path
                            d={pathData}
                            fill="none"
                            stroke={isPositive ? '#22c55e' : '#ef4444'}
                            strokeWidth="1.5"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            className="sparkline-line"
                        />
                    </svg>
                ) : (
                    <div className="chart-placeholder">Загрузка графика...</div>
                )}
            </div>
        </div>
    );
}

