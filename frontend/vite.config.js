import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://7.197.65.7:6000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})