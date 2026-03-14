<template>
  <div class="home-page" :class="{ 'theme-dark': isDark }">
    <div class="bg-orb orb-a"></div>
    <div class="bg-orb orb-b"></div>
    <div class="bg-grid"></div>

    <main class="dashboard-shell">
      <aside class="side-panel">
        <div class="side-brand">
          <div class="logo">LC</div>
          <div>
            <p class="brand-name">LC JUDGE</p>
            <p class="brand-sub">算法练习平台</p>
          </div>
        </div>

        <nav class="side-nav">
          <button
            type="button"
            class="nav-item"
            :class="{ 'nav-item-active': activePanel === 'problems' }"
            @click="setActivePanel('problems')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <span>题库列表</span>
          </button>

          <button
            type="button"
            class="nav-item"
            :class="{ 'nav-item-active': activePanel === 'ai' }"
            @click="setActivePanel('ai')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18l-.813-2.096a2.25 2.25 0 00-1.288-1.288L4.803 13.5l2.096-.813a2.25 2.25 0 001.288-1.288L9 9.303l.813 2.096a2.25 2.25 0 001.288 1.288l2.096.813-2.096.813a2.25 2.25 0 00-1.288 1.288zM18.259 8.715L18 9.75l-.259-1.035a1.875 1.875 0 00-1.355-1.355L15.352 7.1l1.034-.259a1.875 1.875 0 001.355-1.355L18 4.453l.259 1.033a1.875 1.875 0 001.355 1.355l1.034.259-1.034.26a1.875 1.875 0 00-1.355 1.355zM16.5 20.25h-9A2.25 2.25 0 015.25 18V9a2.25 2.25 0 012.25-2.25h9A2.25 2.25 0 0118.75 9v9a2.25 2.25 0 01-2.25 2.25z" />
            </svg>
            <span>AI 出题</span>
          </button>

          <button
            type="button"
            class="nav-item"
            :class="{ 'nav-item-active': activePanel === 'square' }"
            @click="setActivePanel('square')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 9.75h16.5m-16.5 4.5h16.5m-16.5 4.5h10.5m-8.25-13.5h12a2.25 2.25 0 012.25 2.25v10.5A2.25 2.25 0 0118 20.25H6a2.25 2.25 0 01-2.25-2.25V7.5A2.25 2.25 0 016 5.25z" />
            </svg>
            <span>题目广场</span>
          </button>

          <button
            type="button"
            class="nav-item"
            :class="{ 'nav-item-active': activePanel === 'wrongbook' }"
            @click="setActivePanel('wrongbook')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 3.75v16.5M7.5 3.75v16.5M3.75 7.5h16.5M3.75 16.5h16.5" />
            </svg>
            <span>{{ t('错题复习', 'Wrong Book') }}</span>
          </button>

          <button
            type="button"
            class="nav-item"
            :class="{ 'nav-item-active': activePanel === 'profile' }"
            @click="setActivePanel('profile')"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
            </svg>
            <span>个人资料</span>
          </button>

          <button type="button" class="nav-item logout-item" @click="handleLogout">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
            </svg>
            <span>退出登录</span>
          </button>
        </nav>

        <button type="button" class="theme-toggle" @click="toggleTheme">
          <svg v-if="isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
          </svg>
          <span>{{ isDark ? '切换浅色' : '切换深色' }}</span>
        </button>
      </aside>

      <section class="main-panel">
        <header class="top-bar">
          <div class="headline">
            <p class="headline-kicker">{{ headlineKicker }}</p>
            <h1>欢迎回来，{{ username }}</h1>
            <p class="headline-sub">{{ headlineSub }}</p>
          </div>

          <div class="top-actions">
            <button type="button" class="ghost-action" @click="goToSettings">个人设置</button>
            <button type="button" class="avatar" @click="goToSettings">{{ userInitial }}</button>
          </div>
        </header>

        <div class="content-wrap">
          <section v-if="activePanel === 'problems'" class="stats-grid">
            <article class="stat-card">
              <p>题库已通过</p>
              <strong>{{ animatedPassed }}</strong>
              <span class="stat-tag success">AC</span>
            </article>

            <article class="stat-card">
              <p>题库总题</p>
              <strong>{{ animatedTotal }}</strong>
              <span class="stat-tag neutral">All</span>
            </article>

            <article class="stat-card">
              <p>题库完成率</p>
              <strong>{{ animatedRate }}%</strong>
              <div class="progress-track">
                <div class="progress-fill" :style="{ width: progressWidth }"></div>
              </div>
            </article>

            <article class="stat-card">
              <p>题库待完成</p>
              <strong>{{ animatedRemaining }}</strong>
              <span class="stat-tag warning">Todo</span>
            </article>
          </section>

          <transition name="panel-switch" mode="out-in">
            <section v-if="activePanel === 'ai'" key="panel-ai" class="ai-lab-panel">
            <div class="ai-lab-head">
              <div>
                <p class="panel-kicker">AI Practice Generator</p>
                <h2>AI 出题</h2>
                <p class="panel-sub">可按刷题进度估计水平，或手动设定 1-10 级难度。</p>
              </div>
            </div>

            <div class="ai-mode-switch">
              <button
                type="button"
                :class="{ active: aiMode === 'progress' }"
                @click="setAiMode('progress')"
              >
                按进度估计
              </button>
              <button
                type="button"
                :class="{ active: aiMode === 'custom' }"
                @click="setAiMode('custom')"
              >
                自定义难度
              </button>
            </div>

            <div class="ai-controls">
              <div v-if="aiMode === 'progress'" class="ai-mode-box">
                <p>系统会基于你的 AC 题量、完成率和难度分布估计等级后出题。</p>
              </div>
              <div v-else class="ai-mode-box custom">
                <label>难度等级（1-10）</label>
                <div class="level-control">
                  <button type="button" @click="changeCustomLevel(-1)">-</button>
                  <input v-model.number="customLevel" type="range" min="1" max="10" step="1" />
                  <button type="button" @click="changeCustomLevel(1)">+</button>
                  <span>L{{ customLevel }}</span>
                </div>
                <p class="level-hint">{{ levelHint }}</p>
              </div>
            </div>

            <div class="ai-generate-row">
              <button type="button" class="action-btn primary" :disabled="aiGenerating" @click="generateAiProblem">
                {{ aiGenerating ? 'AI 出题中...' : '生成新题' }}
              </button>
              <button
                v-if="generatedProblem?.problem?.id"
                type="button"
                class="action-btn secondary"
                @click="startGeneratedProblem"
              >
                立即做题
              </button>
              <button type="button" class="action-btn secondary" @click="goToProblemList">
                前往题库列表
              </button>
            </div>

            <transition name="status-fade">
              <article v-if="aiProgressVisible" class="ai-progress-card" :class="`state-${aiProgressState}`">
                <div class="ai-progress-head">
                  <span>{{ aiProgressLabel }}</span>
                  <b>{{ aiProgress }}%</b>
                </div>
                <p class="ai-progress-meta">已耗时 {{ aiProgressElapsedSeconds }}s</p>
                <div class="ai-progress-track">
                  <div class="ai-progress-fill" :style="{ width: `${aiProgress}%` }"></div>
                </div>
              </article>
            </transition>

            <transition name="status-fade">
              <p v-if="aiStatusMessage" class="ai-status" :class="aiStatusType">
                {{ aiStatusMessage }}
              </p>
            </transition>

            <article v-if="generatedProblem?.problem" class="ai-result-card">
              <div class="ai-result-head">
                <h3>{{ generatedProblem.problem.title }}</h3>
                <div class="ai-result-tags">
                  <span class="source-tag ai">AI 私有</span>
                  <span class="difficulty-badge" :class="difficultyClass(generatedProblem.problem.difficulty)">
                    {{ difficultyText(generatedProblem.problem.difficulty) }}
                  </span>
                </div>
              </div>
              <p class="ai-result-desc">{{ generatedProblem.problem.description_preview }}</p>
              <div class="ai-result-meta">
                <span>等级 L{{ generatedProblem.generated_level }}</span>
                <span>{{ generatedProblem.level_reason }}</span>
              </div>
            </article>
            </section>

            <section v-else-if="activePanel === 'square'" key="panel-square" class="square-panel">
            <div class="panel-head">
              <div>
                <p class="panel-kicker">Square</p>
                <h2>题目广场</h2>
                <p class="panel-sub">分享你已通过的 AI 私有题，也可以把别人的优质题导入到自己的题库。</p>
              </div>
              <button type="button" class="action-btn secondary" @click="loadSquareProblems">
                刷新广场
              </button>
            </div>

            <transition name="status-fade">
              <p v-if="squareStatusMessage" class="square-status" :class="squareStatusType">
                {{ squareStatusMessage }}
              </p>
            </transition>

            <div class="square-wrap">
              <div class="square-toolbar">
                <div class="square-view-tabs">
                  <button
                    type="button"
                    :class="{ active: squareViewTab === 'square' }"
                    @click="squareViewTab = 'square'"
                  >
                    广场
                    <b>{{ squarePublicItems.length }}</b>
                  </button>
                  <button
                    type="button"
                    :class="{ active: squareViewTab === 'mine' }"
                    @click="squareViewTab = 'mine'"
                  >
                    我的分享
                    <b>{{ mySharedItems.length }}</b>
                  </button>
                </div>

                <label class="square-sort">
                  <span>排序</span>
                  <select v-model="squareSortBy">
                    <option value="stars">Star 数</option>
                    <option value="latest">发布日期</option>
                  </select>
                </label>
              </div>

              <div v-if="squareLoading" class="skeleton-wrap">
                <div v-for="i in 4" :key="`square-skeleton-${i}`" class="square-skeleton-card">
                  <span class="skeleton skeleton-lg"></span>
                  <span class="skeleton skeleton-md"></span>
                  <span class="skeleton skeleton-btn"></span>
                </div>
              </div>

              <div v-else-if="activeSquareItems.length === 0" class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.153-.439 1.592 0L21.75 12M4.5 9.75V19.5a2.25 2.25 0 002.25 2.25h10.5a2.25 2.25 0 002.25-2.25V9.75M9 21.75V15a3 3 0 013-3h0a3 3 0 013 3v6.75" />
                </svg>
                <p>{{ squareEmptyText }}</p>
              </div>

              <div v-else class="square-list">
                <article
                  v-for="item in activeSquareItems"
                  :key="item.id"
                  class="square-card"
                >
                  <div class="square-card-head">
                    <div class="square-title-wrap">
                      <h3>{{ item.title }}</h3>
                      <div class="square-tags">
                        <span class="difficulty-badge" :class="difficultyClass(item.difficulty)">
                          {{ difficultyText(item.difficulty) }}
                        </span>
                        <span class="source-tag ai">广场共享</span>
                      </div>
                    </div>
                    <div class="square-meta">
                      <span class="square-owner">分享者：{{ item.owner_username }}</span>
                      <div class="square-meta-metrics">
                        <span>已导入：{{ item.import_count }}</span>
                        <span>Star：{{ item.star_count || 0 }}</span>
                        <span>发布：{{ formatSquareDate(item.created_at) }}</span>
                      </div>
                    </div>
                  </div>

                  <p class="square-desc">{{ item.description_preview || '暂无题干预览' }}</p>

                  <div class="square-actions">
                    <template v-if="squareViewTab === 'mine'">
                      <button
                        type="button"
                        class="action-btn secondary"
                        @click="goToDiscuss(item.problem_id)"
                      >
                        讨论
                      </button>
                      <button
                        type="button"
                        class="action-btn secondary"
                        @click="goToWorkspace(item.problem_id)"
                      >
                        查看题目
                      </button>
                      <button
                        type="button"
                        class="action-btn danger"
                        :disabled="unsharingShareId === item.id"
                        @click="handleUnshareProblem(item)"
                      >
                        {{ unsharingShareId === item.id ? '取消中...' : '取消分享' }}
                      </button>
                    </template>
                    <template v-else>
                      <button
                        type="button"
                        class="action-btn star"
                        :disabled="starringShareId === item.id || item.is_starred"
                        @click="handleStarSquareProblem(item)"
                      >
                        {{
                          starringShareId === item.id
                            ? 'Star 中...'
                            : item.is_starred
                              ? '已 Star'
                            : 'Star'
                        }}
                      </button>
                      <button
                        type="button"
                        class="action-btn secondary"
                        @click="goToDiscuss(item.problem_id)"
                      >
                        讨论
                      </button>
                      <button
                        v-if="item.is_imported && item.imported_problem_id"
                        type="button"
                        class="action-btn secondary"
                        @click="goToWorkspace(item.imported_problem_id)"
                      >
                        前往我的题库做题
                      </button>
                      <button
                        v-else
                        type="button"
                        class="action-btn primary"
                        :disabled="importingShareId === item.id || !item.can_import"
                        @click="handleImportSquareProblem(item)"
                      >
                        {{
                          importingShareId === item.id
                            ? '导入中...'
                            : item.is_owner
                              ? '本人已分享'
                              : item.is_imported
                                ? '已导入'
                                : '导入到我的题库'
                        }}
                      </button>
                    </template>
                  </div>
                </article>
              </div>
            </div>
            </section>

            <section v-else-if="activePanel === 'wrongbook'" key="panel-wrongbook" class="wrongbook-panel">
            <div class="panel-head">
              <div>
                <p class="panel-kicker">Wrong Book</p>
                <h2>{{ t('错题本复习', 'Wrong Book Review') }}</h2>
                <p class="panel-sub">{{ t('按知识点复盘错题，支持到期提醒和二刷节奏管理。', 'Review mistakes by knowledge tags with due reminders and second-pass planning.') }}</p>
              </div>
              <button type="button" class="action-btn secondary" @click="loadWrongBook">
                {{ t('刷新错题本', 'Refresh') }}
              </button>
            </div>

            <div class="wrongbook-controls">
              <label>
                {{ t('知识点', 'Tag') }}
                <input
                  v-model.trim="wrongBookTag"
                  type="text"
                  :placeholder="t('例如：动态规划', 'e.g. dynamic programming')"
                />
              </label>
              <label class="checkbox">
                <input v-model="wrongBookDueOnly" type="checkbox" />
                {{ t('仅到期复习', 'Due only') }}
              </label>
              <button type="button" class="action-btn primary" @click="loadWrongBook">
                {{ t('应用筛选', 'Apply') }}
              </button>
            </div>

            <transition name="status-fade">
              <p v-if="wrongBookStatusMessage" class="square-status" :class="wrongBookStatusType">
                {{ wrongBookStatusMessage }}
              </p>
            </transition>

            <div v-if="wrongBookLoading" class="skeleton-wrap">
              <div v-for="i in 3" :key="`wrong-skeleton-${i}`" class="square-skeleton-card">
                <span class="skeleton skeleton-lg"></span>
                <span class="skeleton skeleton-md"></span>
                <span class="skeleton skeleton-btn"></span>
              </div>
            </div>

            <div v-else-if="wrongBookItems.length === 0" class="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9.568 3.75h4.864A2.568 2.568 0 0117 6.318v11.364a2.568 2.568 0 01-2.568 2.568H9.568A2.568 2.568 0 017 17.682V6.318A2.568 2.568 0 019.568 3.75z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 8.25h6M9 12h6M9 15.75h3.75" />
              </svg>
              <p>{{ t('暂无可复习错题', 'No review items') }}</p>
            </div>

            <div v-else class="wrongbook-list">
              <article
                v-for="item in wrongBookItems"
                :key="item.problem_id"
                class="wrongbook-card"
              >
                <div class="wrongbook-head">
                  <h3>{{ item.title }}</h3>
                  <span class="difficulty-badge" :class="difficultyClass(item.difficulty)">
                    {{ difficultyText(item.difficulty) }}
                  </span>
                </div>

                <p class="wrongbook-meta">
                  {{ t('错误', 'Wrong') }} {{ item.wrong_count }} {{ t('次', 'times') }} ·
                  {{ t('复习', 'Reviewed') }} {{ item.review_count }} {{ t('次', 'times') }} ·
                  {{ t('下次复习', 'Next review') }} {{ formatWrongBookDate(item.next_review_at) }}
                </p>

                <div class="wrongbook-tags">
                  <span v-for="tag in item.knowledge_tags" :key="`${item.problem_id}-${tag}`">{{ tag }}</span>
                </div>

                <div class="wrongbook-actions">
                  <button type="button" class="action-btn secondary" @click="goToWorkspace(item.problem_id)">
                    {{ t('去做题', 'Solve') }}
                  </button>
                  <button type="button" class="action-btn primary" @click="markWrongProblemReviewed(item.problem_id)">
                    {{ t('标记已复习', 'Mark reviewed') }}
                  </button>
                </div>
              </article>
            </div>
            </section>

            <section v-else-if="activePanel === 'profile'" key="panel-profile" class="profile-panel">
            <div class="panel-head profile-head">
              <div>
                <p class="panel-kicker">Profile</p>
                <h2>个人资料</h2>
                <p class="panel-sub">这里展示你的账号信息，点击右上角可进入详细设置。</p>
              </div>
              <button type="button" class="action-btn secondary" @click="goToSettings">
                前往个人设置
              </button>
            </div>

            <div class="profile-body">
              <article class="profile-hero">
                <div class="profile-hero-avatar">{{ userInitial }}</div>
                <div class="profile-hero-text">
                  <h3>{{ username }}</h3>
                  <p>{{ userStore.user?.email || '未绑定邮箱' }}</p>
                </div>
              </article>

              <div class="profile-grid">
                <article class="profile-info-card">
                  <p>用户名</p>
                  <strong>{{ userStore.user?.username || '--' }}</strong>
                </article>
                <article class="profile-info-card">
                  <p>邮箱</p>
                  <strong>{{ userStore.user?.email || '--' }}</strong>
                </article>
                <article class="profile-info-card">
                  <p>用户角色</p>
                  <strong>{{ userRoleText }}</strong>
                </article>
                <article class="profile-info-card">
                  <p>账号状态</p>
                  <strong>{{ accountStatusText }}</strong>
                </article>
              </div>
            </div>
            </section>

            <section v-else key="panel-problems" class="problem-panel">
            <div class="panel-head">
              <div>
                <p class="panel-kicker">Problems</p>
                <h2>题库列表</h2>
                <p class="panel-sub">
                  {{ t('按难度筛选并快速进入做题，讨论在广场进行。', 'Filter by difficulty and start solving quickly. Discussions are in Square.') }}
                </p>
              </div>
              <div class="panel-controls">
                <div class="source-tabs" role="tablist" aria-label="题目来源切换">
                  <button
                    type="button"
                    class="source-tab"
                    :class="{ active: problemSourceTab === 'official' }"
                    @click="problemSourceTab = 'official'"
                  >
                    题库题
                    <b>{{ officialProblems.length }}</b>
                  </button>
                  <button
                    type="button"
                    class="source-tab"
                    :class="{ active: problemSourceTab === 'personal' }"
                    @click="problemSourceTab = 'personal'"
                  >
                    AI 私有题
                    <b>{{ personalProblems.length }}</b>
                  </button>
                </div>

                <div class="filter-box">
                  <label for="difficulty-select">难度</label>
                  <select id="difficulty-select" v-model="difficultyFilter">
                    <option value="">全部难度</option>
                    <option value="Easy">简单</option>
                    <option value="Medium">中等</option>
                    <option value="Hard">困难</option>
                  </select>
                </div>
              </div>
            </div>

            <transition name="status-fade">
              <article
                v-if="listGeneratingHintVisible"
                class="generation-hint"
                role="status"
                aria-live="polite"
              >
                <span class="generation-dot"></span>
                <strong>当前正在 AI 生题中</strong>
                <span class="generation-detail">{{ listGeneratingHintText }}</span>
                <b>{{ aiProgress }}%</b>
              </article>
            </transition>

            <div class="table-wrap">
              <div v-if="loading" class="skeleton-wrap">
                <div v-for="i in 6" :key="`skeleton-${i}`" class="skeleton-row">
                  <span class="skeleton skeleton-sm"></span>
                  <span class="skeleton skeleton-lg"></span>
                  <span class="skeleton skeleton-md"></span>
                  <span class="skeleton skeleton-btn"></span>
                </div>
              </div>

              <div v-else-if="activeProblems.length === 0" class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p>{{ activeSourceEmptyText }}</p>
              </div>

              <div v-else class="problem-table">
                <div class="table-head">
                  <span>#</span>
                  <span>标题</span>
                  <span>难度</span>
                  <span>操作</span>
                </div>

                <transition-group name="row-fade" tag="div" class="table-body">
                  <div
                    v-for="(problem, index) in activeProblems"
                    :key="problem.id"
                    class="table-row"
                    @click="goToWorkspace(problem.id)"
                  >
                    <span class="col-index">{{ String(index + 1).padStart(2, '0') }}</span>
                    <div class="col-title">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
                      </svg>
                      <div class="title-text">
                        <div class="title-main">
                          <span
                            v-if="problem.is_passed"
                            class="pass-flag"
                            title="已通过"
                            aria-label="已通过"
                          >
                            ✓
                          </span>
                          <span class="problem-title">{{ problem.title }}</span>
                        </div>
                        <span class="source-tag" :class="problemSourceTagClass">
                          {{ problemSourceTagText }}
                        </span>
                        <span v-if="problem.is_square_imported" class="source-tag square">
                          广场导入
                        </span>
                      </div>
                    </div>
                    <span class="difficulty-badge" :class="difficultyClass(problem.difficulty)">
                      {{ difficultyText(problem.difficulty) }}
                    </span>
                    <div class="col-actions">
                      <button type="button" class="action-btn primary" @click.stop="goToWorkspace(problem.id)">做题</button>
                      <button
                        v-if="problemSourceTab === 'official'"
                        type="button"
                        class="action-btn secondary"
                        @click.stop="goToDiscuss(problem.id)"
                      >
                        讨论
                      </button>
                      <button
                        v-if="problemSourceTab === 'personal'"
                        type="button"
                        class="action-btn tertiary"
                        :disabled="sharingProblemId === problem.id || !problem.is_passed || problem.is_shared"
                        @click.stop="handleShareProblem(problem)"
                      >
                        {{
                          problem.is_shared
                            ? '已分享'
                            : sharingProblemId === problem.id
                              ? '分享中...'
                              : problem.is_passed
                                ? '分享到广场'
                                : '先通过再分享'
                        }}
                      </button>
                      <button
                        v-if="problemSourceTab === 'personal'"
                        type="button"
                        class="action-btn danger"
                        :disabled="deletingProblemId === problem.id"
                        @click.stop="handleDeleteProblem(problem)"
                      >
                        {{ deletingProblemId === problem.id ? '删除中...' : '删除' }}
                      </button>
                    </div>
                  </div>
                </transition-group>
              </div>
            </div>
            </section>
          </transition>
        </div>
      </section>
    </main>

    <nav v-if="isMobileViewport" class="mobile-bottom-nav" aria-label="移动端底部导航">
      <button
        type="button"
        :class="{ active: activePanel === 'problems' }"
        @click="setActivePanel('problems')"
      >
        题库
      </button>
      <button
        type="button"
        :class="{ active: activePanel === 'ai' }"
        @click="setActivePanel('ai')"
      >
        AI
      </button>
      <button
        type="button"
        :class="{ active: activePanel === 'square' }"
        @click="setActivePanel('square')"
      >
        广场
      </button>
      <button
        type="button"
        :class="{ active: activePanel === 'wrongbook' }"
        @click="setActivePanel('wrongbook')"
      >
        {{ t('复习', 'Review') }}
      </button>
      <button
        type="button"
        :class="{ active: activePanel === 'profile' }"
        @click="setActivePanel('profile')"
      >
        我的
      </button>
    </nav>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { useUserStore } from '@/store/user'
