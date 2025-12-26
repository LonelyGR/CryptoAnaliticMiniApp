import ScreenWrapper from '../components/ScreenWrapper';
import Header from '../components/Header';

// Тестовые данные записанных вебинаров пользователя
const userBookings = [
    {
        id: 1,
        title: "Основы криптотрейдинга",
        date: "2024-12-20",
        time: "18:00",
        status: "confirmed"
    },
    {
        id: 2,
        title: "Технический анализ криптовалют",
        date: "2024-12-25",
        time: "19:30",
        status: "confirmed"
    }
];

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { day: 'numeric', month: 'long', year: 'numeric' };
    return date.toLocaleDateString('ru-RU', options);
}

export default function Profile({ user }) {
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
                            <span className="info-value">{user?.id || 'Неизвестно'}</span>
                        </div>
                    </div>
                </div>

                <div className="profile-section">
                    <h2 className="section-title">Мои записи на вебинары</h2>
                    {userBookings.length > 0 ? (
                        <div className="bookings-list">
                            {userBookings.map(booking => (
                                <div key={booking.id} className="user-booking-card">
                                    <div className="booking-header">
                                        <h3 className="booking-title">{booking.title}</h3>
                                        <span className="booking-status confirmed">
                                            {booking.status === 'confirmed' ? '✓ Подтверждено' : booking.status}
                                        </span>
                                    </div>
                                    <div className="booking-details">
                                        <span className="booking-date">📅 {formatDate(booking.date)}</span>
                                        <span className="booking-time">🕐 {booking.time}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="empty-state">
                            <p>Вы еще не записаны ни на один вебинар</p>
                            <p className="empty-hint">Перейдите во вкладку "Записи" чтобы выбрать вебинар</p>
                        </div>
                    )}
                </div>
            </div>
        </ScreenWrapper>
    );
}

