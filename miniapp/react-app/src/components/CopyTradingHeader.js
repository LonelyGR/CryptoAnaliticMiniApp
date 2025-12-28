import React from 'react';

export default function CopyTradingHeader({ onDepositClick }) {
    return (
        <header className="copy-trading-header">
            <div className="header-left">
                <div className="logo-bitunix">🍃e</div>
                <span className="logo-separator">×</span>
                <div className="logo-cryptosensei">⛩️</div>
            </div>
            <div className="header-center">
                <h1 className="header-title">Crypto Sensey</h1>
            </div>
            <div className="header-right">
                <button className="deposit-btn" onClick={onDepositClick}>
                    Deposit
                </button>
            </div>
        </header>
    );
}

