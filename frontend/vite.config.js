import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const proxyTarget = (
    env.VITE_API_PROXY_TARGET ||
    env.VITE_API_BASE_URL ||
    'http://127.0.0.1:30881'
  ).replace(/\/+$/, '')
  const allowedHosts = (env.VITE_ALLOWED_HOSTS || 'localhost,127.0.0.1,test.imxbx.cloud')
    .split(',')
    .map(host => host.trim())
    .filter(Boolean)
  const devPort = Number(env.VITE_PORT || 30880)

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    server: {
      port: Number.isFinite(devPort) ? devPort : 30880,
      allowedHosts,
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true
        }
      }
    }
  }
})
