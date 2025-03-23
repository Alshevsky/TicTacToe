import '@styles/App.css'
import 'normalize.css'
import LoginPage from '@components/Login';
import RegistrationPage from '@components/Registration';
import HomePage from '@components/Home';
import GamePage from '@components/Game';
import ProtectedRoute from '@components/ProtectedRoute';
import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthContext } from '@context/AuthContext';
import { AuthProvider } from '@context/AuthContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  const { token } = useContext(AuthContext);
  return (
    <div className="app-container">
      <div className="background-animation">
        {[...Array(30)].map((_, index) => {
          const randomLeft = Math.random() * 100; // Случайное положение по горизонтали
          const randomDelay = Math.random() * 5; // Случайная задержка анимации
          const randomSize = Math.floor(Math.random() * 24) + 16; // Случайный размер (от 16px до 40px)
          return (
            <div
              key={index}
              className="symbol"
              style={{
                left: `${randomLeft}%`,
                animationDelay: `${randomDelay}s`,
                fontSize: `${randomSize}px`,
              }}
            >
              {Math.random() > 0.5 ? '❌' : '⭕'}
            </div>
          );
        })}
      </div>

      <AuthProvider>
      <Router>
        <ToastContainer />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegistrationPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/game/:id"
            element={
              <ProtectedRoute>
                <GamePage />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<div>Страница не найдена</div>} />
        </Routes>
      </Router>
    </AuthProvider>
    </div>
  );
}

export default App;
