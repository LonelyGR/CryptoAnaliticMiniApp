import React, { useState, useEffect } from 'react';
import CopyTradingHeader from '../components/CopyTradingHeader';
import PromoBanner from '../components/PromoBanner';
import TraderCard from '../components/TraderCard';
import FollowModal from '../components/FollowModal';
import ScreenWrapper from '../components/ScreenWrapper';

// Mock data for top performers
const mockTraders = [
    {
        id: 1,
        name: 'Kollectiv',
        rank: 'Cadet No.1',
        avatarIcon: '⚫',
        avatarBg: '#000000',
        masterPnl: 60506.43,
        followerPnl: 271899.85,
        buttonText: 'Copy',
        isFollowing: false
    },
    {
        id: 2,
        name: 'CryptoSensei VIP',
        rank: 'Bronze No.1',
        avatarIcon: '⛩️',
        avatarBg: '#8B4513',
        masterPnl: 186.19,
        followerPnl: 33300.55,
        buttonText: 'Follow Now',
        isFollowing: false
    },
    {
        id: 3,
        name: 'Super Hero',
        rank: 'Silver',
        avatarIcon: '🦸',
        avatarBg: '#1E40AF',
        masterPnl: 1035.66,
        followerPnl: 164981.35,
        buttonText: 'Copy',
        isFollowing: false
    },
    {
        id: 4,
        name: 'ITEKrypto',
        rank: 'Gold',
        avatarIcon: '🐂',
        avatarBg: '#F59E0B',
        masterPnl: 12809.54,
        followerPnl: 644559.81,
        buttonText: 'Copy',
        isFollowing: false
    },
    {
        id: 5,
        name: 'CryptoMaster',
        rank: 'Platinum',
        avatarIcon: '💎',
        avatarBg: '#6366F1',
        masterPnl: 4523.21,
        followerPnl: 98765.43,
        buttonText: 'Follow Now',
        isFollowing: false
    },
    {
        id: 6,
        name: 'TradeKing',
        rank: 'Diamond',
        avatarIcon: '👑',
        avatarBg: '#EC4899',
        masterPnl: 8765.12,
        followerPnl: 234567.89,
        buttonText: 'Copy',
        isFollowing: false
    }
];

export default function Home({ user }) {
    const [traders, setTraders] = useState(mockTraders);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedTrader, setSelectedTrader] = useState(null);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
        // Simulate loading
        setLoading(true);
        setTimeout(() => {
            setLoading(false);
        }, 1000);
    }, []);

    const handleDepositClick = () => {
        // Handle deposit action
        if (window.Telegram?.WebApp) {
            window.Telegram.WebApp.showAlert('Redirecting to deposit...');
        } else {
            alert('Redirecting to deposit...');
        }
    };

    const handleCopyClick = (trader) => {
        setSelectedTrader(trader);
        setShowModal(true);
    };

    const handleFollowClick = (trader) => {
        if (trader.isFollowing) {
            // Unfollow
            setTraders(prev => prev.map(t => 
                t.id === trader.id ? { ...t, isFollowing: false } : t
            ));
        } else {
            handleCopyClick(trader);
        }
    };

    const handleConfirmFollow = async (amount) => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));
        
        setTraders(prev => prev.map(t => 
            t.id === selectedTrader.id ? { ...t, isFollowing: true } : t
        ));
        
        if (window.Telegram?.WebApp) {
            window.Telegram.WebApp.showAlert(`Following ${selectedTrader.name} with ${amount} USDT`);
        }
    };

    const handleTraderCardClick = (trader) => {
        // Navigate to trader detail page (placeholder)
        if (window.Telegram?.WebApp) {
            window.Telegram.WebApp.showAlert(`Viewing ${trader.name} details...`);
        }
    };

    return (
        <ScreenWrapper>
            <CopyTradingHeader onDepositClick={handleDepositClick} />
            
            <div className="copy-trading-home">
                <PromoBanner onDepositClick={handleDepositClick} />

                {error && (
                    <div className="error-banner">
                        <span>{error}</span>
                        <button onClick={() => setError(null)}>Retry</button>
                    </div>
                )}

                {loading ? (
                    <div className="loading-container">
                        <div className="loading-spinner"></div>
                        <p>Loading Top Traders...</p>
                    </div>
                ) : (
                    <section className="top-performers-section">
                        <div className="section-header">
                            <h2 className="section-title">This Week's Top Performers</h2>
                            <p className="section-subtitle">Top-Ranked Master Traders</p>
                        </div>

                        <div className="traders-list">
                            {traders.map((trader, index) => (
                                <div 
                                    key={trader.id}
                                    onClick={() => handleTraderCardClick(trader)}
                                    style={{ cursor: 'pointer' }}
                                >
                                    <TraderCard
                                        trader={trader}
                                        rank={index + 1}
                                        onCopyClick={() => handleCopyClick(trader)}
                                        onFollowClick={() => handleFollowClick(trader)}
                                    />
                                </div>
                            ))}
                        </div>

                        <button className="view-more-btn">
                            View More Traders
                        </button>
                    </section>
                )}
            </div>

            {showModal && selectedTrader && (
                <FollowModal
                    trader={selectedTrader}
                    onClose={() => {
                        setShowModal(false);
                        setSelectedTrader(null);
                    }}
                    onConfirm={handleConfirmFollow}
                />
            )}
        </ScreenWrapper>
    );
}
