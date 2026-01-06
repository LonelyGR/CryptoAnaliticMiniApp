import React, { useState, useRef } from 'react';
import bannerImage from '../assets/baner.jpeg';

export default function PromoBanner({ onDepositClick }) {
    const [expanded, setExpanded] = useState(false);
    const [currentPromo, setCurrentPromo] = useState(0);
    const [isTransitioning, setIsTransitioning] = useState(false);
    const touchStartX = useRef(null);
    const touchEndX = useRef(null);

    const promos = [
        {
            title: "Event 1: Trade Reward",
            subtitle: "(Only for the first 100 people)",
            description: "First Trade → Get 10 - 500 USDT Futures Bonus",
            type: "trade"
        },
        {
            title: "Event 2: Deposit Reward",
            subtitle: "(Deposit bonus only for users registering during the campaign)",
            description: "Deposit and get up to 400 USDT Futures Bonus",
            type: "deposit",
            tiers: [
                { deposit: 100, bonus: 20 },
                { deposit: 200, bonus: 40 },
                { deposit: 500, bonus: 100 },
                { deposit: 1000, bonus: 200 },
                { deposit: 2000, bonus: 400 }
            ],
            timeRange: "14 AUGUST - 13 SEPTEMBER"
        }
    ];

    const current = promos[currentPromo];
    const maxBonus = current.tiers ? Math.max(...current.tiers.map(t => t.bonus)) : 500;

    // Swipe handlers
    const minSwipeDistance = 50;

    const onTouchStart = (e) => {
        touchEndX.current = null;
        touchStartX.current = e.targetTouches[0].clientX;
    };

    const onTouchMove = (e) => {
        touchEndX.current = e.targetTouches[0].clientX;
    };

    const changePromo = (newIndex) => {
        if (newIndex === currentPromo) return;
        setIsTransitioning(true);
        setTimeout(() => {
            setCurrentPromo(newIndex);
            setExpanded(false);
            setTimeout(() => setIsTransitioning(false), 50);
        }, 150);
    };

    const onTouchEnd = () => {
        if (!touchStartX.current || !touchEndX.current) return;
        
        const distance = touchStartX.current - touchEndX.current;
        const isLeftSwipe = distance > minSwipeDistance;
        const isRightSwipe = distance < -minSwipeDistance;

        if (isLeftSwipe && currentPromo < promos.length - 1) {
            changePromo(currentPromo + 1);
        }
        if (isRightSwipe && currentPromo > 0) {
            changePromo(currentPromo - 1);
        }
        
        // Reset touch values
        touchStartX.current = null;
        touchEndX.current = null;
    };

    return (
        <div 
            className="promo-banner"
            style={{ backgroundImage: `url(${bannerImage})` }}
            onTouchStart={onTouchStart}
            onTouchMove={onTouchMove}
            onTouchEnd={onTouchEnd}
        >
            <div className="promo-banner-overlay"></div>
            <div className={`promo-content ${isTransitioning ? 'transitioning' : ''}`}>
                <div className="promo-header">
                    <h3 className="promo-title">{current.title}</h3>
                    <p className="promo-subtitle">{current.subtitle}</p>
                </div>

                <p className="promo-description">
                    {current.description.split('→').map((part, i) => (
                        <React.Fragment key={i}>
                            {i > 0 && ' → '}
                            {part.match(/\d+/g) ? (
                                <span className="highlight-green">{part}</span>
                            ) : (
                                part
                            )}
                        </React.Fragment>
                    ))}
                </p>

                {current.type === 'deposit' && (
                    <>
                        <div className="promo-divider"></div>
                        <div className={`deposit-tiers-wrapper ${expanded ? 'expanded' : ''}`}>
                            {expanded && (
                                <div className="deposit-tiers">
                                    {current.tiers.map((tier, index) => {
                                        const height = (tier.bonus / maxBonus) * 90 + 30;
                                        return (
                                            <div 
                                                key={index} 
                                                className="tier-item"
                                                style={{ animationDelay: `${index * 0.1}s` }}
                                            >
                                                <div className="tier-bar-container">
                                                    <div 
                                                        className="tier-bar"
                                                        style={{ 
                                                            height: `${height}px`,
                                                            animationDelay: `${index * 0.15}s`
                                                        }}
                                                    >
                                                        <div className="tier-bar-gradient"></div>
                                                        <span className="tier-bonus">
                                                            <span className="tier-bonus-number">{tier.bonus}</span>
                                                            <span className="tier-bonus-currency">USDT</span>
                                                        </span>
                                                    </div>
                                                </div>
                                                <div className="tier-label">
                                                    <span className="tier-deposit-amount">{tier.deposit}</span>
                                                    <span className="tier-deposit-label">USDT</span>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                            {expanded && (
                                <div className="promo-time">
                                    <span className="time-icon">⏰</span>
                                    <span className="time-text">{current.timeRange}</span>
                                </div>
                            )}
                        </div>
                    </>
                )}

                <button 
                    className="promo-cta"
                    onClick={(e) => {
                        e.stopPropagation();
                        if (current.type === 'deposit') {
                            setExpanded(!expanded);
                        }
                        if (onDepositClick) onDepositClick();
                    }}
                    onTouchStart={(e) => e.stopPropagation()}
                >
                    {current.type === 'deposit' ? (
                        <>
                            Deposit Rewards {expanded ? '↑' : '↓'}
                        </>
                    ) : (
                        'Get Started'
                    )}
                </button>
            </div>

            {promos.length > 1 && (
                <div className="promo-indicators">
                    {promos.map((_, index) => (
                        <button
                            key={index}
                            className={`promo-dot ${index === currentPromo ? 'active' : ''}`}
                            onClick={() => changePromo(index)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

