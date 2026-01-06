import { useState, useEffect } from 'react';
import ScreenWrapper from '../components/ScreenWrapper';
import { getWebinars, createBooking, getUserByTelegramId } from '../services/api';

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
    const [loading, setLoading] = useState(true);
    const [bookingStatus, setBookingStatus] = useState({});

    useEffect(() => {
        const loadWebinars = async () => {
            if (apiConnected) {
                try {
                    const data = await getWebinars();
                    setWebinars(data || []);
                } catch (error) {
                    console.error('Failed to load webinars:', error);
                    setWebinars([]);
                }
            } else {
                setWebinars([]);
            }
            setLoading(false);
        };

        loadWebinars();
    }, [apiConnected]);

    const handleBookWebinar = async (webinar) => {
        if (!apiConnected || !user?.id) {
            alert('Не удалось подключиться к серверу или пользователь не найден');
            return;
        }

        try {
            // Получаем user_id из БД по telegram_id
            const dbUser = await getUserByTelegramId(user.id);
            if (!dbUser) {
                alert('Пользователь не найден в базе данных');
                return;
            }

            await createBooking({
                user_id: dbUser.id,
                webinar_id: webinar.id,
                type: 'webinar',
                date: webinar.date,
                status: 'active'
            });

            setBookingStatus(prev => ({ ...prev, [webinar.id]: 'success' }));
            alert('Вы успешно записались на вебинар!');
        } catch (error) {
            console.error('Failed to book webinar:', error);
            setBookingStatus(prev => ({ ...prev, [webinar.id]: 'error' }));
            alert('Не удалось записаться на вебинар. Попробуйте позже.');
        }
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
                                
                                <div className="webinar-footer">
                                    <div className="webinar-info">
                                        {webinar.speaker && <span className="webinar-speaker">👤 {webinar.speaker}</span>}
                                        <span className="webinar-status">{getDaysUntil(webinar.date)}</span>
                                    </div>
                                    <button 
                                        className="btn-book"
                                        onClick={() => handleBookWebinar(webinar)}
                                        disabled={!apiConnected || bookingStatus[webinar.id] === 'success'}
                                    >
                                        {bookingStatus[webinar.id] === 'success' ? '✓ Записано' : 'Записаться'}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </ScreenWrapper>
    );
}

