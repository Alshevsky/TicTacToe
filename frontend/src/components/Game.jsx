import React, { useState, useEffect, useRef, useContext } from 'react';
import { useParams } from 'react-router-dom';
import { AuthContext } from '@context/AuthContext';
import '@styles/Game.css';

const GamePage = () => {
  const { token } = useContext(AuthContext);
  const { id } = useParams(); // Получаем ID игры из URL
  const [board, setBoard] = useState(Array(9).fill(null)); // Состояние поля 3x3
  const [currentPlayer, setCurrentPlayer] = useState(null); // Текущий игрок (X или O)
  const [chatMessages, setChatMessages] = useState([]); // Сообщения чата
  const [message, setMessage] = useState(''); // Текущее сообщение
  const wsRef = useRef(null); // Ссылка на WebSocket

  // Подключение к WebSocket
  useEffect(() => {
    const fetchGame = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/games/${id}`);

        if (!response.ok) {
          throw new Error('Ошибка загрузки игры');
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


    // Создаем WebSocket-подключение
    wsRef.current = new WebSocket(`ws://localhost:8000/games/${id}/ws`);

    // Обработка открытия соединения
    wsRef.current.onopen = () => {
      console.log('WebSocket подключен');
    };

    // Обработка входящих сообщений
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'gameState') {
        // Обновляем состояние игры
        setBoard(data.board);
        setCurrentPlayer(data.currentPlayer);
      } else if (data.type === 'chatMessage') {
        // Добавляем сообщение в чат
        setChatMessages((prevMessages) => [...prevMessages, data.message]);
      } else if (data.type === 'auth') {
        wsRef.current.send(JSON.stringify({token: `Bearer ${token}`}));
      }
    };

    // Обработка закрытия соединения
    wsRef.current.onclose = () => {
      console.log('WebSocket отключен');
    };

    // Очистка при размонтировании
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [id]);

  // Обработка хода игрока
  const handleCellClick = (index) => {
    if (board[index] || !currentPlayer) return; // Если клетка занята или не наш ход, ничего не делаем

    // Отправляем ход на сервер
    const move = {
      type: 'makeMove',
      cellIndex: index,
    };
    wsRef.current.send(JSON.stringify(move));
  };

  // Отправка сообщения в чат
  const sendMessage = () => {
    if (message.trim()) {
      const chatMessage = {
        type: 'sendChatMessage',
        message: message,
      };
      wsRef.current.send(JSON.stringify(chatMessage));
      setMessage('');
    }
  };

  return (
    <div className="game-page">
      <h1>Игра #{id}</h1>

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
          />
          <button onClick={sendMessage}>Отправить</button>
        </div>
      </div>
    </div>
  );
};

export default GamePage;