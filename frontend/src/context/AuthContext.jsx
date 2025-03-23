import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token') || null);

  const checkTokenValidity = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/users/me', {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Токен невалидный или истек');
      }
      const data = await response.json();
      return data?.is_active;
    } catch (err) {
      console.error('Ошибка проверки токена:', err);
      return false;
    }
  }

  useEffect(() => {
    const validateToken = async () => {
      if (token) {
        const isValid = await checkTokenValidity();
        if (!isValid) {
          logout();
        }
      }
    };

    validateToken();
  }, [token]);


  // Функция для входа
  const login = (newToken) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
  };

  // Функция для выхода
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};