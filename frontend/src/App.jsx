import '@styles/App.css'
import 'normalize.css'
import LoginPage from '@components/Login';
import RegistrationPage from '@components/Registration';
import HomePage from '@components/Home';
import GamePage from '@components/Game';
import ProfilePage from '@components/Profile';
import ProtectedLayout from '@components/ProtectedLayout';
import React, { useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '@context/AuthContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function BackgroundAnimation() {
  const symbols = useMemo(() => 
    [...Array(30)].map(() => ({
      left: Math.random() * 100,
      delay: Math.random() * 5,
      size: Math.floor(Math.random() * 24) + 16,
      symbol: Math.random() > 0.5 ? '❌' : '⭕'
    })), 
    []
  );

  return (
    <div className="background-animation">
      {symbols.map(({ left, delay, size, symbol }, index) => (
        <div
          key={index}
          className="symbol"
          style={{
            left: `${left}%`,
            animationDelay: `${delay}s`,
            fontSize: `${size}px`,
          }}
        >
          {symbol}
        </div>
      ))}
    </div>
  );
}

function App() {
  return (
    <div className="app-container">
      <BackgroundAnimation />

      <AuthProvider>
        <Router>
          <ToastContainer />
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegistrationPage />} />
            
            <Route
              path="/"
              element={
                <ProtectedLayout useWebSocket={true}>
                  <HomePage />
                </ProtectedLayout>
              }
            />
            
            <Route
              path="/game/:id"
              element={
                <ProtectedLayout useWebSocket={true}>
                  <GamePage />
                </ProtectedLayout>
              }
            />
            
            <Route
              path="/profile"
              element={
                <ProtectedLayout useWebSocket={false}>
                  <ProfilePage />
                </ProtectedLayout>
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
