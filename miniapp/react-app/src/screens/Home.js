import React, { useState, useEffect, useCallback, useRef } from 'react';
import CopyTradingHeader from '../components/CopyTradingHeader';
// import PromoBanner from '../components/PromoBanner';
import CryptoCard from '../components/CryptoCard';
import ScreenWrapper from '../components/ScreenWrapper';
import PaymentFlow from '../components/PaymentFlow';
import { createBooking, getPosts, getUserByTelegramId } from '../services/api';

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
    const [paymentContext, setPaymentContext] = useState(null);
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

    const resolveManagerLink = () => {
        const raw = (process.env.REACT_APP_MANAGER_TELEGRAM || '').trim();
        if (!raw) return '';
        if (raw.startsWith('http://') || raw.startsWith('https://')) return raw;
        if (raw.startsWith('@')) return `https://t.me/${raw.slice(1)}`;
        return `https://t.me/${raw}`;
    };

    const handleContactManager = () => {
        const url = resolveManagerLink();
        if (!url) {
            alert('Контакт менеджера не настроен (REACT_APP_MANAGER_TELEGRAM)');
            return;
        }
        if (window.Telegram?.WebApp?.openTelegramLink) {
            window.Telegram.WebApp.openTelegramLink(url);
        } else if (window.Telegram?.WebApp?.openLink) {
            window.Telegram.WebApp.openLink(url);
        } else {
            window.open(url, '_blank', 'noopener,noreferrer');
        }
    };

    const handlePay = async () => {
        if (!apiConnected) {
            alert('Сервер недоступен. Оплата временно невозможна.');
            return;
        }

        const telegramId = user?.telegram_id || user?.id;
        if (!telegramId) {
            alert('Пользователь не найден. Перезагрузите мини‑приложение.');
            return;
        }

        try {
            const ensuredDbUser = dbUser || await getUserByTelegramId(telegramId);
            if (!ensuredDbUser?.id) {
                alert('Пользователь не найден в базе данных. Перезагрузите мини‑приложение.');
                return;
            }

            const today = new Date().toISOString().slice(0, 10);
            const booking = await createBooking({
                user_id: ensuredDbUser.id,
                type: 'payment',
                date: today,
                status: 'pending',
                topic: 'Оплата',
                message: 'Оплата 590 USDT (TRC20)',
            });

            setAboutModalOpen(false);
            setPaymentContext({
                orderId: `booking-${booking.id}`,
                amount: 590,
                // NOWPayments: price_currency должен быть фиатом (usd/eur), pay_currency — крипта (usdttrc20)
                // Сумму в USDT покажем в UI (pay_amount придёт от NOWPayments).
                priceCurrency: 'usd',
                title: 'Приобрести продукт',
                orderDescription: 'Crypto Sensei · Приобрести продукт · 590 USDT (TRC20)',
                paymentId: booking?.payment_id || null,
            });
        } catch (e) {
            console.error('Failed to start payment:', e);
            alert('Не удалось создать оплату. Попробуйте позже.');
        }
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

                        <div className="neo-platform-actions">
                            <button
                                type="button"
                                className="neo-platform-btn neo-platform-btn--primary"
                                onClick={handlePay}
                            >
                                Pay · 590 USDT (TRC20)
                            </button>
                            <button
                                type="button"
                                className="neo-platform-btn neo-platform-btn--secondary"
                                onClick={handleContactManager}
                            >
                                Contact Manager
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
                                        <h2 className="neo-modal-title">Концепция торгового бота</h2>
                                        <p className="neo-modal-lead">
                                            Наш торговый бот не основан на прогнозировании направления цены. Алгоритм построен на реальной
                                            механике биржи и логике работы маркет‑мейкеров.
                                        </p>

                                        <div className="neo-modal-section">
                                            <h3>Почему это отличается от классического трейдинга</h3>
                                            <p style={{ margin: 0, color: 'rgba(230, 250, 255, 0.85)', fontSize: 14, lineHeight: 1.6 }}>
                                                В классическом трейдинге результат часто зависит от угадывания движения рынка. Наш бот зарабатывает на
                                                ценовых импульсах, ликвидности и возвратах, которые рынок создаёт постоянно.
                                            </p>
                                        </div>

                                        <div className="neo-modal-section">
                                            <h3>Как формируется движение цены</h3>
                                            <ul>
                                                <li>Бирже и маркет‑мейкерам важны оборот и активность, а не “направление”.</li>
                                                <li>Когда падает ликвидность и активность ордеров — создаётся искусственное движение: добавляется объём и цена ускоряется.</li>
                                                <li>Так формируются пампы, дампы и резкие импульсы — часть нормальной рыночной механики.</li>
                                            </ul>
                                        </div>

                                        <div className="neo-modal-section">
                                            <h3>Стратегия бота</h3>
                                            <ul>
                                                <li>Прибыль формируется как на лонг‑, так и на шорт‑позициях.</li>
                                                <li>Лонг используется как базовая позиция стратегии.</li>
                                                <li>Шорты применяются для извлечения дохода на импульсах и коррекциях.</li>
                                                <li>Алгоритм не требует точного определения «верха» или «низа».</li>
                                            </ul>
                                        </div>

                                        <div className="neo-modal-section">
                                            <h3>Алгоритмический подход</h3>
                                            <ul>
                                                <li>Используется технический анализ и виртуальные средние.</li>
                                                <li>Бот одновременно управляет лонг‑ и шорт‑позициями.</li>
                                                <li>Позиции открываются и закрываются по алгоритму, без эмоций.</li>
                                                <li>При импульсном движении фиксируется прибыль, часть ордеров закрывается, бот выходит из рынка с результатом.</li>
                                            </ul>
                                        </div>

                                        <div className="neo-modal-section">
                                            <h3>Управление рисками</h3>
                                            <ul>
                                                <li>Алгоритм ориентирован на контроль позиции, а не на агрессивный вход.</li>
                                                <li>Если позиция временно уходит против движения — бот улучшает среднюю цену входа и перераспределяет объём по заранее заданной логике.</li>
                                                <li>Это снижает влияние краткосрочной волатильности и сохраняет контроль в нестабильных условиях.</li>
                                            </ul>
                                        </div>

                                        <div className="neo-modal-section">
                                            <h3>Ключевые преимущества</h3>
                                            <ul>
                                                <li>Прибыль формируется с обеих сторон рынка.</li>
                                                <li>Базовая структура стратегии — лонг.</li>
                                                <li>Алгоритм адаптирован под реальную механику биржи.</li>
                                                <li>Минимизация эмоционального и субъективного фактора.</li>
                                            </ul>
                                        </div>

                                        <div className="neo-modal-section">
                                            <h3>Почему стратегия Low / Medium Risk</h3>
                                            <ul>
                                                <li>Используется базовая лонг‑структура, соответствующая долгосрочной логике рынка.</li>
                                                <li>Прибыль распределена между лонгами и шортами без односторонней зависимости.</li>
                                                <li>Нет необходимости угадывать направление рынка.</li>
                                                <li>Риск снижается за счёт усреднения и перераспределения, а не за счёт увеличения плеча.</li>
                                            </ul>
                                            <p style={{ margin: '10px 0 0 0', color: 'rgba(230, 250, 255, 0.75)', fontSize: 13, lineHeight: 1.6 }}>
                                                Итог: алгоритм ориентирован на стабильную работу в разных рыночных фазах, а не на агрессивную спекуляцию.
                                            </p>
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

            {paymentContext && (
                <div className="modal-overlay" onClick={() => setPaymentContext(null)}>
                    <div className="modal-content" onClick={(event) => event.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Приобрести продукт</h2>
                            <button
                                className="modal-close"
                                type="button"
                                onClick={() => setPaymentContext(null)}
                                aria-label="Закрыть"
                            >
                                ×
                            </button>
                        </div>
                        <div className="modal-body">
                            <PaymentFlow
                                orderId={paymentContext.orderId}
                                amount={paymentContext.amount}
                                priceCurrency={paymentContext.priceCurrency}
                                fixedPayCurrency="usdttrc20"
                                paymentId={paymentContext.paymentId}
                                title={paymentContext.title}
                                orderDescription={paymentContext.orderDescription}
                                hideHeader={true}
                            />
                        </div>
                    </div>
                </div>
            )}
        </ScreenWrapper>
    );
}
