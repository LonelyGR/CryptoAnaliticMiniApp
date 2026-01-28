import { useState, useEffect, useCallback } from 'react';
import ScreenWrapper from '../components/ScreenWrapper';
import { getConsultations, getSupportTickets, respondToConsultation, deleteTicket } from '../services/api';
import './AdminTickets.css';

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', { 
        day: 'numeric', 
        month: 'long', 
        year: 'numeric' 
    });
}

export default function AdminTickets({ user, apiConnected }) {
    const [activeTab, setActiveTab] = useState('consultations'); // consultations или support
    const [consultations, setConsultations] = useState([]);
    const [supportTickets, setSupportTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedTicket, setSelectedTicket] = useState(null);
    const [responseText, setResponseText] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [filter, setFilter] = useState('all'); // all, active, answered

    const loadConsultations = useCallback(async () => {
        const adminTelegramId = user?.telegram_id || user?.id;
        if (!apiConnected || !adminTelegramId) return;
        
        setLoading(true);
        try {
            const data = await getConsultations(adminTelegramId);
            let filtered = data || [];
            
            if (filter === 'active') {
                filtered = filtered.filter(t => t.status === 'active');
            } else if (filter === 'answered') {
                filtered = filtered.filter(t => t.status === 'answered');
            }
            
            setConsultations(filtered);
        } catch (error) {
            console.error('Failed to load consultations:', error);
            setConsultations([]);
        } finally {
            setLoading(false);
        }
    }, [apiConnected, user?.telegram_id, filter]);

    const loadSupportTickets = useCallback(async () => {
        const adminTelegramId = user?.telegram_id || user?.id;
        if (!apiConnected || !adminTelegramId) return;
        
        setLoading(true);
        try {
            const data = await getSupportTickets(adminTelegramId);
            let filtered = data || [];
            
            if (filter === 'active') {
                filtered = filtered.filter(t => t.status === 'active');
            } else if (filter === 'answered') {
                filtered = filtered.filter(t => t.status === 'answered');
            }
            
            setSupportTickets(filtered);
        } catch (error) {
            console.error('Failed to load support tickets:', error);
            setSupportTickets([]);
        } finally {
            setLoading(false);
        }
    }, [apiConnected, user?.telegram_id, filter]);

    useEffect(() => {
        const adminTelegramId = user?.telegram_id || user?.id;
        if (apiConnected && adminTelegramId) {
            if (activeTab === 'consultations') {
                loadConsultations();
            } else {
                loadSupportTickets();
            }
        }
    }, [apiConnected, user?.telegram_id, user?.id, filter, activeTab, loadConsultations, loadSupportTickets]);

    const handleRespond = async (ticketId) => {
        if (!responseText.trim()) {
            alert('Пожалуйста, введите ответ');
            return;
        }

        setSubmitting(true);
        try {
            const adminTelegramId = user?.telegram_id || user?.id;
            await respondToConsultation(ticketId, adminTelegramId, responseText);
            alert('Ответ отправлен!');
            setResponseText('');
            setSelectedTicket(null);
            if (activeTab === 'consultations') {
                loadConsultations();
            } else {
                loadSupportTickets();
            }
        } catch (error) {
            console.error('Failed to respond:', error);
            alert('Не удалось отправить ответ');
        } finally {
            setSubmitting(false);
        }
    };

    const currentTickets = activeTab === 'consultations' ? consultations : supportTickets;

    if (loading) {
        return (
            <ScreenWrapper>
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Загрузка тикетов...</p>
                </div>
            </ScreenWrapper>
        );
    }

    return (
        <ScreenWrapper>
            <div className="admin-tickets-container">
                <div className="admin-header">
                    <h1 className="page-title">Тикеты</h1>
                    <div className="tabs-container">
                        <button 
                            className={`tab-btn ${activeTab === 'consultations' ? 'active' : ''}`}
                            onClick={() => {
                                setActiveTab('consultations');
                                setFilter('all');
                            }}
                        >
                            Консультации
                        </button>
                        <button 
                            className={`tab-btn ${activeTab === 'support' ? 'active' : ''}`}
                            onClick={() => {
                                setActiveTab('support');
                                setFilter('all');
                            }}
                        >
                            Поддержка
                        </button>
                    </div>
                    <div className="filter-buttons">
                        <button 
                            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                            onClick={() => setFilter('all')}
                        >
                            Все
                        </button>
                        <button 
                            className={`filter-btn ${filter === 'active' ? 'active' : ''}`}
                            onClick={() => setFilter('active')}
                        >
                            Активные
                        </button>
                        <button 
                            className={`filter-btn ${filter === 'answered' ? 'active' : ''}`}
                            onClick={() => setFilter('answered')}
                        >
                            Отвеченные
                        </button>
                    </div>
                </div>

                {currentTickets.length === 0 ? (
                    <div className="empty-state">
                        <p>Нет {activeTab === 'consultations' ? 'консультаций' : 'обращений в поддержку'}</p>
                    </div>
                ) : (
                    <div className="tickets-list">
                        {currentTickets.map(ticket => (
                            <div 
                                key={ticket.id} 
                                className={`ticket-card ${ticket.status === 'answered' ? 'answered' : ''}`}
                            >
                                <div className="ticket-header">
                                    <div className="ticket-user-info">
                                        <h3>
                                            {ticket.user_first_name || 'Пользователь'} 
                                            {ticket.user_username && ` (@${ticket.user_username})`}
                                        </h3>
                                        <p className="ticket-id">ID: {ticket.user_telegram_id}</p>
                                    </div>
                                    <span className={`ticket-status status-${ticket.status}`}>
                                        {ticket.status === 'active' ? 'Активен' : 'Отвечен'}
                                    </span>
                                </div>

                                <div className="ticket-content">
                                    <div className="ticket-info">
                                        <p><strong>{activeTab === 'consultations' ? 'Тема:' : 'Тема обращения:'}</strong> {
                                            activeTab === 'consultations' ? (
                                                ticket.topic === 'beginner' ? 'Базовые основы трейдинга' :
                                                ticket.topic === 'technical' ? 'Технический анализ' :
                                                ticket.topic === 'defi' ? 'DeFi и стейкинг' :
                                                ticket.topic === 'strategy' ? 'Торговые стратегии' :
                                                ticket.topic === 'other' ? 'Другое' : ticket.topic
                                            ) : ticket.topic
                                        }</p>
                                        <p><strong>Дата:</strong> {formatDate(ticket.date)}</p>
                                        {ticket.time && <p><strong>Время:</strong> {ticket.time}</p>}
                                    </div>

                                    {ticket.message && (
                                        <div className="ticket-message">
                                            <strong>Сообщение пользователя:</strong>
                                            <p>{ticket.message}</p>
                                        </div>
                                    )}

                                    {ticket.admin_response && (
                                        <div className="ticket-response">
                                            <strong>Ваш ответ:</strong>
                                            <p>{ticket.admin_response}</p>
                                        </div>
                                    )}
                                </div>

                                <div className="ticket-actions">
                                    {ticket.status === 'active' && selectedTicket?.id === ticket.id ? (
                                        <div className="response-form">
                                            <textarea
                                                className="form-textarea"
                                                value={responseText}
                                                onChange={(e) => setResponseText(e.target.value)}
                                                placeholder="Введите ваш ответ..."
                                                rows="4"
                                            />
                                            <div className="response-actions">
                                                <button
                                                    className="btn-send"
                                                    onClick={() => handleRespond(ticket.id)}
                                                    disabled={submitting}
                                                >
                                                    {submitting ? 'Отправка...' : 'Отправить ответ'}
                                                </button>
                                                <button
                                                    className="btn-cancel"
                                                    onClick={() => {
                                                        setSelectedTicket(null);
                                                        setResponseText('');
                                                    }}
                                                >
                                                    Отмена
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        <div style={{ display: 'flex', gap: '10px', width: '100%' }}>
                                            {ticket.status === 'active' && (
                                                <button
                                                    className="btn-respond"
                                                    onClick={() => {
                                                        setSelectedTicket(ticket);
                                                        setResponseText('');
                                                    }}
                                                    style={{ flex: 1 }}
                                                >
                                                    Ответить
                                                </button>
                                            )}
                                            <button
                                                className="btn-delete-ticket"
                                                onClick={async () => {
                                                    if (window.confirm('Вы уверены, что хотите удалить этот тикет?')) {
                                                        try {
                                                            await deleteTicket(ticket.id, user.telegram_id);
                                                            alert('Тикет удален');
                                                            if (activeTab === 'consultations') {
                                                                loadConsultations();
                                                            } else {
                                                                loadSupportTickets();
                                                            }
                                                        } catch (error) {
                                                            console.error('Failed to delete ticket:', error);
                                                            alert('Не удалось удалить тикет');
                                                        }
                                                    }
                                                }}
                                            >
                                                Удалить
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </ScreenWrapper>
    );
}

