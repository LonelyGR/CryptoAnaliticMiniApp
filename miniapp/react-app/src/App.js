import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();

      setUser(tg.initDataUnsafe?.user || null);
    }
  }, []);

  return (
    <div className="App">
      <h1>Crypto Sensey</h1>
      {user ? (
        <div>
          <p>ID пользователя:</p>
          <b>{user.id}</b>
        </div>
      ) : (
        <p>Телеграм открой для начала!</p>
      )}
    </div>
  );
}

export default App;