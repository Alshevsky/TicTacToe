import React, { useState, useEffect, useContext } from 'react';
import { useParams } from 'react-router-dom';
import { AuthContext } from '@context/AuthContext';
import { useWebSocket } from '@context/WebSocketContext';
import '@styles/Game.css';

const GamePage = () => {
  const { token } = useContext(AuthContext);
  const { id } = useParams();
  const { sendMessage, registerGameHandler, unregisterGameHandler } = useWebSocket();
  const [board, setBoard] = useState(Array(9).fill(null));
  const [currentPlayer, setCurrentPlayer] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchGame = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/games/${id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Ошибка загрузки игры');
        }

        const data = await response.json();
        if (data.gameState) {
          setBoard(data.gameState.board);
          setCurrentPlayer(data.gameState.currentPlayer);
        }
      } catch (err) {
        setError('Не удалось загрузить игру');
      }
    };

    // Регистрируем обработчик для этой игры
    registerGameHandler(id, {
      handleGameState: (gameState) => {
        setBoard(gameState.board);
        setCurrentPlayer(gameState.currentPlayer);
      },
      handleChatMessage: (message) => {
        setChatMessages(prev => [...prev, message]);
      }
    });

    fetchGame();

    // Очистка при размонтировании
    return () => {
      unregisterGameHandler(id);
    };
  }, [id, token, registerGameHandler, unregisterGameHandler]);

  // Обработка хода игрока
  const handleCellClick = (index) => {
    if (board[index] || !currentPlayer) return;

    try {
      const move = {
        type: 'makeMove',
        gameId: id,
        cellIndex: index,
      };
      sendMessage(move);
    } catch (err) {
      console.error('Ошибка отправки хода:', err);
      setError('Не удалось сделать ход');
    }
  };

  // Отправка сообщения в чат
  const handleSendMessage = () => {
    if (!message.trim()) return;

    try {
      const chatMessage = {
        type: 'sendChatMessage',
        gameId: id,
        message: message,
      };
      sendMessage(chatMessage);
      setMessage('');
    } catch (err) {
      console.error('Ошибка отправки сообщения:', err);
      setError('Не удалось отправить сообщение');
    }
  };

  return (
    <div className="game-page">
      <h1>Игра #{id}</h1>
      {error && <div className="error-message">{error}</div>}

      {/* Поле для игры */}
      <div className="board">
        {board.map((cell, index) => (
          <div
            key={index}
            className="cell"
            onClick={() => handleCellClick(index)}
          >
            {cell}
          </div>
        ))}
      </div>

      {/* Чат */}
      <div className="chat">
        <div className="chat-messages">
          {chatMessages.map((msg, i) => (
            <div key={i} className="message">
              <strong>{msg.sender}:</strong> {msg.text}
            </div>
          ))}
        </div>
        <div className="chat-input">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Введите сообщение..."
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <button onClick={handleSendMessage}>Отправить</button>
        </div>
      </div>
    </div>
  );
};

export default GamePage;