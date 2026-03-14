<template>
  <div class="workspace-page" :class="{ 'theme-dark': isDark }">
    <div class="bg-orb orb-a"></div>
    <div class="bg-orb orb-b"></div>
    <div class="bg-grid"></div>

    <main class="workspace-shell">
      <header class="topbar">
        <div class="topbar-left">
          <div class="brand-mark">LC</div>
          <div class="title-wrap">
            <p class="top-kicker">Workspace</p>
            <h1>{{ problemDetail?.title || '加载题目中...' }}</h1>
          </div>
        </div>

        <div class="topbar-actions">
          <button type="button" class="ghost-action" @click="goHome">返回首页</button>
          <button type="button" class="ghost-action" @click="goToSettings">个人设置</button>
          <button type="button" class="ghost-action" @click="toggleTheme">
            {{ isDark ? '浅色' : '深色' }}
          </button>
          <button type="button" class="ghost-action danger" @click="handleLogout">退出</button>
          <button type="button" class="avatar" @click="goToSettings">{{ userInitial }}</button>
        </div>
      </header>

      <section class="workspace-main">
        <transition name="fade">
          <div v-if="loading" class="loading-mask">
            <div class="loading-core"></div>
            <p>正在加载题目内容...</p>
          </div>
        </transition>

        <div v-if="isMobileViewport" class="mobile-switcher">
          <button
            type="button"
            :class="{ active: mobileMainTab === 'problem' }"
            @click="mobileMainTab = 'problem'"
          >
            题目
          </button>
          <button
            type="button"
            :class="{ active: mobileMainTab === 'code' }"
            @click="mobileMainTab = 'code'"
          >
            编码
          </button>
          <button
            type="button"
            :class="{ active: mobileMainTab === 'ai' }"
            @click="mobileMainTab = 'ai'"
          >
            AI 导师
          </button>
        </div>

        <splitpanes class="workspace-layout" :horizontal="isMobileViewport">
          <pane
            v-if="!isMobileViewport || mobileMainTab === 'problem' || mobileMainTab === 'ai'"
            min-size="24"
            :size="isMobileViewport ? 48 : 38"
          >
            <splitpanes horizontal class="left-layout">
              <pane
                v-if="!isMobileViewport || mobileMainTab === 'problem'"
                min-size="16"
                :size="!isMobileViewport ? 70 : 100"
              >
                <section class="problem-pane">
                  <div class="problem-head">
                    <div class="problem-meta">
                      <span class="difficulty-chip" :class="difficultyClass(problemDetail?.difficulty)">
                        {{ difficultyText(problemDetail?.difficulty) }}
                      </span>
                      <span
                        class="source-chip"
                        :class="problemDetail?.source_type === 'ai_generated' ? 'ai' : 'official'"
                      >
                        {{ problemDetail?.source_type === 'ai_generated' ? 'AI 私有题' : '题库题' }}
                      </span>
                      <span v-if="problemDetail?.is_square_imported" class="source-chip square">
                        广场导入
                      </span>
                      <span class="meta-item">时间 {{ problemDetail?.time_limit || '--' }} ms</span>
                      <span class="meta-item">内存 {{ problemDetail?.memory_limit || '--' }} MB</span>
                    </div>
                    <div v-if="problemDetail?.source_type === 'ai_generated'" class="ai-feedback">
                      <button
                        type="button"
                        class="feedback-btn"
                        :disabled="Boolean(aiFeedbackSubmitting)"
                        @click="submitAiFeedback('up')"
                      >
                        有用
                      </button>
                      <button
                        type="button"
                        class="feedback-btn"
                        :disabled="Boolean(aiFeedbackSubmitting)"
                        @click="submitAiFeedback('down')"
                      >
                        无用
                      </button>
                      <span v-if="aiFeedbackScore !== null" class="feedback-score">
                        反馈分 {{ aiFeedbackScore }}
                      </span>
                      <span v-if="aiFeedbackMessage" class="feedback-msg">{{ aiFeedbackMessage }}</span>
                    </div>
                  </div>

                  <article class="problem-description">
                    <div
                      v-if="problemDetail?.description"
                      class="problem-markdown"
                      v-html="renderedDescription"
                    ></div>
                    <div v-else class="empty-copy">暂无题目描述</div>
                  </article>

                  <section class="testcase-panel">
                    <div class="section-head">
                      <p>示例测试用例</p>
                      <span>{{ visibleTestCases.length }} 个</span>
                    </div>
                    <div class="testcase-list">
                      <div v-for="(testCase, index) in visibleTestCases" :key="testCase.id" class="testcase-item">
                        <div class="testcase-title">
                          <span>用例 {{ index + 1 }}</span>
                          <b>公开</b>
                        </div>
                        <div class="testcase-grid">
                          <div>
                            <p>输入</p>
                            <pre>{{ testCase.input_data }}</pre>
                          </div>
                          <div>
                            <p>输出</p>
                            <pre>{{ testCase.expected_output }}</pre>
                          </div>
                        </div>
                      </div>
                    </div>
                  </section>
                </section>
              </pane>

              <pane
                v-if="!isMobileViewport || mobileMainTab === 'ai'"
                min-size="16"
                :size="!isMobileViewport ? 30 : 100"
              >
                <section class="ai-panel">
                  <AiChat
                    :problem-description="problemDetail?.description || ''"
                    :current-code="userCode"
                    :dark="isDark"
                  />
                </section>
              </pane>
            </splitpanes>
          </pane>

          <pane
            v-if="!isMobileViewport || mobileMainTab === 'code'"
            min-size="30"
            :size="isMobileViewport ? 52 : 62"
          >
            <splitpanes
              horizontal
              class="right-layout"
              @resize="handleRightLayoutResize"
              @resized="handleRightLayoutResized"
            >
              <pane min-size="28" :size="editorPaneSize">
                <section class="editor-pane">
                  <div class="editor-hero">
                    <div class="hero-copy">
                      <p class="editor-kicker">Code Studio</p>
                      <h3>写代码区</h3>
                      <p>先运行，再提交，快速验证思路与边界条件。</p>
                    </div>

                    <div class="editor-meta">
                      <span class="meta-chip">{{ languageLabel }}</span>
                      <span class="meta-chip">{{ codeLineCount }} 行</span>
                      <span class="meta-chip">{{ codeCharCount }} 字符</span>
                    </div>
                  </div>

                  <div class="editor-toolbar">
                    <div class="language-picker">
                      <label>语言</label>
                      <select v-model="language">
                        <option value="python">Python</option>
                        <option value="javascript">JavaScript</option>
                        <option value="java">Java</option>
                      </select>
                    </div>

                    <div class="editor-actions">
                      <button type="button" class="action-btn plain" :disabled="submitting" @click="resetCodeTemplate">
                        恢复模板
                      </button>
                      <button type="button" class="action-btn run" :disabled="submitting" @click="runCode">
                        <span class="btn-dot"></span>
                        {{ submitting ? '任务处理中...' : '自定义运行' }}
                      </button>
                      <button type="button" class="action-btn submit" :disabled="submitting" @click="submitCode">
                        <span class="btn-dot"></span>
                        {{ submitting ? '任务处理中...' : '提交判题' }}
                      </button>
                    </div>
                  </div>

                  <div class="custom-input-wrap">
                    <label for="workspace-custom-input">自定义输入运行</label>
                    <textarea
                      id="workspace-custom-input"
                      v-model="customInput"
                      :disabled="submitting"
                      placeholder="输入将通过标准输入传给你的程序。可为空。"
                    ></textarea>
                  </div>

                  <div class="editor-wrap">
                    <div class="editor-glow"></div>
                    <vue-monaco-editor
                      v-model:value="userCode"
                      :language="language"
                      :theme="editorTheme"
                      :options="editorOptions"
                      @mount="handleEditorMounted"
                    />
                  </div>

                  <div class="editor-footnote">
                    <span>Tab 触发智能补全</span>
                    <span class="foot-divider"></span>
                    <span>支持 Python / JavaScript / Java</span>
                    <span class="foot-divider"></span>
                    <span>{{ draftText }}</span>
                  </div>
                </section>
              </pane>

              <pane min-size="20" :size="resultPaneSize">
                <section class="result-pane">
                  <div class="result-tabs">
                    <button
                      type="button"
                      :class="{ active: activeTab === 'output' }"
                      @click="activeTab = 'output'"
                    >
                      输出
                    </button>
                    <button
                      type="button"
                      :class="{ active: activeTab === 'result' }"
                      @click="activeTab = 'result'"
                    >
                      判题详情
                    </button>
                    <button
                      type="button"
                      :class="{ active: activeTab === 'history' }"
                      @click="activeTab = 'history'"
                    >
                      提交历史
                    </button>
                  </div>

                  <div class="result-body">
                    <div v-if="activeTab === 'history'" class="history-panel">
                      <div class="history-toolbar">
                        <button type="button" class="action-btn plain" @click="loadSubmissionHistory(getProblemId())">
                          刷新历史
                        </button>
                      </div>

                      <div v-if="!submissionHistory.length" class="placeholder compact">
                        <p>暂无提交历史</p>
                      </div>

                      <div v-else class="history-content">
                        <div class="history-list">
                          <article
                            v-for="item in submissionHistory"
                            :key="item.id"
                            class="history-item"
                          >
                            <header>
                              <span class="status-pill" :class="historyStatusClass(item.status)">
                                {{ item.status }}
                              </span>
                              <span class="history-meta">{{ item.run_mode === 'run' ? '运行' : '提交' }}</span>
                              <span class="history-meta">{{ formatHistoryDate(item.created_at) }}</span>
                            </header>
                            <div class="history-actions">
                              <button type="button" class="mini-btn" @click="selectedHistoryLeft = item.id">
                                左侧对比
                              </button>
                              <button type="button" class="mini-btn" @click="selectedHistoryRight = item.id">
                                右侧对比
                              </button>
                            </div>
                          </article>
                        </div>

                        <div class="compare-box">
                          <div class="compare-select">
                            <label>
                              左侧版本
                              <select v-model="selectedHistoryLeft">
                                <option v-for="item in submissionHistory" :key="`left-${item.id}`" :value="item.id">
                                  {{ formatHistoryDate(item.created_at) }} / {{ item.status }}
                                </option>
                              </select>
                            </label>
                            <label>
                              右侧版本
                              <select v-model="selectedHistoryRight">
                                <option v-for="item in submissionHistory" :key="`right-${item.id}`" :value="item.id">
                                  {{ formatHistoryDate(item.created_at) }} / {{ item.status }}
                                </option>
                              </select>
                            </label>
                          </div>

                          <div v-if="selectedCompareItemsReady" class="compare-grid">
                            <section class="compare-code">
                              <div class="compare-head">
                                <span>{{ selectedHistoryLeftItem?.run_mode === 'run' ? '运行' : '提交' }}</span>
                                <b>{{ selectedHistoryLeftItem?.status }}</b>
                              </div>
                              <pre>{{ selectedHistoryLeftItem?.code || '' }}</pre>
                            </section>

                            <section class="compare-code">
                              <div class="compare-head">
                                <span>{{ selectedHistoryRightItem?.run_mode === 'run' ? '运行' : '提交' }}</span>
                                <b>{{ selectedHistoryRightItem?.status }}</b>
                              </div>
                              <pre>{{ selectedHistoryRightItem?.code || '' }}</pre>
                            </section>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div v-else-if="!judgeResult && !submitting" class="placeholder">
                      <p>点击“运行代码”或“提交判题”查看结果</p>
                    </div>

                    <div v-else-if="submitting" class="placeholder">
                      <div class="loading-core small"></div>
                      <p>{{ jobStateText || '判题执行中，请稍候...' }}</p>
                      <div class="queue-progress">
                        <div class="queue-progress-fill" :style="{ width: `${jobProgress}%` }"></div>
                      </div>
                      <p class="queue-meta">{{ jobProgress }}%</p>
                    </div>

                    <div v-else-if="judgeResult" class="result-content">
                      <article class="summary-card" :class="statusCardClass">
                        <header>
                          <span class="status-pill" :class="statusPillClass">{{ judgeResult.status }}</span>
                          <p>{{ judgeResult.message }}</p>
                        </header>
                        <div class="summary-metrics">
                          <span>通过 {{ judgeResult.passed_cases }}/{{ judgeResult.total_cases }}</span>
                          <span>耗时 {{ judgeResult.total_time_ms }} ms</span>
                          <span>峰值 {{ judgeResult.max_memory_mb || 0 }} MB</span>
                        </div>
                      </article>

                      <div v-if="activeTab === 'output'" class="output-card">
                        <p class="output-label">输出预览</p>
                        <pre>{{ outputPreview }}</pre>
                      </div>

                      <div v-if="activeTab === 'result'" class="detail-list">
                        <article
                          v-for="(testCase, index) in judgeResult.test_results"
                          :key="`${testCase.test_case_id}-${index}`"
                          class="detail-item"
                          :class="{ pass: testCase.status === 'AC', fail: testCase.status !== 'AC' }"
                        >
                          <div class="detail-head">
                            <p>用例 {{ index + 1 }}</p>
                            <span>{{ testCase.status }}</span>
                          </div>

                          <div class="detail-grid">
                            <div>
                              <p>输入</p>
                              <pre>{{ testCase.input_data }}</pre>
                            </div>
                            <div>
                              <p>期望</p>
                              <pre>{{ testCase.expected_output }}</pre>
                            </div>
                          </div>

                          <div v-if="testCase.status !== 'AC'" class="detail-extra">
                            <p>实际输出</p>
                            <pre>{{ testCase.actual_output || '(无输出)' }}</pre>
                          </div>

                          <div v-if="testCase.error_message" class="detail-extra error">
                            <p>错误信息</p>
                            <pre>{{ testCase.error_message }}</pre>
                          </div>
                        </article>
                      </div>
                    </div>
                  </div>
                </section>
              </pane>
            </splitpanes>
          </pane>
        </splitpanes>
      </section>
    </main>

    <transition name="fade">
      <div v-if="showSuccessModal" class="modal-mask">
        <div class="modal-card">
          <div class="modal-badge">AC</div>
          <h3>提交成功</h3>
          <p>所有测试用例通过，继续保持这个节奏。</p>
          <div class="modal-actions">
            <button type="button" class="ghost-action" @click="stayHere">继续在当前题目</button>
            <button type="button" class="action-btn submit" @click="goHome">返回首页</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'
