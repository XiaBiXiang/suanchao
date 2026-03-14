<template>
  <div class="auth-page">
    <div class="bg-orb orb-left"></div>
    <div class="bg-orb orb-right"></div>
    <div class="grain-layer"></div>

    <main class="auth-shell">
      <section class="brand-panel">
        <div class="brand-header">
          <div class="brand-logo">LC</div>
          <div>
            <p class="brand-name">LC JUDGE</p>
            <p class="brand-slogan">在线算法训练空间</p>
          </div>
        </div>

        <div class="brand-content">
          <p class="eyebrow">Quiet Interface</p>
          <h1>
            稳定节奏，
            <br />
            把注意力留给题目。
          </h1>
          <p class="description">
            从登录开始就进入专注状态。页面保持简洁，信息有层次，动效柔和而不打扰。
          </p>
        </div>

        <div class="demo-card">
          <div class="demo-head">
            <div class="lights">
              <span class="light red"></span>
              <span class="light yellow"></span>
              <span class="light green"></span>
            </div>
            <span>PROBLEM PREVIEW</span>
          </div>
          <div class="demo-body">
            <div class="demo-line w-40"></div>
            <div class="demo-line w-full"></div>
            <div class="demo-line w-10/12"></div>
            <div class="demo-grid">
              <div>
                <p>输入</p>
                <strong>[2,7,11,15]</strong>
              </div>
              <div>
                <p>输出</p>
                <strong>[0,1]</strong>
              </div>
            </div>
            <div class="demo-status">
              <span class="ac-chip">AC</span>
              <div class="status-line"></div>
            </div>
          </div>
        </div>
      </section>

      <section class="auth-panel">
        <div class="auth-card">
          <div class="card-tools">
            <button type="button" class="lang-switch" @click="toggleLocale">
              {{ locale === 'zh' ? 'EN' : '中文' }}
            </button>
          </div>

          <header class="auth-header">
            <p class="auth-kicker">Account Center</p>
            <h2>{{ isLogin ? '欢迎回来' : '创建账户' }}</h2>
            <p class="auth-hint">
              {{ isLogin ? '登录后继续你的刷题进度。' : '注册后即可进入题库开始训练。' }}
            </p>
          </header>

          <div class="mode-switch" :class="{ register: !isLogin }">
            <button type="button" @click="switchToLogin">登录</button>
            <button type="button" @click="switchToRegister">注册</button>
          </div>

          <transition name="mode-fade" mode="out-in">
            <form v-if="isLogin" key="login" @submit.prevent="handleLogin" class="auth-form">
              <label class="field">
                <span>邮箱地址</span>
                <div class="field-box">
                  <svg class="field-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 7.5v9A2.25 2.25 0 0119.5 18.75h-15A2.25 2.25 0 012.25 16.5v-9m19.5 0A2.25 2.25 0 0019.5 5.25h-15A2.25 2.25 0 002.25 7.5m19.5 0l-7.815 5.21a2.25 2.25 0 01-2.37 0L2.25 7.5"/>
                  </svg>
                  <input
                    v-model="loginForm.email"
                    type="email"
                    required
                    placeholder="请输入常用邮箱"
                  />
                </div>
              </label>

              <label class="field">
                <span>登录密码</span>
                <div class="field-box">
                  <svg class="field-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 0h10.5A2.25 2.25 0 0119.5 12.75v6A2.25 2.25 0 0117.25 21h-10.5A2.25 2.25 0 014.5 18.75v-6A2.25 2.25 0 016.75 10.5z"/>
                  </svg>
                  <input
                    v-model="loginForm.password"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    placeholder="请输入密码"
                  />
                  <button type="button" class="ghost-btn" @click="showPassword = !showPassword">
                    {{ showPassword ? '隐藏' : '显示' }}
                  </button>
                </div>
              </label>

              <div class="forgot-row">
                <button type="button" class="switch-link forgot-link" @click="openResetModal">
                  忘记密码？
                </button>
              </div>

              <transition name="banner-fade">
                <div v-if="loginError" class="banner error">
                  {{ loginError }}
                </div>
              </transition>

              <button type="submit" :disabled="loading" class="primary-btn">
                <svg v-if="loading" class="spinner" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.372 0 0 5.372 0 12h4zm2 5.291A7.961 7.961 0 014 12H0c0 3.041 1.134 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ loading ? '登录中' : '进入工作台' }}</span>
              </button>
            </form>

            <form v-else key="register" @submit.prevent="handleRegister" class="auth-form">
              <label class="field">
                <span>用户名</span>
                <div class="field-box">
                  <svg class="field-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.5 20.25a7.5 7.5 0 1115 0"/>
                  </svg>
                  <input
                    v-model="registerForm.username"
                    type="text"
                    required
                    placeholder="3-50 位，字母开头"
                  />
                </div>
              </label>

              <div class="code-row">
                <label class="field">
                  <span>邮箱地址</span>
                  <div class="field-box">
                    <svg class="field-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 7.5v9A2.25 2.25 0 0119.5 18.75h-15A2.25 2.25 0 012.25 16.5v-9m19.5 0A2.25 2.25 0 0019.5 5.25h-15A2.25 2.25 0 002.25 7.5m19.5 0l-7.815 5.21a2.25 2.25 0 01-2.37 0L2.25 7.5"/>
                    </svg>
                    <input
                      v-model="registerForm.email"
                      type="email"
                      required
                      placeholder="请输入邮箱"
                    />
                  </div>
                </label>
                <button
                  type="button"
                  @click="sendCode"
                  :disabled="countdown > 0"
                  class="secondary-btn"
                >
                  {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
                </button>
              </div>

              <label class="field">
                <span>验证码</span>
                <div class="field-box">
                  <svg class="field-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-8.036-2.286A11.959 11.959 0 0112 3.75c2.286 0 4.423.64 6.25 1.755M4.714 6.964A11.91 11.91 0 003 10.5c0 4.97 3.52 9.118 8.25 10.088 4.73-.97 8.25-5.119 8.25-10.088 0-1.273-.23-2.491-.65-3.616"/>
                  </svg>
                  <input
                    v-model="registerForm.verification_code"
                    type="text"
                    maxlength="6"
                    inputmode="numeric"
                    required
                    placeholder="请输入 6 位验证码"
                  />
                </div>
              </label>

              <div class="password-grid">
                <label class="field">
                  <span>设置密码</span>
                  <div class="field-box">
                    <svg class="field-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 0h10.5A2.25 2.25 0 0119.5 12.75v6A2.25 2.25 0 0117.25 21h-10.5A2.25 2.25 0 014.5 18.75v-6A2.25 2.25 0 016.75 10.5z"/>
                    </svg>
                    <input
                      v-model="registerForm.password"
                      :type="showRegisterPassword ? 'text' : 'password'"
                      required
                      placeholder="至少 8 位"
                    />
                    <button type="button" class="ghost-btn" @click="showRegisterPassword = !showRegisterPassword">
                      {{ showRegisterPassword ? '隐藏' : '显示' }}
                    </button>
                  </div>
                </label>

                <label class="field">
                  <span>确认密码</span>
                  <div class="field-box">
                    <svg class="field-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l4.5 4.5L19.5 6.75"/>
                    </svg>
                    <input
                      v-model="registerForm.confirmPassword"
                      :type="showConfirmPassword ? 'text' : 'password'"
                      required
                      placeholder="请再次输入"
                    />
                    <button type="button" class="ghost-btn" @click="showConfirmPassword = !showConfirmPassword">
                      {{ showConfirmPassword ? '隐藏' : '显示' }}
                    </button>
                  </div>
                </label>
              </div>

              <transition name="banner-fade">
                <div v-if="registerError" class="banner error">
                  {{ registerError }}
                </div>
              </transition>
              <transition name="banner-fade">
                <div v-if="registerSuccess" class="banner success">
                  {{ registerSuccess }}
                </div>
              </transition>

              <button type="submit" :disabled="loading" class="primary-btn">
                <svg v-if="loading" class="spinner" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.372 0 0 5.372 0 12h4zm2 5.291A7.961 7.961 0 014 12H0c0 3.041 1.134 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ loading ? '注册中' : '创建账户' }}</span>
              </button>
            </form>
          </transition>

          <footer class="auth-footer">
            <span>{{ isLogin ? '还没有账户？' : '已经有账户？' }}</span>
            <button
              type="button"
              class="switch-link"
              @click="isLogin ? switchToRegister() : switchToLogin()"
            >
              {{ isLogin ? '去注册' : '返回登录' }}
            </button>
          </footer>
        </div>
      </section>
    </main>

    <transition name="banner-fade">
      <div v-if="resetVisible" class="reset-modal-mask" @click.self="closeResetModal">
        <section class="reset-modal-card">
          <header class="reset-modal-head">
            <div>
              <p class="auth-kicker">Password Reset</p>
              <h3>邮箱重置密码</h3>
            </div>
            <button type="button" class="modal-close" @click="closeResetModal">关闭</button>
          </header>

          <div class="reset-form">
            <div class="code-row">
              <label class="field">
                <span>邮箱地址</span>
                <div class="field-box">
                  <svg class="field-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 7.5v9A2.25 2.25 0 0119.5 18.75h-15A2.25 2.25 0 012.25 16.5v-9m19.5 0A2.25 2.25 0 0019.5 5.25h-15A2.25 2.25 0 002.25 7.5m19.5 0l-7.815 5.21a2.25 2.25 0 01-2.37 0L2.25 7.5"/>
                  </svg>
                  <input
                    v-model="resetForm.email"
                    type="email"
                    required
                    placeholder="请输入注册邮箱"
                  />
                </div>
              </label>
              <button
                type="button"
                @click="sendResetCode"
                :disabled="resetCountdown > 0 || resetLoading"
                class="secondary-btn"
              >
                {{ resetCountdown > 0 ? `${resetCountdown}s` : '发送验证码' }}
              </button>
            </div>

            <label class="field">
              <span>验证码</span>
              <div class="field-box">
                <svg class="field-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-8.036-2.286A11.959 11.959 0 0112 3.75c2.286 0 4.423.64 6.25 1.755M4.714 6.964A11.91 11.91 0 003 10.5c0 4.97 3.52 9.118 8.25 10.088 4.73-.97 8.25-5.119 8.25-10.088 0-1.273-.23-2.491-.65-3.616"/>
                </svg>
                <input
                  v-model="resetForm.verification_code"
                  type="text"
                  maxlength="6"
                  inputmode="numeric"
                  required
                  placeholder="请输入 6 位验证码"
                />
              </div>
            </label>

            <div class="password-grid">
              <label class="field">
                <span>新密码</span>
                <div class="field-box">
                  <svg class="field-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 0h10.5A2.25 2.25 0 0119.5 12.75v6A2.25 2.25 0 0117.25 21h-10.5A2.25 2.25 0 014.5 18.75v-6A2.25 2.25 0 016.75 10.5z"/>
                  </svg>
                  <input
                    v-model="resetForm.new_password"
                    :type="showResetPassword ? 'text' : 'password'"
                    required
                    placeholder="至少 8 位，含字母和数字"
                  />
                  <button type="button" class="ghost-btn" @click="showResetPassword = !showResetPassword">
                    {{ showResetPassword ? '隐藏' : '显示' }}
                  </button>
                </div>
              </label>

              <label class="field">
                <span>确认新密码</span>
                <div class="field-box">
                  <svg class="field-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l4.5 4.5L19.5 6.75"/>
                  </svg>
                  <input
                    v-model="resetForm.confirm_password"
                    :type="showResetConfirmPassword ? 'text' : 'password'"
                    required
                    placeholder="请再次输入"
                  />
                  <button type="button" class="ghost-btn" @click="showResetConfirmPassword = !showResetConfirmPassword">
                    {{ showResetConfirmPassword ? '隐藏' : '显示' }}
                  </button>
                </div>
              </label>
            </div>

            <transition name="banner-fade">
              <div v-if="resetError" class="banner error">
                {{ resetError }}
              </div>
            </transition>
            <transition name="banner-fade">
              <div v-if="resetSuccess" class="banner success">
                {{ resetSuccess }}
              </div>
            </transition>

            <button type="button" :disabled="resetLoading" class="primary-btn" @click="handleResetPassword">
              <svg v-if="resetLoading" class="spinner" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.372 0 0 5.372 0 12h4zm2 5.291A7.961 7.961 0 014 12H0c0 3.041 1.134 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ resetLoading ? '重置中' : '确认重置密码' }}</span>
            </button>
          </div>
        </section>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { onBeforeUnmount, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import api from '@/api'
import { useLocale } from '@/composables/locale'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const { locale, toggleLocale } = useLocale()

const isLogin = ref(true)
const loading = ref(false)
const loginError = ref('')
const registerError = ref('')
const registerSuccess = ref('')
const countdown = ref(0)
const resetCountdown = ref(0)
const showPassword = ref(false)
const showRegisterPassword = ref(false)
const showConfirmPassword = ref(false)
const showResetPassword = ref(false)
const showResetConfirmPassword = ref(false)
const resetVisible = ref(false)
const resetLoading = ref(false)
const resetError = ref('')
const resetSuccess = ref('')

let countdownTimer = null
let resetCountdownTimer = null

const loginForm = reactive({
  email: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  verification_code: ''
})

const resetForm = reactive({
  email: '',
  verification_code: '',
  new_password: '',
  confirm_password: ''
})

const clearMessages = () => {
  loginError.value = ''
  registerError.value = ''
  registerSuccess.value = ''
}

const switchToRegister = () => {
  isLogin.value = false
  clearMessages()
}

const switchToLogin = () => {
  isLogin.value = true
  clearMessages()
}

const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)

