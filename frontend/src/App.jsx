import '@styles/App.css'
import 'normalize.css'
import LoginPage from '@components/Login';
import RegistrationPage from '@components/Registration';
import HomePage from '@components/Home';
import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext } from '@context/AuthContext';
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

      <Router>
        <ToastContainer />
        <Routes>
          <Route
            path="/login"
            element={token ? <Navigate to="/" /> : <LoginPage />}
          />
          <Route
            path="/register"
            element={token ? <Navigate to="/" /> : <RegistrationPage />}
          />
          <Route
            path="/"
            element={token ? <HomePage /> : <Navigate to="/login" />}
          />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
