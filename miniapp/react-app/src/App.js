import { useState, useEffect, useRef } from "react";
import "./App.css";
import Home from "./screens/Home";
import Bookings from "./screens/Bookings";
import Support from "./screens/Support";
import Profile from "./screens/Profile";
import AdminWebinars from "./screens/AdminWebinars";
import AdminTickets from "./screens/AdminTickets";
import UsersManagement from "./screens/UsersManagement";
import { getUserByTelegramId, createOrUpdateUser, checkApiHealth } from "./services/api";

function App() {
  const [activeTab, setActiveTab] = useState("home");
  const [user, setUser] = useState(null);
  const [dbUser, setDbUser] = useState(null);
  const [apiConnected, setApiConnected] = useState(false);
  const [indicatorPosition, setIndicatorPosition] = useState('0px');
  const navRef = useRef(null);

  useEffect(() => {
    // Получаем данные пользователя из Telegram WebApp
    let telegramUser = null;
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();
      setTimeout(() => {
        tg.expand();
      }, 100);
      tg.onEvent('viewportChanged', () => {
        tg.expand();
      });
      telegramUser = tg.initDataUnsafe?.user || null;
      setUser(telegramUser);
      console.log('Telegram WebApp user:', telegramUser);
    } else {
      console.warn('Telegram WebApp не доступен. Приложение запущено вне Telegram.');
    }

    // Проверяем подключение к API и загружаем/создаем пользователя в БД
    const loadUserData = async () => {
      const isApiAvailable = await checkApiHealth();
      setApiConnected(isApiAvailable);

      if (!isApiAvailable) {
        console.error('API недоступен');
        return;
      }

      if (telegramUser?.id) {
        try {
          console.log('Загрузка пользователя с telegram_id:', telegramUser.id);
          
          // Пытаемся получить пользователя из БД
          let userFromDb = await getUserByTelegramId(telegramUser.id);
          
          // Если пользователя нет, создаем его
          if (!userFromDb) {
            console.log('Пользователь не найден в БД, создаем нового...');
            userFromDb = await createOrUpdateUser(telegramUser.id, {
              username: telegramUser.username || null,
              first_name: telegramUser.first_name || null,
              last_name: telegramUser.last_name || null,
              photo_url: telegramUser.photo_url || null,
            });
          } else {
            // Обновляем данные пользователя если они изменились
            console.log('Пользователь найден в БД, обновляем данные...');
            userFromDb = await createOrUpdateUser(telegramUser.id, {
              username: telegramUser.username || null,
              first_name: telegramUser.first_name || null,
              last_name: telegramUser.last_name || null,
              photo_url: telegramUser.photo_url || null,
            });
          }

          if (userFromDb) {
            console.log('Пользователь загружен из БД:', userFromDb);
            setDbUser(userFromDb);
          } else {
            console.error('Не удалось создать/обновить пользователя в БД');
          }
        } catch (error) {
          console.error('Failed to load user from database:', error);
          console.error('Error details:', error.message, error.stack);
        }
      } else {
        console.warn('Telegram user ID не найден. Пользователь не может быть создан в БД.');
      }
    };

    loadUserData();
  }, []);

  // Используем данные из БД если доступны, иначе данные из Telegram
  const displayUser = dbUser || user;

  // Обновляем позицию индикатора при изменении активной вкладки
  useEffect(() => {
    const updateIndicatorPosition = () => {
      if (!navRef.current) return;
      
      const navItems = navRef.current.querySelectorAll('.nav-item[data-tab]');
      if (navItems.length === 0) return;
      
      let activeIndex = -1;
      navItems.forEach((item, index) => {
        if (item.getAttribute('data-tab') === activeTab) {
          activeIndex = index;
        }
      });
      
      if (activeIndex === -1) return;
      
      const navWidth = navRef.current.offsetWidth;
      const itemWidth = navWidth / navItems.length;
      const indicatorWidth = 56;
      const position = (activeIndex * itemWidth) + (itemWidth / 2) - (indicatorWidth / 2);
      
      setIndicatorPosition(`${position}px`);
    };

    // Обновляем позицию после рендера
    setTimeout(updateIndicatorPosition, 0);
    window.addEventListener('resize', updateIndicatorPosition);
    
    return () => window.removeEventListener('resize', updateIndicatorPosition);
  }, [activeTab, displayUser?.is_admin]);

  if (displayUser?.is_blocked) {
    return (
      <div className="app">
        <div className="blocked-screen">
          <div className="blocked-card">
            <div className="blocked-icon">⛔</div>
            <h1>Доступ закрыт</h1>
            <p>К сожалению, ваш аккаунт заблокирован. Обратитесь в поддержку.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      {!apiConnected && (
        <div className="api-warning" style={{
          padding: '8px',
          backgroundColor: 'var(--yellow)',
          color: 'var(--bg)',
          textAlign: 'center',
          fontSize: '12px'
        }}>
          ⚠️ Сервер недоступен. Данные не загружаются.
        </div>
      )}
      <div className="content">
        {activeTab === "home" && <Home user={displayUser} apiConnected={apiConnected} dbUser={displayUser} />}
        {activeTab === "bookings" && <Bookings user={displayUser} apiConnected={apiConnected} />}
        {activeTab === "support" && <Support user={displayUser} apiConnected={apiConnected} />}
        {activeTab === "profile" && (
          <Profile
            user={displayUser}
            apiConnected={apiConnected}
            onNavigate={(tab) => setActiveTab(tab)}
          />
        )}
        {activeTab === "admin-users" && (
          <UsersManagement
            user={displayUser}
            apiConnected={apiConnected}
            onBack={() => setActiveTab("profile")}
          />
        )}
        {activeTab === "admin-webinars" && displayUser?.is_admin && <AdminWebinars user={displayUser} apiConnected={apiConnected} />}
        {activeTab === "admin-tickets" && displayUser?.is_admin && <AdminTickets user={displayUser} apiConnected={apiConnected} />}
      </div>

      <div className="bottom-nav" ref={navRef}>
        <div
          className={`nav-item ${activeTab === "home" ? "active" : ""}`}
          onClick={() => setActiveTab("home")}
          data-tab="home"
        >
          <span className="nav-icon">🏠</span>
          <span className="nav-label">Home</span>
        </div>

        <div
          className={`nav-item ${activeTab === "bookings" ? "active" : ""}`}
          onClick={() => setActiveTab("bookings")}
          data-tab="bookings"
        >
          <span className="nav-icon">📋</span>
          <span className="nav-label">Vebinars</span>
        </div>

        {displayUser?.is_admin && (
          <div
            className={`nav-item ${activeTab === "admin-webinars" ? "active" : ""}`}
            onClick={() => setActiveTab("admin-webinars")}
            data-tab="admin-webinars"
          >
            <span className="nav-icon">➕</span>
            <span className="nav-label">Создать</span>
          </div>
        )}

        {displayUser?.is_admin && (
          <div
            className={`nav-item ${activeTab === "admin-tickets" ? "active" : ""}`}
            onClick={() => setActiveTab("admin-tickets")}
            data-tab="admin-tickets"
          >
            <span className="nav-icon">🎫</span>
            <span className="nav-label">Тикеты</span>
          </div>
        )}

        {!displayUser?.is_admin && (
          <div
            className={`nav-item ${activeTab === "support" ? "active" : ""}`}
            onClick={() => setActiveTab("support")}
            data-tab="support"
          >
            <span className="nav-icon">💼</span>
            <span className="nav-label">Support</span>
          </div>
        )}

        <div
          className={`nav-item ${activeTab === "profile" ? "active" : ""}`}
          onClick={() => setActiveTab("profile")}
          data-tab="profile"
        >
          <span className="nav-icon">👤</span>
          <span className="nav-label">Profile</span>
        </div>

        <div 
          className="nav-indicator" 
          style={{ left: indicatorPosition }}
        />
      </div>
    </div>
  );
}

export default App;