import { useLocale } from '@/composables/locale'

const router = useRouter()
const userStore = useUserStore()
const { t, locale } = useLocale()
const HOME_STATE_KEY = 'home_view_state_v1'
const MOBILE_BREAKPOINT = 980
const AI_MODE_PROGRESS = 'progress'
const AI_MODE_CUSTOM = 'custom'

const normalizeAiMode = (mode) => {
  if (mode === 'estimate') return AI_MODE_PROGRESS
  if (mode === AI_MODE_PROGRESS || mode === AI_MODE_CUSTOM) return mode
  return AI_MODE_PROGRESS
}

const loading = ref(true)
const problems = ref([])
const difficultyFilter = ref('')
const isDark = ref(false)
const userStats = ref({
  total_problems: 0,
  passed_problems: 0,
  completion_rate: 0
})

const animatedPassed = ref(0)
const animatedTotal = ref(0)
const animatedRate = ref(0)
const animatedRemaining = ref(0)
const activePanel = ref('problems')
const problemSourceTab = ref('official')
const aiMode = ref(AI_MODE_PROGRESS)
const customLevel = ref(5)
const aiGenerating = ref(false)
const aiStatusMessage = ref('')
const aiStatusType = ref('success')
const generatedProblem = ref(null)
const deletingProblemId = ref('')
const sharingProblemId = ref('')
const unsharingShareId = ref('')
const squareLoading = ref(false)
const squarePublicItems = ref([])
const mySharedItems = ref([])
const squareViewTab = ref('square')
const squareSortBy = ref('stars')
const importingShareId = ref('')
const starringShareId = ref('')
const squareStatusMessage = ref('')
const squareStatusType = ref('success')
const wrongBookLoading = ref(false)
const wrongBookItems = ref([])
const wrongBookTag = ref('')
const wrongBookDueOnly = ref(false)
const wrongBookStatusMessage = ref('')
const wrongBookStatusType = ref('success')
const aiProgress = ref(0)
const aiProgressTarget = ref(0)
const aiProgressVisible = ref(false)
const aiProgressLabel = ref('')
const aiProgressState = ref('idle')
const aiProgressElapsedSeconds = ref(0)
const isMobileViewport = ref(false)
const pendingHomeScrollY = ref(0)
let aiProgressTimer = null
let aiProgressElapsedTimer = null
let homeScrollRestoreTimer = null

