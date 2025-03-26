import React, { useState, useEffect, useContext, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '@context/AuthContext';
import '@styles/Home.css';

const HomePage = () => {
  const { token, logout } = useContext(AuthContext);
  const [userName, setUserName] = useState('');
  const [games, setGames] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [gameName, setGameName] = useState('');
  const [playerItem, setPlayerItem] = useState('X');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const wsRef = useRef(null);

  useEffect(() => {
    const fetchGames = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/games', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Ошибка загрузки списка игр');
        }

        const data = await response.json();
        if (Array.isArray(data.gamesList)) {
          setGames(data.gamesList);
        } else {
          console.error('Ожидался массив, но получен:', data);
          setGames([]);
        }
        setUserName(data.userName)
      } catch (err) {
        setError('Не удалось загрузить список игр');
      }
    };

    fetchGames();
  }, [token]);

  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8000/games/ws');
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        ws.send(JSON.stringify({ token }));
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'auth') {
          return;
        }

        switch (data.type) {
          case 'gameAdded':
            setGames(prevGames => [...prevGames, data.game]);
            break;
          case 'gameRemoved':
            setGames(prevGames => prevGames.filter(game => game.id !== data.gameId));
            break;
          case 'gameUpdated':
            setGames(prevGames => 
              prevGames.map(game => 
                game.id === data.game.id ? data.game : game
              )
            );
            break;
          default:
            console.warn('Unknown message type:', data.type);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Ошибка подключения к серверу');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        // Попытка переподключения через 3 секунды
        setTimeout(connectWebSocket, 3000);
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [token]);

  const handleJoinGame = (gameId) => {
    navigate(`/game/${gameId}`);
  };

  const handleCreateGame = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/games', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          gameName: gameName,
          currentPlayerItem: playerItem,
        }),
      });
      console.log(response.ok)
      if (!response.ok) {
        throw new Error('Ошибка создания игры');
      }

      const data = await response.json();
      setGames((prevGames) =>
        prevGames.push(data)
      )
      setIsModalOpen(false)
    } catch (err) {
      setError('Не удалось создать игру');
    }
  };

  return (
    <div className="home-container">
      <header className="header">
        <div className="logo">Tic-Tac-Toe Online</div>
        <div className="header-buttons">
          <button className="btn-profile">Профиль</button>
          <button className="btn-logout" onClick={logout}>
            Выйти
          </button>
        </div>
      </header>

      <h1 className="welcome-message">Добро пожаловать, {userName}!</h1>

      <div className="games-list">
        {games.length > 0 ? (
          games.map((game) => (
            <div key={game.id} className="game-item">
              <span>{game.gameName}</span>
              <button
                className={game.currentPlayerName == userName ? 'btn-join-disabled' : 'btn-join'}
                onClick={() => handleJoinGame(game.id)}
                disabled={game.currentPlayerName == userName}
              >
                Подключиться
              </button>
            </div>
          ))
        ) : (
          <p>Нет доступных игр</p>
        )}
      </div>

      <button className="btn-create-game" onClick={() => setIsModalOpen(true)}>
        Создать игру
      </button>

      {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <h2>Создать игру</h2>
            <input
              type="text"
              placeholder="Название игры"
              value={gameName}
              onChange={(e) => setGameName(e.target.value)}
            />
            <span>Выберите вашу фигуру</span>
            <select
              value={playerItem}
              onChange={(e) => setPlayerItem(e.target.value)}
            >
              <option value="X">X</option>
              <option value="O">O</option>
            </select>
            <button onClick={handleCreateGame}>Создать</button>
            <button onClick={() => setIsModalOpen(false)}>Отмена</button>
          </div>
        </div>
      )}

      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default HomePage;