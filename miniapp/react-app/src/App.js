import { useState, useEffect } from "react";
import "./App.css";
import Home from "./screens/Home";
import Bookings from "./screens/Bookings";
import Support from "./screens/Support";
import Profile from "./screens/Profile";
import { getUserByTelegramId, createOrUpdateUser, checkApiHealth } from "./services/api";

function App() {
  const [activeTab, setActiveTab] = useState("home");
  const [user, setUser] = useState(null);
  const [dbUser, setDbUser] = useState(null);
  const [apiConnected, setApiConnected] = useState(false);

  useEffect(() => {
    // Получаем данные пользователя из Telegram WebApp
    let telegramUser = null;
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();
      telegramUser = tg.initDataUnsafe?.user || null;
      setUser(telegramUser);
    }

    // Проверяем подключение к API и загружаем/создаем пользователя в БД
    const loadUserData = async () => {
      const isApiAvailable = await checkApiHealth();
      setApiConnected(isApiAvailable);

      if (isApiAvailable && telegramUser?.id) {
        try {
          // Пытаемся получить пользователя из БД
          let userFromDb = await getUserByTelegramId(telegramUser.id);
          
          // Если пользователя нет, создаем его
          if (!userFromDb) {
            userFromDb = await createOrUpdateUser(telegramUser.id, {
              username: telegramUser.username,
              first_name: telegramUser.first_name,
              last_name: telegramUser.last_name,
              photo_url: telegramUser.photo_url,
            });
          } else {
            // Обновляем данные пользователя если они изменились
            userFromDb = await createOrUpdateUser(telegramUser.id, {
              username: telegramUser.username,
              first_name: telegramUser.first_name,
              last_name: telegramUser.last_name,
              photo_url: telegramUser.photo_url,
            });
          }

          if (userFromDb) {
            setDbUser(userFromDb);
          }
        } catch (error) {
          console.error('Failed to load user from database:', error);
        }
      }
    };

    loadUserData();
  }, []);

  // Используем данные из БД если доступны, иначе данные из Telegram
  const displayUser = dbUser || user;

  return (
    <div className="app">
      {!apiConnected && (
        <div className="api-warning" style={{
          padding: '8px',
          backgroundColor: '#ff9800',
          color: 'white',
          textAlign: 'center',
          fontSize: '12px'
        }}>
          ⚠️ Сервер недоступен. Данные не загружаются.
        </div>
      )}
      <div className="content">
        {activeTab === "home" && <Home user={displayUser} apiConnected={apiConnected} />}
        {activeTab === "bookings" && <Bookings user={displayUser} apiConnected={apiConnected} />}
        {activeTab === "support" && <Support user={displayUser} apiConnected={apiConnected} />}
        {activeTab === "profile" && <Profile user={displayUser} apiConnected={apiConnected} />}
      </div>

      <div className="bottom-nav">
        <div
          className={`nav-item ${activeTab === "home" ? "active" : ""}`}
          onClick={() => setActiveTab("home")}
        >
          <span className="nav-icon">🏠</span>
          <span className="nav-label">Home</span>
        </div>

        <div
          className={`nav-item ${activeTab === "bookings" ? "active" : ""}`}
          onClick={() => setActiveTab("bookings")}
        >
          <span className="nav-icon">📋</span>
          <span className="nav-label">Vebinars</span>
        </div>

        <div
          className={`nav-item ${activeTab === "support" ? "active" : ""}`}
          onClick={() => setActiveTab("support")}
        >
          <span className="nav-icon">💼</span>
          <span className="nav-label">Support</span>
        </div>

        <div
          className={`nav-item ${activeTab === "profile" ? "active" : ""}`}
          onClick={() => setActiveTab("profile")}
        >
          <span className="nav-icon">👤</span>
          <span className="nav-label">Profile</span>
        </div>

        <div className={`nav-indicator ${activeTab}`} />
      </div>
    </div>
  );
}

export default App;