const isValidPassword = (password) => {
  return password.length >= 8 && /[a-zA-Z]/.test(password) && /[0-9]/.test(password)
}

const startCountdown = () => {
  if (countdownTimer) clearInterval(countdownTimer)
  countdown.value = 60
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

const startResetCountdown = () => {
  if (resetCountdownTimer) clearInterval(resetCountdownTimer)
  resetCountdown.value = 60
  resetCountdownTimer = setInterval(() => {
    resetCountdown.value--
    if (resetCountdown.value <= 0) {
      clearInterval(resetCountdownTimer)
      resetCountdownTimer = null
    }
  }, 1000)
}

const openResetModal = () => {
  resetVisible.value = true
  resetError.value = ''
  resetSuccess.value = ''
  if (!resetForm.email && loginForm.email) {
    resetForm.email = loginForm.email
  }
}

const closeResetModal = () => {
  resetVisible.value = false
  resetError.value = ''
  resetSuccess.value = ''
  showResetPassword.value = false
  showResetConfirmPassword.value = false
}

const sendCode = async () => {
  registerError.value = ''
  registerSuccess.value = ''

  if (!registerForm.email) {
    registerError.value = '请先输入邮箱地址'
    return
  }

  if (!isValidEmail(registerForm.email)) {
    registerError.value = '邮箱格式不正确'
    return
  }

  try {
    const res = await api.post('/api/auth/send-code', {
      email: registerForm.email
    })

    if (res.code === 0) {
      registerSuccess.value = '验证码已发送，请检查邮箱'
      startCountdown()
    } else {
      registerError.value = res.message || '发送失败'
    }
  } catch (error) {
    registerError.value = '网络错误，请稍后重试'
  }
}

const sendResetCode = async () => {
  resetError.value = ''
  resetSuccess.value = ''

  if (!resetForm.email) {
    resetError.value = '请先输入邮箱地址'
    return
  }

  if (!isValidEmail(resetForm.email)) {
    resetError.value = '邮箱格式不正确'
    return
  }

  try {
    const res = await api.post('/api/auth/send-reset-code', {
      email: resetForm.email
    })

    if (res.code === 0) {
      resetSuccess.value = '重置验证码已发送，请检查邮箱'
      startResetCountdown()
    } else {
      resetError.value = res.message || '发送失败'
    }
  } catch (error) {
    resetError.value = error.response?.data?.message || '网络错误，请稍后重试'
  }
}

const handleLogin = async () => {
  loginError.value = ''

  if (!loginForm.email || !loginForm.password) {
    loginError.value = '请填写完整的登录信息'
    return
  }

  if (!isValidEmail(loginForm.email)) {
    loginError.value = '邮箱格式不正确'
    return
  }

  loading.value = true
  try {
    const result = await userStore.login(loginForm.email, loginForm.password)
    if (result.success) {
      const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
      router.push(redirect)
    } else {
      loginError.value = result.message || '邮箱或密码错误'
    }
  } catch (error) {
    loginError.value = '网络异常，请稍后重试'
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  registerError.value = ''
  registerSuccess.value = ''

  if (!registerForm.username || !registerForm.email || !registerForm.password) {
    registerError.value = '请填写所有必填项'
    return
  }

  if (registerForm.username.length < 3 || registerForm.username.length > 50) {
    registerError.value = '用户名长度需在 3-50 个字符之间'
    return
  }

  if (!isValidEmail(registerForm.email)) {
    registerError.value = '邮箱格式不正确'
    return
  }

  if (!registerForm.verification_code || registerForm.verification_code.length !== 6) {
    registerError.value = '请输入 6 位验证码'
    return
  }

  if (!isValidPassword(registerForm.password)) {
    registerError.value = '密码至少 8 位，需包含字母和数字'
    return
  }

  if (registerForm.password !== registerForm.confirmPassword) {
    registerError.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  try {
    const result = await api.post('/api/auth/register', {
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      verification_code: registerForm.verification_code
    })

    if (result.code === 0) {
      registerSuccess.value = '注册成功，正在切换到登录页...'
      setTimeout(() => {
        isLogin.value = true
        registerForm.username = ''
        registerForm.email = ''
        registerForm.password = ''
        registerForm.confirmPassword = ''
        registerForm.verification_code = ''
        registerSuccess.value = ''
      }, 1500)
    } else {
      registerError.value = result.message || '注册失败'
    }
  } catch (error) {
    registerError.value = error.response?.data?.message || '网络异常，请稍后重试'
  } finally {
    loading.value = false
  }
}

const handleResetPassword = async () => {
  resetError.value = ''
  resetSuccess.value = ''

  if (!resetForm.email || !isValidEmail(resetForm.email)) {
    resetError.value = '请输入正确的邮箱地址'
    return
  }

  if (!resetForm.verification_code || resetForm.verification_code.length !== 6) {
    resetError.value = '请输入 6 位验证码'
    return
  }

  if (!isValidPassword(resetForm.new_password)) {
    resetError.value = '密码至少 8 位，需包含字母和数字'
    return
  }

  if (resetForm.new_password !== resetForm.confirm_password) {
    resetError.value = '两次输入的密码不一致'
    return
  }

  resetLoading.value = true
  try {
    const res = await api.post('/api/auth/reset-password', {
      email: resetForm.email,
      verification_code: resetForm.verification_code,
      new_password: resetForm.new_password
    })

    if (res.code === 0) {
      resetSuccess.value = '密码重置成功，请使用新密码登录'
      loginForm.email = resetForm.email
      setTimeout(() => {
        resetVisible.value = false
        resetForm.verification_code = ''
        resetForm.new_password = ''
        resetForm.confirm_password = ''
        resetSuccess.value = ''
      }, 1200)
    } else {
      resetError.value = res.message || '重置失败'
    }
  } catch (error) {
    resetError.value = error.response?.data?.message || '网络异常，请稍后重试'
  } finally {
    resetLoading.value = false
  }
}

onBeforeUnmount(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  if (resetCountdownTimer) {
    clearInterval(resetCountdownTimer)
    resetCountdownTimer = null
  }
})
</script>

<style scoped>
.auth-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  padding: 20px;
  background:
    radial-gradient(circle at 9% 12%, rgba(255, 212, 163, 0.36), transparent 24%),
    radial-gradient(circle at 88% 82%, rgba(120, 176, 234, 0.2), transparent 26%),
    linear-gradient(160deg, #f8f3ec 0%, #f2ebe0 44%, #e9dfd3 100%);
  font-family: "Avenir Next", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
}

.grain-layer {
  position: absolute;
  inset: 0;
  opacity: 0.08;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(120, 113, 108, 0.09) 1px, transparent 1px),
    linear-gradient(90deg, rgba(120, 113, 108, 0.08) 1px, transparent 1px);
  background-size: 48px 48px;
}

.bg-orb {
  position: absolute;
  border-radius: 9999px;
  filter: blur(100px);
  pointer-events: none;
  animation: orbit 13s ease-in-out infinite;
}

.orb-left {
  left: -9%;
  top: 6%;
  width: 360px;
  height: 360px;
  background: rgba(198, 151, 94, 0.26);
}

.orb-right {
  right: -8%;
  bottom: 7%;
  width: 320px;
  height: 320px;
  background: rgba(123, 166, 214, 0.24);
  animation-delay: -5s;
}

.auth-shell {
  position: relative;
  z-index: 2;
  width: min(1180px, 100%);
  min-height: calc(100vh - 40px);
  display: grid;
  grid-template-columns: 1.03fr 0.97fr;
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 34px;
  overflow: hidden;
  background: rgba(255, 253, 249, 0.8);
  box-shadow: 0 34px 86px rgba(57, 44, 28, 0.16);
  backdrop-filter: blur(14px);
  animation: shell-in 0.8s ease both;
}

.brand-panel {
  padding: 52px 54px 44px;
  background:
    linear-gradient(145deg, rgba(255, 251, 245, 0.96) 0%, rgba(248, 241, 232, 0.92) 100%);
  border-right: 1px solid rgba(219, 205, 188, 0.68);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 30px;
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-logo {
  width: 54px;
  height: 54px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  color: #f8f6f2;
  font-weight: 700;
  letter-spacing: 0.2em;
  padding-left: 0.2em;
  background: linear-gradient(145deg, #1f1b17 0%, #3a322a 100%);
  box-shadow: 0 16px 34px rgba(37, 30, 23, 0.24);
}

.brand-name {
  font-size: 13px;
  letter-spacing: 0.24em;
  color: #4d4439;
  font-weight: 700;
}

.brand-slogan {
  margin-top: 5px;
  font-size: 14px;
  color: #8a7c68;
}

.eyebrow {
  font-size: 11px;
  letter-spacing: 0.2em;
  color: #9f917b;
  font-weight: 700;
  text-transform: uppercase;
}

.brand-content h1 {
  margin-top: 18px;
  font-family: "STSong", "Songti SC", "Noto Serif SC", serif;
  font-size: clamp(2.2rem, 4vw, 3.45rem);
  line-height: 1.12;
  letter-spacing: -0.04em;
  color: #2f281f;
}

.description {
  margin-top: 18px;
  max-width: 520px;
  color: #6b5d4b;
  line-height: 1.9;
  font-size: 16px;
}

.demo-card {
  border-radius: 28px;
  border: 1px solid rgba(210, 198, 180, 0.82);
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 20px 44px rgba(48, 39, 30, 0.09);
  padding: 16px;
  animation: soft-up 0.75s ease both;
}

.demo-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 6px 12px;
  color: #998d7b;
  font-size: 11px;
  letter-spacing: 0.16em;
}

.lights {
  display: flex;
  gap: 7px;
}

.light {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}

.light.red {
  background: #dca08e;
}

.light.yellow {
  background: #d8bb8a;
}

.light.green {
  background: #94c39b;
}

.demo-body {
  border-radius: 18px;
  background: #f8f4ee;
  padding: 16px;
}

.demo-line {
  height: 10px;
  border-radius: 999px;
  background: #ded3c4;
  margin-bottom: 10px;
}

.demo-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 14px 0;
}

.demo-grid div {
  border-radius: 14px;
  padding: 12px;
  background: #ffffff;
}

.demo-grid p {
  font-size: 12px;
  color: #9f927f;
}

.demo-grid strong {
  margin-top: 5px;
  display: block;
  font-size: 13px;
  color: #4f463d;
  letter-spacing: 0.02em;
}

.demo-status {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ac-chip {
  border-radius: 999px;
  background: rgba(82, 170, 121, 0.2);
  color: #2f7b4e;
  font-weight: 700;
  font-size: 12px;
  padding: 4px 10px;
}

.status-line {
  height: 7px;
  flex: 1;
  border-radius: 999px;
  background: rgba(177, 163, 144, 0.34);
}

.auth-panel {
  padding: 28px;
  display: flex;
  align-items: stretch;
  justify-content: center;
  background: linear-gradient(180deg, rgba(255, 252, 248, 0.96) 0%, rgba(250, 245, 237, 0.9) 100%);
}

.auth-card {
  width: min(520px, 100%);
  border-radius: 28px;
  border: 1px solid rgba(211, 200, 184, 0.75);
  background: rgba(255, 255, 255, 0.88);
  padding: 30px;
  box-shadow: 0 24px 56px rgba(47, 38, 31, 0.13);
  display: flex;
  flex-direction: column;
  animation: soft-up 0.75s ease both;
}

.card-tools {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.lang-switch {
  height: 32px;
  min-width: 54px;
  border-radius: 10px;
  border: 1px solid #d9cdbb;
  background: #fff;
  color: #4e4438;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: all 0.2s ease;
}

.lang-switch:hover {
  border-color: #b98a58;
  color: #8a5d30;
}

.auth-kicker {
  color: #988a74;
  font-size: 11px;
  letter-spacing: 0.21em;
  text-transform: uppercase;
  font-weight: 700;
}

.auth-header h2 {
  margin-top: 14px;
  color: #2a241d;
  font-size: clamp(1.85rem, 3vw, 2.3rem);
  letter-spacing: -0.03em;
}

.auth-hint {
  margin-top: 8px;
  color: #7a6d5b;
  font-size: 14px;
}

.mode-switch {
  margin-top: 22px;
  position: relative;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  background: #ece4d8;
  padding: 5px;
  border-radius: 15px;
}

.mode-switch::before {
  content: "";
  position: absolute;
  left: 5px;
  top: 5px;
  width: calc(50% - 5px);
  height: calc(100% - 10px);
  border-radius: 11px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(71, 57, 43, 0.14);
  transition: transform 0.28s ease;
}

.mode-switch.register::before {
  transform: translateX(100%);
}

.mode-switch button {
  position: relative;
  z-index: 1;
  border: 0;
  background: transparent;
  height: 42px;
  cursor: pointer;
  color: #5c5144;
  font-size: 14px;
  font-weight: 700;
}

.auth-form {
  margin-top: 18px;
  display: grid;
  gap: 16px;
}

.field span {
  display: block;
  margin-bottom: 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: #8e816f;
  text-transform: uppercase;
}

.field-box {
  min-height: 54px;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #d5c8b7;
  border-radius: 14px;
  padding: 0 14px;
  background: #fffdfa;
  transition: border-color 0.24s ease, box-shadow 0.24s ease, transform 0.24s ease;
}

.field-box:focus-within {
  border-color: #b99266;
  box-shadow: 0 0 0 3px rgba(183, 137, 84, 0.14);
  transform: translateY(-1px);
}

.field-icon {
  width: 17px;
  height: 17px;
  color: #a49681;
  flex-shrink: 0;
}

.field-box input {
  width: 100%;
  border: 0;
  outline: none;
  background: transparent;
  color: #30291f;
  font-size: 14px;
}

.field-box input::placeholder {
  color: #a99a85;
}

.ghost-btn {
  border: 0;
  background: transparent;
  color: #7d6f5f;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.ghost-btn:hover {
  color: #a2713e;
}

.forgot-row {
  margin-top: -6px;
  display: flex;
  justify-content: flex-end;
}

.forgot-link {
  font-size: 12px;
  color: #7a6a58;
}

.forgot-link:hover {
  color: #9a6735;
}

.code-row {
  display: grid;
  gap: 12px;
  grid-template-columns: 1fr auto;
  align-items: end;
}

.secondary-btn {
  height: 54px;
  min-width: 120px;
  border: 1px solid #d3c5b2;
  border-radius: 14px;
  background: #fffdfa;
  color: #544a3f;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.24s ease;
}

.secondary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  color: #986636;
  border-color: #bb9f81;
}

.secondary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.password-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.banner {
  border-radius: 12px;
  padding: 11px 12px;
  font-size: 13px;
  line-height: 1.6;
}

.banner.error {
  border: 1px solid rgba(220, 83, 83, 0.22);
  background: rgba(254, 238, 238, 0.85);
  color: #b43030;
}

.banner.success {
  border: 1px solid rgba(73, 165, 107, 0.2);
  background: rgba(233, 249, 239, 0.9);
  color: #22683f;
}

.primary-btn {
  margin-top: 4px;
  height: 54px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #2e2720 0%, #4c3f32 55%, #6e563f 100%);
  color: #f6f2ec;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.02em;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  box-shadow: 0 18px 36px rgba(53, 42, 31, 0.24);
  transition: transform 0.24s ease, box-shadow 0.24s ease, opacity 0.24s ease;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 22px 40px rgba(53, 42, 31, 0.27);
}

.primary-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  animation: spin 0.9s linear infinite;
}

.auth-footer {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid #e0d5c7;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #7d6f5f;
  font-size: 13px;
}

.switch-link {
  border: 0;
  background: transparent;
  color: #2f281f;
  font-weight: 700;
  cursor: pointer;
  transition: color 0.2s ease;
}

.switch-link:hover {
  color: #936334;
}

.reset-modal-mask {
  position: fixed;
  inset: 0;
  z-index: 40;
  display: grid;
  place-items: center;
  background: rgba(39, 30, 21, 0.34);
  backdrop-filter: blur(3px);
  padding: 18px;
}

.reset-modal-card {
  width: min(640px, 100%);
  max-height: min(88vh, 860px);
  overflow: auto;
  border-radius: 24px;
  border: 1px solid rgba(211, 200, 184, 0.85);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 26px 60px rgba(47, 38, 31, 0.24);
  padding: 22px;
}

.reset-modal-head {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 12px;
}

.reset-modal-head h3 {
  margin-top: 8px;
  color: #2a241d;
  font-size: clamp(1.35rem, 2.2vw, 1.65rem);
  letter-spacing: -0.02em;
}

.modal-close {
  border: 1px solid #d5c8b7;
  border-radius: 10px;
  height: 34px;
  min-width: 62px;
  padding: 0 10px;
  background: #fffdfa;
  color: #5a4f43;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.modal-close:hover {
  border-color: #b99266;
  color: #8f5e2d;
}

.reset-form {
  margin-top: 14px;
  display: grid;
  gap: 14px;
}

.mode-fade-enter-active,
.mode-fade-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.mode-fade-enter-from,
.mode-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

.banner-fade-enter-active,
.banner-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.banner-fade-enter-from,
.banner-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@keyframes shell-in {
  from {
    opacity: 0;
    transform: translateY(18px) scale(0.985);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes soft-up {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes orbit {
  0%,
  100% {
    transform: translate3d(0, 0, 0);
  }
  50% {
    transform: translate3d(18px, -10px, 0);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1120px) {
  .auth-shell {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .brand-panel {
    border-right: none;
    border-bottom: 1px solid rgba(219, 205, 188, 0.68);
    padding: 40px 30px 30px;
  }

  .auth-panel {
    padding: 24px;
  }
}

@media (max-width: 760px) {
  .auth-page {
    padding: 14px;
  }

  .auth-shell {
    border-radius: 24px;
  }

  .brand-panel {
    padding: 30px 20px 24px;
  }

  .auth-panel {
    padding: 14px;
  }

  .auth-card {
    border-radius: 20px;
    padding: 20px;
  }

  .code-row {
    grid-template-columns: 1fr;
  }

  .secondary-btn {
    width: 100%;
  }

  .password-grid {
    grid-template-columns: 1fr;
  }

  .reset-modal-card {
    border-radius: 18px;
    padding: 16px;
  }
}
</style>
