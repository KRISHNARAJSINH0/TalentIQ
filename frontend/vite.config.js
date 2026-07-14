import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // Recharts and d3 are very large libraries, split them out
            if (id.includes('recharts') || id.includes('d3')) {
              return 'vendor-charts'
            }
            // Framer motion is also large, split it out
            if (id.includes('framer-motion')) {
              return 'vendor-motion'
            }
            // React core packages
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router')) {
              return 'vendor-react'
            }
            // Other packages
            return 'vendor-helpers'
          }
        }
      }
    }
  }
})
