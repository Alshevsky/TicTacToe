import React, { createContext, useContext, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from './AuthContext';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
  const { token } = useContext(AuthContext);
  const wsRef = useRef(null);
  const navigate = useNavigate();
  const [gameInvite, setGameInvite] = React.useState(null);

  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8000/ws');
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        // ws.send(JSON.stringify({ token }));
      };

      ws.onmessage = (event) => {
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

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
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

  return (
    <WebSocketContext.Provider value={{ sendMessage }}>
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
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
}; 