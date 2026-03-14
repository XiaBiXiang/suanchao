<template>
  <div class="discuss-page" :class="{ 'theme-dark': isDark }">
    <div class="bg-orb orb-a"></div>
    <div class="bg-orb orb-b"></div>
    <div class="bg-grid"></div>

    <main class="discuss-shell">
      <header class="topbar">
        <div class="top-left">
          <button type="button" class="ghost-btn" @click="goBack">返回</button>
          <div>
            <p class="top-kicker">Discuss</p>
            <h1>{{ problem?.title || '题目讨论区' }}</h1>
          </div>
        </div>

        <div class="top-right">
          <button type="button" class="ghost-btn" @click="toggleTheme">
            {{ isDark ? '浅色' : '深色' }}
          </button>
          <button type="button" class="ghost-btn" @click="goToSettings">个人设置</button>
          <button type="button" class="avatar-btn" @click="goToSettings">
            {{ userStore.user?.username?.charAt(0)?.toUpperCase() || 'U' }}
          </button>
        </div>
      </header>

      <section class="content">
        <article class="compose-card">
          <div class="compose-head">
            <p>发布讨论</p>
            <span>分享你的思路、坑点或优化方向</span>
          </div>

          <textarea
            v-model="newPost.content"
            rows="4"
            placeholder="描述你的想法：比如如何拆解问题、为什么会超时、怎么优化..."
          ></textarea>

          <div class="compose-foot">
            <p>支持普通文本，建议分段表达更清晰。</p>
            <button
              type="button"
              class="primary-btn"
              :disabled="!newPost.content.trim() || posting"
              @click="submitPost"
            >
              {{ posting ? '发布中...' : '发布讨论' }}
            </button>
          </div>
        </article>

        <section class="posts-panel">
          <header class="panel-head">
            <div>
              <p class="panel-kicker">Threads</p>
              <h2>讨论列表</h2>
            </div>
            <span class="count-badge">{{ posts.length }}</span>
          </header>

          <div class="panel-body">
            <div v-if="loading" class="loading-state">
              <div class="loading-core"></div>
              <p>加载讨论中...</p>
            </div>

            <div v-else-if="posts.length === 0" class="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 9h6.75m-6.75 3h4.5m6.375 4.5H6.75A2.25 2.25 0 014.5 14.25V6.75A2.25 2.25 0 016.75 4.5h10.5a2.25 2.25 0 012.25 2.25v7.5A2.25 2.25 0 0117.25 16.5z" />
              </svg>
              <p>还没有讨论内容，来发表第一条观点。</p>
            </div>

            <transition-group v-else name="post-fade" tag="div" class="post-list">
              <article v-for="post in posts" :key="post.id" class="post-card">
                <header class="post-head">
                  <div class="author">
                    <div class="author-avatar">
                      {{ post.user?.username?.charAt(0)?.toUpperCase() || 'U' }}
                    </div>
                    <div>
                      <p class="author-name">{{ post.user?.username || '匿名用户' }}</p>
                      <p class="author-time">{{ formatTime(post.created_at) }}</p>
                    </div>
                  </div>

                  <button
                    v-if="post.user_id === userStore.user?.id"
                    type="button"
                    class="delete-btn"
                    @click="deletePost(post.id)"
                  >
                    删除
                  </button>
                </header>

                <p class="post-content">{{ post.content }}</p>

                <section class="comment-block">
                  <div class="comment-head">
                    <span>回复 {{ post.comments?.length || 0 }}</span>
                  </div>

                  <div v-if="post.comments?.length" class="comment-list">
                    <article v-for="comment in post.comments" :key="comment.id" class="comment-item">
                      <div class="comment-avatar">
                        {{ comment.user?.username?.charAt(0)?.toUpperCase() || 'U' }}
                      </div>
                      <div class="comment-main">
                        <p class="comment-line">
                          <strong>{{ comment.user?.username || '用户' }}</strong>
                          <span>{{ comment.content }}</span>
                        </p>
                        <p class="comment-time">{{ formatTime(comment.created_at) }}</p>
                      </div>
                      <button
                        v-if="canDeleteComment(post, comment)"
                        type="button"
                        class="comment-delete-btn"
                        @click="deleteComment(comment.id)"
                      >
                        删除
                      </button>
                    </article>
                  </div>

                  <div class="comment-input-row">
                    <input
                      v-model="post.newComment"
                      type="text"
                      placeholder="添加回复..."
                      @keyup.enter="submitComment(post)"
                    />
                    <button
                      type="button"
                      class="secondary-btn"
                      :disabled="!post.newComment?.trim()"
                      @click="submitComment(post)"
                    >
                      回复
                    </button>
                  </div>
                </section>
              </article>
            </transition-group>
          </div>
        </section>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import api from '@/api'
import { useLocale } from '@/composables/locale'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { t } = useLocale()

