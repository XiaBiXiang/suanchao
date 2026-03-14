import { createRouter, createWebHistory } from 'vue-router'
import Workspace from '@/views/Workspace.vue'
import Login from '@/views/Login.vue'
import Home from '@/views/Home.vue'
import Settings from '@/views/Settings.vue'
import Discuss from '@/views/Discuss.vue'
import { useUserStore } from '@/store/user'

const LAST_ROUTE_KEY = 'lc_last_route_v1'
const LAST_ROUTE_TTL_MS = 1000 * 60 * 60 * 24

const saveLastRoute = (route) => {
  if (!route?.meta?.requiresAuth) return
  if (route.name === 'Login') return
  try {
    localStorage.setItem(
      LAST_ROUTE_KEY,
      JSON.stringify({
        path: route.fullPath,
        ts: Date.now()
      })
    )
  } catch (error) {
    console.warn('保存最近访问路由失败:', error)
  }
}

const readLastRoute = () => {
  try {
    const raw = localStorage.getItem(LAST_ROUTE_KEY)
    if (!raw) return ''
    const payload = JSON.parse(raw)
    const ts = Number(payload?.ts || 0)
    if (!payload?.path || !ts) return ''
    if (Date.now() - ts > LAST_ROUTE_TTL_MS) return ''
    return String(payload.path)
  } catch (error) {
    return ''
  }
}

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/workspace/:id?',
    name: 'Workspace',
    component: Workspace,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true }
  },
  {
    path: '/discuss/:id',
    name: 'Discuss',
    component: Discuss,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    if (!userStore.isAuthenticated) {
      // 未登录，跳转到登录页
      next({ name: 'Login', query: { redirect: to.fullPath } })
    } else {
      // 冷启动恢复：若意外回到首页，优先恢复最近访问页面
      const isInitialNavigation = !from.name
      if (isInitialNavigation && to.fullPath === '/') {
        const lastPath = readLastRoute()
        if (lastPath && lastPath !== '/' && lastPath !== to.fullPath && lastPath !== '/login') {
          next(lastPath)
          return
        }
      }
      next()
    }
  } else {
    // 已登录用户访问登录页，跳转到工作台
    if (to.name === 'Login' && userStore.isAuthenticated) {
      next({ name: 'Workspace' })
    } else {
      next()
    }
  }
})

router.afterEach((to) => {
  saveLastRoute(to)
})

export default router
