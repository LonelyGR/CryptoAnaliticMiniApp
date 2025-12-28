import React, { useState } from 'react';

export default function PromoBanner({ onDepositClick }) {
    const [expanded, setExpanded] = useState(false);
    const [currentPromo, setCurrentPromo] = useState(0);

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

    return (
        <div className="promo-banner">
            <div className="promo-content">
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
                        {expanded && (
                            <div className="deposit-tiers">
                                {current.tiers.map((tier, index) => {
                                    const height = (tier.bonus / maxBonus) * 120 + 40;
                                    return (
                                        <div key={index} className="tier-item">
                                            <div className="tier-bar-container">
                                                <div 
                                                    className="tier-bar"
                                                    style={{ height: `${height}px` }}
                                                >
                                                    <span className="tier-bonus">{tier.bonus} USDT</span>
                                                </div>
                                            </div>
                                            <div className="tier-label">
                                                Deposit {tier.deposit} USDT
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                        {expanded && (
                            <div className="promo-time">
                                TIME: {current.timeRange}
                            </div>
                        )}
                    </>
                )}

                <button 
                    className="promo-cta"
                    onClick={() => {
                        if (current.type === 'deposit') {
                            setExpanded(!expanded);
                        }
                        if (onDepositClick) onDepositClick();
                    }}
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
                            onClick={() => setCurrentPromo(index)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

