<template>
  <div class="settings-page" :class="{ 'theme-dark': isDark }">
    <div class="bg-orb orb-a"></div>
    <div class="bg-orb orb-b"></div>
    <div class="bg-grid"></div>

    <main class="settings-shell">
      <header class="topbar">
        <div class="top-left">
          <button type="button" class="ghost-btn" @click="goHome">返回首页</button>
          <div>
            <p class="top-kicker">Account</p>
            <h1>个人设置</h1>
          </div>
        </div>

        <div class="top-right">
          <button type="button" class="ghost-btn" @click="toggleLocale">
            {{ locale === 'zh' ? 'EN' : '中文' }}
          </button>
          <button type="button" class="ghost-btn" @click="toggleTheme">
            {{ isDark ? '浅色' : '深色' }}
          </button>
          <button type="button" class="ghost-btn danger" @click="handleLogout">退出</button>
          <button type="button" class="avatar-btn">{{ userInitial }}</button>
        </div>
      </header>

      <section class="content">
        <article class="profile-card">
          <header class="card-head">
            <div class="profile-badge">
              {{ userInitial }}
            </div>
            <div>
              <p class="card-kicker">Profile</p>
              <h2>资料设置</h2>
              <p class="card-sub">更新昵称并保持账号信息一致。</p>
            </div>
          </header>

          <div class="field-grid">
            <label class="field">
              <span>用户名</span>
              <input
                v-model="profileForm.username"
                type="text"
                placeholder="输入新的用户名"
              />
            </label>

            <label class="field">
              <span>邮箱</span>
              <input
                v-model="profileForm.email"
                type="email"
                disabled
              />
            </label>
          </div>

          <button
            type="button"
            class="primary-btn"
            :disabled="saving"
            @click="saveProfile"
          >
            {{ saving ? '保存中...' : '保存资料' }}
          </button>

          <transition name="fade-slide">
            <div v-if="message" class="status-banner" :class="messageType === 'success' ? 'success' : 'error'">
              {{ message }}
            </div>
          </transition>
        </article>

        <article class="password-card">
          <header class="card-head simple">
            <div>
              <p class="card-kicker">Security</p>
              <h2>修改密码</h2>
              <p class="card-sub">建议使用字母+数字的强密码，至少 8 位。</p>
            </div>
          </header>

          <div class="field-grid">
            <label class="field">
              <span>当前密码</span>
              <input
                v-model="passwordForm.oldPassword"
                type="password"
                placeholder="输入当前密码"
              />
            </label>

            <label class="field">
              <span>新密码</span>
              <input
                v-model="passwordForm.newPassword"
                type="password"
                placeholder="输入新密码"
              />
            </label>

            <label class="field">
              <span>确认新密码</span>
              <input
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="再次输入新密码"
              />
            </label>
          </div>

          <button
            type="button"
            class="primary-btn"
            :disabled="changing"
            @click="changePassword"
          >
            {{ changing ? '修改中...' : '更新密码' }}
          </button>

          <transition name="fade-slide">
            <div
              v-if="passwordMessage"
              class="status-banner"
              :class="passwordMessageType === 'success' ? 'success' : 'error'"
            >
              {{ passwordMessage }}
            </div>
          </transition>
        </article>

        <article class="danger-card">
          <header class="card-head simple">
            <div>
              <p class="card-kicker">Danger Zone</p>
              <h2>注销账号</h2>
              <p class="card-sub">通过邮箱验证码确认后，将永久删除当前账号及其关联数据。</p>
            </div>
          </header>

          <p class="danger-note">
            注销后不可恢复。你的提交记录、讨论内容以及 AI 私有题将被清理。
          </p>

          <div class="field-grid">
            <label class="field">
              <span>邮箱验证码</span>
              <div class="inline-field">
                <input
                  v-model="deleteForm.verificationCode"
                  type="text"
                  maxlength="6"
                  inputmode="numeric"
                  placeholder="输入 6 位验证码"
                />
                <button
                  type="button"
                  class="inline-btn"
                  :disabled="deleteSending || deleteCountdown > 0 || deletingAccount"
                  @click="sendDeleteCode"
                >
                  {{ deleteCountdown > 0 ? `${deleteCountdown}s 后重发` : (deleteSending ? '发送中...' : '发送验证码') }}
                </button>
              </div>
            </label>
          </div>

          <button
            type="button"
            class="danger-btn"
            :disabled="deletingAccount"
            @click="handleDeleteAccount"
          >
            {{ deletingAccount ? '注销中...' : '确认注销账号' }}
          </button>

          <transition name="fade-slide">
            <div
              v-if="deleteMessage"
              class="status-banner"
              :class="deleteMessageType === 'success' ? 'success' : 'error'"
            >
              {{ deleteMessage }}
            </div>
          </transition>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import api from '@/api'
