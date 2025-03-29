import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import { AuthContext } from './AuthContext';
import { useNavigate } from 'react-router-dom';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
  const { token } = useContext(AuthContext);
  const [ws, setWs] = useState(null);
  const wsRef = useRef(null);
  const navigate = useNavigate();
  const [gameInvite, setGameInvite] = React.useState(null);

  useEffect(() => {
    if (!token) return;

    const wsUrl = `ws://localhost:8000/ws`;
    const websocket = new WebSocket(wsUrl);
    wsRef.current = websocket;

    websocket.onopen = () => {
      console.log('WebSocket соединение установлено');
    };

    websocket.onclose = () => {
      console.log('WebSocket соединение закрыто');
      setWs(null);
      wsRef.current = null;
    };

    websocket.onerror = (error) => {
      console.error('WebSocket ошибка:', error);
      setWs(null);
      wsRef.current = null;
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'auth') {
        sendMessage({
          type: 'auth',
          token: `Bearer ${token}`,
        });
        return;
      }

      if (data.type === 'GameInvite') {
        setGameInvite(data);
      }
    };

    setWs(websocket);

    return () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.close(1000, "Provider unmounting");
      }
    };
  }, [token]);

  const sendMessage = (message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  const handleAcceptInvite = () => {
    sendMessage({
      type: 'GameIsAccepted',
      gameId: gameInvite.gameId
    });
    navigate(`/game/${gameInvite.gameId}`);
    setGameInvite(null);
  };

  const handleRejectInvite = () => {
    sendMessage({
      type: 'GameIsAborted',
      gameId: gameInvite.gameId
    });
    setGameInvite(null);
  };

  const value = {
    ws: wsRef.current,
    sendMessage,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
      {gameInvite && (
        <div className="modal">
          <div className="modal-content">
            <h2>Приглашение в игру</h2>
            <p>Игрок {gameInvite.playerName} хочет присоединиться к вашей игре.</p>
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

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket должен использоваться внутри WebSocketProvider');
  }
  return context;
}; 