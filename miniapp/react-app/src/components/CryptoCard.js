import React from 'react';

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

    // Sparkline data removed until the chart is rendered.

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

        </div>
    );
}

