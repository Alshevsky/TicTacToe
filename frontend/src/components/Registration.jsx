import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '@styles/Registration.css';

const RegistrationPage = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    try {
        const userData = {
            username: username,
            email: email,
            password: password,
        };

        const response = await fetch('http://localhost:8000/api/v1/auth/register', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        if (!response.ok) {
            toast.error(await response.json())
            throw new Error('Ошибка регистрации');
        }

        const data = await response.json();

        // Уведомление об успешной регистрации
        toast.success('Регистрация прошла успешно!');
        navigate('/login'); // Перенаправляем на страницу входа
    } catch (err) {
        setError('Ошибка при регистрации');
    }
  };

  return (
    <div className="registration-container">
      <h1 className="game-title">Tic-Tac-Toe Online</h1>
      <h2 className="registration-title">Регистрация</h2>
      <form className="registration-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Имя пользователя:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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
        <div className="form-group">
          <label htmlFor="confirmPassword">Подтвердите пароль:</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>
        {error && <p className="error-message">{error}</p>}
        <button type="submit" className="btn-register">
          Зарегистрироваться
        </button>
        <button
          type="button"
          className="btn-login"
          onClick={() => navigate('/login')}
        >
          Уже есть аккаунт? Войти
        </button>
      </form>
    </div>
  );
};

export default RegistrationPage;