import MarkdownIt from 'markdown-it'
import api from '@/api'
import AiChat from '@/components/AiChat.vue'
import { useUserStore } from '@/store/user'
import { useLocale } from '@/composables/locale'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { t } = useLocale()

const loading = ref(true)
const submitting = ref(false)
const isDark = ref(false)
const language = ref('python')
const userCode = ref('')
const problemDetail = ref(null)
const judgeResult = ref(null)
const activeTab = ref('output')
const showSuccessModal = ref(false)
const completionRegistered = ref(false)
const editorPaneSize = ref(62)
const resultPaneSize = ref(38)
const isMobileViewport = ref(false)
const mobileMainTab = ref('code')
const customInput = ref('')
const submissionHistory = ref([])
const selectedHistoryLeft = ref('')
const selectedHistoryRight = ref('')
const aiFeedbackSubmitting = ref('')
const aiFeedbackMessage = ref('')
const aiFeedbackScore = ref(null)
const jobState = ref({
  jobId: '',
  status: '',
  progress: 0,
  queuePosition: 0,
  message: '',
  runMode: 'submit',
})
const draftSavedAt = ref(0)

const RIGHT_LAYOUT_STORAGE_KEY = 'workspace_right_layout_editor_size'
const WORKSPACE_VIEW_STATE_KEY_PREFIX = 'workspace_view_state_v1'
const MOBILE_BREAKPOINT = 900
const EDITOR_PANE_MIN_SIZE = 28
const RESULT_PANE_MIN_SIZE = 20
const DEFAULT_EDITOR_PANE_SIZE = 62
const HISTORY_LIMIT = 40
const JOB_POLL_INTERVAL_MS = 900
const DRAFT_DEBOUNCE_MS = 600
let jobPollTimer = null
let draftSaveTimer = null

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

