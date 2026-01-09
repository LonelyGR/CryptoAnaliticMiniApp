import { useState, useEffect, useCallback } from 'react';
import ScreenWrapper from '../components/ScreenWrapper';
import { getWebinars, createWebinar, updateWebinar, deleteWebinar } from '../services/api';
import './AdminWebinars.css';

export default function AdminWebinars({ user, apiConnected }) {
    const [webinars, setWebinars] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [editingWebinar, setEditingWebinar] = useState(null);
    const [formData, setFormData] = useState({
        title: '',
        date: '',
        time: '',
        duration: '',
        speaker: '',
        description: '',
        status: 'upcoming',
        price: 0,
        price_currency: 'USD'
    });

    const loadWebinars = useCallback(async () => {
        if (apiConnected) {
            try {
                const data = await getWebinars();
                setWebinars(data || []);
            } catch (error) {
                console.error('Failed to load webinars:', error);
            }
        }
        setLoading(false);
    }, [apiConnected]);

    useEffect(() => {
        loadWebinars();
    }, [loadWebinars]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!apiConnected || !user?.telegram_id) {
            alert('Ошибка: пользователь не найден');
            return;
        }

        // Преобразуем цену в нужный формат для API
        const submitData = {
            ...formData,
            price_usd: formData.price_currency === 'USD' ? formData.price : 0,
            price_eur: formData.price_currency === 'EUR' ? formData.price : 0
        };
        // Удаляем временные поля
        delete submitData.price;
        delete submitData.price_currency;

        try {
            if (editingWebinar) {
                await updateWebinar(editingWebinar.id, user.telegram_id, submitData);
                alert('Вебинар обновлен!');
            } else {
                await createWebinar(user.telegram_id, submitData);
                alert('Вебинар создан!');
            }
            setShowCreateForm(false);
            setEditingWebinar(null);
            setFormData({
                title: '',
                date: '',
                time: '',
                duration: '',
                speaker: '',
                description: '',
                status: 'upcoming',
                price: 0,
                price_currency: 'USD'
            });
            loadWebinars();
        } catch (error) {
            console.error('Failed to save webinar:', error);
            alert('Не удалось сохранить вебинар');
        }
    };

    const handleEdit = (webinar) => {
        setEditingWebinar(webinar);
        // Определяем валюту и цену для редактирования
        let price = 0;
        let currency = 'USD';
        if (webinar.price_usd && webinar.price_usd > 0) {
            price = webinar.price_usd;
            currency = 'USD';
        } else if (webinar.price_eur && webinar.price_eur > 0) {
            price = webinar.price_eur;
            currency = 'EUR';
        }
        
        setFormData({
            title: webinar.title || '',
            date: webinar.date || '',
            time: webinar.time || '',
            duration: webinar.duration || '',
            speaker: webinar.speaker || '',
            description: webinar.description || '',
            status: webinar.status || 'upcoming',
            price: price,
            price_currency: currency
        });
        setShowCreateForm(true);
    };

    const handleDelete = async (webinarId) => {
        if (!window.confirm('Вы уверены, что хотите удалить этот вебинар?')) {
            return;
        }

        try {
            await deleteWebinar(webinarId, user.telegram_id);
            alert('Вебинар удален!');
            loadWebinars();
        } catch (error) {
            console.error('Failed to delete webinar:', error);
            alert('Не удалось удалить вебинар');
        }
    };

    if (loading) {
        return (
            <ScreenWrapper>
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Загрузка вебинаров...</p>
                </div>
            </ScreenWrapper>
        );
    }

    return (
        <ScreenWrapper>
            <div className="admin-webinars-container">
                <div className="admin-header">
                    <h1 className="page-title">Управление вебинарами</h1>
                    <button 
                        className="btn-create"
                        onClick={() => {
                            setShowCreateForm(!showCreateForm);
                            setEditingWebinar(null);
                            setFormData({
                                title: '',
                                date: '',
                                time: '',
                                duration: '',
                                speaker: '',
                                description: '',
                                status: 'upcoming'
                            });
                        }}
                    >
                        {showCreateForm ? '✕ Отмена' : '+ Создать вебинар'}
                    </button>
                </div>

                {showCreateForm && (
                    <form className="webinar-form" onSubmit={handleSubmit}>
                        <h2>{editingWebinar ? 'Редактировать вебинар' : 'Создать вебинар'}</h2>
                        
                        <div className="form-group">
                            <label>Название вебинара *</label>
                            <input
                                type="text"
                                className="form-input"
                                value={formData.title}
                                onChange={(e) => setFormData({...formData, title: e.target.value})}
                                required
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Дата *</label>
                                <input
                                    type="date"
                                    className="form-input"
                                    value={formData.date}
                                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                                    min={new Date().toISOString().split('T')[0]}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>Время *</label>
                                <input
                                    type="time"
                                    className="form-input"
                                    value={formData.time}
                                    onChange={(e) => setFormData({...formData, time: e.target.value})}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Продолжительность</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={formData.duration}
                                    onChange={(e) => setFormData({...formData, duration: e.target.value})}
                                    placeholder="Например: 2 часа"
                                />
                            </div>

                            <div className="form-group">
                                <label>Спикер</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={formData.speaker}
                                    onChange={(e) => setFormData({...formData, speaker: e.target.value})}
                                    placeholder="Имя спикера"
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Статус</label>
                            <select
                                className="form-select"
                                value={formData.status}
                                onChange={(e) => setFormData({...formData, status: e.target.value})}
                            >
                                <option value="upcoming">Предстоящий</option>
                                <option value="completed">Завершен</option>
                                <option value="cancelled">Отменен</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Описание</label>
                            <textarea
                                className="form-textarea"
                                value={formData.description}
                                onChange={(e) => setFormData({...formData, description: e.target.value})}
                                rows="4"
                                placeholder="Описание вебинара..."
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Цена *</label>
                                <input
                                    type="number"
                                    className="form-input"
                                    value={formData.price}
                                    onChange={(e) => setFormData({...formData, price: parseFloat(e.target.value) || 0})}
                                    min="0"
                                    step="0.01"
                                    placeholder="0.00"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>Валюта *</label>
                                <select
                                    className="form-select"
                                    value={formData.price_currency}
                                    onChange={(e) => setFormData({...formData, price_currency: e.target.value})}
                                    required
                                >
                                    <option value="USD">USD ($)</option>
                                    <option value="EUR">EUR (€)</option>
                                </select>
                            </div>
                        </div>

                        <div className="form-actions">
                            <button type="submit" className="btn-primary">
                                {editingWebinar ? 'Сохранить изменения' : 'Создать вебинар'}
                            </button>
                            <button 
                                type="button" 
                                className="btn-secondary"
                                onClick={() => {
                                    setShowCreateForm(false);
                                    setEditingWebinar(null);
                                }}
                            >
                                Отмена
                            </button>
                        </div>
                    </form>
                )}

                <div className="webinars-list">
                    {webinars.length === 0 ? (
                        <div className="empty-state">
                            <p>Нет созданных вебинаров</p>
                        </div>
                    ) : (
                        webinars.map(webinar => (
                            <div key={webinar.id} className="webinar-card-admin">
                                <div className="webinar-card-header">
                                    <h3>{webinar.title}</h3>
                                    <span className={`status-badge status-${webinar.status}`}>
                                        {webinar.status === 'upcoming' ? 'Предстоящий' : 
                                         webinar.status === 'completed' ? 'Завершен' : 'Отменен'}
                                    </span>
                                </div>
                                
                                <div className="webinar-card-info">
                                    <p><strong>Дата:</strong> {new Date(webinar.date).toLocaleDateString('ru-RU')}</p>
                                    <p><strong>Время:</strong> {webinar.time}</p>
                                    {webinar.duration && <p><strong>Продолжительность:</strong> {webinar.duration}</p>}
                                    {webinar.speaker && <p><strong>Спикер:</strong> {webinar.speaker}</p>}
                                    {((webinar.price_usd && webinar.price_usd > 0) || (webinar.price_eur && webinar.price_eur > 0)) && (
                                        <p><strong>Цена:</strong> {
                                            [
                                                webinar.price_usd > 0 ? `$${webinar.price_usd}` : null,
                                                webinar.price_eur > 0 ? `€${webinar.price_eur}` : null
                                            ].filter(Boolean).join(' / ')
                                        }</p>
                                    )}
                                    {webinar.description && <p><strong>Описание:</strong> {webinar.description}</p>}
                                </div>

                                <div className="webinar-card-actions">
                                    <button 
                                        className="btn-edit"
                                        onClick={() => handleEdit(webinar)}
                                    >
                                        ✏️ Редактировать
                                    </button>
                                    <button 
                                        className="btn-delete"
                                        onClick={() => handleDelete(webinar.id)}
                                    >
                                        🗑️ Удалить
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </ScreenWrapper>
    );
}

