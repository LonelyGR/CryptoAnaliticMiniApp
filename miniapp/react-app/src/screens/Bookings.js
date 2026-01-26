import { useState, useEffect } from 'react';
import ScreenWrapper from '../components/ScreenWrapper';
import PaymentFlow from '../components/PaymentFlow';
import { getWebinars, createBooking, getUserByTelegramId, getUserBookings, getWebinarMaterials } from '../services/api';

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

function getWebinarStartDateTime(webinar) {
    // webinar.date: YYYY-MM-DD, webinar.time: HH:MM
    // Создаем local datetime. Если время отсутствует — считаем 00:00.
    const time = webinar?.time ? `${webinar.time}:00` : '00:00:00';
    return new Date(`${webinar.date}T${time}`);
}

export default function Bookings({ user, apiConnected }) {
    const [webinars, setWebinars] = useState([]);
    const [userBookings, setUserBookings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [bookingStatus, setBookingStatus] = useState({});
    const [materials, setMaterials] = useState({});
    const [paymentContext, setPaymentContext] = useState(null);
    
    const isDeveloper = ['разработчик', 'developer', 'владелец', 'owner'].includes((user?.role || '').toLowerCase());

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
            if (!isDeveloper && ((webinar.price_usd && webinar.price_usd > 0) || (webinar.price_eur && webinar.price_eur > 0))) {
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
        const amount = webinar.price_usd || webinar.price_eur || 0;
        const priceCurrency = 'usd';
        const existingPaymentId = bookingId
            ? userBookings.find(b => b.id === bookingId)?.payment_id
            : null;
        setPaymentContext({
            orderId: `booking-${bookingId}`,
            amount,
            priceCurrency,
            webinarTitle: webinar.title,
            paymentId: existingPaymentId
        });
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
                    <div className="error-banner" style={{ margin: '20px 0', padding: '15px', backgroundColor: 'var(--yellow)', color: 'var(--bg)', borderRadius: '8px' }}>
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
                                        💰 Цена: {webinar.price_usd || webinar.price_eur} USDT
                                    </div>
                                )}
                                {((webinar.price_usd && webinar.price_usd > 0) || (webinar.price_eur && webinar.price_eur > 0)) && (
                                    <div className="webinar-price">
                                        💳 Оплата: USDT (TRC20)
                                    </div>
                                )}
                                
                                {webinar.meeting_platform && (
                                    <div className="webinar-platform">
                                        📹 Платформа: {webinar.meeting_platform}
                                    </div>
                                )}
                                
                                {(() => {
                                    const userBooking = getUserBookingForWebinar(webinar.id);
                                    const isBooked = userBooking || bookingStatus[webinar.id] === 'booked';
                                    const isPaid = userBooking?.payment_status === 'paid';
                                    const canAccessWebinar = isDeveloper || isPaid;
                                    const showJoinSection = canAccessWebinar && (isDeveloper || isBooked);
                                    const startAt = getWebinarStartDateTime(webinar);
                                    const joinAvailableAt = new Date(startAt.getTime() - 15 * 60 * 1000);
                                    const now = new Date();
                                    const isJoinEnabled = now >= joinAvailableAt;
                                    const hasMeetingLink = Boolean(webinar.meeting_link);
                                    const isJoinButtonEnabled = isJoinEnabled && hasMeetingLink;
                                    
                                    return (
                                        <>
                                            {showJoinSection && (
                                                <div className="webinar-meeting-link">
                                                    <button
                                                        type="button"
                                                        className="btn-meeting-link"
                                                        disabled={!isJoinButtonEnabled}
                                                        onClick={() => {
                                                            if (!isJoinButtonEnabled) return;
                                                            window.open(webinar.meeting_link, '_blank', 'noopener,noreferrer');
                                                        }}
                                                    >
                                                        🔗 Подключиться
                                                    </button>
                                                    {!hasMeetingLink && (
                                                        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.8 }}>
                                                            Ссылка на встречу ещё не добавлена
                                                        </div>
                                                    )}
                                                    {hasMeetingLink && !isJoinEnabled && (
                                                        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.8 }}>
                                                            Доступно за 15 минут до начала
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                            
                                            {!isDeveloper && userBooking && userBooking.payment_status === 'unpaid' && 
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
                                        
                                        if (isDeveloper) {
                                            return <span className="booking-status-paid">✓ Оплачено</span>;
                                        } else if (isPaid) {
                                            return <span className="booking-status-paid">✓ Оплачено</span>;
                                        } else if (!isDeveloper && isBooked && ((webinar.price_usd && webinar.price_usd > 0) || (webinar.price_eur && webinar.price_eur > 0))) {
                                            // Важно: userBooking может быть ещё не загружен, даже если статус "booked" уже выставлен
                                            if (!userBooking?.id) {
                                                return (
                                                    <button className="btn-pay" disabled>
                                                        ⏳ Подготовка оплаты...
                                                    </button>
                                                );
                                            }
                                            return (
                                                <button 
                                                    className="btn-pay"
                                                    onClick={() => handlePayment(webinar, userBooking.id)}
                                                >
                                                    💳 Оплатить сейчас
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
            {paymentContext && (
                <div className="modal-overlay" onClick={() => setPaymentContext(null)}>
                    <div className="modal-content" onClick={(event) => event.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Оплата: {paymentContext.webinarTitle}</h2>
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
                                onClose={() => setPaymentContext(null)}
                                onComplete={(payment, success) => {
                                    if (success) {
                                        loadUserBookings();
                                    }
                                }}
                            />
                        </div>
                    </div>
                </div>
            )}
        </ScreenWrapper>
    );
}