import { useLocale } from '@/composables/locale'

const router = useRouter()
const userStore = useUserStore()
const { locale, toggleLocale, t } = useLocale()

const isDark = ref(false)
const saving = ref(false)
const message = ref('')
const messageType = ref('success')

const profileForm = reactive({
  username: '',
  email: ''
})

const changing = ref(false)
const passwordMessage = ref('')
const passwordMessageType = ref('success')

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const deleteSending = ref(false)
const deletingAccount = ref(false)
const deleteCountdown = ref(0)
const deleteMessage = ref('')
const deleteMessageType = ref('success')
const deleteForm = reactive({
  verificationCode: ''
})
let deleteCodeTimer = null

const userInitial = computed(() => userStore.user?.username?.charAt(0)?.toUpperCase() || 'U')

const initTheme = () => {
  const savedTheme = localStorage.getItem('theme')
  isDark.value = savedTheme === 'dark'
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

const goHome = () => {
  router.push('/')
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const saveProfile = async () => {
  if (!profileForm.username || profileForm.username.length < 3) {
    message.value = '用户名至少需要3个字符'
    messageType.value = 'error'
    return
  }

  saving.value = true
  message.value = ''

  try {
    const res = await api.put('/api/user/profile', {
      username: profileForm.username
    })

    if (res.code === 0) {
      userStore.updateUserInfo({ ...userStore.userInfo, username: profileForm.username })
      message.value = '保存成功'
      messageType.value = 'success'
    } else {
      message.value = res.message || '保存失败'
      messageType.value = 'error'
    }
  } catch (error) {
    message.value = '保存失败，请稍后重试'
    messageType.value = 'error'
  } finally {
    saving.value = false
  }
}

const changePassword = async () => {
  if (!passwordForm.oldPassword || !passwordForm.newPassword) {
    passwordMessage.value = '请填写所有密码字段'
    passwordMessageType.value = 'error'
    return
  }

  if (passwordForm.newPassword.length < 8) {
    passwordMessage.value = '新密码至少需要8个字符'
    passwordMessageType.value = 'error'
    return
  }

  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordMessage.value = '两次密码输入不一致'
    passwordMessageType.value = 'error'
    return
  }

  changing.value = true
  passwordMessage.value = ''

  try {
    const res = await api.put('/api/user/password', {
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    if (res.code === 0) {
      passwordMessage.value = '密码修改成功'
      passwordMessageType.value = 'success'
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
    } else {
      passwordMessage.value = res.message || '修改失败'
      passwordMessageType.value = 'error'
    }
  } catch (error) {
    passwordMessage.value = '修改失败，请稍后重试'
    passwordMessageType.value = 'error'
  } finally {
    changing.value = false
  }
}

const clearDeleteCodeTimer = () => {
  if (deleteCodeTimer) {
    clearInterval(deleteCodeTimer)
    deleteCodeTimer = null
  }
}

const startDeleteCodeCountdown = () => {
  clearDeleteCodeTimer()
  deleteCountdown.value = 60
  deleteCodeTimer = setInterval(() => {
    if (deleteCountdown.value <= 1) {
      clearDeleteCodeTimer()
      deleteCountdown.value = 0
      return
    }
    deleteCountdown.value -= 1
  }, 1000)
}

const sendDeleteCode = async () => {
  if (deleteSending.value || deleteCountdown.value > 0 || deletingAccount.value) {
    return
  }

  deleteSending.value = true
  deleteMessage.value = ''

  try {
    const res = await api.post('/api/user/send-delete-code')
    if (res.code === 0) {
      const debugCode = res.data?.code ? `（调试验证码：${res.data.code}）` : ''
      deleteMessage.value = `注销验证码已发送到注册邮箱${debugCode}`
      deleteMessageType.value = 'success'
      startDeleteCodeCountdown()
    } else {
      deleteMessage.value = res.message || '发送失败，请稍后重试'
      deleteMessageType.value = 'error'
    }
  } catch (error) {
    deleteMessage.value = '发送失败，请稍后重试'
    deleteMessageType.value = 'error'
  } finally {
    deleteSending.value = false
  }
}

const handleDeleteAccount = async () => {
  const code = (deleteForm.verificationCode || '').trim()
  if (!/^\d{6}$/.test(code)) {
    deleteMessage.value = '请输入 6 位数字验证码'
    deleteMessageType.value = 'error'
    return
  }

  const confirmed = window.confirm(
    t('注销后将删除账号及关联数据，且不可恢复。确认继续吗？', 'This will delete your account and related data permanently. Continue?')
  )
  if (!confirmed) {
    return
  }

  deletingAccount.value = true
  deleteMessage.value = ''

  try {
    const res = await api.delete('/api/user/account', {
      data: { verification_code: code }
    })
    if (res.code === 0) {
      deleteMessage.value = '账号已注销，正在退出登录...'
      deleteMessageType.value = 'success'
      clearDeleteCodeTimer()
      setTimeout(() => {
        userStore.logout()
        router.push('/login')
      }, 600)
    } else {
      deleteMessage.value = res.message || '注销失败，请稍后重试'
      deleteMessageType.value = 'error'
    }
  } catch (error) {
    deleteMessage.value = error.response?.data?.message || '注销失败，请稍后重试'
    deleteMessageType.value = 'error'
  } finally {
    deletingAccount.value = false
  }
}

onMounted(() => {
  initTheme()
  profileForm.username = userStore.user?.username || ''
  profileForm.email = userStore.user?.email || ''
})

onBeforeUnmount(() => {
  clearDeleteCodeTimer()
})
</script>

<style scoped>
.settings-page {
  --page-bg: linear-gradient(162deg, #f8f3ec 0%, #f2ebe0 45%, #e8dfd2 100%);
  --shell-bg: rgba(255, 253, 248, 0.84);
  --shell-border: rgba(255, 255, 255, 0.72);
  --line: #ddcfbc;
  --line-soft: #eadfd0;
  --card-bg: rgba(255, 255, 255, 0.9);
  --card-soft: rgba(253, 249, 242, 0.92);
  --text-main: #2f271f;
  --text-sub: #7b6d5b;
  --text-muted: #998a74;
  --accent: #9b6a39;
  --accent-strong: #7f5024;
  --danger: #b24545;
  --shadow-shell: 0 34px 86px rgba(57, 44, 28, 0.16);
  --shadow-card: 0 18px 40px rgba(53, 40, 25, 0.12);
  --success-bg: rgba(75, 166, 116, 0.15);
  --success-text: #2b744a;
  --error-bg: rgba(219, 86, 86, 0.14);
  --error-text: #a03333;
  --orb-a: rgba(191, 144, 87, 0.24);
  --orb-b: rgba(116, 163, 213, 0.2);
  min-height: 100vh;
  padding: 20px;
  position: relative;
  overflow: hidden;
  background: var(--page-bg);
  color: var(--text-main);
  font-family: "Avenir Next", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.settings-page.theme-dark {
  --page-bg: linear-gradient(160deg, #151820 0%, #10131a 48%, #0d1016 100%);
  --shell-bg: rgba(20, 25, 34, 0.92);
  --shell-border: rgba(70, 80, 96, 0.5);
  --line: #313b4a;
  --line-soft: #26303f;
  --card-bg: rgba(23, 29, 39, 0.92);
  --card-soft: rgba(20, 26, 36, 0.94);
  --text-main: #ecf0f7;
  --text-sub: #a8b1bf;
  --text-muted: #8a94a6;
  --accent: #d4a06f;
  --accent-strong: #ecbb86;
  --danger: #e18a8a;
  --shadow-shell: 0 34px 86px rgba(5, 8, 13, 0.5);
  --shadow-card: 0 18px 40px rgba(5, 8, 13, 0.35);
  --success-bg: rgba(63, 152, 98, 0.24);
  --success-text: #8fd2ac;
  --error-bg: rgba(199, 78, 78, 0.23);
  --error-text: #f2a7a7;
  --orb-a: rgba(116, 76, 36, 0.32);
  --orb-b: rgba(42, 96, 154, 0.26);
}

.bg-grid {
  position: absolute;
  inset: 0;
  opacity: 0.1;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(120, 113, 108, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(120, 113, 108, 0.08) 1px, transparent 1px);
  background-size: 44px 44px;
}

.bg-orb {
  position: absolute;
  border-radius: 9999px;
  filter: blur(96px);
  pointer-events: none;
  animation: drift 14s ease-in-out infinite;
}

.orb-a {
  top: 2%;
  left: -8%;
  width: 340px;
  height: 340px;
  background: var(--orb-a);
}

.orb-b {
  right: -9%;
  bottom: 6%;
  width: 360px;
  height: 360px;
  background: var(--orb-b);
  animation-delay: -6s;
}

.settings-shell {
  position: relative;
  z-index: 2;
  width: min(980px, 100%);
  margin: 0 auto;
  min-height: calc(100vh - 40px);
  border-radius: 30px;
  border: 1px solid var(--shell-border);
  background: var(--shell-bg);
  box-shadow: var(--shadow-shell);
  backdrop-filter: blur(16px);
  overflow: hidden;
  display: grid;
  grid-template-rows: auto 1fr;
  animation: rise-in 0.72s ease both;
}

.topbar {
  border-bottom: 1px solid var(--line);
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.top-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.top-kicker {
  font-size: 11px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 700;
}

.top-left h1 {
  margin-top: 4px;
  font-size: clamp(1.2rem, 2.2vw, 1.6rem);
  letter-spacing: -0.03em;
}

.top-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ghost-btn {
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-main);
  border-radius: 10px;
  height: 36px;
  padding: 0 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.22s ease;
}

.ghost-btn:hover {
  border-color: var(--accent);
  color: var(--accent-strong);
}

.ghost-btn.danger:hover {
  border-color: var(--danger);
  color: var(--danger);
}

.avatar-btn {
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 50%;
  color: #fff;
  font-weight: 700;
  background: linear-gradient(145deg, #875c33 0%, #c18652 100%);
  box-shadow: 0 10px 20px rgba(86, 57, 30, 0.3);
}

.content {
  padding: 20px;
  overflow: auto;
  display: grid;
  gap: 16px;
}

.profile-card,
.password-card,
.danger-card {
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--card-bg);
  box-shadow: var(--shadow-card);
  padding: 16px;
}

.danger-card {
  border-color: color-mix(in srgb, var(--danger) 40%, var(--line));
}

.card-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.card-head.simple {
  margin-bottom: 10px;
}

.profile-badge {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(145deg, #875c33 0%, #c18652 100%);
  box-shadow: 0 10px 20px rgba(86, 57, 30, 0.24);
}

.card-kicker {
  font-size: 11px;
  letter-spacing: 0.18em;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 700;
}

.card-head h2 {
  margin-top: 4px;
  font-size: 1.3rem;
  letter-spacing: -0.02em;
}

.card-sub {
  margin-top: 4px;
  font-size: 13px;
  color: var(--text-sub);
}

.field-grid {
  display: grid;
  gap: 12px;
}

.field span {
  display: block;
  margin-bottom: 7px;
  font-size: 11px;
  letter-spacing: 0.16em;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 700;
}

.field input {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 12px;
  height: 42px;
  background: var(--card-soft);
  color: var(--text-main);
  outline: none;
  padding: 0 12px;
  transition: border-color 0.2s ease;
}

.field input:focus {
  border-color: var(--accent);
}

.field input:disabled {
  opacity: 0.75;
  cursor: not-allowed;
}

.inline-field {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}

.inline-btn {
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-main);
  border-radius: 10px;
  height: 42px;
  padding: 0 12px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s ease;
}

.inline-btn:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent-strong);
}

.inline-btn:disabled {
  opacity: 0.68;
  cursor: not-allowed;
}

.primary-btn {
  margin-top: 12px;
  border: 0;
  height: 38px;
  border-radius: 10px;
  padding: 0 14px;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  background: linear-gradient(145deg, #83552b 0%, #ab7543 100%);
  box-shadow: 0 10px 20px rgba(105, 68, 35, 0.24);
  cursor: pointer;
  transition: transform 0.22s ease, opacity 0.22s ease;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.primary-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.danger-note {
  margin: 0 0 10px;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--error-text);
  background: color-mix(in srgb, var(--error-bg) 84%, transparent);
  border: 1px solid color-mix(in srgb, var(--error-text) 28%, transparent);
}

.danger-btn {
  margin-top: 12px;
  border: 0;
  height: 38px;
  border-radius: 10px;
  padding: 0 14px;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  background: linear-gradient(145deg, #973737 0%, #c95f5f 100%);
  box-shadow: 0 10px 20px rgba(125, 52, 52, 0.24);
  cursor: pointer;
  transition: transform 0.22s ease, opacity 0.22s ease;
}

.danger-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.danger-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.status-banner {
  margin-top: 10px;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 13px;
  line-height: 1.55;
}

.status-banner.success {
  background: var(--success-bg);
  color: var(--success-text);
  border: 1px solid color-mix(in srgb, var(--success-text) 28%, transparent);
}

.status-banner.error {
  background: var(--error-bg);
  color: var(--error-text);
  border: 1px solid color-mix(in srgb, var(--error-text) 30%, transparent);
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

@keyframes drift {
  0%,
  100% {
    transform: translate3d(0, 0, 0);
  }
  50% {
    transform: translate3d(16px, -12px, 0);
  }
}

@keyframes rise-in {
  from {
    opacity: 0;
    transform: translateY(14px) scale(0.99);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 860px) {
  .settings-page {
    padding: 12px;
  }

  .settings-shell {
    min-height: calc(100vh - 24px);
    border-radius: 20px;
  }

  .topbar {
    flex-wrap: wrap;
  }

  .top-right {
    width: 100%;
    justify-content: flex-end;
    flex-wrap: wrap;
  }

  .content {
    padding: 12px;
  }
}

@media (max-width: 620px) {
  .top-right .ghost-btn {
    display: none;
  }

  .inline-field {
    grid-template-columns: 1fr;
  }
}
</style>
