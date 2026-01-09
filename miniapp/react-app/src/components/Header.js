export default function Header({ username, user }) {
    const avatarUrl = user?.photo_url;
    const getInitials = () => {
        if (user?.first_name) {
            return user.first_name.charAt(0).toUpperCase();
        }
        return "?";
    };

    return (
      <div className="header">
        <div className="avatar">
          {avatarUrl ? (
            <img src={avatarUrl} alt="Avatar" className="avatar-img" />
          ) : (
            <div className="avatar-placeholder">{getInitials()}</div>
          )}
        </div>
        <h1>Привет, {username || "Гость"}!</h1>
        {user?.is_admin && (
          <p className="admin-badge-header" style={{ 
            color: '#4CAF50', 
            fontWeight: 'bold', 
            fontSize: '12px',
            marginTop: '5px'
          }}>
            👑 Администратор {user?.role ? `(${user.role})` : ''}
          </p>
        )}
        <p className="user-id">Telegram ID: {user?.telegram_id || user?.id || 'Неизвестно'}</p>
      </div>
    );
}
  