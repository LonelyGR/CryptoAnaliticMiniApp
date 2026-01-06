import React, { useState, useEffect, useCallback } from 'react';
import CopyTradingHeader from '../components/CopyTradingHeader';
import PromoBanner from '../components/PromoBanner';
import CryptoCard from '../components/CryptoCard';
import ScreenWrapper from '../components/ScreenWrapper';

// Popular cryptocurrencies to fetch
const CRYPTO_IDS = ['bitcoin', 'ethereum', 'binancecoin', 'solana', 'cardano', 'ripple'];

export default function Home({ user, apiConnected }) {
    const [cryptos, setCryptos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const getMockCryptoData = useCallback(() => {
        // Generate mock sparkline data for fallback
        const generateMockSparkline = (basePrice, change) => {
            const points = 24;
            const data = [];
            for (let i = 0; i < points; i++) {
                const variation = (Math.random() - 0.5) * (change / 100) * 0.3;
                const price = basePrice * (1 + variation * (i / points));
                data.push(price);
            }
            return data;
        };

        return [
            { id: 'bitcoin', name: 'Bitcoin', symbol: 'btc', current_price: 43250.50, price_change_percentage_24h: 2.45, market_cap: 850000000000, image: 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png', sparkline_in_7d: { price: generateMockSparkline(43250.50, 2.45) } },
            { id: 'ethereum', name: 'Ethereum', symbol: 'eth', current_price: 2650.30, price_change_percentage_24h: -1.23, market_cap: 320000000000, image: 'https://assets.coingecko.com/coins/images/279/large/ethereum.png', sparkline_in_7d: { price: generateMockSparkline(2650.30, -1.23) } },
            { id: 'binancecoin', name: 'BNB', symbol: 'bnb', current_price: 315.80, price_change_percentage_24h: 0.85, market_cap: 47000000000, image: 'https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png', sparkline_in_7d: { price: generateMockSparkline(315.80, 0.85) } },
            { id: 'solana', name: 'Solana', symbol: 'sol', current_price: 98.45, price_change_percentage_24h: 3.12, market_cap: 45000000000, image: 'https://assets.coingecko.com/coins/images/4128/large/solana.png', sparkline_in_7d: { price: generateMockSparkline(98.45, 3.12) } },
            { id: 'cardano', name: 'Cardano', symbol: 'ada', current_price: 0.52, price_change_percentage_24h: -0.45, market_cap: 18000000000, image: 'https://assets.coingecko.com/coins/images/975/large/cardano.png', sparkline_in_7d: { price: generateMockSparkline(0.52, -0.45) } },
            { id: 'ripple', name: 'XRP', symbol: 'xrp', current_price: 0.62, price_change_percentage_24h: 1.25, market_cap: 34000000000, image: 'https://assets.coingecko.com/coins/images/44/large/xrp-symbol-white-128.png', sparkline_in_7d: { price: generateMockSparkline(0.62, 1.25) } }
        ];
    }, []);

    const fetchCryptoData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            
            const ids = CRYPTO_IDS.join(',');
            // Request with sparkline=true to get price history data
            const response = await fetch(
                `https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=${ids}&order=market_cap_desc&per_page=10&page=1&sparkline=true&price_change_percentage=24h`
            );
            
            if (!response.ok) {
                throw new Error('Failed to fetch crypto data');
            }
            
            const data = await response.json();
            setCryptos(data);
        } catch (err) {
            console.error('Error fetching crypto data:', err);
            setError('Не удалось загрузить данные о криптовалютах');
            // Fallback to mock data if API fails
            setCryptos(getMockCryptoData());
        } finally {
            setLoading(false);
        }
    }, [getMockCryptoData]);

    useEffect(() => {
        fetchCryptoData();
        // Refresh data every 15 seconds for live updates
        const interval = setInterval(fetchCryptoData, 15000);
        return () => clearInterval(interval);
    }, [fetchCryptoData]);

    const handleDepositClick = () => {
        // Handle deposit action - можно добавить навигацию или другую логику
        // Пока оставляем пустым, так как кнопка в PromoBanner обрабатывает свою логику
    };

    return (
        <ScreenWrapper>
            <CopyTradingHeader user={user} username={user?.first_name} onDepositClick={handleDepositClick} />
            
            <div className="copy-trading-home">
                <PromoBanner onDepositClick={handleDepositClick} />

                {loading ? (
                    <div className="loading-container">
                        <div className="loading-spinner"></div>
                        <p>Загрузка курсов криптовалют...</p>
                    </div>
                ) : (
                    <section className="crypto-rates-section">
                        <div className="section-header">
                            <h2 className="section-title">Курсы криптовалют</h2>
                            <p className="section-subtitle">Актуальные цены и графики</p>
                        </div>

                        {error && (
                            <div className="error-banner">
                                <span>{error}</span>
                                <button onClick={fetchCryptoData}>Повторить</button>
                            </div>
                        )}

                        <div className="crypto-list">
                            {cryptos.map((crypto) => (
                                <CryptoCard key={crypto.id} crypto={crypto} />
                            ))}
                        </div>

                        <button className="view-more-btn" onClick={fetchCryptoData}>
                            Обновить данные
                        </button>
                    </section>
                )}
            </div>
        </ScreenWrapper>
    );
}
