import React, { useState, useEffect, useCallback, useRef } from 'react';
import CopyTradingHeader from '../components/CopyTradingHeader';
// import PromoBanner from '../components/PromoBanner';
import CryptoCard from '../components/CryptoCard';
import ScreenWrapper from '../components/ScreenWrapper';
import { getPosts } from '../services/api';

// Popular cryptocurrencies to fetch from Binance
const BINANCE_SYMBOLS = [
    { symbol: 'BTCUSDT', name: 'Bitcoin', id: 'bitcoin', image: 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png' },
    { symbol: 'ETHUSDT', name: 'Ethereum', id: 'ethereum', image: 'https://assets.coingecko.com/coins/images/279/large/ethereum.png' },
    { symbol: 'BNBUSDT', name: 'BNB', id: 'binancecoin', image: 'https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png' },
    { symbol: 'SOLUSDT', name: 'Solana', id: 'solana', image: 'https://assets.coingecko.com/coins/images/4128/large/solana.png' },
    { symbol: 'ADAUSDT', name: 'Cardano', id: 'cardano', image: 'https://assets.coingecko.com/coins/images/975/large/cardano.png' },
    { symbol: 'XRPUSDT', name: 'XRP', id: 'ripple', image: 'https://assets.coingecko.com/coins/images/44/large/xrp-symbol-white-128.png' }
];

export default function Home({ user, apiConnected, dbUser }) {
    const [cryptos, setCryptos] = useState([]);
    const [currentCryptoIndex, setCurrentCryptoIndex] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [aboutModalOpen, setAboutModalOpen] = useState(false);
    const [posts, setPosts] = useState([]);
    // Admin actions were moved to backend admin panel (/admin)
    const touchStartX = useRef(null);
    const touchEndX = useRef(null);

    // Mini app: no admin actions here (use backend admin panel)

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
            setError(null);
            
            // Fetch 24hr ticker data for all symbols
            const tickerPromises = BINANCE_SYMBOLS.map(async (crypto) => {
                try {
                    const tickerResponse = await fetch(
                        `https://api.binance.com/api/v3/ticker/24hr?symbol=${crypto.symbol}`
                    );
                    if (!tickerResponse.ok) throw new Error('Ticker failed');
                    const tickerData = await tickerResponse.json();
                    
                    // Fetch klines for sparkline (last 24 hours, 1 hour intervals = 24 points)
                    const klinesResponse = await fetch(
                        `https://api.binance.com/api/v3/klines?symbol=${crypto.symbol}&interval=1h&limit=24`
                    );
                    let sparklineData = [];
                    if (klinesResponse.ok) {
                        const klinesData = await klinesResponse.json();
                        sparklineData = klinesData.map(k => parseFloat(k[4])); // Close price
                    }
                    
                    return {
                        id: crypto.id,
                        name: crypto.name,
                        symbol: crypto.symbol.replace('USDT', '').toLowerCase(),
                        current_price: parseFloat(tickerData.lastPrice),
                        price_change_percentage_24h: parseFloat(tickerData.priceChangePercent),
                        market_cap: parseFloat(tickerData.quoteVolume) * parseFloat(tickerData.lastPrice), // Approximate
                        image: crypto.image,
                        sparkline_in_7d: { price: sparklineData }
                    };
                } catch (err) {
                    console.error(`Error fetching ${crypto.symbol}:`, err);
                    return null;
                }
            });
            
            const results = await Promise.all(tickerPromises);
            const validResults = results.filter(r => r !== null);
            
            if (validResults.length > 0) {
                setCryptos(validResults);
            } else {
                throw new Error('No data received');
            }
        } catch (err) {
            console.error('Error fetching crypto data:', err);
            setError('Не удалось загрузить данные о криптовалютах');
            // Fallback to mock data if API fails
            setCryptos(getMockCryptoData());
        } finally {
            setLoading(false);
        }
    }, [getMockCryptoData]);

    // Загрузка постов
    const loadPosts = useCallback(async () => {
        if (!apiConnected) return;
        try {
            const data = await getPosts();
            setPosts(data || []);
        } catch (error) {
            console.error('Failed to load posts:', error);
            setPosts([]);
        }
    }, [apiConnected]);

    useEffect(() => {
        fetchCryptoData();
        loadPosts();
        
        // Обновление данных криптовалют каждые 5 секунд (Binance API быстрее чем CoinGecko)
        const cryptoInterval = setInterval(() => {
            fetchCryptoData();
        }, 5000);
        
        return () => clearInterval(cryptoInterval);
    }, [fetchCryptoData, loadPosts]);

    // Swipe handlers для слайдера криптовалют
    const minSwipeDistance = 50;

    const onTouchStart = (e) => {
        touchEndX.current = null;
        touchStartX.current = e.targetTouches[0].clientX;
    };

    const onTouchMove = (e) => {
        touchEndX.current = e.targetTouches[0].clientX;
    };

    const onTouchEnd = () => {
        if (!touchStartX.current || !touchEndX.current || cryptos.length === 0) return;
        
        const distance = touchStartX.current - touchEndX.current;
        const isLeftSwipe = distance > minSwipeDistance;
        const isRightSwipe = distance < -minSwipeDistance;

        if (isLeftSwipe && currentCryptoIndex < cryptos.length - 1) {
            setCurrentCryptoIndex(currentCryptoIndex + 1);
        }
        if (isRightSwipe && currentCryptoIndex > 0) {
            setCurrentCryptoIndex(currentCryptoIndex - 1);
        }
        
        touchStartX.current = null;
        touchEndX.current = null;
    };

    const handleDepositClick = () => {
        // Handle deposit action
    };

    // Creating/updating/deleting posts is handled in backend admin panel.

    const formatDate = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <ScreenWrapper>
            <CopyTradingHeader user={user} username={user?.first_name} onDepositClick={handleDepositClick} />
            <br />
            <div className="copy-trading-home">
                <section className="neo-dashboard-section">
                    <div className="neo-dashboard">
                        <div className="neo-dashboard-header">
                            <div className="neo-kicker">Платформа</div>
                            <div className="neo-title-row">
                                <h2 className="neo-title">Crypto Sensei</h2>
                            </div>
                            <p className="neo-subtitle">
                                Умная панель управления активами с прозрачной аналитикой и защитой капитала.
                            </p>
                        </div>

                        <div className="neo-grid">
                            <button
                                type="button"
                                className="neo-card neo-card--hero"
                                onClick={() => setAboutModalOpen(true)}
                            >
                                <div className="neo-card-title">Кто мы</div>
                                <div className="neo-card-subtitle">Подробно о проекте</div>
                                <div className="neo-card-cta">Открыть описание</div>
                                <div className="neo-card-glow" />
                            </button>
                    </div>


                        {aboutModalOpen && (
                            <div
                                className="neo-modal-overlay"
                                role="dialog"
                                aria-modal="true"
                                aria-label="Описание проекта"
                                onClick={() => setAboutModalOpen(false)}
                            >
                                <div className="neo-modal-card" onClick={(event) => event.stopPropagation()}>
                                    <button
                                        type="button"
                                        className="neo-modal-back"
                                        onClick={() => setAboutModalOpen(false)}
                                        aria-label="Назад"
                                    >
                                        ←
                                    </button>
                                    <br />
                                    <div className="neo-modal-body">
                                        <h2 className="neo-modal-title">Кто мы</h2>
                                        <p className="neo-modal-lead">
                                            Мы создаем интеллектуальную экосистему для управления криптопортфелем и автоматизации
                                            сделок в режиме реального времени.
                                        </p>

                                        <div className="neo-modal-section">
                                            <h3>Что мы предлагаем</h3>
                                            <ul>
                                                <li>Гибкую стратегию распределения активов с динамической защитой капитала.</li>
                                                <li>Синхронизацию DeFi-инструментов и торговых ботов в единой панели.</li>
                                                <li>Прозрачную аналитику рисков и скоростную обработку сигналов.</li>
                                            </ul>
                                        </div>

                                        <div className="neo-modal-section">
                                            <h3>Почему это работает</h3>
                                            <ul>
                                                <li>Мы используем матричный подход к контролю волатильности.</li>
                                                <li>Автоматизация снижает эмоциональные решения и усиливает дисциплину.</li>
                                                <li>Глубокая фильтрация данных дает преимущество в быстрых циклах рынка.</li>
                                            </ul>
                                        </div>

                                        <div className="neo-modal-section">
                                            <h3>Почему выбирают нас</h3>
                                            <ul>
                                                <li>Команда с опытом построения трейдинговых систем и финтех-продуктов.</li>
                                                <li>Детализированные отчеты и поддержка 24/7.</li>
                                                <li>Фокус на безопасности, прозрачности и росте капитала клиента.</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </section>

                {/* <PromoBanner onDepositClick={handleDepositClick} /> */}

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
                            </div>
                        )}

                        {cryptos.length > 0 && (
                            <div 
                                className="crypto-slider-container"
                                onTouchStart={onTouchStart}
                                onTouchMove={onTouchMove}
                                onTouchEnd={onTouchEnd}
                            >
                                <div className="crypto-slider-wrapper">
                                    <CryptoCard crypto={cryptos[currentCryptoIndex]} />
                                </div>
                                
                                {cryptos.length > 1 && (
                                    <div className="crypto-indicators">
                                        {cryptos.map((_, index) => (
                                            <button
                                                key={index}
                                                className={`crypto-dot ${index === currentCryptoIndex ? 'active' : ''}`}
                                                onClick={() => setCurrentCryptoIndex(index)}
                                            />
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                    </section>
                )}

                {/* Админ‑действия (создание/удаление постов) перенесены в backend админ‑панель (/admin) */}

                {/* Список постов */}
                <section className="posts-list-section">
                    <h2 className="section-title">Новости</h2>
                    {!apiConnected ? (
                        <div className="error-banner">
                            Сервер недоступен. Новости не могут быть загружены.
                        </div>
                    ) : posts.length === 0 ? (
                        <div className="empty-state">
                            <p>Нет новостей</p>
                        </div>
                    ) : (
                        <div className="posts-list">
                            {posts.map(post => (
                                <div key={post.id} className="post-card">
                                    <div className="post-header">
                                        <h3 className="post-title">{post.title}</h3>
                                    </div>
                                    <p className="post-content">{post.content}</p>
                                    <div className="post-date">
                                        {formatDate(post.created_at)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            </div>
        </ScreenWrapper>
    );
}
