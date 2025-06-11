import path from "path"
import tailwindcss from "@tailwindcss/vite"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react(), tailwindcss()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    server: {
        port: 3000,
        proxy: {
            '/api': {
                target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
                changeOrigin: true,
                secure: false,
            },
        },
    },
})
