import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/leo": {
        target: "http://localhost:5000", // donde corre Flask
        target: "http://127.0.0.1:5000", // donde corre Flask
        changeOrigin: true,
      },
    },
  },
});
