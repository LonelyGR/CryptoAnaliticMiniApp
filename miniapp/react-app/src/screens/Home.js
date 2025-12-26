import Header from '../components/Header';
import ScreenWrapper from '../components/ScreenWrapper';

export default function Home({ user }) {
    return (
        <ScreenWrapper>
            <Header username={user?.first_name} user={user} />
            
            <div className="home-content">
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon">📊</div>
                        <div className="stat-value">12</div>
                        <div className="stat-label">Вебинаров</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon">✅</div>
                        <div className="stat-value">3</div>
                        <div className="stat-label">Записан</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon">🎓</div>
                        <div className="stat-value">8</div>
                        <div className="stat-label">Завершено</div>
                    </div>
                </div>

                <div className="welcome-message">
                    <h2>Добро пожаловать!</h2>
                    <p>Мы рады видеть вас в нашем приложении для аналитики криптовалют. Здесь вы найдете полезные вебинары, консультации и многое другое.</p>
                </div>
            </div>
        </ScreenWrapper>
    );
}
