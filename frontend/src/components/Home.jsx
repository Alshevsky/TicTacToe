import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '@context/AuthContext';
import { useWebSocket } from '@context/WebSocketContext';
import '@styles/Home.css';

const HomePage = () => {
  const { token, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const { ws, closeConnection, sendMessage } = useWebSocket();
  const [games, setGames] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [gameName, setGameName] = useState('');
  const [playerItem, setPlayerItem] = useState('❌');
  const [currentPlayerName, setCurrentPlayerName] = useState('');
  const [error, setError] = useState('');
  const [isWaitingModalOpen, setIsWaitingModalOpen] = useState(false);
  const [waitingGameId, setWaitingGameId] = useState(null);

  useEffect(() => {
    const fetchGames = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/games', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Ошибка загрузки игр');
        }

        const data = await response.json();
        if (Array.isArray(data.gamesList)) {
          setGames(data.gamesList);
          setCurrentPlayerName(data.userName);
        } else {
          console.error('Ожидался массив игр, но получен:', data);
          setGames([]);
        }
      } catch (err) {
        console.error('Ошибка загрузки игр:', err);
        setError('Не удалось загрузить игры');
        setGames([]);
      }
    };

    fetchGames();
  }, [token]);

  useEffect(() => {
    if (!ws) return;

    const handleWebSocketMessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'gameAdded':
          setGames(prevGames => [...prevGames, data.game]);
          break;
        case 'gameDeleted':
          setGames(prevGames => prevGames.filter(game => game.id !== data.gameId));
          break;
        case 'gameUpdated':
          setGames(prevGames => 
            prevGames.map(game => 
              game.id === data.game.id ? data.game : game
            )
          );
          break;
        case 'GameIsAccepted':
          if (waitingGameId === data.gameId) {
            setIsWaitingModalOpen(false);
            navigate(`/game/${data.gameId}`);
          }
          break;
        case 'GameIsAborted':
          if (waitingGameId === data.gameId) {
            setIsWaitingModalOpen(false);
            setError('Игра была отклонена');
          }
          break;
        case "auth":
          sendMessage({
            type: "auth",
            token: `Bearer ${token}`,
          });
          break;
        default:
          console.log('Неизвестный тип сообщения:', data.type);
      }
    };

    ws.onmessage = handleWebSocketMessage;
    
    return () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close(1000, "Component unmounting");
      }
    };
  }, [ws, waitingGameId, navigate]);

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

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Ошибка создания игры');
      }

      const data = await response.json();
      setGames(prevGames => [...prevGames, data]);
      setIsModalOpen(false);
    } catch (err) {
      setError(err.message || 'Не удалось создать игру');
    }
  };

  const handleJoinGame = async (game) => {
    try {
      setWaitingGameId(game.id);
      setIsWaitingModalOpen(true);

      if (ws && ws.readyState === WebSocket.OPEN) {
        sendMessage(JSON.stringify({
          type: 'joinGame',
          gameId: game.id,
          targetPlayer: game.currentPlayerName,
        }));
      } else {
        throw new Error('WebSocket соединение не установлено');
      }
    } catch (err) {
      setError('Не удалось присоединиться к игре');
      setIsWaitingModalOpen(false);
      setWaitingGameId(null);
    }
  };

  const handleEndGame = async (gameId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/games/${gameId}/end`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Не удалось завершить игру');
      }

      setGames(prevGames => prevGames.filter(game => game.id !== gameId));
    } catch (err) {
      setError(err.message || 'Не удалось завершить игру');
    }
  };

  const handleProfileClick = () => {
    navigate('/profile');
  };

  return (
    <div className="home-container">
      <header className="header">
        <div className="logo">Tic-Tac-Toe Online</div>
        <div className="header-buttons">
          <button className="btn-profile" onClick={handleProfileClick}>Профиль</button>
          <button className="btn-logout" onClick={logout}>
            Выйти
          </button>
        </div>
      </header>

      <div className="content">
        <div className="games-section">
          <h2>Доступные игры</h2>
          <button className="btn-create-game" onClick={() => setIsModalOpen(true)}>
            Создать игру
          </button>

          <div className="games-list">
            {games.map((game) => (
              <div key={game.id} className="game-item">
                <span className="game-name">{game.gameName}</span>
                <span className="game-creator">
                  Создатель: {game.currentPlayerName || 'Неизвестно'}
                </span>
                <div className="game-buttons">
                  {game.currentPlayerName === currentPlayerName ? (
                    <button
                      className="btn-end-game"
                      onClick={() => handleEndGame(game.id)}
                    >
                      Завершить игру
                    </button>
                  ) : (
                    <button
                      className={`btn-join ${!game.isActive ? 'btn-join-disabled' : ''}`}
                      onClick={() => handleJoinGame(game)}
                      disabled={!game.isActive}
                    >
                      {!game.isActive ? 'В игре' : 'Присоединиться'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <h2>Создание новой игры</h2>
            <input
              type="text"
              placeholder="Название игры"
              value={gameName}
              onChange={(e) => setGameName(e.target.value)}
            />
            <div className="player-item-select">
              <label>Выберите символ:</label>
              <div className="player-item-options">
                <button
                  className={`player-item-btn ${playerItem === 'X' ? 'active' : ''}`}
                  onClick={() => setPlayerItem('X')}
                >
                  ❌
                </button>
                <button
                  className={`player-item-btn ${playerItem === 'O' ? 'active' : ''}`}
                  onClick={() => setPlayerItem('O')}
                >
                  ⭕
                </button>
              </div>
            </div>
            <div className="modal-buttons">
              <button onClick={handleCreateGame}>Создать</button>
              <button onClick={() => setIsModalOpen(false)}>Отмена</button>
            </div>
          </div>
        </div>
      )}

      {isWaitingModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <div className="loading-spinner"></div>
            <p>Ожидаем принятие приглашения игроком...</p>
          </div>
        </div>
      )}

      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default HomePage;