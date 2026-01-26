import React from 'react';

export default function TraderCard({ trader, rank, onCopyClick, onFollowClick }) {
    const getRankBadge = () => {
        if (rank === 1) return { icon: '🥇', color: 'var(--yellow)', label: '01' };
        if (rank === 2) return { icon: '🥈', color: 'var(--text-2)', label: '02' };
        if (rank === 3) return { icon: '🥉', color: 'var(--text-3)', label: '03' };
        return null;
    };

    const rankBadge = getRankBadge();
    const isTopThree = rank <= 3;

    return (
        <div className={`trader-card ${isTopThree ? 'top-three' : ''}`}>
            {isTopThree && (
                <div className="rank-badge" style={{ borderColor: rankBadge.color }}>
                    <span className="rank-icon">{rankBadge.icon}</span>
                    <span className="rank-number">{rankBadge.label}</span>
                </div>
            )}
            
            <div className="trader-avatar-container">
                <div className="trader-avatar" style={{ background: trader.avatarBg || 'var(--bg-2)' }}>
                    {trader.avatarIcon || '👤'}
                </div>
                {isTopThree && <div className="rank-glow" style={{ borderColor: rankBadge.color }}></div>}
            </div>

            <div className="trader-info">
                <div className="trader-name-row">
                    <h3 className="trader-name">{trader.name}</h3>
                    {trader.rank && <span className="trader-rank-badge">{trader.rank}</span>}
                </div>
                <div className="trader-pnl">
                    <div className="pnl-line">
                        <span className="pnl-label">Master's P&L:</span>
                        <span className="pnl-value positive">+{trader.masterPnl.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                    </div>
                    <div className="pnl-line">
                        <span className="pnl-label">Follower's P&L:</span>
                        <span className="pnl-value positive bold">{trader.followerPnl.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                    </div>
                </div>
            </div>

            <div className="trader-actions">
                {trader.isFollowing ? (
                    <button className="copy-btn following" onClick={onFollowClick}>
                        Following
                    </button>
                ) : (
                    <button 
                        className={`copy-btn ${isTopThree ? 'top-three-btn' : ''}`}
                        onClick={onCopyClick || onFollowClick}
                    >
                        {trader.buttonText || 'Copy'}
                    </button>
                )}
            </div>
        </div>
    );
}

