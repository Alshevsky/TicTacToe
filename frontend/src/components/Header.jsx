import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '@context/AuthContext';
import '@styles/Header.css';

const Header = () => {
  const navigate = useNavigate();
  const { logout } = useContext(AuthContext);

  const handleProfileClick = () => {
    navigate('/profile');
  };

  const handleLogoClick = () => {
    navigate('/');
  };

  return (
    <header className="header">
      <div className="logo" onClick={handleLogoClick}>
        Tic-Tac-Toe Online
      </div>
      <div className="header-buttons">
        <button className="btn-profile" onClick={handleProfileClick}>
          Профиль
        </button>
        <button className="btn-logout" onClick={logout}>
          Выйти
        </button>
      </div>
    </header>
  );
};

export default Header; 