import { useState, useEffect } from "react";
import "./App.css";
import Home from "./screens/Home";
import Bookings from "./screens/Bookings";
import Support from "./screens/Support";
import Profile from "./screens/Profile";

function App() {
  const [activeTab, setActiveTab] = useState("home");
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Получаем данные пользователя из Telegram WebApp
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();
      setUser(tg.initDataUnsafe?.user || null);
    } 
  }, []);

  return (
    <div className="app">
      <div className="content">
        {activeTab === "home" && <Home user={user} />}
        {activeTab === "bookings" && <Bookings />}
        {activeTab === "support" && <Support />}
        {activeTab === "profile" && <Profile user={user} />}
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
