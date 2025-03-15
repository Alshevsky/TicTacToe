// src/components/HomePage.jsx
import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '@context/AuthContext';

const HomePage = () => {
  const { token, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div>
      <h1>Добро пожаловать!</h1>
      <p>Вы авторизованы.</p>
      <button onClick={handleLogout}>Выйти</button>
    </div>
  );
};

export default HomePage;