const defaultCode = {
  python: `# 请在这里编写你的代码
def solution():
    # 在这里实现你的算法
    pass

if __name__ == "__main__":
    solution()
`,
  javascript: `// 请在这里编写你的代码
function solution() {
    // 在这里实现你的算法
}

// 读取输入
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.on('close', () => {
    solution();
});
`,
  java: `// 请在这里编写你的代码
import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        // 在这里实现你的算法
    }
}
`
}

const userInitial = computed(() => userStore.user?.username?.charAt(0)?.toUpperCase() || 'U')

const editorTheme = computed(() => (isDark.value ? 'vs-dark' : 'vs'))

const languageLabel = computed(() => {
  const labelMap = {
    python: 'Python',
    javascript: 'JavaScript',
    java: 'Java'
  }
  return labelMap[language.value] || language.value
})

const codeLineCount = computed(() => {
  if (!userCode.value) return 0
  return userCode.value.split('\n').length
})

const codeCharCount = computed(() => userCode.value?.length || 0)
const jobProgress = computed(() => Math.max(0, Math.min(100, Number(jobState.value.progress || 0))))
const jobStateText = computed(() => {
  if (!jobState.value.status) return ''
  if (jobState.value.status === 'queued') {
    const position = Number(jobState.value.queuePosition || 0)
    return position > 0
      ? `排队中，前方还有 ${Math.max(position - 1, 0)} 个任务`
      : '排队中，等待分配执行器'
  }
  if (jobState.value.status === 'running') return jobState.value.message || '任务执行中...'
  if (jobState.value.status === 'completed') return '执行完成'
  if (jobState.value.status === 'failed') return '执行失败'
  return jobState.value.message || ''
})
const draftText = computed(() => {
  if (!draftSavedAt.value) return '草稿自动保存已开启'
  return `草稿已保存 ${new Date(draftSavedAt.value).toLocaleTimeString('zh-CN', { hour12: false })}`
})

const renderedDescription = computed(() => {
  if (!problemDetail.value?.description) return ''
  return md.render(problemDetail.value.description)
})

const visibleTestCases = computed(() => problemDetail.value?.test_cases || [])

const statusCardClass = computed(() => {
  const status = judgeResult.value?.status
  if (status === 'AC') return 'pass'
  if (status === 'WA') return 'warn'
  if (status === 'TLE') return 'warn'
  if (status === 'RE' || status === 'MLE' || status === 'CE') return 'fail'
  return 'neutral'
})

const statusPillClass = computed(() => {
  const status = judgeResult.value?.status
  if (status === 'AC') return 'pass'
  if (status === 'WA') return 'warn'
  if (status === 'TLE') return 'warn'
  if (status === 'RE' || status === 'MLE' || status === 'CE') return 'fail'
  return 'neutral'
})

const outputPreview = computed(() => {
  if (!judgeResult.value?.test_results?.length) return t('暂无输出', 'No output')
  const failedCase = judgeResult.value.test_results.find((testCase) => testCase.status !== 'AC')
  if (failedCase) {
    return failedCase.actual_output || failedCase.error_message || t('(无输出)', '(No output)')
  }
  const firstCase = judgeResult.value.test_results[0]
  return firstCase.actual_output || t('运行成功', 'Run success')
})
const selectedHistoryLeftItem = computed(() =>
  submissionHistory.value.find((item) => item.id === selectedHistoryLeft.value)
)
const selectedHistoryRightItem = computed(() =>
  submissionHistory.value.find((item) => item.id === selectedHistoryRight.value)
)
const selectedCompareItemsReady = computed(
  () => Boolean(selectedHistoryLeftItem.value && selectedHistoryRightItem.value)
)

const editorOptions = {
  minimap: { enabled: false },
  fontSize: 14,
  lineNumbers: 'on',
  scrollBeyondLastLine: false,
  automaticLayout: true,
  tabSize: 4,
  wordWrap: 'on',
  padding: { top: 16, bottom: 16 },
  scrollbar: {
    verticalScrollbarSize: 8,
    horizontalScrollbarSize: 8
  },
  quickSuggestions: true,
  suggestOnTriggerCharacters: true,
  acceptSuggestionOnEnter: 'on',
  tabCompletion: 'on',
  wordBasedSuggestions: 'all'
}

const normalizeEditorPaneSize = (size) => {
  const value = Number(size)
  if (!Number.isFinite(value)) return DEFAULT_EDITOR_PANE_SIZE
  const maxEditorSize = 100 - RESULT_PANE_MIN_SIZE
  return Math.min(maxEditorSize, Math.max(EDITOR_PANE_MIN_SIZE, Number(value.toFixed(2))))
}

const applyEditorPaneSize = (size) => {
  const nextEditorSize = normalizeEditorPaneSize(size)
  editorPaneSize.value = nextEditorSize
  resultPaneSize.value = Number((100 - nextEditorSize).toFixed(2))
}

const loadRightLayoutPreference = () => {
  try {
    const savedValue = localStorage.getItem(RIGHT_LAYOUT_STORAGE_KEY)
    if (!savedValue) return
    applyEditorPaneSize(savedValue)
  } catch (error) {
    console.warn('读取代码区尺寸配置失败:', error)
  }
}

const persistRightLayoutPreference = () => {
  try {
    localStorage.setItem(RIGHT_LAYOUT_STORAGE_KEY, String(editorPaneSize.value))
  } catch (error) {
    console.warn('保存代码区尺寸配置失败:', error)
  }
}

const handleRightLayoutResize = (payload) => {
  const panes = payload?.panes
  if (!Array.isArray(panes) || panes.length < 2) return
  applyEditorPaneSize(panes[0].size)
}

const handleRightLayoutResized = (payload) => {
  handleRightLayoutResize(payload)
  persistRightLayoutPreference()
}

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

