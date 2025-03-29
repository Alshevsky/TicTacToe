import React from 'react';
import ProtectedRoute from './ProtectedRoute';
import { WebSocketProvider } from '@context/WebSocketContext';

const ProtectedLayout = ({ children, useWebSocket = true }) => {
  const content = useWebSocket ? (
    <WebSocketProvider>
      {children}
    </WebSocketProvider>
  ) : (
    children
  );

  return (
    <ProtectedRoute>
      {content}
    </ProtectedRoute>
  );
};

export default ProtectedLayout; 