const username = computed(() => userStore.user?.username || 'Coder')
const userInitial = computed(() => username.value.charAt(0).toUpperCase())
const userRoleText = computed(() => (userStore.user?.is_superuser ? t('管理员', 'Admin') : t('普通用户', 'User')))
const accountStatusText = computed(() => (userStore.user?.is_active === false ? t('已禁用', 'Disabled') : t('正常', 'Normal')))
const headlineKicker = computed(() => {
  if (activePanel.value === 'ai') return 'AI Lab'
  if (activePanel.value === 'square') return 'Square'
  if (activePanel.value === 'wrongbook') return 'Wrong Book'
  if (activePanel.value === 'profile') return 'Profile'
  return 'Dashboard'
})
const headlineSub = computed(() => {
  if (activePanel.value === 'ai') return t('通过 AI 生成适配你当前水平的训练题目。', 'Generate practice problems matched to your level with AI.')
  if (activePanel.value === 'square') return t('分享你已通过的 AI 私有题，导入别人精选题目。', 'Share passed AI private problems and import selected ones from others.')
  if (activePanel.value === 'wrongbook') return t('集中复习做错题，按知识点二刷并跟进提醒。', 'Review your wrong answers by knowledge tags with spaced reminders.')
  if (activePanel.value === 'profile') return t('查看你的账号信息，或前往设置页更新资料。', 'Check your account info or go to settings to update it.')
  return t('继续今天的训练，保持稳定节奏。', 'Keep training today and stay in rhythm.')
})
const listGeneratingHintVisible = computed(
  () => aiGenerating.value || (aiProgressVisible.value && aiProgressState.value === 'running')
)
const listGeneratingHintText = computed(
  () => aiProgressLabel.value || t('生成完成后会自动同步到题库列表。', 'Generated problem will be synced to your list automatically.')
)
const progressWidth = computed(() => `${Math.max(0, Math.min(animatedRate.value, 100))}%`)
const levelHint = computed(() => {
  if (customLevel.value <= 3) return t('偏基础，适合巩固语法和常见思路', 'Basic level, good for syntax and common patterns')
  if (customLevel.value <= 7) return t('中等综合，强调数据结构和复杂度控制', 'Intermediate level, focuses on data structures and complexity')
  return t('偏高难，强调抽象建模和边界处理', 'Advanced level, focuses on modeling and edge cases')
})

const difficultyOrder = {
  Easy: 0,
  Medium: 1,
  Hard: 2
}

const sortProblemsByDifficulty = (items) =>
  items
    .map((problem, index) => ({ problem, index }))
    .sort((a, b) => {
      const rankA = difficultyOrder[a.problem.difficulty] ?? 99
      const rankB = difficultyOrder[b.problem.difficulty] ?? 99
      if (rankA !== rankB) return rankA - rankB
      return a.index - b.index
    })
    .map((item) => item.problem)

const filteredProblems = computed(() => {
  if (!difficultyFilter.value) return problems.value
  return problems.value.filter((problem) => problem.difficulty === difficultyFilter.value)
})

const officialProblems = computed(() =>
  sortProblemsByDifficulty(
    filteredProblems.value.filter((problem) => problem.source_type !== 'ai_generated')
  )
)

const personalProblems = computed(() =>
  sortProblemsByDifficulty(
    filteredProblems.value.filter((problem) => problem.source_type === 'ai_generated')
  )
)

const activeProblems = computed(() =>
  problemSourceTab.value === 'official' ? officialProblems.value : personalProblems.value
)

const activeSourceEmptyText = computed(() =>
  problemSourceTab.value === 'official'
    ? t('当前筛选下暂无题库题', 'No official problems under current filters')
    : t('当前筛选下暂无 AI 私有题', 'No AI private problems under current filters')
)

const problemSourceTagText = computed(() =>
  problemSourceTab.value === 'official' ? t('题库', 'Official') : t('AI 私有', 'AI Private')
)

const problemSourceTagClass = computed(() =>
  problemSourceTab.value === 'official' ? 'official' : 'ai'
)
const activeSquareItems = computed(() =>
  squareViewTab.value === 'mine' ? mySharedItems.value : squarePublicItems.value
)
const squareEmptyText = computed(() =>
  squareViewTab.value === 'mine'
    ? t('你还没有分享题目，先在 AI 私有题中通过后再分享。', "You haven't shared any problem yet. Pass an AI private problem first.")
    : t('广场还没有可导入题目，稍后再来看看。', 'No importable problems in square yet. Check back later.')
)

