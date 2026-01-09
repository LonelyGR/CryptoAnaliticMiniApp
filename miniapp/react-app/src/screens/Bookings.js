import { useState, useEffect } from 'react';
import ScreenWrapper from '../components/ScreenWrapper';
import { getWebinars, createBooking, getUserByTelegramId, getUserBookings, createPayment, getWebinarMaterials } from '../services/api';

function getDaysUntil(dateString) {
    const today = new Date();
    const webinarDate = new Date(dateString);
    const diffTime = webinarDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'Прошел';
    if (diffDays === 0) return 'Сегодня';
    if (diffDays === 1) return 'Завтра';
    return `Через ${diffDays} дн.`;
}

export default function Bookings({ user, apiConnected }) {
    const [webinars, setWebinars] = useState([]);
    const [userBookings, setUserBookings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [bookingStatus, setBookingStatus] = useState({});
    const [materials, setMaterials] = useState({});

    const loadUserBookings = async () => {
        if (!apiConnected) return [];
        const telegramId = user?.telegram_id || user?.id;
        if (!telegramId) return [];
        
        try {
            const bookings = await getUserBookings(telegramId);
            setUserBookings(bookings || []);
            return bookings || [];
        } catch (error) {
            console.error('Failed to load user bookings:', error);
            return [];
        }
    };

    useEffect(() => {
        const loadData = async () => {
            if (apiConnected) {
                try {
                    const webinarsData = await getWebinars();
                    setWebinars(webinarsData || []);
                    
                    // Загружаем записи пользователя
                    await loadUserBookings();
                    
                    // Загружаем материалы для вебинаров
                    const materialsData = {};
                    for (const webinar of webinarsData || []) {
                        try {
                            const mats = await getWebinarMaterials(webinar.id);
                            materialsData[webinar.id] = mats || [];
                        } catch (err) {
                            console.error(`Failed to load materials for webinar ${webinar.id}:`, err);
                            materialsData[webinar.id] = [];
                        }
                    }
                    setMaterials(materialsData);
                } catch (error) {
                    console.error('Failed to load data:', error);
                    setWebinars([]);
                }
            } else {
                setWebinars([]);
            }
            setLoading(false);
        };

        loadData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [apiConnected]);

    const handleBookWebinar = async (webinar) => {
        if (!apiConnected) {
            alert('Не удалось подключиться к серверу');
            return;
        }

        const telegramId = user?.telegram_id || user?.id;
        if (!telegramId) {
            alert('Пользователь не найден. Пожалуйста, перезагрузите приложение.');
            return;
        }

        try {
            const dbUser = await getUserByTelegramId(telegramId);
            if (!dbUser) {
                alert('Пользователь не найден в базе данных. Пожалуйста, перезагрузите приложение.');
                return;
            }

            const booking = await createBooking({
                user_id: dbUser.id,
                webinar_id: webinar.id,
                type: 'webinar',
                date: webinar.date,
                status: 'pending'
            });

            setBookingStatus(prev => ({ ...prev, [webinar.id]: 'booked' }));
            
            // Если вебинар платный, переходим к оплате
            if ((webinar.price_usd && webinar.price_usd > 0) || (webinar.price_eur && webinar.price_eur > 0)) {
                handlePayment(webinar, booking.id);
            } else {
                alert('Вы успешно записались на вебинар!');
                loadUserBookings();
            }
        } catch (error) {
            console.error('Failed to book webinar:', error);
            setBookingStatus(prev => ({ ...prev, [webinar.id]: 'error' }));
            alert('Не удалось записаться на вебинар. Попробуйте позже.');
        }
    };

    const handlePayment = async (webinar, bookingId) => {
        // Здесь должна быть интеграция с платежной системой
        // Пока делаем симуляцию оплаты
        const priceText = [];
        if (webinar.price_usd && webinar.price_usd > 0) {
            priceText.push(`$${webinar.price_usd}`);
        }
        if (webinar.price_eur && webinar.price_eur > 0) {
            priceText.push(`€${webinar.price_eur}`);
        }
        const priceDisplay = priceText.length > 0 ? priceText.join(' / ') : '$0';
        
        const confirmed = window.confirm(
            `Оплатить вебинар "${webinar.title}" на сумму ${priceDisplay}?\n\n` +
            'В реальном приложении здесь будет интеграция с платежной системой (Stripe, PayPal и т.д.)'
        );
        
        if (confirmed) {
            try {
                // Создаем платеж (используем USD как основную валюту)
                await createPayment({
                    booking_id: bookingId,
                    amount: webinar.price_usd || webinar.price_eur || 0,
                    currency: webinar.price_usd > 0 ? 'USD' : 'EUR',
                    payment_method: 'card',
                    payment_provider: 'stripe',
                    status: 'completed',
                    transaction_id: `TXN-${Date.now()}`
                });
                
                alert('Оплата успешно завершена! Ссылка на вебинар будет доступна в вашем профиле.');
                loadUserBookings();
            } catch (error) {
                console.error('Payment failed:', error);
                alert('Ошибка при обработке платежа. Попробуйте позже.');
            }
        }
    };

    const getUserBookingForWebinar = (webinarId) => {
        return userBookings.find(b => b.webinar_id === webinarId && b.type === 'webinar');
    };

    return (
        <ScreenWrapper>
            <div className="bookings-container">
                <h1 className="page-title">Доступные вебинары</h1>
                <p className="page-subtitle">Выберите интересующий вас вебинар и запишитесь</p>
                
                {!apiConnected && (
                    <div className="error-banner" style={{ margin: '20px 0', padding: '15px', backgroundColor: '#ff9800', color: 'white', borderRadius: '8px' }}>
                        ⚠️ Сервер недоступен. Вебинары не могут быть загружены.
                    </div>
                )}

                {loading ? (
                    <div className="loading-container">
                        <div className="loading-spinner"></div>
                        <p>Загрузка вебинаров...</p>
                    </div>
                ) : webinars.length === 0 ? (
                    <div className="empty-state" style={{ padding: '40px 20px', textAlign: 'center' }}>
                        <p>Нет доступных вебинаров</p>
                        {apiConnected && <p className="empty-hint">Вебинары будут добавлены позже</p>}
                    </div>
                ) : (
                    <div className="webinars-list">
                        {webinars.map(webinar => (
                            <div key={webinar.id} className="webinar-card">
                                <div className="webinar-header">
                                    <div className="webinar-date-badge">
                                        <div className="date-day">{new Date(webinar.date).getDate()}</div>
                                        <div className="date-month">
                                            {new Date(webinar.date).toLocaleDateString('ru-RU', { month: 'short' })}
                                        </div>
                                    </div>
                                    <div className="webinar-title-section">
                                        <h2 className="webinar-title">{webinar.title}</h2>
                                        <div className="webinar-meta">
                                            <span className="webinar-time">🕐 {webinar.time}</span>
                                            {webinar.duration && <span className="webinar-duration">⏱ {webinar.duration}</span>}
                                        </div>
                                    </div>
                                </div>
                                
                                {webinar.description && <p className="webinar-description">{webinar.description}</p>}
                                
                                {((webinar.price_usd && webinar.price_usd > 0) || (webinar.price_eur && webinar.price_eur > 0)) && (
                                    <div className="webinar-price">
                                        💰 Цена: {
                                            [
                                                webinar.price_usd > 0 ? `$${webinar.price_usd}` : null,
                                                webinar.price_eur > 0 ? `€${webinar.price_eur}` : null
                                            ].filter(Boolean).join(' / ')
                                        }
                                    </div>
                                )}
                                
                                {webinar.meeting_platform && (
                                    <div className="webinar-platform">
                                        📹 Платформа: {webinar.meeting_platform}
                                    </div>
                                )}
                                
                                {(() => {
                                    const userBooking = getUserBookingForWebinar(webinar.id);
                                    const isPaid = userBooking?.payment_status === 'paid';
                                    const hasMeetingLink = webinar.meeting_link && isPaid;
                                    
                                    return (
                                        <>
                                            {hasMeetingLink && (
                                                <div className="webinar-meeting-link">
                                                    <a 
                                                        href={webinar.meeting_link} 
                                                        target="_blank" 
                                                        rel="noopener noreferrer"
                                                        className="btn-meeting-link"
                                                    >
                                                        🔗 Перейти на вебинар
                                                    </a>
                                                </div>
                                            )}
                                            
                                            {userBooking && userBooking.payment_status === 'unpaid' && 
                                             ((webinar.price_usd && webinar.price_usd > 0) || (webinar.price_eur && webinar.price_eur > 0)) && (
                                                <div className="webinar-payment-pending">
                                                    ⏳ Ожидается оплата
                                                </div>
                                            )}
                                            
                                            {materials[webinar.id] && materials[webinar.id].length > 0 && (
                                                <div className="webinar-materials">
                                                    <h4>Материалы:</h4>
                                                    {materials[webinar.id].map(material => (
                                                        <a 
                                                            key={material.id}
                                                            href={material.file_url} 
                                                            target="_blank" 
                                                            rel="noopener noreferrer"
                                                            className="material-link"
                                                        >
                                                            📎 {material.title}
                                                        </a>
                                                    ))}
                                                </div>
                                            )}
                                            
                                            {webinar.recording_link && (isPaid || (!webinar.price_usd && !webinar.price_eur)) && (
                                                <div className="webinar-recording">
                                                    <a 
                                                        href={webinar.recording_link} 
                                                        target="_blank" 
                                                        rel="noopener noreferrer"
                                                        className="btn-recording-link"
                                                    >
                                                        🎥 Запись вебинара
                                                    </a>
                                                </div>
                                            )}
                                        </>
                                    );
                                })()}
                                
                                <div className="webinar-footer">
                                    <div className="webinar-info">
                                        {webinar.speaker && <span className="webinar-speaker">👤 {webinar.speaker}</span>}
                                        <span className="webinar-status">{getDaysUntil(webinar.date)}</span>
                                    </div>
                                    {(() => {
                                        const userBooking = getUserBookingForWebinar(webinar.id);
                                        const isBooked = userBooking || bookingStatus[webinar.id] === 'booked';
                                        const isPaid = userBooking?.payment_status === 'paid';
                                        
                                        if (isPaid) {
                                            return <span className="booking-status-paid">✓ Оплачено</span>;
                                        } else if (isBooked && ((webinar.price_usd && webinar.price_usd > 0) || (webinar.price_eur && webinar.price_eur > 0))) {
                                            return (
                                                <button 
                                                    className="btn-pay"
                                                    onClick={() => handlePayment(webinar, userBooking.id)}
                                                >
                                                    💳 Оплатить
                                                </button>
                                            );
                                        } else if (isBooked) {
                                            return <span className="booking-status-confirmed">✓ Записано</span>;
                                        } else {
                                            return (
                                                <button 
                                                    className="btn-book"
                                                    onClick={() => handleBookWebinar(webinar)}
                                                    disabled={!apiConnected || bookingStatus[webinar.id] === 'booked'}
                                                >
                                                    Записаться
                                                </button>
                                            );
                                        }
                                    })()}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </ScreenWrapper>
    );
}

