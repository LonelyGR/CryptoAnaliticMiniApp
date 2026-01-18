import { useCallback, useEffect, useMemo, useState } from 'react';
import ScreenWrapper from '../components/ScreenWrapper';
import Header from '../components/Header';
import { getUsers, updateUserBlocked } from '../services/api';

export default function UsersManagement({ user, apiConnected, onBack }) {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [updatingUserId, setUpdatingUserId] = useState(null);
    const [searchValue, setSearchValue] = useState('');

    const loadUsers = useCallback(async () => {
        if (!apiConnected) {
            setUsers([]);
            setLoading(false);
            return;
        }

        setLoading(true);
        try {
            const data = await getUsers();
            const filtered = (data || []).filter((entry) => !entry.is_admin);
            setUsers(filtered);
        } catch (error) {
            console.error('Failed to load users:', error);
            setUsers([]);
        } finally {
            setLoading(false);
        }
    }, [apiConnected]);

    useEffect(() => {
        loadUsers();
    }, [loadUsers]);

    const filteredUsers = useMemo(() => {
        const normalized = searchValue.trim().toLowerCase().replace('@', '');
        if (!normalized) return users;

        return users.filter((entry) => {
            const username = (entry.username || '').toLowerCase();
            const telegramId = String(entry.telegram_id || '');
            const internalId = String(entry.id || '');
            return (
                username.includes(normalized) ||
                telegramId.includes(normalized) ||
                internalId.includes(normalized)
            );
        });
    }, [searchValue, users]);

    const handleToggleBlocked = async (targetUser) => {
        if (!user?.telegram_id && !user?.id) return;
        const adminTelegramId = user?.telegram_id || user?.id;
        setUpdatingUserId(targetUser.id);
        try {
            await updateUserBlocked(targetUser.id, adminTelegramId, !targetUser.is_blocked);
            await loadUsers();
        } catch (error) {
            alert('Не удалось изменить статус блокировки пользователя');
        } finally {
            setUpdatingUserId(null);
        }
    };

    return (
        <ScreenWrapper>
            <Header username={user?.first_name} user={user} />
            <div className="profile-container">
                <div className="profile-section">
                    <div className="section-header-row">
                        <h2 className="section-title">Управление пользователями</h2>
                        <button className="btn-secondary-admin" onClick={onBack}>Назад</button>
                    </div>

                    {!apiConnected && (
                        <div className="error-banner">
                            Сервер недоступен. Пользователи не могут быть загружены.
                        </div>
                    )}

                    <div className="form-group" style={{ marginBottom: '16px' }}>
                        <input
                            type="text"
                            className="form-input"
                            value={searchValue}
                            onChange={(event) => setSearchValue(event.target.value)}
                            placeholder="Поиск по ID или username"
                        />
                    </div>

                    {loading ? (
                        <div className="loading-container">
                            <div className="loading-spinner"></div>
                            <p>Загрузка пользователей...</p>
                        </div>
                    ) : filteredUsers.length === 0 ? (
                        <div className="empty-state">
                            <p>Пользователи не найдены</p>
                        </div>
                    ) : (
                        <div className="users-list">
                            {filteredUsers.map((entry) => (
                                <div key={entry.id} className="user-row">
                                    <div className="user-row-info">
                                        <div className="user-row-name">
                                            {entry.first_name || entry.username || 'Пользователь'} {entry.last_name || ''}
                                        </div>
                                        <div className="user-row-meta">
                                            {entry.username ? `@${entry.username}` : 'Без username'} · ID {entry.telegram_id}
                                        </div>
                                    </div>
                                    <button
                                        className={`btn-block-user ${entry.is_blocked ? 'active' : ''}`}
                                        onClick={() => handleToggleBlocked(entry)}
                                        disabled={updatingUserId === entry.id}
                                    >
                                        {entry.is_blocked ? 'Разблокировать' : 'Заблокировать'}
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </ScreenWrapper>
    );
}
