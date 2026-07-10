import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/render": "http://localhost:8000",
      "/renders": "http://localhost:8000",
      "/find-it-on-amazon": "http://localhost:8000",
      "/select-similar-from-amazon": "http://localhost:8000",
      "/add-it-to-shopping-cart": "http://localhost:8000",
      "/add-it-to-shopping-list": "http://localhost:8000",
    },
  },
})