const difficultyText = (difficulty) => {
  const map = {
    Easy: t('简单', 'Easy'),
    Medium: t('中等', 'Medium'),
    Hard: t('困难', 'Hard')
  }
  return map[difficulty] || (difficulty || t('未分类', 'Uncategorized'))
}

const difficultyClass = (difficulty) => {
  if (difficulty === 'Easy') return 'easy'
  if (difficulty === 'Medium') return 'medium'
  if (difficulty === 'Hard') return 'hard'
  return 'neutral'
}

const getProblemId = () => route.params.id || '729d97ed-703f-4ff6-853d-c39d507a5caf'
const getDraftStorageKey = (problemId, lang) =>
  `workspace_draft:${userStore.user?.id || 'anonymous'}:${problemId}:${lang}`
const getWorkspaceViewKey = (problemId) =>
  `${WORKSPACE_VIEW_STATE_KEY_PREFIX}:${userStore.user?.id || 'anonymous'}:${problemId}`

const updateViewportState = () => {
  if (typeof window === 'undefined') return
  isMobileViewport.value = window.innerWidth <= MOBILE_BREAKPOINT
}

const persistWorkspaceViewState = (problemId = getProblemId()) => {
  if (!problemId) return
  try {
    localStorage.setItem(
      getWorkspaceViewKey(problemId),
      JSON.stringify({
        language: language.value,
        activeTab: activeTab.value,
        customInput: customInput.value,
        mobileMainTab: mobileMainTab.value,
        editorPaneSize: editorPaneSize.value,
        resultPaneSize: resultPaneSize.value,
        selectedHistoryLeft: selectedHistoryLeft.value,
        selectedHistoryRight: selectedHistoryRight.value,
        ts: Date.now(),
      })
    )
  } catch (error) {
    console.warn('保存工作区视图状态失败:', error)
  }
}

const restoreWorkspaceViewState = (problemId) => {
  if (!problemId) return
  try {
    const raw = localStorage.getItem(getWorkspaceViewKey(problemId))
    if (!raw) return
    const payload = JSON.parse(raw)
    const savedLanguage = payload?.language
    if (savedLanguage && defaultCode[savedLanguage]) {
      language.value = savedLanguage
    }
    if (['output', 'result', 'history'].includes(payload?.activeTab)) {
      activeTab.value = payload.activeTab
    }
    if (typeof payload?.customInput === 'string') {
      customInput.value = payload.customInput
    }
    if (['problem', 'code', 'ai'].includes(payload?.mobileMainTab)) {
      mobileMainTab.value = payload.mobileMainTab
    }
    if (Number.isFinite(payload?.editorPaneSize)) {
      applyEditorPaneSize(payload.editorPaneSize)
    } else if (Number.isFinite(payload?.resultPaneSize)) {
      const computedEditor = 100 - Number(payload.resultPaneSize)
      applyEditorPaneSize(computedEditor)
    }
    if (typeof payload?.selectedHistoryLeft === 'string') {
      selectedHistoryLeft.value = payload.selectedHistoryLeft
    }
    if (typeof payload?.selectedHistoryRight === 'string') {
      selectedHistoryRight.value = payload.selectedHistoryRight
    }
  } catch (error) {
    console.warn('恢复工作区视图状态失败:', error)
  }
}

const handlePageHide = () => {
  stopJobPolling()
  stopDraftTimer()
  persistWorkspaceViewState()
  persistRightLayoutPreference()
  saveDraft(getProblemId(), language.value, userCode.value)
}

const handleVisibilityChange = () => {
  if (document.visibilityState === 'hidden') {
    handlePageHide()
    return
  }
  if (
    document.visibilityState === 'visible' &&
    submitting.value &&
    jobState.value.jobId
  ) {
    pollJobStatus(jobState.value.jobId, jobState.value.runMode || 'submit')
  }
}

const stopJobPolling = () => {
  if (jobPollTimer) {
    clearTimeout(jobPollTimer)
    jobPollTimer = null
  }
}

const stopDraftTimer = () => {
  if (draftSaveTimer) {
    clearTimeout(draftSaveTimer)
    draftSaveTimer = null
  }
}

const readDraft = (problemId, lang) => {
  try {
    const payload = localStorage.getItem(getDraftStorageKey(problemId, lang))
    if (!payload) return ''
    const parsed = JSON.parse(payload)
    return typeof parsed?.code === 'string' ? parsed.code : ''
  } catch (error) {
    console.warn('读取草稿失败:', error)
    return ''
  }
}

const saveDraft = (problemId, lang, code) => {
  try {
    localStorage.setItem(
      getDraftStorageKey(problemId, lang),
      JSON.stringify({
        code,
        saved_at: Date.now()
      })
    )
    draftSavedAt.value = Date.now()
  } catch (error) {
    console.warn('保存草稿失败:', error)
  }
}

const scheduleDraftSave = () => {
  stopDraftTimer()
  const problemId = getProblemId()
  draftSaveTimer = setTimeout(() => {
    saveDraft(problemId, language.value, userCode.value)
  }, DRAFT_DEBOUNCE_MS)
}

const loadDraftOrTemplate = (problemId, lang) => {
  const draft = readDraft(problemId, lang)
  userCode.value = draft || defaultCode[lang] || ''
}

const historyStatusClass = (status) => {
  if (status === 'AC') return 'pass'
  if (status === 'WA' || status === 'TLE') return 'warn'
  if (status === 'RE' || status === 'MLE' || status === 'CE' || status === 'SYSTEM_ERROR') return 'fail'
  return 'neutral'
}

const formatHistoryDate = (value) => {
  if (!value) return '--'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '--'
  return date.toLocaleString('zh-CN', { hour12: false })
}

const loadSubmissionHistory = async (problemId) => {
  try {
    const res = await api.get(`/api/submit/history/${problemId}`, {
      params: { limit: HISTORY_LIMIT }
    })
    if (res.code !== 0) return
    submissionHistory.value = res.data?.items || []

    if (!submissionHistory.value.length) {
      selectedHistoryLeft.value = ''
      selectedHistoryRight.value = ''
      return
    }

    if (!selectedHistoryLeft.value || !submissionHistory.value.some((item) => item.id === selectedHistoryLeft.value)) {
      selectedHistoryLeft.value = submissionHistory.value[0].id
    }
    if (!selectedHistoryRight.value || !submissionHistory.value.some((item) => item.id === selectedHistoryRight.value)) {
      selectedHistoryRight.value = submissionHistory.value[1]?.id || submissionHistory.value[0].id
    }
  } catch (error) {
    console.error('加载提交历史失败:', error)
  }
}

const loadProblem = async (problemId) => {
  try {
    loading.value = true
    const res = await api.get(`/api/problems/${problemId}`)
    if (res.code === 0) {
      problemDetail.value = res.data
      aiFeedbackMessage.value = ''
      aiFeedbackScore.value = null
      restoreWorkspaceViewState(problemId)
      loadDraftOrTemplate(problemId, language.value)
      await loadSubmissionHistory(problemId)
    }
  } catch (error) {
    console.error('加载题目失败:', error)
  } finally {
    loading.value = false
  }
}

const scheduleNextJobPoll = (jobId, mode) => {
  stopJobPolling()
  jobPollTimer = setTimeout(() => {
    pollJobStatus(jobId, mode)
  }, JOB_POLL_INTERVAL_MS)
}

