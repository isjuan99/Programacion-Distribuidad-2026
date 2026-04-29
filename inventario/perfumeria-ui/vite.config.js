import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // Sirve como archivos publicos la carpeta ../imagenes (fuera del frontend)
  publicDir: "../imagenes",
  server: {
    port: 5173,
    open: true
  }
})
