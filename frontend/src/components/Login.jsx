// src/components/LoginPage.jsx
import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '@context/AuthContext';
import '@styles/Login.css';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // Отправляем запрос на бэкенд
      const response = await fetch('http://localhost:8000/api/v1/auth/jwt/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify({ username: username, password: password, grant_type: 'password'}),
      });

      if (!response.ok) {
        toast.error(await response.json())
        throw new Error('Ошибка авторизации');
      }

      const data = await response.json();
      const token = data.token; // Предполагаем, что токен приходит в ответе

      // Сохраняем токен и перенаправляем на главную страницу
      login(token);
      navigate('/');
    } catch (err) {
      setError('Неверный логин или пароль');
    }
  };

  return (
    <div className="login-container">
      <h1 className="game-title">Tic-Tac-Toe Online</h1>
      <h2 className="login-title">Вход</h2>
      <form className="login-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Логин:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Пароль:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <p className="error-message">{error}</p>}
        <button type="submit" className="btn-login">
          Войти
        </button>
        <button type="button" className="btn-register" onClick={() => navigate('/register')}>
          Регистрация
        </button>
        <button type="button" className="btn-forgot-password" onClick={() => navigate('/forgot-password')}>
          Забыли пароль?
        </button>
      </form>
    </div>
  );
};

export default LoginPage;