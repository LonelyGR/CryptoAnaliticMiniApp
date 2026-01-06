import { useState, useEffect } from 'react';
import ScreenWrapper from '../components/ScreenWrapper';
import Header from '../components/Header';
import { getUserBookings, getWebinars } from '../services/api';

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { day: 'numeric', month: 'long', year: 'numeric' };
    return date.toLocaleDateString('ru-RU', options);
}

export default function Profile({ user, apiConnected }) {
    const [bookings, setBookings] = useState([]);
    const [webinars, setWebinars] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadUserData = async () => {
            if (apiConnected && user?.id) {
                try {
                    const [userBookings, allWebinars] = await Promise.all([
                        getUserBookings(user.id),
                        getWebinars()
                    ]);
                    
                    setBookings(userBookings || []);
                    setWebinars(allWebinars || []);
                } catch (error) {
                    console.error('Failed to load user data:', error);
                    setBookings([]);
                    setWebinars([]);
                }
            } else {
                setBookings([]);
                setWebinars([]);
            }
            setLoading(false);
        };

        loadUserData();
    }, [apiConnected, user?.id]);

    // Получаем название вебинара по webinar_id
    const getWebinarTitle = (webinarId) => {
        const webinar = webinars.find(w => w.id === webinarId);
        return webinar ? webinar.title : 'Вебинар';
    };

    return (
        <ScreenWrapper>
            <Header username={user?.first_name} user={user} />
            
            <div className="profile-container">
                <div className="profile-section">
                    <h2 className="section-title">Мои данные</h2>
                    <div className="profile-info-card">
                        <div className="info-row">
                            <span className="info-label">Имя:</span>
                            <span className="info-value">{user?.first_name || 'Не указано'}</span>
                        </div>
                        <div className="info-row">
                            <span className="info-label">Фамилия:</span>
                            <span className="info-value">{user?.last_name || 'Не указано'}</span>
                        </div>
                        <div className="info-row">
                            <span className="info-label">Username:</span>
                            <span className="info-value">@{user?.username || 'Не указано'}</span>
                        </div>
                        <div className="info-row">
                            <span className="info-label">User ID:</span>
                            <span className="info-value">{user?.id || user?.telegram_id || 'Неизвестно'}</span>
                        </div>
                    </div>
                </div>

                <div className="profile-section">
                    <h2 className="section-title">Мои записи на вебинары</h2>
                    {!apiConnected && (
                        <div className="error-banner" style={{ margin: '20px 0', padding: '15px', backgroundColor: '#ff9800', color: 'white', borderRadius: '8px' }}>
                            ⚠️ Сервер недоступен. Записи не могут быть загружены.
                        </div>
                    )}
                    {loading ? (
                        <div className="loading-container">
                            <div className="loading-spinner"></div>
                            <p>Загрузка записей...</p>
                        </div>
                    ) : bookings.length > 0 ? (
                        <div className="bookings-list">
                            {bookings.map(booking => (
                                <div key={booking.id} className="user-booking-card">
                                    <div className="booking-header">
                                        <h3 className="booking-title">
                                            {booking.webinar_id ? getWebinarTitle(booking.webinar_id) : (booking.topic || 'Консультация')}
                                        </h3>
                                        <span className={`booking-status ${booking.status === 'confirmed' || booking.status === 'active' ? 'confirmed' : ''}`}>
                                            {booking.status === 'confirmed' || booking.status === 'active' ? '✓ Подтверждено' : booking.status}
                                        </span>
                                    </div>
                                    <div className="booking-details">
                                        <span className="booking-date">📅 {formatDate(booking.date)}</span>
                                        {booking.time && <span className="booking-time">🕐 {booking.time}</span>}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="empty-state">
                            <p>Вы еще не записаны ни на один вебинар</p>
                            {apiConnected && <p className="empty-hint">Перейдите во вкладку "Vebinars" чтобы выбрать вебинар</p>}
                        </div>
                    )}
                </div>
            </div>
        </ScreenWrapper>
    );
}

