import { useState } from 'react';
import ScreenWrapper from '../components/ScreenWrapper';
import { createBooking, getUserByTelegramId, createOrUpdateUser } from '../services/api';

export default function Support({ user, apiConnected }) {
    const [activeTab, setActiveTab] = useState('support');
    const [formData, setFormData] = useState({
        subject: '',
        message: '',
        topic: '',
        date: '',
        time: '',
        consultationMessage: ''
    });
    const [submitting, setSubmitting] = useState(false);

    const handleSupportSubmit = async (e) => {
        e.preventDefault();
        if (!apiConnected) {
            alert('Сервер недоступен');
            return;
        }

        if (!formData.subject || !formData.message) {
            alert('Пожалуйста, заполните тему и сообщение');
            return;
        }

        setSubmitting(true);
        try {
            const telegramId = user?.telegram_id || user?.id;
            if (!telegramId) {
                alert('Пользователь не найден');
                return;
            }
            
            let dbUser = await getUserByTelegramId(telegramId);
            if (!dbUser) {
                // Пытаемся создать пользователя
                dbUser = await createOrUpdateUser(telegramId, {
                    username: user?.username || null,
                    first_name: user?.first_name || null,
                    last_name: user?.last_name || null,
                    photo_url: user?.photo_url || null,
                });
            }
            
            if (!dbUser) {
                alert('Не удалось создать пользователя в базе данных');
                return;
            }

            await createBooking({
                user_id: dbUser.id,
                type: 'support',
                date: new Date().toISOString().split('T')[0],
                topic: formData.subject,
                message: formData.message,
                status: 'active'
            });

            alert('Ваше обращение отправлено! Мы свяжемся с вами в ближайшее время.');
            setFormData({
                subject: '',
                message: '',
                topic: formData.topic,
                date: formData.date,
                time: formData.time,
                consultationMessage: formData.consultationMessage
            });
        } catch (error) {
            console.error('Failed to create support ticket:', error);
            alert('Не удалось отправить обращение. Попробуйте позже.');
        } finally {
            setSubmitting(false);
        }
    };

    const handleConsultationSubmit = async (e) => {
        e.preventDefault();
        if (!apiConnected) {
            alert('Сервер недоступен');
            return;
        }

        if (!formData.topic || !formData.date || !formData.time) {
            alert('Пожалуйста, заполните все обязательные поля');
            return;
        }

        setSubmitting(true);
        try {
            const telegramId = user?.telegram_id || user?.id;
            if (!telegramId) {
                alert('Пользователь не найден');
                return;
            }
            
            let dbUser = await getUserByTelegramId(telegramId);
            if (!dbUser) {
                // Пытаемся создать пользователя
                dbUser = await createOrUpdateUser(telegramId, {
                    username: user?.username || null,
                    first_name: user?.first_name || null,
                    last_name: user?.last_name || null,
                    photo_url: user?.photo_url || null,
                });
            }
            
            if (!dbUser) {
                alert('Не удалось создать пользователя в базе данных');
                return;
            }

            await createBooking({
                user_id: dbUser.id,
                type: 'consultation',
                date: formData.date,
                time: formData.time,
                topic: formData.topic,
                message: formData.consultationMessage,
                status: 'active'
            });

            alert('Вы успешно записались на консультацию!');
            setFormData({
                subject: '',
                message: '',
                topic: '',
                date: '',
                time: '',
                consultationMessage: ''
            });
        } catch (error) {
            console.error('Failed to create consultation:', error);
            alert('Не удалось записаться на консультацию. Попробуйте позже.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <ScreenWrapper>
            <div className="support-container">
                <h1 className="page-title">Поддержка</h1>
                
                {!apiConnected && (
                    <div className="error-banner" style={{ margin: '20px 0', padding: '15px', backgroundColor: '#ff9800', color: 'white', borderRadius: '8px' }}>
                        ⚠️ Сервер недоступен. Запись на консультацию недоступна.
                    </div>
                )}
                
                <div className="support-tabs">
                    <button 
                        className={`support-tab ${activeTab === 'support' ? 'active' : ''}`}
                        onClick={() => setActiveTab('support')}
                    >
                        Обращение в поддержку
                    </button>
                    <button 
                        className={`support-tab ${activeTab === 'consultation' ? 'active' : ''}`}
                        onClick={() => setActiveTab('consultation')}
                    >
                        Запись на консультацию
                    </button>
                </div>

                {activeTab === 'support' ? (
                    <form className="support-form" onSubmit={handleSupportSubmit}>
                        <div className="form-group">
                            <label htmlFor="subject">Тема обращения</label>
                            <input 
                                type="text" 
                                id="subject"
                                className="form-input"
                                placeholder="Например: Проблема с записью на вебинар"
                                value={formData.subject}
                                onChange={(e) => setFormData({...formData, subject: e.target.value})}
                            />
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="message">Сообщение</label>
                            <textarea 
                                id="message"
                                className="form-textarea"
                                rows="6"
                                placeholder="Опишите вашу проблему или вопрос..."
                                value={formData.message}
                                onChange={(e) => setFormData({...formData, message: e.target.value})}
                            />
                        </div>
                        
                        <button type="submit" className="btn-primary" disabled={!apiConnected || submitting}>
                            {submitting ? 'Отправка...' : 'Отправить обращение'}
                        </button>
                    </form>
                ) : (
                    <form className="consultation-form" onSubmit={handleConsultationSubmit}>
                        <div className="consultation-info">
                            <p>Запишитесь на персональную консультацию с нашим экспертом. Мы поможем вам разобраться в тонкостях криптотрейдинга и ответим на все ваши вопросы.</p>
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="consultation-topic">Тема консультации</label>
                            <select 
                                id="consultation-topic" 
                                className="form-select"
                                value={formData.topic}
                                onChange={(e) => setFormData({...formData, topic: e.target.value})}
                                required
                            >
                                <option value="">Выберите тему</option>
                                <option value="beginner">Базовые основы трейдинга</option>
                                <option value="technical">Технический анализ</option>
                                <option value="defi">DeFi и стейкинг</option>
                                <option value="strategy">Торговые стратегии</option>
                                <option value="other">Другое</option>
                            </select>
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="consultation-date">Предпочтительная дата</label>
                            <input 
                                type="date" 
                                id="consultation-date"
                                className="form-input"
                                min={new Date().toISOString().split('T')[0]}
                                value={formData.date}
                                onChange={(e) => setFormData({...formData, date: e.target.value})}
                                required
                            />
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="consultation-time">Предпочтительное время</label>
                            <select 
                                id="consultation-time" 
                                className="form-select"
                                value={formData.time}
                                onChange={(e) => setFormData({...formData, time: e.target.value})}
                                required
                            >
                                <option value="">Выберите время</option>
                                <option value="10:00">10:00</option>
                                <option value="12:00">12:00</option>
                                <option value="14:00">14:00</option>
                                <option value="16:00">16:00</option>
                                <option value="18:00">18:00</option>
                                <option value="20:00">20:00</option>
                            </select>
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="consultation-message">Дополнительная информация</label>
                            <textarea 
                                id="consultation-message"
                                className="form-textarea"
                                rows="4"
                                placeholder="Опишите вопросы, которые хотели бы обсудить..."
                                value={formData.consultationMessage}
                                onChange={(e) => setFormData({...formData, consultationMessage: e.target.value})}
                            />
                        </div>
                        
                        <button 
                            type="submit" 
                            className="btn-primary" 
                            disabled={!apiConnected || submitting}
                        >
                            {submitting ? 'Запись...' : 'Записаться на консультацию'}
                        </button>
                    </form>
                )}
            </div>
        </ScreenWrapper>
    );
}

