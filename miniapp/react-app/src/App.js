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
          🏠
        </div>

        <div
          className={`nav-item ${activeTab === "bookings" ? "active" : ""}`}
          onClick={() => setActiveTab("bookings")}
        >
          📅
        </div>

        <div
          className={`nav-item ${activeTab === "support" ? "active" : ""}`}
          onClick={() => setActiveTab("support")}
        >
          💬
        </div>

        <div
          className={`nav-item ${activeTab === "profile" ? "active" : ""}`}
          onClick={() => setActiveTab("profile")}
        >
          👤
        </div>

        <div className={`nav-indicator ${activeTab}`} />
      </div>
    </div>
  );
}

export default App;
