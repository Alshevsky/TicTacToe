import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '@context/AuthContext';
import '@styles/Profile.css';
import Header from '@components/Header';


const ProfilePage = () => {
  const { token, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [userName, setUserName] = useState('');
  const [stats, setStats] = useState({
    totalGames: 0,
    wins: 0,
    losses: 0
  });
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/profile', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Ошибка загрузки профиля');
        }

        const data = await response.json();
        setUserName(data.userName);
        setStats(data.stats);
      } catch (err) {
        setError('Не удалось загрузить профиль');
      }
    };

    fetchProfile();
  }, [token]);

  const handlePasswordChange = async () => {
    if (newPassword !== confirmPassword) {
      setError('Новые пароли не совпадают');
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/v1/profile/password', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          oldPassword,
          newPassword,
        }),
      });

      if (!response.ok) {
        throw new Error('Ошибка смены пароля');
      }

      setSuccess('Пароль успешно изменен');
      setIsPasswordModalOpen(false);
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setError('Не удалось изменить пароль');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="profile-container">
      <Header />

      <div className="profile-content">
        <h1>Профиль пользователя</h1>
        <div className="profile-info">
          <h2>{userName}</h2>
          <div className="stats-container">
            <div className="stat-item">
              <span className="stat-label">Всего игр:</span>
              <span className="stat-value">{stats.totalGames}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Победы:</span>
              <span className="stat-value wins">{stats.wins}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Поражения:</span>
              <span className="stat-value losses">{stats.losses}</span>
            </div>
          </div>
        </div>

        <button 
          className="btn-change-password"
          onClick={() => setIsPasswordModalOpen(true)}
        >
          Сменить пароль
        </button>

        {isPasswordModalOpen && (
          <div className="modal">
            <div className="modal-content">
              <h2>Смена пароля</h2>
              <input
                type="password"
                placeholder="Текущий пароль"
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
              />
              <input
                type="password"
                placeholder="Новый пароль"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
              <input
                type="password"
                placeholder="Подтвердите новый пароль"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
              <div className="modal-buttons">
                <button onClick={handlePasswordChange}>Сохранить</button>
                <button onClick={() => setIsPasswordModalOpen(false)}>Отмена</button>
              </div>
            </div>
          </div>
        )}

        {error && <p className="error-message">{error}</p>}
        {success && <p className="success-message">{success}</p>}
      </div>
    </div>
  );
};

export default ProfilePage; 