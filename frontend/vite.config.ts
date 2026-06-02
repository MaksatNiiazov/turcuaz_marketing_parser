import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  resolve: {
    preserveSymlinks: true,
  },
  server: {
    host: '0.0.0.0',
    port: 7503,
    proxy: {
      '/api': {
        target: process.env.VITE_PROXY_TARGET || 'http://localhost:8503',
        changeOrigin: true,
      },
      '/identity-api': {
        target: process.env.VITE_IDENTITY_PROXY_TARGET || 'http://localhost:8500',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/identity-api/, '/api/v1'),
      },
    },
  },
});
