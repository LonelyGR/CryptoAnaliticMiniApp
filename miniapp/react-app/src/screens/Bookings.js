import ScreenWrapper from '../components/ScreenWrapper';

// Тестовые данные вебинаров
const webinars = [
    {
        id: 1,
        title: "Основы криптотрейдинга",
        date: "2024-12-20",
        time: "18:00",
        duration: "2 часа",
        speaker: "Иван Петров",
        status: "upcoming",
        description: "Изучите базовые принципы торговли криптовалютами и начните свой путь в трейдинге."
    },
    {
        id: 2,
        title: "Технический анализ криптовалют",
        date: "2024-12-25",
        time: "19:30",
        duration: "2.5 часа",
        speaker: "Мария Сидорова",
        status: "upcoming",
        description: "Глубокое погружение в технические индикаторы и паттерны для анализа рынка."
    },
    {
        id: 3,
        title: "DeFi и стейкинг",
        date: "2025-01-05",
        time: "17:00",
        duration: "3 часа",
        speaker: "Алексей Козлов",
        status: "upcoming",
        description: "Все о децентрализованных финансах и способах пассивного заработка на криптовалютах."
    }
];

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { day: 'numeric', month: 'long', year: 'numeric' };
    return date.toLocaleDateString('ru-RU', options);
}

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

export default function Bookings() {
    return (
        <ScreenWrapper>
            <div className="bookings-container">
                <h1 className="page-title">Доступные вебинары</h1>
                <p className="page-subtitle">Выберите интересующий вас вебинар и запишитесь</p>
                
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
                                        <span className="webinar-duration">⏱ {webinar.duration}</span>
                                    </div>
                                </div>
                            </div>
                            
                            <p className="webinar-description">{webinar.description}</p>
                            
                            <div className="webinar-footer">
                                <div className="webinar-info">
                                    <span className="webinar-speaker">👤 {webinar.speaker}</span>
                                    <span className="webinar-status">{getDaysUntil(webinar.date)}</span>
                                </div>
                                <button className="btn-book">Записаться</button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </ScreenWrapper>
    );
}

