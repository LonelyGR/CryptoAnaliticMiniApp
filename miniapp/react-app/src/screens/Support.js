import { useState } from 'react';
import ScreenWrapper from '../components/ScreenWrapper';

export default function Support() {
    const [activeTab, setActiveTab] = useState('support');

    return (
        <ScreenWrapper>
            <div className="support-container">
                <h1 className="page-title">Поддержка</h1>
                
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
                    <div className="support-form">
                        <div className="form-group">
                            <label htmlFor="subject">Тема обращения</label>
                            <input 
                                type="text" 
                                id="subject"
                                className="form-input"
                                placeholder="Например: Проблема с записью на вебинар"
                            />
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="message">Сообщение</label>
                            <textarea 
                                id="message"
                                className="form-textarea"
                                rows="6"
                                placeholder="Опишите вашу проблему или вопрос..."
                            />
                        </div>
                        
                        <button className="btn-primary">Отправить обращение</button>
                    </div>
                ) : (
                    <div className="consultation-form">
                        <div className="consultation-info">
                            <p>Запишитесь на персональную консультацию с нашим экспертом. Мы поможем вам разобраться в тонкостях криптотрейдинга и ответим на все ваши вопросы.</p>
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="consultation-topic">Тема консультации</label>
                            <select id="consultation-topic" className="form-select">
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
                            />
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="consultation-time">Предпочтительное время</label>
                            <select id="consultation-time" className="form-select">
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
                            />
                        </div>
                        
                        <button className="btn-primary">Записаться на консультацию</button>
                    </div>
                )}
            </div>
        </ScreenWrapper>
    );
}

