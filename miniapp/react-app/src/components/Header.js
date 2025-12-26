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
        {user?.id && <p className="user-id">ID: {user.id}</p>}
      </div>
    );
}
  