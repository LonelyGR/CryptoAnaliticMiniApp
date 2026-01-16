import React from 'react';
import logo from '../assets/logo.jpg';

export default function CopyTradingHeader({ username, user, onDepositClick }) {
    const avatarUrl = user?.photo_url;
    const getInitials = () => {
        if (user?.first_name) {
            return user.first_name.charAt(0).toUpperCase();
        }
        if (username) {
            return username.charAt(0).toUpperCase();
        }
        return "?";
    };

    return (
        <header className="copy-trading-header">
            <div className="header-left">
                <div className="logo-bitunix">
                    <img src={logo} alt="Crypto Sensey logo" className="logo-img" />
                </div>
            </div>
            <div className="header-center">
                <h1 className="header-title">CRYPTO SENSEI</h1>
            </div>
            <div className="avatar">
                {avatarUrl ? (
                    <img 
                        src={avatarUrl} 
                        alt="Avatar" 
                        className="avatar-img" 
                        onError={(e) => {
                            e.target.style.display = 'none';
                            const placeholder = e.target.parentElement.querySelector('.avatar-placeholder');
                            if (placeholder) {
                                placeholder.style.display = 'flex';
                            }
                        }} 
                    />
                ) : null}
                <div className="avatar-placeholder" style={{ display: avatarUrl ? 'none' : 'flex' }}>
                    {getInitials()}
                </div>
            </div>            
        </header>
    );
}

