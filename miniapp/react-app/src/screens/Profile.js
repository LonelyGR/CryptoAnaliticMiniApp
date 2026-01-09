import { useState, useEffect } from 'react';
import ScreenWrapper from '../components/ScreenWrapper';
import Header from '../components/Header';
import { getUserBookings, getWebinars, createAdmin, getAdmins, updateAdmin, deleteAdmin } from '../services/api';

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { day: 'numeric', month: 'long', year: 'numeric' };
    return date.toLocaleDateString('ru-RU', options);
}

export default function Profile({ user, apiConnected }) {
    const [bookings, setBookings] = useState([]);
    const [webinars, setWebinars] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddAdminForm, setShowAddAdminForm] = useState(false);
    const [adminFormData, setAdminFormData] = useState({
        telegram_id: '',
        role: 'Администратор'
    });
    const [submittingAdmin, setSubmittingAdmin] = useState(false);
    const [admins, setAdmins] = useState([]);
    const [loadingAdmins, setLoadingAdmins] = useState(false);
    const [editingAdmin, setEditingAdmin] = useState(null);

    // Проверка, является ли пользователь разработчиком
    const isDeveloper = user?.role === 'разработчик' || user?.role === 'developer';

    useEffect(() => {
        const loadUserData = async () => {
            // Получаем telegram_id из объекта user (может быть из БД или из Telegram WebApp)
            const telegramId = user?.telegram_id || user?.id;
            
            if (apiConnected && telegramId) {
                try {
                    const [userBookings, allWebinars] = await Promise.all([
                        getUserBookings(telegramId),
                        getWebinars()
                    ]);
                    
                    // Фильтруем записи - показываем только те, где вебинар существует
                    const validBookings = (userBookings || []).filter(booking => {
                        if (booking.webinar_id) {
                            return allWebinars.some(w => w.id === booking.webinar_id);
                        }
                        return true; // Консультации всегда показываем
                    });
                    
                    setBookings(validBookings);
                    setWebinars(allWebinars || []);
                } catch (error) {
                    console.error('Failed to load user data:', error);
                    setBookings([]);
                    setWebinars([]);
                }
            } else {
                setBookings([]);
                setWebinars([]);
            }
            setLoading(false);
        };

        loadUserData();
    }, [apiConnected, user?.telegram_id, user?.id]);

    // Загружаем список админов для разработчика
    useEffect(() => {
        const loadAdmins = async () => {
            if (isDeveloper && apiConnected) {
                setLoadingAdmins(true);
                try {
                    const adminsList = await getAdmins();
                    setAdmins(adminsList || []);
                } catch (error) {
                    console.error('Failed to load admins:', error);
                    setAdmins([]);
                } finally {
                    setLoadingAdmins(false);
                }
            }
        };

        loadAdmins();
    }, [isDeveloper, apiConnected]);

    // Получаем название вебинара по webinar_id
    const getWebinarTitle = (webinarId) => {
        const webinar = webinars.find(w => w.id === webinarId);
        return webinar ? webinar.title : 'Вебинар';
    };

    const handleAddAdmin = async (e) => {
        e.preventDefault();
        if (!apiConnected) {
            alert('Сервер недоступен');
            return;
        }

        const telegramId = parseInt(adminFormData.telegram_id);
        if (!telegramId || isNaN(telegramId)) {
            alert('Введите корректный Telegram ID');
            return;
        }

        setSubmittingAdmin(true);
        try {
            await createAdmin({
                telegram_id: telegramId,
                role: adminFormData.role
            });
            alert('Администратор успешно добавлен!');
            setAdminFormData({
                telegram_id: '',
                role: 'Администратор'
            });
            setShowAddAdminForm(false);
            // Перезагружаем список админов
            const adminsList = await getAdmins();
            setAdmins(adminsList || []);
        } catch (error) {
            console.error('Failed to create admin:', error);
            alert('Не удалось добавить администратора. Проверьте, что пользователь существует и не является админом.');
        } finally {
            setSubmittingAdmin(false);
        }
    };

    const handleUpdateAdmin = async (adminId, newRole) => {
        try {
            await updateAdmin(adminId, {
                role: newRole
            });
            alert('Роль администратора обновлена!');
            const adminsList = await getAdmins();
            setAdmins(adminsList || []);
            setEditingAdmin(null);
        } catch (error) {
            console.error('Failed to update admin:', error);
            alert('Не удалось обновить роль администратора');
        }
    };

    const handleDeleteAdmin = async (adminId) => {
        if (!window.confirm('Вы уверены, что хотите удалить этого администратора?')) {
            return;
        }

        try {
            await deleteAdmin(adminId);
            alert('Администратор удален!');
            const adminsList = await getAdmins();
            setAdmins(adminsList || []);
        } catch (error) {
            console.error('Failed to delete admin:', error);
            alert('Не удалось удалить администратора');
        }
    };

    return (
        <ScreenWrapper>
            <Header username={user?.first_name} user={user} />
            
            <div className="profile-container">
                <div className="profile-section">
                    <h2 className="section-title">Мои данные</h2>
                    <div className="profile-info-card">
                        {user?.is_admin && (
                            <div className="admin-badge" style={{
                                padding: '10px',
                                backgroundColor: '#4CAF50',
                                color: 'white',
                                borderRadius: '8px',
                                marginBottom: '15px',
                                textAlign: 'center',
                                fontWeight: 'bold'
                            }}>
                                👑 АДМИНИСТРАТОР {user?.role ? `- ${user.role}` : ''}
                            </div>
                        )}
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
                            <span className="info-label">Telegram ID:</span>
                            <span className="info-value">{user?.telegram_id || user?.id || 'Неизвестно'}</span>
                        </div>
                        {user?.id && user?.id !== user?.telegram_id && (
                            <div className="info-row">
                                <span className="info-label">ID в БД:</span>
                                <span className="info-value">{user.id}</span>
                            </div>
                        )}
                    </div>
                </div>

                {isDeveloper && (
                    <div className="profile-section">
                        <h2 className="section-title">Управление администраторами</h2>
                        <div className="profile-info-card">
                            {!showAddAdminForm ? (
                                <button
                                    className="btn-primary"
                                    onClick={() => setShowAddAdminForm(true)}
                                    style={{ marginBottom: '20px', width: '100%' }}
                                >
                                    + Добавить администратора
                                </button>
                            ) : (
                                <form onSubmit={handleAddAdmin} className="admin-form" style={{ marginBottom: '20px' }}>
                                    <div className="form-group">
                                        <label>Telegram ID пользователя *</label>
                                        <input
                                            type="number"
                                            className="form-input"
                                            value={adminFormData.telegram_id}
                                            onChange={(e) => setAdminFormData({...adminFormData, telegram_id: e.target.value})}
                                            placeholder="Введите Telegram ID"
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Роль</label>
                                        <select
                                            className="form-select"
                                            value={adminFormData.role}
                                            onChange={(e) => setAdminFormData({...adminFormData, role: e.target.value})}
                                        >
                                            <option value="Администратор">Администратор</option>
                                            <option value="разработчик">Разработчик</option>
                                            <option value="Модератор">Модератор</option>
                                        </select>
                                    </div>
                                    <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
                                        <button
                                            type="submit"
                                            className="btn-primary"
                                            disabled={submittingAdmin}
                                            style={{ flex: 1, opacity: submittingAdmin ? 0.6 : 1 }}
                                        >
                                            {submittingAdmin ? 'Добавление...' : 'Добавить'}
                                        </button>
                                        <button
                                            type="button"
                                            className="btn-secondary-admin"
                                            onClick={() => {
                                                setShowAddAdminForm(false);
                                                setAdminFormData({
                                                    telegram_id: '',
                                                    role: 'Администратор'
                                                });
                                            }}
                                        >
                                            Отмена
                                        </button>
                                    </div>
                                </form>
                            )}

                            <div className="admins-list">
                                {loadingAdmins ? (
                                    <div className="empty-state">
                                        <p>Загрузка...</p>
                                    </div>
                                ) : admins.length === 0 ? (
                                    <div className="empty-state">
                                        <p>Нет администраторов</p>
                                    </div>
                                ) : (
                                    admins.map(admin => (
                                        <div key={admin.id} className="admin-item">
                                            <div className="admin-item-info">
                                                <p className="admin-telegram-id">Telegram ID: {admin.telegram_id}</p>
                                                {editingAdmin?.id === admin.id ? (
                                                    <select
                                                        className="form-select admin-role-select"
                                                        value={editingAdmin.role}
                                                        onChange={(e) => setEditingAdmin({...editingAdmin, role: e.target.value})}
                                                    >
                                                        <option value="Администратор">Администратор</option>
                                                        <option value="разработчик">Разработчик</option>
                                                        <option value="Модератор">Модератор</option>
                                                    </select>
                                                ) : (
                                                    <p className="admin-role">Роль: {admin.role}</p>
                                                )}
                                            </div>
                                            <div className="admin-item-actions">
                                                {editingAdmin?.id === admin.id ? (
                                                    <>
                                                        <button
                                                            className="btn-save-admin"
                                                            onClick={() => handleUpdateAdmin(admin.id, editingAdmin.role)}
                                                        >
                                                            Сохранить
                                                        </button>
                                                        <button
                                                            className="btn-cancel-admin"
                                                            onClick={() => setEditingAdmin(null)}
                                                        >
                                                            Отмена
                                                        </button>
                                                    </>
                                                ) : (
                                                    <>
                                                        <button
                                                            className="btn-edit-admin"
                                                            onClick={() => setEditingAdmin(admin)}
                                                        >
                                                            Редактировать
                                                        </button>
                                                        <button
                                                            className="btn-delete-admin"
                                                            onClick={() => handleDeleteAdmin(admin.id)}
                                                        >
                                                            Удалить
                                                        </button>
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                )}

                <div className="profile-section">
                    <h2 className="section-title">Мои записи на вебинары</h2>
                    {!apiConnected && (
                        <div className="error-banner" style={{ margin: '20px 0', padding: '15px', backgroundColor: '#ff9800', color: 'white', borderRadius: '8px' }}>
                            ⚠️ Сервер недоступен. Записи не могут быть загружены.
                        </div>
                    )}
                    {loading ? (
                        <div className="loading-container">
                            <div className="loading-spinner"></div>
                            <p>Загрузка записей...</p>
                        </div>
                    ) : bookings.length > 0 ? (
                        <div className="bookings-list">
                            {bookings.map(booking => (
                                <div key={booking.id} className="user-booking-card">
                                    <div className="booking-header">
                                        <h3 className="booking-title">
                                            {booking.webinar_id ? getWebinarTitle(booking.webinar_id) : (booking.topic || 'Консультация')}
                                        </h3>
                                        <span className={`booking-status ${booking.status === 'confirmed' || booking.status === 'active' ? 'confirmed' : ''}`}>
                                            {booking.status === 'confirmed' || booking.status === 'active' ? '✓ Подтверждено' : booking.status}
                                        </span>
                                    </div>
                                    <div className="booking-details">
                                        <span className="booking-date">📅 {formatDate(booking.date)}</span>
                                        {booking.time && <span className="booking-time">🕐 {booking.time}</span>}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="empty-state">
                            <p>Вы еще не записаны ни на один вебинар</p>
                            {apiConnected && <p className="empty-hint">Перейдите во вкладку "Vebinars" чтобы выбрать вебинар</p>}
                        </div>
                    )}
                </div>
            </div>
        </ScreenWrapper>
    );
}