const animateValue = (target, current, setter, duration = 650) => {
  const start = current
  const range = target - start
  if (range === 0) return

  const startTime = performance.now()
  const step = (now) => {
    const elapsed = now - startTime
    const progress = Math.min(elapsed / duration, 1)
    const easeOut = 1 - Math.pow(1 - progress, 3)
    setter(Math.round(start + range * easeOut))
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

watch(
  userStats,
  (stats) => {
    const remaining = Math.max((stats.total_problems || 0) - (stats.passed_problems || 0), 0)
    animateValue(stats.passed_problems || 0, animatedPassed.value, (value) => {
      animatedPassed.value = value
    })
    animateValue(stats.total_problems || 0, animatedTotal.value, (value) => {
      animatedTotal.value = value
    })
    animateValue(stats.completion_rate || 0, animatedRate.value, (value) => {
      animatedRate.value = value
    })
    animateValue(remaining, animatedRemaining.value, (value) => {
      animatedRemaining.value = value
    })
  },
  { deep: true }
)

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
  return map[difficulty] || difficulty
}

const difficultyClass = (difficulty) => {
  if (difficulty === 'Easy') return 'easy'
  if (difficulty === 'Medium') return 'medium'
  if (difficulty === 'Hard') return 'hard'
  return ''
}

const formatSquareDate = (value) => {
  if (!value) return '--'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '--'
  return date.toLocaleDateString('zh-CN')
}

const formatWrongBookDate = (value) => {
  if (!value) return t('未设置', 'Not set')
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '--'
  return date.toLocaleString(locale.value === 'en' ? 'en-US' : 'zh-CN', { hour12: false })
}

const containsCjk = (value) => /[\u3400-\u9FFF]/.test(String(value || ''))

const pickLocalizedMessage = (message, fallbackZh, fallbackEn) => {
  if (!message) return t(fallbackZh, fallbackEn)
  if (locale.value === 'en' && containsCjk(message)) {
    return fallbackEn || fallbackZh
  }
  return message
}

const updateViewportState = () => {
  if (typeof window === 'undefined') return
  isMobileViewport.value = window.innerWidth <= MOBILE_BREAKPOINT
}

const clearHomeScrollRestoreTimer = () => {
  if (homeScrollRestoreTimer) {
    clearTimeout(homeScrollRestoreTimer)
    homeScrollRestoreTimer = null
  }
}

const scheduleHomeScrollRestore = () => {
  if (typeof window === 'undefined') return
  const originalTarget = Number(pendingHomeScrollY.value || 0)
  if (originalTarget <= 0) return

  clearHomeScrollRestoreTimer()
  let attempts = 0

  const restore = () => {
    const maxScroll = Math.max(0, document.documentElement.scrollHeight - window.innerHeight)
    const target = Math.min(originalTarget, maxScroll)
    window.scrollTo({ top: target, behavior: 'auto' })

    const reachedTarget = Math.abs(window.scrollY - target) <= 2
    const canReachOriginal = maxScroll >= originalTarget - 2
    if ((reachedTarget && canReachOriginal) || attempts >= 16) {
      pendingHomeScrollY.value = 0
      clearHomeScrollRestoreTimer()
      return
    }

    attempts += 1
    homeScrollRestoreTimer = window.setTimeout(restore, 120)
  }

  homeScrollRestoreTimer = window.setTimeout(restore, 0)
}

const persistHomeViewState = () => {
  try {
    localStorage.setItem(
      HOME_STATE_KEY,
      JSON.stringify({
        activePanel: activePanel.value,
        problemSourceTab: problemSourceTab.value,
        difficultyFilter: difficultyFilter.value,
        aiMode: aiMode.value,
        customLevel: customLevel.value,
        squareViewTab: squareViewTab.value,
        squareSortBy: squareSortBy.value,
        wrongBookTag: wrongBookTag.value,
        wrongBookDueOnly: wrongBookDueOnly.value,
        scrollY: window.scrollY || 0,
        ts: Date.now()
      })
    )
  } catch (error) {
    console.warn('保存首页视图状态失败:', error)
  }
}

const restoreHomeViewState = async () => {
  try {
    const raw = localStorage.getItem(HOME_STATE_KEY)
    if (!raw) return
    const payload = JSON.parse(raw)
    if (typeof payload?.activePanel === 'string') {
      activePanel.value = payload.activePanel
    }
    if (typeof payload?.problemSourceTab === 'string') {
      problemSourceTab.value = payload.problemSourceTab
    }
    if (typeof payload?.difficultyFilter === 'string') {
      difficultyFilter.value = payload.difficultyFilter
    }
    if (typeof payload?.aiMode === 'string') {
      aiMode.value = normalizeAiMode(payload.aiMode)
    }
    if (Number.isFinite(payload?.customLevel)) {
      customLevel.value = Math.max(1, Math.min(10, Number(payload.customLevel)))
    }
    if (typeof payload?.squareViewTab === 'string') {
      squareViewTab.value = payload.squareViewTab
    }
    if (typeof payload?.squareSortBy === 'string') {
      squareSortBy.value = payload.squareSortBy
    }
    if (typeof payload?.wrongBookTag === 'string') {
      wrongBookTag.value = payload.wrongBookTag
    }
    wrongBookDueOnly.value = Boolean(payload?.wrongBookDueOnly)

    pendingHomeScrollY.value = Math.max(0, Number(payload?.scrollY || 0))
    await nextTick()
    scheduleHomeScrollRestore()
  } catch (error) {
    console.warn('恢复首页视图状态失败:', error)
  }
}

const handleVisibilityChange = () => {
  if (document.visibilityState === 'hidden') {
    persistHomeViewState()
  }
}

const setActivePanel = (panel) => {
  if (!panel || activePanel.value === panel) return
  activePanel.value = panel
  if (isMobileViewport.value) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const navigateFromHome = (path) => {
  persistHomeViewState()
  router.push(path)
}

const goToWorkspace = (problemId) => {
  navigateFromHome(`/workspace/${problemId}`)
}

const goToDiscuss = (problemId) => {
  navigateFromHome(`/discuss/${problemId}`)
}

const setAiMode = (mode) => {
  aiMode.value = normalizeAiMode(mode)
  aiStatusMessage.value = ''
}

const changeCustomLevel = (delta) => {
  customLevel.value = Math.max(1, Math.min(10, customLevel.value + delta))
}

const clearAiProgressTimer = () => {
  if (aiProgressTimer) {
    clearInterval(aiProgressTimer)
    aiProgressTimer = null
  }
}

const clearAiProgressElapsedTimer = () => {
  if (aiProgressElapsedTimer) {
    clearInterval(aiProgressElapsedTimer)
    aiProgressElapsedTimer = null
  }
}

const setAiProgressStage = (stage) => {
  const stageConfig = {
    preparing: { target: 12, label: '正在整理出题参数...' },
    requesting: { target: 72, label: '正在调用 AI 模型生成题目...' },
    validating: { target: 86, label: '正在校验题目结构与测试用例...' },
    syncing: { target: 96, label: '正在同步题目到你的私有题库...' },
  }

  const config = stageConfig[stage]
  if (!config) return

  aiProgressState.value = 'running'
  aiProgressLabel.value = config.label
  aiProgressTarget.value = Math.max(aiProgressTarget.value, config.target)
}

const startAiProgress = () => {
  clearAiProgressTimer()
  clearAiProgressElapsedTimer()
  aiProgressVisible.value = true
  aiProgressState.value = 'running'
  aiProgress.value = 4
  aiProgressTarget.value = 4
  aiProgressElapsedSeconds.value = 0
  setAiProgressStage('preparing')

  aiProgressTimer = setInterval(() => {
    if (aiProgress.value >= aiProgressTarget.value) {
      if (aiProgressTarget.value >= 100 && aiProgressState.value !== 'running') {
        clearAiProgressTimer()
        clearAiProgressElapsedTimer()
      }
      return
    }

    const remaining = aiProgressTarget.value - aiProgress.value
    const step = remaining > 30 ? 4 : remaining > 14 ? 3 : remaining > 6 ? 2 : 1
    aiProgress.value = Math.min(aiProgressTarget.value, aiProgress.value + step)
  }, 180)

  aiProgressElapsedTimer = setInterval(() => {
    aiProgressElapsedSeconds.value += 1
  }, 1000)
}

const finishAiProgress = (state) => {
  aiProgressState.value = state
  aiProgressTarget.value = 100
  aiProgressLabel.value =
    state === 'success' ? '题目生成完成，已加入你的私有题库。' : '题目生成失败，请稍后重试。'
}

const generateAiProblem = async () => {
  aiGenerating.value = true
  aiStatusMessage.value = ''
  startAiProgress()
  setAiProgressStage('requesting')

  try {
    const currentMode = normalizeAiMode(aiMode.value)
    if (currentMode !== aiMode.value) {
      aiMode.value = currentMode
    }
    const payload = {
      mode: currentMode,
      level: currentMode === AI_MODE_CUSTOM ? customLevel.value : undefined,
    }
    const res = await api.post('/api/ai/generate-problem', payload)
    if (res.code === 0) {
      setAiProgressStage('validating')
      generatedProblem.value = res.data

      const isFallback = res.data?.generation_source === 'fallback'
      if (isFallback) {
        aiStatusType.value = 'warning'
        aiStatusMessage.value =
          res.data?.generation_note || 'AI 服务响应较慢，已生成备用题目。'
      } else {
        aiStatusType.value = 'success'
        aiStatusMessage.value = `出题成功：${res.data.problem?.title || '已生成新题'}`
      }

      setAiProgressStage('syncing')
      await Promise.all([loadProblems(), loadUserStats()])
      finishAiProgress('success')
    } else {
      aiStatusType.value = 'error'
      aiStatusMessage.value = res.message || 'AI 出题失败'
      finishAiProgress('error')
    }
  } catch (error) {
    aiStatusType.value = 'error'
    aiStatusMessage.value = error.response?.data?.message || 'AI 出题失败，请稍后重试'
    finishAiProgress('error')
  } finally {
    aiGenerating.value = false
  }
}

const goToProblemList = () => {
  setActivePanel('problems')
}

const startGeneratedProblem = () => {
  if (!generatedProblem.value?.problem?.id) return
  goToWorkspace(generatedProblem.value.problem.id)
}

const handleDeleteProblem = async (problem) => {
  if (!problem?.id || problemSourceTab.value !== 'personal') return
  if (deletingProblemId.value) return

  const title = problem.title || t('该题目', 'this problem')
  const confirmed = window.confirm(
    t(`确定删除「${title}」吗？删除后不可恢复。`, `Delete "${title}"? This action cannot be undone.`)
  )
  if (!confirmed) return

  deletingProblemId.value = problem.id
  try {
    const res = await api.delete(`/api/problems/${problem.id}`)
    if (res.code === 0) {
      if (generatedProblem.value?.problem?.id === problem.id) {
        generatedProblem.value = null
      }
      aiStatusType.value = 'success'
      aiStatusMessage.value = `已删除：${title}`
      await Promise.all([loadProblems(), loadUserStats(), loadSquareProblems()])
    } else {
      aiStatusType.value = 'error'
      aiStatusMessage.value = res.message || '删除失败'
    }
  } catch (error) {
    aiStatusType.value = 'error'
    aiStatusMessage.value = error.response?.data?.message || '删除失败，请稍后重试'
  } finally {
    deletingProblemId.value = ''
  }
}

const setSquareStatus = (type, message) => {
  squareStatusType.value = type
  squareStatusMessage.value = message
}

const handleShareProblem = async (problem) => {
  if (!problem?.id || problemSourceTab.value !== 'personal') return
  if (sharingProblemId.value) return

  if (problem.is_shared) {
    setSquareStatus('success', '该题已在广场中')
    return
  }
  if (!problem.is_passed) {
    setSquareStatus('error', '请先通过该题后再分享')
    return
  }

  const confirmed = window.confirm(
    t(`确定将「${problem.title || '该题'}」分享到广场吗？`, `Share "${problem.title || t('该题', 'this problem')}" to square?`)
  )
  if (!confirmed) return

  sharingProblemId.value = problem.id
  try {
    const res = await api.post(`/api/square/problems/${problem.id}/share`)
    if (res.code === 0) {
      setSquareStatus('success', res.message || '分享成功')
      await Promise.all([loadProblems(), loadSquareProblems()])
    } else {
      setSquareStatus('error', res.message || '分享失败')
    }
  } catch (error) {
    setSquareStatus('error', error.response?.data?.message || '分享失败，请稍后重试')
  } finally {
    sharingProblemId.value = ''
  }
}

const handleImportSquareProblem = async (item) => {
  if (!item?.id) return
  if (importingShareId.value) return

  if (item.is_owner) {
    setSquareStatus('error', '不能导入自己分享的题目')
    return
  }
  if (item.is_imported && item.imported_problem_id) {
    goToWorkspace(item.imported_problem_id)
    return
  }

  importingShareId.value = item.id
  try {
    const res = await api.post(`/api/square/shared/${item.id}/import`)
    if (res.code === 0) {
      setSquareStatus('success', res.message || '导入成功')
      await Promise.all([loadProblems(), loadUserStats(), loadSquareProblems()])
    } else {
      setSquareStatus('error', res.message || '导入失败')
    }
  } catch (error) {
    setSquareStatus('error', error.response?.data?.message || '导入失败，请稍后重试')
  } finally {
    importingShareId.value = ''
  }
}

const handleStarSquareProblem = async (item) => {
  if (!item?.id) return
  if (starringShareId.value) return

  if (item.is_starred) {
    setSquareStatus('success', '你已 Star 过该题')
    return
  }

  starringShareId.value = item.id
  try {
    const res = await api.post(`/api/square/shared/${item.id}/star`)
    if (res.code === 0) {
      setSquareStatus('success', res.message || 'Star 成功')
      await loadSquareProblems()
    } else {
      setSquareStatus('error', res.message || 'Star 失败')
    }
  } catch (error) {
    setSquareStatus('error', error.response?.data?.message || 'Star 失败，请稍后重试')
  } finally {
    starringShareId.value = ''
  }
}

const handleUnshareProblem = async (item) => {
  if (!item?.id) return
  if (unsharingShareId.value) return

  const confirmed = window.confirm(
    t(`确定取消分享「${item.title || '该题'}」吗？`, `Unshare "${item.title || t('该题', 'this problem')}"?`)
  )
  if (!confirmed) return

  unsharingShareId.value = item.id
  try {
    const res = await api.delete(`/api/square/shared/${item.id}`)
    if (res.code === 0) {
      setSquareStatus('success', res.message || '已取消分享')
      await Promise.all([loadProblems(), loadSquareProblems()])
    } else {
      setSquareStatus('error', res.message || '取消分享失败')
    }
  } catch (error) {
    setSquareStatus('error', error.response?.data?.message || '取消分享失败，请稍后重试')
  } finally {
    unsharingShareId.value = ''
  }
}

const goToSettings = () => {
  navigateFromHome('/settings')
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const loadProblems = async () => {
  try {
    loading.value = true
    const pageSize = 100
    const firstPage = await api.get('/api/problems', {
      params: { page: 1, page_size: pageSize }
    })
    if (firstPage.code === 0) {
      const allItems = [...(firstPage.data.items || [])]
      const totalPages = firstPage.data.total_pages || 1

      if (totalPages > 1) {
        for (let page = 2; page <= totalPages; page += 1) {
          const pageRes = await api.get('/api/problems', {
            params: { page, page_size: pageSize }
          })
          if (pageRes.code !== 0) continue
          allItems.push(...(pageRes.data.items || []))
        }
      }

      problems.value = allItems
    }
  } catch (error) {
    console.error('加载题目失败:', error)
  } finally {
    loading.value = false
    await nextTick()
    scheduleHomeScrollRestore()
  }
}

const loadUserStats = async () => {
  try {
    const res = await api.get('/api/problems/stats')
    if (res.code === 0) {
      userStats.value = res.data
    }
  } catch (error) {
    console.error('加载用户统计失败:', error)
  }
}

const loadSquareByScope = async (scope, sortBy = squareSortBy.value) => {
  const pageSize = 100
  const firstPage = await api.get('/api/square/problems', {
    params: { page: 1, page_size: pageSize, scope, sort_by: sortBy }
  })
  if (firstPage.code !== 0) return []

  const allItems = [...(firstPage.data.items || [])]
  const totalPages = firstPage.data.total_pages || 1
  if (totalPages > 1) {
    for (let page = 2; page <= totalPages; page += 1) {
      const pageRes = await api.get('/api/square/problems', {
        params: { page, page_size: pageSize, scope, sort_by: sortBy }
      })
      if (pageRes.code !== 0) continue
      allItems.push(...(pageRes.data.items || []))
    }
  }
  return allItems
}

const loadSquareProblems = async () => {
  try {
    squareLoading.value = true
    const currentSort = squareSortBy.value
    const [squareItems, mineItems] = await Promise.all([
      loadSquareByScope('square', currentSort),
      loadSquareByScope('mine', currentSort)
    ])
    squarePublicItems.value = squareItems
    mySharedItems.value = mineItems
  } catch (error) {
    console.error('加载广场题目失败:', error)
  } finally {
    squareLoading.value = false
  }
}

const setWrongBookStatus = (type, message) => {
  wrongBookStatusType.value = type
  wrongBookStatusMessage.value = message
}

const loadWrongBook = async () => {
  try {
    wrongBookLoading.value = true
    const res = await api.get('/api/problems/wrong-book', {
      params: {
        page: 1,
        page_size: 100,
        due_only: wrongBookDueOnly.value,
        tag: wrongBookTag.value || undefined
      }
    })
    if (res.code === 0) {
      wrongBookItems.value = res.data?.items || []
      if (!wrongBookItems.value.length) {
        setWrongBookStatus(
          'success',
          wrongBookDueOnly.value
            ? t('当前没有到期复习的错题。', 'No due items right now.')
            : t('当前暂无错题记录。', 'No wrong-book records yet.')
        )
      } else {
        setWrongBookStatus(
          'success',
          t(`已加载 ${wrongBookItems.value.length} 条错题记录`, `Loaded ${wrongBookItems.value.length} items`)
        )
      }
    } else {
      const isLegacyRouteMiss =
        res.code === 404 &&
        typeof res.message === 'string' &&
        res.message.includes('题目不存在')
      if (isLegacyRouteMiss) {
        setWrongBookStatus(
          'error',
          t(
            '错题本接口未生效，请重启后端服务后重试。',
            'Wrong-book API is not active yet. Please restart backend and retry.'
          )
        )
      } else {
        setWrongBookStatus(
          'error',
          pickLocalizedMessage(res.message, '加载错题本失败', 'Failed to load wrong-book')
        )
      }
    }
  } catch (error) {
    const backendErrorText = String(
      error.response?.data?.message || error.response?.data?.detail || error.message || ''
    )
    const isWrongBookTableMissing =
      backendErrorText.includes('wrong_problem_notes') ||
      backendErrorText.includes('UndefinedTable') ||
      backendErrorText.includes('does not exist')

    if (isWrongBookTableMissing) {
      setWrongBookStatus(
        'error',
        t(
          '错题本数据表未初始化，请先执行数据库迁移并重启后端。',
          'Wrong-book table is missing. Run DB migrations and restart backend.'
        )
      )
      return
    }

    setWrongBookStatus(
      'error',
      pickLocalizedMessage(
        error.response?.data?.message,
        '加载错题本失败，请稍后重试',
        'Failed to load wrong-book, please retry later'
      )
    )
  } finally {
    wrongBookLoading.value = false
  }
}

const markWrongProblemReviewed = async (problemId) => {
  if (!problemId) return
  try {
    const res = await api.post(`/api/problems/wrong-book/${problemId}/reviewed`)
    if (res.code === 0) {
      setWrongBookStatus('success', t('复习进度已更新', 'Review progress updated'))
      await loadWrongBook()
    } else {
      setWrongBookStatus(
        'error',
        pickLocalizedMessage(res.message, '更新复习进度失败', 'Failed to update review progress')
      )
    }
  } catch (error) {
    setWrongBookStatus(
      'error',
      pickLocalizedMessage(
        error.response?.data?.message,
        '更新复习进度失败',
        'Failed to update review progress'
      )
    )
  }
}

watch(activePanel, (panel) => {
  if (panel === 'square') {
    loadSquareProblems()
  }
  if (panel === 'wrongbook') {
    loadWrongBook()
  }
})

watch(squareSortBy, () => {
  if (activePanel.value === 'square') {
    loadSquareProblems()
  }
})

watch(wrongBookDueOnly, () => {
  if (activePanel.value === 'wrongbook') {
    loadWrongBook()
  }
})

watch(
  [
    activePanel,
    problemSourceTab,
    difficultyFilter,
    aiMode,
    customLevel,
    squareViewTab,
    squareSortBy,
    wrongBookTag,
    wrongBookDueOnly,
  ],
  () => {
    persistHomeViewState()
  }
)

onMounted(() => {
  updateViewportState()
  restoreHomeViewState()
  window.addEventListener('resize', updateViewportState, { passive: true })
  window.addEventListener('pagehide', persistHomeViewState)
  document.addEventListener('visibilitychange', handleVisibilityChange)
  initTheme()
  loadProblems()
  loadUserStats()
  loadSquareProblems()
  loadWrongBook()
})

onBeforeUnmount(() => {
  persistHomeViewState()
  window.removeEventListener('resize', updateViewportState)
  window.removeEventListener('pagehide', persistHomeViewState)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  clearHomeScrollRestoreTimer()
  clearAiProgressTimer()
  clearAiProgressElapsedTimer()
})
</script>

<style scoped>
.home-page {
  --page-bg: linear-gradient(160deg, #f8f3ec 0%, #f2ebe0 45%, #e8dfd2 100%);
  --shell-bg: rgba(255, 253, 248, 0.82);
  --shell-border: rgba(255, 255, 255, 0.72);
  --panel-bg: rgba(255, 255, 255, 0.88);
  --panel-soft: rgba(253, 249, 242, 0.92);
  --line: #ddcfbc;
  --line-soft: #eadfd0;
  --text-main: #2f271f;
  --text-sub: #7b6d5b;
  --text-muted: #998a74;
  --accent: #9b6a39;
  --accent-strong: #7f5024;
  --chip-bg: #efe4d5;
  --hover-row: rgba(229, 214, 196, 0.35);
  --shadow-shell: 0 34px 86px rgba(57, 44, 28, 0.16);
  --shadow-panel: 0 22px 52px rgba(53, 40, 25, 0.12);
  --orb-a: rgba(191, 144, 87, 0.24);
  --orb-b: rgba(116, 163, 213, 0.2);
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  padding: 20px;
  background: var(--page-bg);
  color: var(--text-main);
  font-family: "Avenir Next", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.home-page.theme-dark {
  --page-bg: linear-gradient(160deg, #151820 0%, #10131a 48%, #0d1016 100%);
  --shell-bg: rgba(20, 25, 34, 0.9);
  --shell-border: rgba(70, 80, 96, 0.5);
  --panel-bg: rgba(23, 29, 39, 0.92);
  --panel-soft: rgba(20, 26, 36, 0.92);
  --line: #313b4a;
  --line-soft: #26303f;
  --text-main: #ecf0f7;
  --text-sub: #a8b1bf;
  --text-muted: #8a94a6;
  --accent: #d4a06f;
  --accent-strong: #ecbb86;
  --chip-bg: #263242;
  --hover-row: rgba(52, 64, 82, 0.54);
  --shadow-shell: 0 34px 86px rgba(5, 8, 13, 0.5);
  --shadow-panel: 0 22px 52px rgba(5, 8, 13, 0.35);
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

.dashboard-shell {
  position: relative;
  z-index: 2;
  width: min(1360px, 100%);
  margin: 0 auto;
  min-height: calc(100vh - 40px);
  border-radius: 30px;
  border: 1px solid var(--shell-border);
  background: var(--shell-bg);
  box-shadow: var(--shadow-shell);
  backdrop-filter: blur(16px);
  display: grid;
  grid-template-columns: 260px 1fr;
  overflow: hidden;
  animation: rise-in 0.72s ease both;
}

.side-panel {
  border-right: 1px solid var(--line);
  padding: 24px 18px;
  background: linear-gradient(180deg, var(--panel-bg) 0%, var(--panel-soft) 100%);
  display: flex;
  flex-direction: column;
}

.side-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 8px 20px;
}

.logo {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-weight: 700;
  letter-spacing: 0.2em;
  padding-left: 0.2em;
  color: #f8f5f0;
  background: linear-gradient(145deg, #211b16 0%, #42362c 100%);
  box-shadow: 0 12px 26px rgba(31, 25, 19, 0.25);
}

.home-page.theme-dark .logo {
  background: linear-gradient(145deg, #2d3544 0%, #46516b 100%);
}

.brand-name {
  font-size: 12px;
  letter-spacing: 0.2em;
  font-weight: 700;
}

.brand-sub {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-sub);
}

.side-nav {
  display: grid;
  gap: 8px;
}

.nav-item {
  border: 0;
  background: transparent;
  height: 44px;
  border-radius: 12px;
  color: var(--text-sub);
  font-size: 14px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 0 12px;
  cursor: pointer;
  transition: all 0.24s ease;
}

.nav-item svg {
  width: 18px;
  height: 18px;
}

.nav-item:hover {
  background: var(--chip-bg);
  color: var(--text-main);
  transform: translateX(2px);
}

.nav-item-active {
  background: var(--chip-bg);
  color: var(--accent-strong);
}

.theme-toggle {
  margin-top: auto;
  border: 1px solid var(--line);
  border-radius: 12px;
  height: 44px;
  background: transparent;
  color: var(--text-sub);
  font-weight: 600;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.24s ease;
}

.theme-toggle svg {
  width: 16px;
  height: 16px;
}

.theme-toggle:hover {
  border-color: var(--accent);
  color: var(--accent-strong);
}

.main-panel {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.mobile-bottom-nav {
  position: fixed;
  left: 12px;
  right: 12px;
  bottom: calc(10px + env(safe-area-inset-bottom, 0px));
  z-index: 40;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--panel-bg);
  box-shadow: 0 12px 30px rgba(23, 18, 13, 0.18);
  backdrop-filter: blur(12px);
  padding: 6px;
  display: none;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 4px;
}

.mobile-bottom-nav button {
  border: 0;
  background: transparent;
  color: var(--text-sub);
  height: 34px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.22s ease;
}

.mobile-bottom-nav button.active {
  color: var(--accent-strong);
  background: var(--chip-bg);
}

.top-bar {
  border-bottom: 1px solid var(--line);
  padding: 24px 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.headline-kicker {
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 700;
}

.headline h1 {
  margin-top: 8px;
  font-size: clamp(1.6rem, 2.2vw, 2.3rem);
  letter-spacing: -0.03em;
}

.headline-sub {
  margin-top: 6px;
  color: var(--text-sub);
  font-size: 14px;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ghost-action {
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-main);
  border-radius: 12px;
  height: 40px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.24s ease;
}

.ghost-action:hover {
  border-color: var(--accent);
  color: var(--accent-strong);
}

.avatar {
  width: 40px;
  height: 40px;
  border: 0;
  border-radius: 50%;
  cursor: pointer;
  color: #fff;
  font-weight: 700;
  background: linear-gradient(145deg, #875c33 0%, #c18652 100%);
  box-shadow: 0 10px 20px rgba(86, 57, 30, 0.3);
  transition: transform 0.24s ease;
}

.avatar:hover {
  transform: scale(1.06);
}

.content-wrap {
  padding: 24px 30px;
  display: grid;
  gap: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.ai-lab-panel {
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--panel-bg);
  box-shadow: var(--shadow-panel);
  padding: 18px;
  display: grid;
  gap: 12px;
}

.ai-lab-head h2 {
  margin-top: 6px;
  font-size: 1.4rem;
  letter-spacing: -0.03em;
}

.ai-mode-switch {
  display: inline-grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  max-width: 360px;
}

.ai-mode-switch button {
  border: 1px solid var(--line);
  background: var(--panel-soft);
  color: var(--text-sub);
  border-radius: 10px;
  height: 36px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.22s ease;
}

.ai-mode-switch button.active {
  border-color: var(--accent);
  color: var(--accent-strong);
  background: color-mix(in srgb, var(--chip-bg) 74%, transparent);
}

.ai-mode-box {
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  background: var(--panel-soft);
  padding: 12px;
}

.ai-mode-box p {
  margin: 0;
  font-size: 13px;
  color: var(--text-sub);
  line-height: 1.7;
}

.ai-mode-box.custom {
  display: grid;
  gap: 8px;
}

.ai-mode-box.custom label {
  font-size: 12px;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  font-weight: 700;
}

.level-control {
  display: grid;
  grid-template-columns: 34px 1fr 34px auto;
  align-items: center;
  gap: 8px;
}

.level-control button {
  border: 1px solid var(--line);
  background: var(--panel-bg);
  color: var(--text-main);
  border-radius: 9px;
  height: 34px;
  cursor: pointer;
  font-weight: 700;
}

.level-control input[type="range"] {
  width: 100%;
}

.level-control span {
  min-width: 40px;
  text-align: right;
  font-weight: 700;
  color: var(--accent-strong);
}

.level-hint {
  font-size: 12px;
  color: var(--text-sub);
  line-height: 1.6;
}

.ai-generate-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.ai-progress-card {
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  background: var(--panel-soft);
  padding: 10px 12px;
  display: grid;
  gap: 8px;
}

.ai-progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.ai-progress-head span {
  color: var(--text-sub);
  font-size: 13px;
  line-height: 1.5;
}

.ai-progress-head b {
  color: var(--text-main);
  font-size: 13px;
  letter-spacing: 0.02em;
}

.ai-progress-meta {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}

.ai-progress-track {
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
  background: var(--line-soft);
}

.ai-progress-fill {
  height: 100%;
  border-radius: inherit;
  width: 0;
  transition: width 0.26s ease;
  background: linear-gradient(90deg, #8d6034 0%, #c9935d 100%);
}

.ai-progress-card.state-running .ai-progress-fill {
  background: linear-gradient(90deg, #8d6034 0%, #c9935d 100%);
}

.ai-progress-card.state-success .ai-progress-fill {
  background: linear-gradient(90deg, #2c8b5a 0%, #57c08a 100%);
}

.ai-progress-card.state-error .ai-progress-fill {
  background: linear-gradient(90deg, #9f3d3d 0%, #d46868 100%);
}

.home-page.theme-dark .ai-progress-card.state-running .ai-progress-fill {
  background: linear-gradient(90deg, #a87a4b 0%, #d6a36f 100%);
}

.home-page.theme-dark .ai-progress-card.state-success .ai-progress-fill {
  background: linear-gradient(90deg, #4fa778 0%, #79cda0 100%);
}

.home-page.theme-dark .ai-progress-card.state-error .ai-progress-fill {
  background: linear-gradient(90deg, #bc6161 0%, #e08d8d 100%);
}

.ai-status {
  margin: 0;
  font-size: 13px;
  border-radius: 10px;
  padding: 10px 12px;
}

.ai-status.success {
  background: rgba(75, 166, 116, 0.14);
  color: #2b744a;
  border: 1px solid rgba(75, 166, 116, 0.32);
}

.ai-status.error {
  background: rgba(219, 86, 86, 0.14);
  color: #a03333;
  border: 1px solid rgba(219, 86, 86, 0.32);
}

.ai-status.warning {
  background: rgba(214, 158, 78, 0.16);
  color: #8e5b1d;
  border: 1px solid rgba(214, 158, 78, 0.36);
}

.home-page.theme-dark .ai-status.success {
  color: #8fd2ac;
}

.home-page.theme-dark .ai-status.error {
  color: #f2a7a7;
}

.home-page.theme-dark .ai-status.warning {
  color: #f1d5a0;
}

.ai-result-card {
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  background: var(--panel-soft);
  padding: 12px;
  display: grid;
  gap: 8px;
}

.ai-result-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.ai-result-tags {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.ai-result-head h3 {
  margin: 0;
  font-size: 15px;
  letter-spacing: -0.01em;
}

.ai-result-desc {
  margin: 0;
  color: var(--text-sub);
  font-size: 13px;
  line-height: 1.7;
}

.ai-result-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.ai-result-meta span {
  height: 24px;
  border-radius: 999px;
  padding: 0 10px;
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  color: var(--text-sub);
  border: 1px solid var(--line-soft);
  background: var(--panel-bg);
}

.square-panel {
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--panel-bg);
  box-shadow: var(--shadow-panel);
  overflow: hidden;
}

.wrongbook-panel {
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--panel-bg);
  box-shadow: var(--shadow-panel);
  padding-bottom: 16px;
}

.wrongbook-controls {
  padding: 12px 16px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: flex-end;
}

.wrongbook-controls label {
  display: grid;
  gap: 6px;
  font-size: 12px;
  color: var(--text-sub);
  font-weight: 700;
}

.wrongbook-controls label.checkbox {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 36px;
}

.wrongbook-controls input[type="text"] {
  width: 180px;
  height: 36px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--panel-soft);
  color: var(--text-main);
  font-size: 13px;
  padding: 0 10px;
}

.wrongbook-list {
  padding: 12px 16px 0;
  display: grid;
  gap: 10px;
}

.wrongbook-card {
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--panel-soft);
  padding: 12px;
  display: grid;
  gap: 8px;
}

.wrongbook-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.wrongbook-head h3 {
  margin: 0;
  font-size: 15px;
}

.wrongbook-meta {
  margin: 0;
  font-size: 12px;
  color: var(--text-sub);
}

.wrongbook-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.wrongbook-tags span {
  height: 22px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid var(--line-soft);
  background: var(--panel-bg);
  color: var(--text-sub);
  font-size: 11px;
  display: inline-flex;
  align-items: center;
}

.wrongbook-actions {
  display: inline-flex;
  gap: 8px;
  flex-wrap: wrap;
}

.square-status {
  margin: 12px 16px 0;
  font-size: 13px;
  border-radius: 10px;
  padding: 10px 12px;
}

.square-status.success {
  background: rgba(75, 166, 116, 0.14);
  color: #2b744a;
  border: 1px solid rgba(75, 166, 116, 0.32);
}

.square-status.error {
  background: rgba(219, 86, 86, 0.14);
  color: #a03333;
  border: 1px solid rgba(219, 86, 86, 0.32);
}

.home-page.theme-dark .square-status.success {
  color: #8fd2ac;
}

.home-page.theme-dark .square-status.error {
  color: #f2a7a7;
}

.square-wrap {
  padding: 12px 16px 16px;
}

.square-toolbar {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.square-view-tabs {
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 4px;
  background: var(--panel-soft);
  display: inline-grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 4px;
  min-width: 230px;
}

.square-view-tabs button {
  border: 0;
  height: 34px;
  border-radius: 9px;
  background: transparent;
  color: var(--text-sub);
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.22s ease;
}

.square-view-tabs button b {
  min-width: 20px;
  height: 20px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  background: color-mix(in srgb, var(--line-soft) 66%, transparent);
  color: var(--text-muted);
}

.square-view-tabs button.active {
  background: color-mix(in srgb, var(--chip-bg) 72%, transparent);
  color: var(--accent-strong);
}

.square-view-tabs button.active b {
  background: color-mix(in srgb, var(--accent) 16%, transparent);
  color: var(--accent-strong);
}

.square-sort {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-sub);
  font-weight: 700;
}

.square-sort select {
  height: 34px;
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0 10px;
  background: var(--panel-soft);
  color: var(--text-main);
  outline: none;
}

.square-list {
  display: grid;
  gap: 12px;
}

.square-card {
  border: 1px solid var(--line-soft);
  border-radius: 14px;
  background: var(--panel-soft);
  padding: 14px;
  display: grid;
  gap: 10px;
}

.square-card-head {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 12px;
}

.square-title-wrap {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.square-title-wrap h3 {
  margin: 0;
  font-size: 15px;
  letter-spacing: -0.01em;
}

.square-tags {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.square-meta {
  display: grid;
  justify-items: end;
  gap: 6px;
}

.square-owner,
.square-meta-metrics span {
  font-size: 12px;
  color: var(--text-sub);
}

.square-meta-metrics {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.square-desc {
  margin: 0;
  font-size: 13px;
  color: var(--text-sub);
  line-height: 1.6;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.square-actions {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.square-skeleton-card {
  border: 1px solid var(--line-soft);
  border-radius: 14px;
  min-height: 86px;
  display: grid;
  align-content: center;
  gap: 10px;
  padding: 14px;
  background: var(--panel-soft);
}

.stat-card {
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--panel-bg);
  box-shadow: var(--shadow-panel);
  padding: 18px;
  position: relative;
  overflow: hidden;
  animation: card-up 0.56s ease both;
}

.stat-card::before {
  content: "";
  position: absolute;
  inset: 0 auto auto 0;
  width: 120px;
  height: 120px;
  background: radial-gradient(circle, rgba(174, 132, 84, 0.2) 0%, transparent 68%);
  pointer-events: none;
}

.home-page.theme-dark .stat-card::before {
  background: radial-gradient(circle, rgba(103, 137, 178, 0.2) 0%, transparent 68%);
}

.stat-card p {
  font-size: 13px;
  color: var(--text-sub);
  position: relative;
}

.stat-card strong {
  margin-top: 8px;
  display: block;
  font-size: clamp(1.9rem, 2.6vw, 2.2rem);
  letter-spacing: -0.03em;
  position: relative;
}

.stat-tag {
  margin-top: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 24px;
  min-width: 54px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  position: relative;
}

.stat-tag.success {
  background: rgba(75, 166, 116, 0.18);
  color: #2b744a;
}

.stat-tag.neutral {
  background: rgba(128, 146, 167, 0.2);
  color: #4e6177;
}

.stat-tag.warning {
  background: rgba(214, 145, 88, 0.22);
  color: #915929;
}

.progress-track {
  margin-top: 10px;
  height: 7px;
  border-radius: 999px;
  background: var(--line-soft);
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #ad7642 0%, #d39a65 100%);
  transition: width 0.72s cubic-bezier(0.4, 0, 0.2, 1);
}

.profile-panel {
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--panel-bg);
  box-shadow: var(--shadow-panel);
  overflow: hidden;
}

.profile-head {
  align-items: center;
}

.profile-body {
  padding: 18px;
  display: grid;
  gap: 14px;
}

.profile-hero {
  border: 1px solid var(--line-soft);
  border-radius: 16px;
  background: var(--panel-soft);
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.profile-hero-avatar {
  width: 62px;
  height: 62px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 1.35rem;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(145deg, #875c33 0%, #c18652 100%);
  box-shadow: 0 12px 26px rgba(86, 57, 30, 0.28);
  flex-shrink: 0;
}

.profile-hero-text h3 {
  margin: 0;
  font-size: 1.1rem;
  letter-spacing: -0.02em;
}

.profile-hero-text p {
  margin-top: 4px;
  color: var(--text-sub);
  font-size: 13px;
  word-break: break-all;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.profile-info-card {
  border: 1px solid var(--line-soft);
  border-radius: 14px;
  background: var(--panel-soft);
  padding: 12px;
  min-height: 92px;
  display: grid;
  align-content: center;
  gap: 4px;
}

.profile-info-card p {
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 700;
}

.profile-info-card strong {
  font-size: 15px;
  color: var(--text-main);
  word-break: break-all;
}

.problem-panel {
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--panel-bg);
  box-shadow: var(--shadow-panel);
  overflow: hidden;
}

.generation-hint {
  margin: 12px 16px 0;
  border: 1px solid color-mix(in srgb, var(--accent) 34%, var(--line-soft));
  border-radius: 12px;
  background: color-mix(in srgb, var(--chip-bg) 70%, transparent);
  min-height: 40px;
  padding: 0 12px;
  display: grid;
  grid-template-columns: auto auto 1fr auto;
  align-items: center;
  gap: 8px;
}

.generation-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #d1843d;
  animation: pulse-dot 1.2s ease-in-out infinite;
}

.generation-hint strong {
  font-size: 12px;
  color: var(--accent-strong);
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.generation-detail {
  font-size: 12px;
  color: var(--text-sub);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.generation-hint b {
  font-size: 12px;
  color: var(--text-main);
  letter-spacing: 0.02em;
}

.panel-head {
  padding: 20px 20px 16px;
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid var(--line);
}

.panel-kicker {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.17em;
  color: var(--text-muted);
  font-weight: 700;
}

.panel-head h2 {
  margin-top: 6px;
  font-size: 1.5rem;
  letter-spacing: -0.03em;
}

.panel-sub {
  margin-top: 4px;
  color: var(--text-sub);
  font-size: 13px;
}

.panel-controls {
  display: inline-flex;
  align-items: end;
  gap: 10px;
  flex-wrap: wrap;
}

.source-tabs {
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 4px;
  background: var(--panel-soft);
  display: inline-grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 4px;
  min-width: 250px;
}

.source-tab {
  border: 0;
  height: 34px;
  border-radius: 9px;
  background: transparent;
  color: var(--text-sub);
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.22s ease;
}

.source-tab b {
  min-width: 20px;
  height: 20px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  background: color-mix(in srgb, var(--line-soft) 66%, transparent);
  color: var(--text-muted);
}

.source-tab.active {
  background: color-mix(in srgb, var(--chip-bg) 72%, transparent);
  color: var(--accent-strong);
}

.source-tab.active b {
  background: color-mix(in srgb, var(--accent) 16%, transparent);
  color: var(--accent-strong);
}

.filter-box {
  display: grid;
  gap: 6px;
}

.filter-box label {
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 700;
}

.filter-box select {
  min-width: 132px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--panel-soft);
  color: var(--text-main);
  height: 38px;
  padding: 0 10px;
  outline: none;
  font-size: 13px;
}

.table-wrap {
  padding: 10px 16px 14px;
}

.problem-table {
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--line-soft);
}

.dual-problem-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.problem-column {
  border-radius: 14px;
  border: 1px solid var(--line-soft);
  background: color-mix(in srgb, var(--panel-bg) 88%, transparent);
  overflow: hidden;
  min-width: 0;
}

.column-head {
  min-height: 46px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-bottom: 1px solid var(--line-soft);
  background: var(--panel-soft);
}

.column-title-wrap {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.column-title-wrap p {
  margin: 0;
  font-size: 12px;
  color: var(--text-sub);
}

.column-head b {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 700;
}

.column-empty {
  min-height: 170px;
  display: grid;
  place-items: center;
  padding: 12px;
  text-align: center;
  color: var(--text-sub);
  font-size: 13px;
}

.problem-column .problem-table {
  border: 0;
  border-radius: 0;
}

.problem-column .table-head,
.problem-column .table-row {
  grid-template-columns: 56px minmax(0, 1fr) 88px 248px;
}

.problem-column .table-row {
  min-height: 64px;
}

.problem-column .col-actions {
  gap: 6px;
}

.problem-column .action-btn {
  height: 31px;
  padding: 0 10px;
  font-size: 12px;
}

.table-head,
.table-row {
  display: grid;
  grid-template-columns: 68px 1fr 120px 286px;
  align-items: center;
}

.table-head {
  min-height: 44px;
  padding: 0 14px;
  background: var(--panel-soft);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.table-body {
  display: block;
}

.table-row {
  min-height: 68px;
  padding: 10px 14px;
  border-top: 1px solid var(--line-soft);
  cursor: pointer;
  transition: background-color 0.22s ease;
}

.table-row:hover {
  background: var(--hover-row);
}

.col-index {
  font-size: 13px;
  color: var(--text-muted);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.col-title {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
}

.title-text {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.title-main {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-width: 0;
}

.col-title svg {
  width: 16px;
  height: 16px;
  color: #b37d47;
  flex-shrink: 0;
}

.pass-flag {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
  color: #1f6a42;
  background: rgba(73, 177, 121, 0.18);
  border: 1px solid rgba(73, 177, 121, 0.36);
  flex-shrink: 0;
}

.home-page.theme-dark .pass-flag {
  color: #aef5cd;
  background: rgba(73, 177, 121, 0.22);
  border-color: rgba(109, 219, 161, 0.42);
}

.problem-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  font-weight: 600;
}

.source-tag {
  height: 22px;
  border-radius: 999px;
  padding: 0 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  border: 1px solid var(--line-soft);
  color: var(--text-sub);
  background: var(--panel-soft);
  flex-shrink: 0;
}

.source-tag.ai {
  border-color: rgba(101, 141, 205, 0.45);
  background: rgba(101, 141, 205, 0.14);
  color: #31588f;
}

.source-tag.official {
  border-color: rgba(182, 138, 84, 0.42);
  background: rgba(182, 138, 84, 0.14);
  color: #875121;
}

.source-tag.square {
  border-color: rgba(86, 124, 188, 0.42);
  background: rgba(86, 124, 188, 0.14);
  color: #2f5786;
}

.home-page.theme-dark .source-tag.ai {
  border-color: rgba(125, 158, 219, 0.5);
  background: rgba(90, 126, 190, 0.24);
  color: #bdd4ff;
}

.home-page.theme-dark .source-tag.official {
  border-color: rgba(212, 168, 113, 0.5);
  background: rgba(156, 118, 71, 0.24);
  color: #ffd8aa;
}

.home-page.theme-dark .source-tag.square {
  border-color: rgba(128, 166, 224, 0.5);
  background: rgba(88, 129, 187, 0.24);
  color: #bdd4ff;
}

.difficulty-badge {
  justify-self: start;
  border-radius: 999px;
  height: 28px;
  min-width: 62px;
  padding: 0 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.difficulty-badge.easy {
  background: rgba(80, 169, 119, 0.18);
  color: #2a7449;
}

.difficulty-badge.medium {
  background: rgba(214, 158, 78, 0.2);
  color: #8e5b1d;
}

.difficulty-badge.hard {
  background: rgba(219, 86, 86, 0.18);
  color: #a03333;
}

.col-actions {
  justify-self: end;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  border: 0;
  height: 34px;
  border-radius: 10px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease, box-shadow 0.2s ease;
}

.action-btn.primary {
  background: linear-gradient(145deg, #83552b 0%, #ab7543 100%);
  color: #fff;
  box-shadow: 0 10px 20px rgba(105, 68, 35, 0.24);
}

.action-btn.secondary {
  border: 1px solid var(--line);
  background: transparent;
  color: var(--text-main);
}

.action-btn.tertiary {
  border: 1px solid rgba(88, 129, 187, 0.35);
  background: rgba(88, 129, 187, 0.12);
  color: #2f5786;
}

.home-page.theme-dark .action-btn.tertiary {
  border-color: rgba(128, 166, 224, 0.42);
  background: rgba(88, 129, 187, 0.24);
  color: #bdd4ff;
}

.action-btn.star {
  border: 1px solid rgba(214, 158, 78, 0.38);
  background: rgba(214, 158, 78, 0.14);
  color: #8e5b1d;
}

.home-page.theme-dark .action-btn.star {
  border-color: rgba(225, 178, 108, 0.46);
  background: rgba(180, 129, 57, 0.22);
  color: #f0ce9e;
}

.action-btn.danger {
  border: 1px solid rgba(177, 74, 74, 0.38);
  background: rgba(177, 74, 74, 0.12);
  color: #9c3a3a;
}

.home-page.theme-dark .action-btn.danger {
  border-color: rgba(216, 120, 120, 0.42);
  background: rgba(158, 74, 74, 0.22);
  color: #f2b5b5;
}

.action-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  transform: none;
}

.action-btn:hover {
  transform: translateY(-1px);
}

.skeleton-wrap {
  display: grid;
  gap: 10px;
}

.skeleton-row {
  border: 1px solid var(--line-soft);
  border-radius: 12px;
  min-height: 62px;
  display: grid;
  grid-template-columns: 68px 1fr 120px 286px;
  align-items: center;
  padding: 0 14px;
  background: var(--panel-soft);
}

.skeleton {
  border-radius: 999px;
  display: block;
  background: linear-gradient(90deg, rgba(209, 195, 177, 0.36) 25%, rgba(224, 212, 197, 0.72) 50%, rgba(209, 195, 177, 0.36) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s linear infinite;
}

.home-page.theme-dark .skeleton {
  background: linear-gradient(90deg, rgba(62, 72, 89, 0.48) 25%, rgba(82, 95, 116, 0.84) 50%, rgba(62, 72, 89, 0.48) 75%);
  background-size: 200% 100%;
}

.skeleton-sm {
  width: 34px;
  height: 10px;
}

.skeleton-lg {
  width: min(360px, 72%);
  height: 12px;
}

.skeleton-md {
  width: 66px;
  height: 24px;
}

.skeleton-btn {
  justify-self: end;
  width: 130px;
  height: 30px;
}

.empty-state {
  border-radius: 14px;
  border: 1px dashed var(--line);
  min-height: 220px;
  display: grid;
  place-items: center;
  color: var(--text-sub);
  gap: 10px;
  text-align: center;
  padding: 20px;
}

.empty-state svg {
  width: 46px;
  height: 46px;
  color: var(--text-muted);
}

.panel-switch-enter-active,
.panel-switch-leave-active {
  transition: opacity 0.24s ease, transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

.panel-switch-enter-from,
.panel-switch-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.row-fade-enter-active,
.row-fade-leave-active {
  transition: all 0.24s ease;
}

.row-fade-enter-from,
.row-fade-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

.row-fade-move {
  transition: transform 0.24s ease;
}

.status-fade-enter-active,
.status-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.status-fade-enter-from,
.status-fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

@media (prefers-reduced-motion: reduce) {
  .panel-switch-enter-active,
  .panel-switch-leave-active {
    transition: none;
  }

  .panel-switch-enter-from,
  .panel-switch-leave-to {
    opacity: 1;
    transform: none;
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

@keyframes card-up {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@keyframes pulse-dot {
  0%,
  100% {
    opacity: 0.45;
    transform: scale(0.9);
  }
  50% {
    opacity: 1;
    transform: scale(1.06);
  }
}

@media (max-width: 1180px) {
  .dashboard-shell {
    grid-template-columns: 84px 1fr;
  }

  .brand-name,
  .brand-sub,
  .nav-item span,
  .theme-toggle span {
    display: none;
  }

  .side-brand {
    justify-content: center;
    padding-left: 0;
    padding-right: 0;
  }

  .nav-item {
    justify-content: center;
    padding: 0;
  }

  .theme-toggle {
    padding: 0;
  }
}

@media (max-width: 980px) {
  .home-page {
    padding: 12px;
  }

  .bg-orb {
    display: none;
  }

  .dashboard-shell {
    min-height: calc(100vh - 24px);
    border-radius: 20px;
    grid-template-columns: 1fr;
  }

  .side-panel {
    border-right: 0;
    border-bottom: 1px solid var(--line);
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
  }

  .side-nav {
    display: flex;
    justify-content: flex-end;
    gap: 6px;
  }

  .nav-item {
    width: 42px;
    height: 42px;
    border: 1px solid var(--line);
    border-radius: 12px;
  }

  .nav-item-active {
    border-color: var(--accent);
  }

  .side-nav .nav-item:not(.logout-item) {
    display: none;
  }

  .theme-toggle {
    width: 42px;
    height: 42px;
    border-radius: 12px;
  }

  .top-bar {
    padding: 18px 16px;
  }

  .content-wrap {
    padding: 16px;
    padding-bottom: calc(92px + env(safe-area-inset-bottom, 0px));
  }

  .mobile-bottom-nav {
    display: grid;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .panel-head {
    flex-direction: column;
    align-items: stretch;
  }

  .panel-controls {
    width: 100%;
    display: grid;
    gap: 10px;
  }

  .source-tabs {
    width: 100%;
    min-width: 0;
  }

  .square-view-tabs {
    width: 100%;
    min-width: 0;
  }

  .square-toolbar {
    align-items: stretch;
  }

  .square-sort {
    width: 100%;
    justify-content: space-between;
  }

  .square-sort select {
    width: 100%;
  }

  .wrongbook-controls {
    align-items: stretch;
  }

  .wrongbook-controls label {
    width: 100%;
  }

  .wrongbook-controls input[type="text"] {
    width: 100%;
  }

  .generation-hint {
    margin: 10px 12px 0;
  }

  .profile-head .action-btn {
    width: 100%;
  }

  .filter-box select {
    width: 100%;
  }

  .ai-mode-switch {
    max-width: 100%;
  }

  .ai-generate-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .dual-problem-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .top-actions .ghost-action {
    display: none;
  }

  .headline h1 {
    font-size: 1.45rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .level-control {
    grid-template-columns: 30px 1fr 30px auto;
  }

  .ai-generate-row {
    grid-template-columns: 1fr;
  }

  .profile-grid {
    grid-template-columns: 1fr;
  }

  .square-card-head {
    flex-direction: column;
  }

  .square-meta {
    justify-items: start;
  }

  .square-meta-metrics {
    justify-content: flex-start;
  }

  .square-actions {
    display: grid;
  }

  .wrongbook-actions {
    display: grid;
  }

  .source-tab {
    width: 100%;
  }

  .square-view-tabs {
    width: 100%;
  }

  .square-sort {
    width: 100%;
  }

  .generation-hint {
    grid-template-columns: auto 1fr auto;
    row-gap: 4px;
  }

  .generation-hint strong {
    grid-column: 2 / 3;
  }

  .generation-detail {
    grid-column: 1 / 3;
    white-space: normal;
    line-height: 1.4;
  }

  .table-head {
    display: none;
  }

  .table-row {
    grid-template-columns: 1fr;
    align-items: start;
    gap: 10px;
    padding: 14px;
  }

  .problem-column .table-row {
    grid-template-columns: 1fr;
    align-items: start;
    gap: 10px;
    padding: 14px;
  }

  .col-index {
    display: none;
  }

  .problem-title {
    white-space: normal;
    line-height: 1.5;
  }

  .col-actions {
    justify-self: start;
  }

  .skeleton-row {
    grid-template-columns: 1fr;
    gap: 10px;
    padding: 12px;
  }

  .skeleton-sm {
    width: 50px;
  }

  .skeleton-lg,
  .skeleton-md,
  .skeleton-btn {
    width: 100%;
    justify-self: stretch;
  }
}
</style>
