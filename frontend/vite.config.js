import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path'; // Импортируем модуль path

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // Настраиваем алиасы
      '@': path.resolve(__dirname, './src'), // Корень проекта
      '@components': path.resolve(__dirname, './src/components'), // Папка с компонентами
      '@context': path.resolve(__dirname, './src/context'), // Папка с компонентами
      '@styles': path.resolve(__dirname, './src/styles'), // Папка со стилями
      '@assets': path.resolve(__dirname, './src/assets'), // Папка с ассетами
    },
  },
});