const pollJobStatus = async (jobId, mode) => {
  try {
    const res = await api.get(`/api/submit/jobs/${jobId}`)
    if (res.code !== 0) {
      submitting.value = false
      stopJobPolling()
      alert(res.message || t('获取判题进度失败', 'Failed to fetch judge progress'))
      return
    }

    const data = res.data || {}
    jobState.value = {
      jobId: data.job_id || jobId,
      status: data.status || '',
      progress: Number(data.progress || 0),
      queuePosition: Number(data.queue_position || 0),
      message: data.message || '',
      runMode: data.run_mode || mode || jobState.value.runMode || 'submit',
    }

    if (data.status === 'completed') {
      submitting.value = false
      stopJobPolling()
      judgeResult.value = data.result_data || null
      activeTab.value = mode === 'run' ? 'output' : 'result'
      await loadSubmissionHistory(getProblemId())
      if (mode === 'submit' && data.result_data?.status === 'AC') {
        showSuccessModal.value = true
      }
      return
    }

    if (data.status === 'failed') {
      submitting.value = false
      stopJobPolling()
      alert(data.error_message || data.message || t('判题失败，请稍后重试', 'Judge failed, please retry later'))
      return
    }

    scheduleNextJobPoll(jobId, mode)
  } catch (error) {
    console.error('轮询判题状态失败:', error)
    submitting.value = false
    stopJobPolling()
    alert(error.response?.data?.message || t('判题失败，请稍后重试', 'Judge failed, please retry later'))
  }
}

const executeJudge = async (mode = 'run') => {
  if (!userCode.value.trim()) {
    alert(t('请先编写代码', 'Please write code first'))
    return
  }
  if (submitting.value) return

  submitting.value = true
  judgeResult.value = null
  activeTab.value = mode === 'run' ? 'output' : 'result'
  jobState.value = {
    jobId: '',
    status: 'queued',
    progress: 0,
    queuePosition: 0,
    message: '任务入队中...',
    runMode: mode,
  }

  try {
    const res = await api.post('/api/submit/queue', {
      problem_id: getProblemId(),
      code: userCode.value,
      language: language.value,
      run_mode: mode,
      custom_input: mode === 'run' ? customInput.value : undefined
    })
    if (res.code !== 0) {
      throw new Error(res.message || t('判题任务提交失败', 'Failed to submit judge job'))
    }
    const data = res.data || {}
    jobState.value = {
      jobId: data.job_id || '',
      status: data.status || 'queued',
      progress: Number(data.progress || 0),
      queuePosition: Number(data.queue_position || 0),
      message: data.message || '已进入判题队列',
      runMode: mode,
    }
    await pollJobStatus(data.job_id, mode)
  } catch (error) {
    console.error('判题失败:', error)
    submitting.value = false
    stopJobPolling()
    alert(error.response?.data?.message || t('判题失败，请稍后重试', 'Judge failed, please retry later'))
  }
}

const runCode = async () => {
  await executeJudge('run')
}

const submitCode = async () => {
  await executeJudge('submit')
}

const submitAiFeedback = async (vote) => {
  if (problemDetail.value?.source_type !== 'ai_generated') return
  if (aiFeedbackSubmitting.value) return

  aiFeedbackSubmitting.value = vote
  try {
    const res = await api.post(`/api/ai/problems/${getProblemId()}/feedback`, { vote })
    if (res.code === 0) {
      aiFeedbackScore.value = res.data?.feedback_score ?? aiFeedbackScore.value
      aiFeedbackMessage.value = vote === 'up' ? '已标记有用' : '已标记无用'
    } else {
      aiFeedbackMessage.value = res.message || '反馈提交失败'
    }
  } catch (error) {
    aiFeedbackMessage.value = error.response?.data?.message || '反馈提交失败'
  } finally {
    aiFeedbackSubmitting.value = ''
  }
}

const resetCodeTemplate = () => {
  if (submitting.value) return
  const template = defaultCode[language.value] || ''
  if (userCode.value === template) return

  const shouldReset = window.confirm(
    t('确定恢复当前语言默认模板吗？当前代码会被覆盖。', 'Reset to default template for this language? Current code will be overwritten.')
  )
  if (shouldReset) {
    userCode.value = template
    judgeResult.value = null
  }
}

const goHome = () => {
  showSuccessModal.value = false
  router.push('/')
}

const goToSettings = () => {
  router.push('/settings')
}