const loading = ref(true)
const posting = ref(false)
const isDark = ref(false)
const posts = ref([])
const problem = ref(null)
const newPost = reactive({
  content: ''
})

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

const goBack = () => {
  router.back()
}

const goToSettings = () => {
  router.push('/settings')
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return t('刚刚', 'Just now')
  if (diff < 3600000) return `${Math.floor(diff / 60000)}${t('分钟前', 'm ago')}`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}${t('小时前', 'h ago')}`
  return date.toLocaleDateString(t('zh-CN', 'en-US'))
}

const loadProblem = async () => {
  try {
    const res = await api.get(`/api/problems/${route.params.id}`)
    if (res.code === 0) {
      problem.value = res.data
    }
  } catch (error) {
    console.error('加载题目失败:', error)
  }
}

const loadPosts = async () => {
  try {
    loading.value = true
    const res = await api.get(`/api/discuss/${route.params.id}`)
    if (res.code === 0) {
      posts.value = (res.data.items || []).map((post) => ({
        ...post,
        newComment: ''
      }))
    }
  } catch (error) {
    console.error('加载帖子失败:', error)
  } finally {
    loading.value = false
  }
}

const submitPost = async () => {
  if (!newPost.content.trim()) return

  posting.value = true
  try {
    const res = await api.post('/api/discuss', {
      problem_id: route.params.id,
      content: newPost.content
    })
    if (res.code === 0) {
      newPost.content = ''
      loadPosts()
    }
  } catch (error) {
    console.error('发布失败:', error)
  } finally {
    posting.value = false
  }
}

const submitComment = async (post) => {
  if (!post.newComment?.trim()) return

  try {
    const res = await api.post('/api/discuss/comment', {
      post_id: post.id,
      content: post.newComment
    })
    if (res.code === 0) {
      post.newComment = ''
      loadPosts()
    }
  } catch (error) {
    console.error('评论失败:', error)
  }
}

const deletePost = async (postId) => {
  if (!confirm(t('确定要删除这条帖子吗？', 'Delete this post?'))) return

  try {
    const res = await api.delete(`/api/discuss/${postId}`)
    if (res.code === 0) {
      loadPosts()
    } else {
      alert(res.message || t('删除失败', 'Delete failed'))
    }
  } catch (error) {
    alert(t('删除失败，请稍后重试', 'Delete failed, please retry later'))
  }
}

const canDeleteComment = (post, comment) => {
  const currentUserId = userStore.user?.id
  if (!currentUserId) return false
  return post.user_id === currentUserId || comment.user_id === currentUserId
}

const deleteComment = async (commentId) => {
  if (!confirm(t('确定要删除这条评论吗？', 'Delete this comment?'))) return

  try {
    const res = await api.delete(`/api/discuss/comment/${commentId}`)
    if (res.code === 0) {
      loadPosts()
    } else {
      alert(res.message || t('删除评论失败', 'Delete comment failed'))
    }
  } catch (error) {
    alert(t('删除评论失败，请稍后重试', 'Delete comment failed, please retry later'))
  }
}

onMounted(() => {
  initTheme()
  loadProblem()
  loadPosts()
})
</script>

<style scoped>
.discuss-page {
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

.discuss-page.theme-dark {
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

.discuss-shell {
  position: relative;
  z-index: 2;
  width: min(1180px, 100%);
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
  min-width: 0;
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
  font-size: clamp(1.15rem, 2.1vw, 1.55rem);
  letter-spacing: -0.03em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

.avatar-btn {
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 50%;
  cursor: pointer;
  color: #fff;
  font-weight: 700;
  background: linear-gradient(145deg, #875c33 0%, #c18652 100%);
  box-shadow: 0 10px 20px rgba(86, 57, 30, 0.3);
  transition: transform 0.22s ease;
}

.avatar-btn:hover {
  transform: scale(1.06);
}

.content {
  padding: 20px;
  display: grid;
  gap: 16px;
  overflow: auto;
}

.compose-card,
.posts-panel {
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--card-bg);
  box-shadow: var(--shadow-card);
}

.compose-card {
  padding: 16px;
}

.compose-head p {
  font-size: 15px;
  font-weight: 700;
}

.compose-head span {
  margin-top: 4px;
  display: block;
  font-size: 13px;
  color: var(--text-sub);
}

.compose-card textarea {
  width: 100%;
  margin-top: 12px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--card-soft);
  color: var(--text-main);
  outline: none;
  padding: 10px 12px;
  line-height: 1.65;
  resize: vertical;
  min-height: 120px;
}

.compose-card textarea:focus {
  border-color: var(--accent);
}

.compose-card textarea::placeholder {
  color: var(--text-muted);
}

.compose-foot {
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.compose-foot p {
  font-size: 12px;
  color: var(--text-sub);
}

.primary-btn,
.secondary-btn {
  border: 0;
  height: 36px;
  border-radius: 10px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.22s ease;
}

.primary-btn {
  color: #fff;
  background: linear-gradient(145deg, #83552b 0%, #ab7543 100%);
  box-shadow: 0 10px 20px rgba(105, 68, 35, 0.24);
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.primary-btn:disabled,
.secondary-btn:disabled {
  opacity: 0.62;
  cursor: not-allowed;
}

.posts-panel {
  overflow: hidden;
}

.panel-head {
  padding: 14px 16px;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.panel-kicker {
  font-size: 11px;
  letter-spacing: 0.17em;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 700;
}

.panel-head h2 {
  margin-top: 5px;
  font-size: 1.3rem;
  letter-spacing: -0.03em;
}

.count-badge {
  border-radius: 999px;
  min-width: 38px;
  height: 26px;
  padding: 0 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--card-soft);
  color: var(--text-sub);
  border: 1px solid var(--line-soft);
  font-size: 12px;
  font-weight: 700;
}

.panel-body {
  padding: 14px;
}

.loading-state {
  min-height: 180px;
  display: grid;
  place-items: center;
  gap: 10px;
  color: var(--text-sub);
}

.loading-core {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 3px solid rgba(120, 120, 120, 0.24);
  border-top-color: var(--accent);
  animation: spin 0.9s linear infinite;
}

.empty-state {
  border: 1px dashed var(--line);
  border-radius: 12px;
  min-height: 180px;
  display: grid;
  place-items: center;
  text-align: center;
  gap: 10px;
  color: var(--text-sub);
  padding: 16px;
}

.empty-state svg {
  width: 42px;
  height: 42px;
  color: var(--text-muted);
}

.post-list {
  display: grid;
  gap: 12px;
}

.post-card {
  border: 1px solid var(--line-soft);
  border-radius: 14px;
  background: var(--card-soft);
  padding: 12px;
}

.post-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.author {
  display: flex;
  align-items: center;
  gap: 10px;
}

.author-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 700;
  background: linear-gradient(145deg, #875c33 0%, #c18652 100%);
}

.author-name {
  font-size: 13px;
  font-weight: 700;
}

.author-time {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.delete-btn {
  border: 1px solid rgba(178, 69, 69, 0.4);
  background: transparent;
  color: var(--danger);
  border-radius: 8px;
  height: 30px;
  padding: 0 10px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.post-content {
  margin-top: 10px;
  font-size: 14px;
  line-height: 1.72;
  white-space: pre-wrap;
  word-break: break-word;
}

.comment-block {
  margin-top: 12px;
  border-top: 1px solid var(--line);
  padding-top: 10px;
}

.comment-head {
  font-size: 12px;
  color: var(--text-sub);
  font-weight: 700;
}

.comment-list {
  margin-top: 8px;
  display: grid;
  gap: 8px;
}

.comment-item {
  display: flex;
  gap: 8px;
}

.comment-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 11px;
  color: var(--text-main);
  border: 1px solid var(--line-soft);
  background: var(--card-bg);
  flex-shrink: 0;
}

.comment-main {
  min-width: 0;
  flex: 1;
}

.comment-line {
  font-size: 13px;
  line-height: 1.6;
}

.comment-line strong {
  margin-right: 6px;
}

.comment-line span {
  color: var(--text-sub);
  word-break: break-word;
}

.comment-time {
  margin-top: 2px;
  font-size: 11px;
  color: var(--text-muted);
}

.comment-delete-btn {
  border: 1px solid rgba(178, 69, 69, 0.35);
  background: transparent;
  color: var(--danger);
  border-radius: 8px;
  height: 26px;
  padding: 0 9px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  align-self: flex-start;
  transition: all 0.2s ease;
}

.comment-delete-btn:hover {
  border-color: var(--danger);
  background: rgba(178, 69, 69, 0.08);
}

.comment-input-row {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}

.comment-input-row input {
  flex: 1;
  border: 1px solid var(--line);
  border-radius: 10px;
  height: 36px;
  padding: 0 10px;
  background: var(--card-bg);
  color: var(--text-main);
  outline: none;
}

.comment-input-row input:focus {
  border-color: var(--accent);
}

.comment-input-row input::placeholder {
  color: var(--text-muted);
}

.secondary-btn {
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-main);
}

.secondary-btn:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent-strong);
}

.post-fade-enter-active,
.post-fade-leave-active {
  transition: all 0.24s ease;
}

.post-fade-enter-from,
.post-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 920px) {
  .discuss-page {
    padding: 12px;
  }

  .discuss-shell {
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

@media (max-width: 640px) {
  .top-right .ghost-btn {
    display: none;
  }

  .compose-foot {
    flex-direction: column;
    align-items: stretch;
  }

  .primary-btn {
    width: 100%;
  }

  .comment-input-row {
    flex-direction: column;
  }

  .secondary-btn {
    width: 100%;
  }
}
</style>
