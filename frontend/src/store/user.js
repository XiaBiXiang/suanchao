import { defineStore } from 'pinia'
import api from '@/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null'),
    isLoggedIn: !!localStorage.getItem('token')
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    user: (state) => state.userInfo
  },
  
  actions: {
    async login(email, password) {
      try {
        const res = await api.post('/api/auth/login', {
          email,
          password
        })
        
        if (res.code === 0) {
          const { access_token, user } = res.data
          
          // 保存 token
          this.token = access_token
          localStorage.setItem('token', access_token)
          
          // 保存用户信息
          this.userInfo = user
          localStorage.setItem('userInfo', JSON.stringify(user))
          
          this.isLoggedIn = true
          
          return { success: true, data: user }
        } else {
          return { success: false, message: res.message }
        }
      } catch (error) {
        const msg = error.response?.data?.message || '登录失败，请稍后重试'
        return { success: false, message: msg }
      }
    },
    
    async register(username, email, password) {
      try {
        const res = await api.post('/api/auth/register', {
          username,
          email,
          password
        })
        
        if (res.code === 0) {
          return { success: true, message: '注册成功，请登录' }
        } else {
          return { success: false, message: res.message }
        }
      } catch (error) {
        const msg = error.response?.data?.message || '注册失败，请稍后重试'
        return { success: false, message: msg }
      }
    },
    
    logout() {
      this.token = ''
      this.userInfo = null
      this.isLoggedIn = false
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    },
    
    async fetchCurrentUser() {
      if (!this.token) return null
      
      try {
        const res = await api.get('/api/auth/me')
        if (res.code === 0) {
          this.userInfo = res.data
          localStorage.setItem('userInfo', JSON.stringify(res.data))
          return res.data
        }
      } catch (error) {
        this.logout()
      }
      return null
    },
    
    updateUserInfo(userInfo) {
      this.userInfo = userInfo
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
    }
  }
})