const stayHere = () => {
  showSuccessModal.value = false
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

watch(language, (newLang) => {
  const problemId = getProblemId()
  loadDraftOrTemplate(problemId, newLang)
})

watch(userCode, () => {
  scheduleDraftSave()
})

watch(
  () => route.params.id,
  async (nextId, prevId) => {
    if (!nextId || nextId === prevId) return
    stopJobPolling()
    judgeResult.value = null
    showSuccessModal.value = false
    await loadProblem(nextId)
  }
)

watch(activeTab, (tab) => {
  if (tab === 'history') {
    loadSubmissionHistory(getProblemId())
  }
})

watch(
  [
    language,
    activeTab,
    customInput,
    mobileMainTab,
    editorPaneSize,
    resultPaneSize,
    selectedHistoryLeft,
    selectedHistoryRight,
  ],
  () => {
    persistWorkspaceViewState()
  }
)

const handleEditorMounted = (editor, monaco) => {
  if (!monaco || completionRegistered.value) return
  completionRegistered.value = true

  monaco.languages.registerCompletionItemProvider('python', {
    provideCompletionItems: () => ({
      suggestions: [
        {
          label: 'def',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'def ${1:function_name}(${2:params}):\n    ${3:pass}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: '定义函数',
          range: null
        },
        {
          label: 'for',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'for ${1:i} in range(${2:n}):\n    ${3:pass}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'for 循环',
          range: null
        },
        {
          label: 'ifmain',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'if __name__ == "__main__":\n    ${1:solution()}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: '主入口',
          range: null
        }
      ]
    })
  })

  monaco.languages.registerCompletionItemProvider('java', {
    provideCompletionItems: () => ({
      suggestions: [
        {
          label: 'main',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'public static void main(String[] args) {\n    ${1:// code}\n}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: '主函数',
          range: null
        },
        {
          label: 'for',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n    ${3:// code}\n}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'for 循环',
          range: null
        }
      ]
    })
  })
}

onMounted(() => {
  updateViewportState()
  window.addEventListener('resize', updateViewportState, { passive: true })
  window.addEventListener('pagehide', handlePageHide)
  document.addEventListener('visibilitychange', handleVisibilityChange)
  initTheme()
  loadRightLayoutPreference()
  loadProblem(getProblemId())
})

onBeforeUnmount(() => {
  handlePageHide()
  window.removeEventListener('resize', updateViewportState)
  window.removeEventListener('pagehide', handlePageHide)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  stopJobPolling()
  stopDraftTimer()
})
</script>

<style scoped>
.workspace-page {
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
  --hover: rgba(229, 214, 196, 0.32);
  --code-bg: #f6f1e9;
  --success-bg: rgba(75, 166, 116, 0.16);
  --success-text: #2b744a;
  --warn-bg: rgba(214, 145, 88, 0.2);
  --warn-text: #915929;
  --fail-bg: rgba(219, 86, 86, 0.16);
  --fail-text: #a03333;
  --neutral-bg: rgba(119, 129, 145, 0.16);
  --neutral-text: #4d596b;
  --editor-hero-bg: linear-gradient(155deg, rgba(255, 252, 246, 0.95) 0%, rgba(244, 235, 224, 0.9) 100%);
  --editor-wrap-border: rgba(149, 113, 74, 0.34);
  --editor-glow: rgba(199, 149, 97, 0.24);
  --shadow-shell: 0 34px 86px rgba(57, 44, 28, 0.16);
  --shadow-card: 0 22px 52px rgba(53, 40, 25, 0.12);
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

.workspace-page.theme-dark {
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
  --hover: rgba(52, 64, 82, 0.54);
  --code-bg: #121821;
  --success-bg: rgba(63, 152, 98, 0.24);
  --success-text: #8fd2ac;
  --warn-bg: rgba(209, 140, 63, 0.24);
  --warn-text: #e7bf8f;
  --fail-bg: rgba(199, 78, 78, 0.23);
  --fail-text: #f2a7a7;
  --neutral-bg: rgba(109, 123, 145, 0.24);
  --neutral-text: #b7c3d7;
  --editor-hero-bg: linear-gradient(158deg, rgba(30, 36, 47, 0.92) 0%, rgba(22, 28, 39, 0.94) 100%);
  --editor-wrap-border: rgba(115, 133, 165, 0.4);
  --editor-glow: rgba(114, 144, 197, 0.26);
  --shadow-shell: 0 34px 86px rgba(5, 8, 13, 0.5);
  --shadow-card: 0 22px 52px rgba(5, 8, 13, 0.35);
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

.workspace-shell {
  position: relative;
  z-index: 2;
  width: min(1420px, 100%);
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
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.brand-mark {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: #f8f5f0;
  font-weight: 700;
  letter-spacing: 0.2em;
  padding-left: 0.2em;
  background: linear-gradient(145deg, #211b16 0%, #42362c 100%);
  box-shadow: 0 12px 26px rgba(31, 25, 19, 0.25);
  flex-shrink: 0;
}

.workspace-page.theme-dark .brand-mark {
  background: linear-gradient(145deg, #2d3544 0%, #46516b 100%);
}

.title-wrap {
  min-width: 0;
}

.top-kicker {
  font-size: 11px;
  letter-spacing: 0.2em;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 700;
}

.title-wrap h1 {
  margin-top: 4px;
  font-size: clamp(1.1rem, 1.8vw, 1.45rem);
  letter-spacing: -0.02em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ghost-action {
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

.ghost-action:hover {
  border-color: var(--accent);
  color: var(--accent-strong);
}

.ghost-action.danger:hover {
  border-color: #bb5252;
  color: #bb5252;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 0;
  cursor: pointer;
  color: #fff;
  font-weight: 700;
  background: linear-gradient(145deg, #875c33 0%, #c18652 100%);
  box-shadow: 0 10px 20px rgba(86, 57, 30, 0.3);
  transition: transform 0.22s ease;
}

.avatar:hover {
  transform: scale(1.06);
}

.workspace-main {
  position: relative;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.mobile-switcher {
  display: none;
}

.mobile-switcher button {
  border: 0;
  background: transparent;
  color: var(--text-sub);
  height: 34px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mobile-switcher button.active {
  color: var(--accent-strong);
  background: var(--card-bg);
  border: 1px solid var(--line);
}

.loading-mask {
  position: absolute;
  inset: 0;
  z-index: 10;
  background: rgba(15, 20, 28, 0.4);
  backdrop-filter: blur(4px);
  display: grid;
  place-items: center;
  gap: 10px;
  color: #eef2f8;
}

.loading-mask p {
  font-size: 14px;
}

.loading-core {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: 4px solid rgba(255, 255, 255, 0.25);
  border-top-color: rgba(255, 255, 255, 0.95);
  animation: spin 0.9s linear infinite;
}

.loading-core.small {
  width: 36px;
  height: 36px;
  border-width: 3px;
}

.workspace-layout,
.left-layout,
.right-layout {
  height: 100%;
  min-height: 0;
}

:deep(.splitpanes__splitter) {
  background: var(--line);
  position: relative;
}

:deep(.splitpanes__splitter::before) {
  content: "";
  position: absolute;
  inset: 0;
  background: var(--accent);
  opacity: 0;
  transition: opacity 0.25s ease;
}

:deep(.splitpanes__splitter:hover::before) {
  opacity: 0.28;
}

:deep(.right-layout.splitpanes--horizontal > .splitpanes__splitter) {
  min-height: 12px;
  background: transparent;
  border-top: 1px solid var(--line-soft);
  border-bottom: 1px solid var(--line-soft);
}

:deep(.right-layout.splitpanes--horizontal > .splitpanes__splitter::after) {
  content: "";
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 68px;
  height: 4px;
  border-radius: 999px;
  background: var(--line);
  box-shadow: 0 4px 10px rgba(79, 55, 31, 0.16);
  transition: width 0.2s ease, background 0.2s ease;
}

:deep(.right-layout.splitpanes--horizontal > .splitpanes__splitter:hover::after) {
  width: 88px;
  background: var(--accent);
}

.problem-pane,
.editor-pane,
.result-pane {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--card-bg);
}

.problem-head {
  padding: 14px 16px;
  border-bottom: 1px solid var(--line);
}

.problem-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.ai-feedback {
  margin-top: 10px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.feedback-btn {
  border: 1px solid var(--line);
  background: var(--card-soft);
  color: var(--text-main);
  border-radius: 999px;
  height: 28px;
  padding: 0 12px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.feedback-btn:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent-strong);
}

.feedback-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.feedback-score,
.feedback-msg {
  font-size: 12px;
  color: var(--text-sub);
}

.difficulty-chip {
  border-radius: 999px;
  height: 28px;
  min-width: 64px;
  padding: 0 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.difficulty-chip.easy {
  background: var(--success-bg);
  color: var(--success-text);
}

.difficulty-chip.medium {
  background: var(--warn-bg);
  color: var(--warn-text);
}

.difficulty-chip.hard {
  background: var(--fail-bg);
  color: var(--fail-text);
}

.difficulty-chip.neutral {
  background: var(--neutral-bg);
  color: var(--neutral-text);
}

.source-chip {
  border-radius: 999px;
  padding: 0 10px;
  height: 26px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid transparent;
}

.source-chip.ai {
  border-color: rgba(101, 141, 205, 0.45);
  background: rgba(101, 141, 205, 0.14);
  color: #31588f;
}

.source-chip.official {
  border-color: rgba(182, 138, 84, 0.42);
  background: rgba(182, 138, 84, 0.14);
  color: #875121;
}

.source-chip.square {
  border-color: rgba(86, 124, 188, 0.42);
  background: rgba(86, 124, 188, 0.14);
  color: #2f5786;
}

.workspace-page.theme-dark .source-chip.ai {
  border-color: rgba(125, 158, 219, 0.5);
  background: rgba(90, 126, 190, 0.24);
  color: #bdd4ff;
}

.workspace-page.theme-dark .source-chip.official {
  border-color: rgba(212, 168, 113, 0.5);
  background: rgba(156, 118, 71, 0.24);
  color: #ffd8aa;
}

.workspace-page.theme-dark .source-chip.square {
  border-color: rgba(128, 166, 224, 0.5);
  background: rgba(88, 129, 187, 0.24);
  color: #bdd4ff;
}

.meta-item {
  border-radius: 999px;
  padding: 0 10px;
  height: 26px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--text-sub);
  background: var(--card-soft);
}

.problem-description {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 16px;
}

.problem-markdown {
  color: var(--text-main);
  line-height: 1.8;
}

:deep(.problem-markdown h1),
:deep(.problem-markdown h2),
:deep(.problem-markdown h3),
:deep(.problem-markdown h4) {
  margin-top: 1.2em;
  margin-bottom: 0.55em;
  color: var(--text-main);
  line-height: 1.3;
}

:deep(.problem-markdown p) {
  margin: 0 0 1em;
}

:deep(.problem-markdown code) {
  border: 1px solid var(--line-soft);
  background: var(--card-soft);
  border-radius: 6px;
  padding: 0.15em 0.45em;
  font-size: 0.88em;
}

:deep(.problem-markdown pre) {
  margin: 1em 0;
  border: 1px solid var(--line);
  background: var(--code-bg);
  border-radius: 12px;
  padding: 12px;
  overflow-x: auto;
}

:deep(.problem-markdown pre code) {
  border: 0;
  background: transparent;
  padding: 0;
}

:deep(.problem-markdown a) {
  color: var(--accent-strong);
}

:deep(.problem-markdown blockquote) {
  border-left: 3px solid var(--line);
  margin: 1em 0;
  padding: 0.5em 0 0.5em 1em;
  color: var(--text-sub);
}

.empty-copy {
  height: 100%;
  display: grid;
  place-items: center;
  color: var(--text-sub);
}

.testcase-panel {
  border-top: 1px solid var(--line);
  background: var(--card-soft);
}

.section-head {
  padding: 12px 16px;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-head p {
  font-size: 13px;
  font-weight: 700;
}

.section-head span {
  font-size: 12px;
  color: var(--text-sub);
}

.testcase-list {
  max-height: 210px;
  overflow: auto;
}

.testcase-item {
  padding: 12px 16px;
  border-bottom: 1px solid var(--line-soft);
}

.testcase-item:last-child {
  border-bottom: 0;
}

.testcase-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.testcase-title span {
  font-size: 12px;
  font-weight: 700;
}

.testcase-title b {
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  height: 22px;
  padding: 0 9px;
  display: inline-flex;
  align-items: center;
  background: var(--success-bg);
  color: var(--success-text);
}

.testcase-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.testcase-grid p {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 5px;
}

.testcase-grid pre {
  margin: 0;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--code-bg);
  padding: 8px;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.ai-panel {
  height: 100%;
  min-height: 0;
  border-top: 1px solid var(--line);
}

.editor-pane {
  position: relative;
}

.editor-hero {
  border-bottom: 1px solid var(--line);
  padding: 14px 16px 12px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  background: var(--editor-hero-bg);
}

.hero-copy {
  min-width: 0;
}

.editor-kicker {
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 700;
}

.hero-copy h3 {
  margin-top: 4px;
  font-size: 1.02rem;
  letter-spacing: -0.01em;
}

.hero-copy p {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-sub);
}

.editor-meta {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-chip {
  height: 24px;
  border-radius: 999px;
  padding: 0 10px;
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  font-weight: 700;
  border: 1px solid var(--line);
  background: var(--card-bg);
  color: var(--text-sub);
}

.editor-toolbar {
  border-bottom: 1px solid var(--line);
  padding: 10px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: var(--card-soft);
}

.language-picker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.language-picker label {
  font-size: 12px;
  color: var(--text-sub);
  font-weight: 700;
  letter-spacing: 0.06em;
}

.language-picker select {
  appearance: none;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--card-bg);
  color: var(--text-main);
  height: 34px;
  padding: 0 28px 0 10px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.22s ease, box-shadow 0.22s ease;
}

.language-picker select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(154, 109, 63, 0.14);
}

.editor-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.custom-input-wrap {
  border-bottom: 1px solid var(--line);
  padding: 10px 14px;
  display: grid;
  gap: 8px;
  background: var(--card-bg);
}

.custom-input-wrap label {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-sub);
}

.custom-input-wrap textarea {
  width: 100%;
  min-height: 74px;
  resize: vertical;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--card-soft);
  color: var(--text-main);
  font-size: 12px;
  line-height: 1.5;
  padding: 9px 10px;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.custom-input-wrap textarea:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(154, 109, 63, 0.13);
}

.action-btn {
  border: 0;
  height: 36px;
  border-radius: 10px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  cursor: pointer;
  transition: transform 0.22s ease, opacity 0.22s ease, box-shadow 0.22s ease;
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.action-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.action-btn.plain {
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-main);
}

.action-btn.plain:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent-strong);
  box-shadow: none;
}

.btn-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.46);
  animation: dot-pulse 1.9s ease-in-out infinite;
}

.action-btn.run {
  background: linear-gradient(145deg, #4f865e 0%, #68ab78 100%);
  color: #fff;
  box-shadow: 0 10px 18px rgba(47, 112, 72, 0.22);
}

.action-btn.submit {
  background: linear-gradient(145deg, #83552b 0%, #ab7543 100%);
  color: #fff;
  box-shadow: 0 10px 20px rgba(105, 68, 35, 0.24);
}

.editor-wrap {
  flex: 1;
  min-height: 0;
  margin: 12px;
  position: relative;
  border-radius: 14px;
  border: 1px solid var(--editor-wrap-border);
  overflow: hidden;
  background: var(--code-bg);
  box-shadow: 0 18px 34px rgba(42, 30, 18, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.22);
}

.editor-glow {
  position: absolute;
  top: -78px;
  left: 14%;
  width: 56%;
  height: 140px;
  border-radius: 50%;
  background: var(--editor-glow);
  filter: blur(32px);
  pointer-events: none;
  z-index: 0;
}

.editor-wrap :deep(.monaco-editor),
.editor-wrap :deep(.overflow-guard) {
  position: relative;
  z-index: 1;
}

.editor-footnote {
  border-top: 1px solid var(--line);
  padding: 8px 14px 10px;
  font-size: 11px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  background: var(--card-soft);
}

.foot-divider {
  width: 1px;
  height: 12px;
  background: var(--line);
}

.result-tabs {
  border-bottom: 1px solid var(--line);
  padding: 8px;
  display: flex;
  gap: 8px;
  background: var(--card-soft);
}

.result-tabs button {
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-sub);
  height: 34px;
  padding: 0 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.22s ease;
}

.result-tabs button.active {
  border-color: var(--line);
  background: var(--card-bg);
  color: var(--text-main);
}

.result-body {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 12px;
}

.placeholder {
  height: 100%;
  min-height: 180px;
  border: 1px dashed var(--line);
  border-radius: 12px;
  display: grid;
  place-items: center;
  gap: 10px;
  text-align: center;
  color: var(--text-sub);
  padding: 16px;
}

.placeholder.compact {
  min-height: 120px;
}

.queue-progress {
  width: min(420px, 100%);
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
  background: var(--line-soft);
}

.queue-progress-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #5a8fd1 0%, #7f6fde 100%);
  transition: width 0.3s ease;
}

.queue-meta {
  font-size: 12px;
  color: var(--text-muted);
}

.result-content {
  display: grid;
  gap: 10px;
}

.history-panel {
  display: grid;
  gap: 10px;
}

.history-toolbar {
  display: flex;
  justify-content: flex-end;
}

.history-content {
  display: grid;
  gap: 10px;
  grid-template-columns: 260px minmax(0, 1fr);
}

.history-list {
  display: grid;
  gap: 8px;
  max-height: 420px;
  overflow: auto;
}

.history-item {
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--card-soft);
  padding: 10px;
  display: grid;
  gap: 8px;
}

.history-item header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.history-meta {
  font-size: 11px;
  color: var(--text-sub);
}

.history-actions {
  display: flex;
  gap: 8px;
}

.mini-btn {
  border: 1px solid var(--line);
  height: 28px;
  border-radius: 8px;
  background: transparent;
  color: var(--text-main);
  font-size: 12px;
  font-weight: 700;
  padding: 0 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mini-btn:hover {
  border-color: var(--accent);
  color: var(--accent-strong);
}

.compare-box {
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--card-soft);
  padding: 10px;
  display: grid;
  gap: 10px;
  min-width: 0;
}

.compare-select {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.compare-select label {
  display: grid;
  gap: 6px;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-sub);
}

.compare-select select {
  border: 1px solid var(--line);
  height: 32px;
  border-radius: 8px;
  background: var(--card-bg);
  color: var(--text-main);
  padding: 0 8px;
  outline: none;
}

.compare-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  min-width: 0;
}

.compare-code {
  border: 1px solid var(--line-soft);
  border-radius: 10px;
  overflow: hidden;
  min-width: 0;
}

.compare-head {
  height: 34px;
  padding: 0 10px;
  border-bottom: 1px solid var(--line-soft);
  background: var(--card-bg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-sub);
}

.compare-code pre {
  margin: 0;
  padding: 10px;
  min-height: 260px;
  max-height: 420px;
  overflow: auto;
  background: var(--code-bg);
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
  line-height: 1.5;
}

.summary-card {
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--card-soft);
  padding: 12px;
}

.summary-card header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-card header p {
  font-size: 13px;
  color: var(--text-main);
}

.summary-card.pass {
  border-color: rgba(75, 166, 116, 0.36);
}

.summary-card.warn {
  border-color: rgba(214, 145, 88, 0.4);
}

.summary-card.fail {
  border-color: rgba(219, 86, 86, 0.38);
}

.summary-card.neutral {
  border-color: var(--line);
}

.status-pill {
  border-radius: 999px;
  height: 26px;
  min-width: 50px;
  padding: 0 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.status-pill.pass {
  background: var(--success-bg);
  color: var(--success-text);
}

.status-pill.warn {
  background: var(--warn-bg);
  color: var(--warn-text);
}

.status-pill.fail {
  background: var(--fail-bg);
  color: var(--fail-text);
}

.status-pill.neutral {
  background: var(--neutral-bg);
  color: var(--neutral-text);
}

.summary-metrics {
  margin-top: 10px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.summary-metrics span {
  height: 24px;
  border-radius: 999px;
  padding: 0 10px;
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  color: var(--text-sub);
  background: var(--card-bg);
  border: 1px solid var(--line-soft);
}

.output-card {
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--card-soft);
  padding: 12px;
}

.output-label {
  font-size: 12px;
  color: var(--text-sub);
  margin-bottom: 8px;
}

.output-card pre {
  margin: 0;
  border: 1px solid var(--line-soft);
  border-radius: 10px;
  background: var(--code-bg);
  padding: 10px;
  min-height: 72px;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
  line-height: 1.5;
}

.detail-list {
  display: grid;
  gap: 10px;
}

.detail-item {
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--card-soft);
  padding: 12px;
}

.detail-item.pass {
  border-color: rgba(75, 166, 116, 0.34);
}

.detail-item.fail {
  border-color: rgba(219, 86, 86, 0.32);
}

.detail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-head p {
  font-size: 13px;
  font-weight: 700;
}

.detail-head span {
  border-radius: 999px;
  height: 22px;
  padding: 0 10px;
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  font-weight: 700;
  background: var(--neutral-bg);
  color: var(--neutral-text);
}

.detail-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.detail-grid p,
.detail-extra p {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 5px;
}

.detail-grid pre,
.detail-extra pre {
  margin: 0;
  border: 1px solid var(--line-soft);
  border-radius: 10px;
  background: var(--code-bg);
  padding: 8px;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-extra {
  margin-top: 8px;
}

.detail-extra.error pre {
  border-color: rgba(219, 86, 86, 0.3);
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(14, 18, 24, 0.56);
  backdrop-filter: blur(4px);
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal-card {
  width: min(420px, 100%);
  border-radius: 20px;
  border: 1px solid var(--line);
  background: var(--card-bg);
  box-shadow: var(--shadow-card);
  padding: 22px;
  text-align: center;
}

.modal-badge {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  margin: 0 auto 10px;
  display: grid;
  place-items: center;
  font-size: 18px;
  font-weight: 800;
  background: var(--success-bg);
  color: var(--success-text);
}

.modal-card h3 {
  font-size: 1.25rem;
  letter-spacing: -0.02em;
}

.modal-card p {
  margin-top: 6px;
  color: var(--text-sub);
  font-size: 14px;
}

.modal-actions {
  margin-top: 14px;
  display: grid;
  gap: 8px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.22s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
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

@keyframes dot-pulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.45);
    transform: scale(0.95);
  }
  50% {
    box-shadow: 0 0 0 7px rgba(255, 255, 255, 0);
    transform: scale(1.08);
  }
}

@media (max-width: 1120px) {
  .workspace-page {
    padding: 12px;
  }

  .workspace-shell {
    min-height: calc(100vh - 24px);
    border-radius: 20px;
  }

  .topbar {
    flex-wrap: wrap;
  }

  .topbar-actions {
    width: 100%;
    justify-content: flex-end;
    flex-wrap: wrap;
  }

  .ghost-action {
    height: 34px;
    padding: 0 10px;
    font-size: 12px;
  }
}

@media (max-width: 820px) {
  .bg-orb {
    display: none;
  }

  .workspace-shell {
    backdrop-filter: none;
  }

  .topbar-actions .ghost-action {
    display: none;
  }

  .topbar-actions .ghost-action.danger {
    display: inline-flex;
  }

  .workspace-shell {
    grid-template-rows: auto 1fr;
  }

  .workspace-main {
    overflow: auto;
    display: grid;
    grid-template-rows: auto 1fr;
    gap: 8px;
    padding: 8px;
  }

  .mobile-switcher {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 6px;
    border: 1px solid var(--line);
    background: var(--card-soft);
    border-radius: 12px;
    padding: 5px;
  }

  .workspace-layout {
    height: auto;
    min-height: 0;
  }

  .testcase-grid,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  :deep(.workspace-layout > .splitpanes__splitter) {
    display: none;
  }

  .editor-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .history-content,
  .compare-grid,
  .compare-select {
    grid-template-columns: 1fr;
  }

  .editor-hero {
    flex-direction: column;
  }

  .editor-meta {
    justify-content: flex-start;
  }

  .editor-actions {
    justify-content: stretch;
    flex-wrap: wrap;
  }

  .editor-actions .action-btn {
    flex: 1;
    min-width: 120px;
  }

  .problem-description,
  .result-body,
  .testcase-list,
  .history-list,
  .compare-code pre {
    max-height: none;
  }
}
</style>
