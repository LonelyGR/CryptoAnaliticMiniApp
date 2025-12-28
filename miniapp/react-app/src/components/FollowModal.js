import React, { useState } from 'react';

export default function FollowModal({ trader, onClose, onConfirm }) {
    const [amount, setAmount] = useState('');
    const [loading, setLoading] = useState(false);

    const handleConfirm = async () => {
        if (!amount || parseFloat(amount) <= 0) return;
        
        setLoading(true);
        try {
            await onConfirm(parseFloat(amount));
            onClose();
        } catch (error) {
            console.error('Error confirming follow:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Follow {trader.name}</h2>
                    <button className="modal-close" onClick={onClose}>×</button>
                </div>
                
                <div className="modal-body">
                    <div className="trader-summary">
                        <div className="trader-avatar-small">
                            {trader.avatarIcon || '👤'}
                        </div>
                        <div>
                            <p className="trader-name-small">{trader.name}</p>
                            <p className="trader-stats-small">
                                Master's P&L: <span className="positive">+{trader.masterPnl.toLocaleString()}</span>
                            </p>
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="amount">Amount to Copy (USDT)</label>
                        <input
                            id="amount"
                            type="number"
                            className="form-input"
                            placeholder="Enter amount"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            min="1"
                            step="0.01"
                        />
                    </div>

                    <div className="modal-info">
                        <p>Your trades will automatically copy {trader.name}'s positions.</p>
                    </div>
                </div>

                <div className="modal-footer">
                    <button className="btn-secondary" onClick={onClose}>
                        Cancel
                    </button>
                    <button 
                        className="btn-primary" 
                        onClick={handleConfirm}
                        disabled={!amount || parseFloat(amount) <= 0 || loading}
                    >
                        {loading ? 'Confirming...' : 'Confirm'}
                    </button>
                </div>
            </div>
        </div>
    );
}

