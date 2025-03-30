import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import { AuthContext } from './AuthContext';
import { useNavigate } from 'react-router-dom';

const WebSocketContext = createContext();

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket должен использоваться внутри WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const wsRef = useRef(null);
  const { token } = useContext(AuthContext);
  const [isConnected, setIsConnected] = useState(false);
  const [gameInvite, setGameInvite] = useState(null);
  const navigate = useNavigate();
  const gameHandlers = useRef(new Map());

  useEffect(() => {
    if (!token) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      setIsConnected(false);
      return;
    }

    const connect = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        return;
      }

      const ws = new WebSocket(`ws://localhost:8000/ws`);
      
      ws.onopen = () => {
        console.log('WebSocket соединение установлено');
        setIsConnected(true);
        // Отправляем токен сразу после установки соединения
        ws.send(JSON.stringify({ type: 'auth', token: `Bearer ${token}` }));
      };

      ws.onclose = () => {
        console.log('WebSocket соединение закрыто');
        setIsConnected(false);
        wsRef.current = null;
      };

      ws.onerror = (error) => {
        console.error('WebSocket ошибка:', error);
        setIsConnected(false);
        wsRef.current = null;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Получено сообщение:', data);
          
          switch (data.type) {
            case 'auth':
              if (data.status === 'success') {
                console.log('Аутентификация успешна');
              } else {
                console.error('Ошибка аутентификации:', data.message);
              }
              break;
            case 'gameInvite':
              setGameInvite(data.game);
              break;
            default:
              console.log('Неизвестный тип сообщения:', data.type);
          }
        } catch (error) {
          console.error('Ошибка при обработке сообщения:', error);
        }
      };

      wsRef.current = ws;
    };

    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close(1000, "Component unmounting");
        wsRef.current = null;
      }
    };
  }, [token]);

  const sendMessage = (message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket не подключен');
    }
  };

  const registerGameHandler = (gameId, handler) => {
    gameHandlers.current.set(gameId, handler);
  };

  const unregisterGameHandler = (gameId) => {
    gameHandlers.current.delete(gameId);
  };

  const handleAcceptInvite = () => {
    if (!gameInvite) return;
    
    sendMessage({
      type: 'GameIsAccepted',
      gameId: gameInvite.gameId
    });
    navigate(`/game/${gameInvite.gameId}`);
    setGameInvite(null);
  };

  const handleRejectInvite = () => {
    if (!gameInvite) return;
    
    sendMessage({
      type: 'GameIsAborted',
      gameId: gameInvite.gameId
    });
    setGameInvite(null);
  };

  return (
    <WebSocketContext.Provider value={{ ws: wsRef.current, sendMessage, isConnected, gameInvite }}>
      {children}
      {gameInvite && (
        <div className="modal">
          <div className="modal-content">
            <h2>Приглашение в игру</h2>
            <p>Игрок {gameInvite.senderPlayer} хочет присоединиться к вашей игре.</p>
            <div className="stats">
              <p>Всего игр: {gameInvite.stats.totalGames}</p>
              <p>Победы: {gameInvite.stats.wins}</p>
              <p>Поражения: {gameInvite.stats.losses}</p>
            </div>
            <div className="modal-buttons">
              <button className="btn-accept" onClick={handleAcceptInvite}>
                Принять
              </button>
              <button className="btn-reject" onClick={handleRejectInvite}>
                Отклонить
              </button>
            </div>
          </div>
        </div>
      )}
    </WebSocketContext.Provider>
  );
}; 