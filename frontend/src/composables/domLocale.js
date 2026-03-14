import { watch } from 'vue'
import { locale } from '@/composables/locale'

const TRANSLATABLE_ATTRS = ['placeholder', 'title', 'aria-label']

const textNodeOriginMap = new WeakMap()
const attrOriginMap = new WeakMap()

let mutationObserver = null
let refreshScheduled = false
let stopLocaleWatch = null

const directTranslations = [
  ['算法练习平台', 'Algorithm Practice Platform'],
  ['在线算法训练空间', 'Online Algorithm Training Space'],
  ['稳定节奏，', 'Steady rhythm,'],
  ['把注意力留给题目。', 'Keep your focus on problems.'],
  ['从登录开始就进入专注状态。页面保持简洁，信息有层次，动效柔和而不打扰。', 'Enter focus mode from login. Clean layout, structured info, and gentle motion.'],
  ['欢迎回来', 'Welcome Back'],
  ['创建账户', 'Create Account'],
  ['登录后继续你的刷题进度。', 'Sign in to continue your progress.'],
  ['注册后即可进入题库开始训练。', 'Sign up to enter the problem bank.'],
  ['登录', 'Login'],
  ['注册', 'Register'],
  ['邮箱地址', 'Email'],
  ['请输入常用邮箱', 'Enter your email'],
  ['登录密码', 'Password'],
  ['请输入密码', 'Enter password'],
  ['隐藏', 'Hide'],
  ['显示', 'Show'],
  ['忘记密码？', 'Forgot password?'],
  ['登录中', 'Signing in...'],
  ['进入工作台', 'Enter Workspace'],
  ['用户名', 'Username'],
  ['3-50 位，字母开头', '3-50 chars, starts with a letter'],
  ['请输入邮箱', 'Enter email'],
  ['发送验证码', 'Send Code'],
  ['验证码', 'Verification Code'],
  ['请输入 6 位验证码', 'Enter 6-digit code'],
  ['设置密码', 'Set Password'],
  ['至少 8 位', 'At least 8 characters'],
  ['确认密码', 'Confirm Password'],
  ['请再次输入', 'Enter again'],
  ['注册中', 'Registering...'],
  ['还没有账户？', "Don't have an account?"],
  ['已经有账户？', 'Already have an account?'],
  ['去注册', 'Sign Up'],
  ['返回登录', 'Back to Login'],
  ['邮箱重置密码', 'Reset Password by Email'],
  ['关闭', 'Close'],
  ['请输入注册邮箱', 'Enter your registered email'],
  ['新密码', 'New Password'],
  ['至少 8 位，含字母和数字', 'At least 8 chars with letters and numbers'],
  ['确认新密码', 'Confirm New Password'],
  ['重置中', 'Resetting...'],
  ['确认重置密码', 'Confirm Password Reset'],
  ['返回首页', 'Home'],
  ['个人设置', 'Settings'],
  ['个人资料', 'Profile'],
  ['退出登录', 'Logout'],
  ['退出', 'Logout'],
  ['切换浅色', 'Switch to Light'],
  ['切换深色', 'Switch to Dark'],
  ['浅色', 'Light'],
  ['深色', 'Dark'],
  ['题库列表', 'Problem List'],
  ['题库题', 'Official Problems'],
  ['AI 出题', 'AI Generator'],
  ['题目广场', 'Square'],
  ['欢迎回来，', 'Welcome back, '],
  ['题库已通过', 'Passed'],
  ['题库总题', 'Total'],
  ['题库完成率', 'Completion'],
  ['题库待完成', 'Remaining'],
  ['可按刷题进度估计水平，或手动设定 1-10 级难度。', 'Estimate by progress or set difficulty level 1-10 manually.'],
  ['按进度估计', 'By Progress'],
  ['自定义难度', 'Custom Level'],
  ['系统会基于你的 AC 题量、完成率和难度分布估计等级后出题。', 'AI estimates level from your AC count, completion rate, and difficulty mix.'],
  ['难度等级（1-10）', 'Difficulty Level (1-10)'],
  ['AI 出题中...', 'Generating...'],
  ['生成新题', 'Generate New'],
  ['立即做题', 'Start Solving'],
  ['前往题库列表', 'Go to Problem List'],
  ['已耗时 ', 'Elapsed '],
  ['AI 私有', 'AI Private'],
  ['等级 L', 'Level L'],
  ['分享你已通过的 AI 私有题，也可以把别人的优质题导入到自己的题库。', 'Share your passed AI private problems and import quality problems from others.'],
  ['刷新广场', 'Refresh'],
  ['广场', 'Square'],
  ['我的分享', 'My Shares'],
  ['排序', 'Sort'],
  ['发布日期', 'Publish Date'],
  ['广场共享', 'Shared'],
  ['分享者：', 'Author: '],
  ['已导入：', 'Imports: '],
  ['发布：', 'Published: '],
  ['暂无题干预览', 'No description preview'],
  ['查看题目', 'View'],
  ['取消中...', 'Canceling...'],
  ['取消分享', 'Unshare'],
  ['Star 中...', 'Starring...'],
  ['已 Star', 'Starred'],
  ['前往我的题库做题', 'Solve in My List'],
  ['导入中...', 'Importing...'],
  ['本人已分享', 'Already Shared'],
  ['已导入', 'Imported'],
  ['导入到我的题库', 'Import to My List'],
  ['这里展示你的账号信息，点击右上角可进入详细设置。', 'Your account info is shown here. Click top-right for detailed settings.'],
  ['前往个人设置', 'Go to Settings'],
  ['未绑定邮箱', 'No email bound'],
  ['用户角色', 'Role'],
  ['账号状态', 'Status'],
  ['按难度筛选并快速进入做题或讨论。', 'Filter by difficulty and jump to solving or discussion quickly.'],
  ['题目来源切换', 'Problem Source Switch'],
  ['难度', 'Difficulty'],
  ['全部难度', 'All Difficulties'],
  ['简单', 'Easy'],
  ['中等', 'Medium'],
  ['困难', 'Hard'],
  ['当前正在 AI 生题中', 'AI is generating problems'],
  ['标题', 'Title'],
  ['操作', 'Actions'],
  ['已通过', 'Passed'],
  ['广场导入', 'Imported from Square'],
  ['做题', 'Solve'],
  ['讨论', 'Discuss'],
  ['已分享', 'Shared'],
  ['分享中...', 'Sharing...'],
  ['分享到广场', 'Share to Square'],
  ['先通过再分享', 'Pass before sharing'],
  ['删除中...', 'Deleting...'],
  ['删除', 'Delete'],
  ['管理员', 'Admin'],
  ['普通用户', 'User'],
  ['已禁用', 'Disabled'],
  ['正常', 'Normal'],
  ['通过 AI 生成适配你当前水平的训练题目。', 'Generate practice problems matched to your level with AI.'],
  ['分享你已通过的 AI 私有题，导入别人精选题目。', 'Share passed AI private problems and import selected ones from others.'],
  ['查看你的账号信息，或前往设置页更新资料。', 'Check your account info or go to settings to update it.'],
  ['继续今天的训练，保持稳定节奏。', 'Keep training today and stay in rhythm.'],
  ['生成完成后会自动同步到题库列表。', 'Generated problem will be synced to your list automatically.'],
  ['偏基础，适合巩固语法和常见思路', 'Basic level, good for syntax and common patterns'],
  ['中等综合，强调数据结构和复杂度控制', 'Intermediate level, focuses on data structures and complexity'],
  ['偏高难，强调抽象建模和边界处理', 'Advanced level, focuses on modeling and edge cases'],
  ['当前筛选下暂无题库题', 'No official problems under current filters'],
  ['当前筛选下暂无 AI 私有题', 'No AI private problems under current filters'],
  ['题库', 'Official'],
  ['你还没有分享题目，先在 AI 私有题中通过后再分享。', "You haven't shared any problem yet. Pass an AI private problem first."],
  ['广场还没有可导入题目，稍后再来看看。', 'No importable problems in square yet. Check back later.'],
  ['正在整理出题参数...', 'Preparing generation parameters...'],
  ['正在调用 AI 模型生成题目...', 'Calling AI model to generate problem...'],
  ['正在校验题目结构与测试用例...', 'Validating structure and test cases...'],
  ['正在同步题目到你的私有题库...', 'Syncing problem to your private list...'],
  ['题目生成完成，已加入你的私有题库。', 'Generation completed. Added to your private list.'],
  ['题目生成失败，请稍后重试。', 'Generation failed. Please retry later.'],
  ['AI 服务响应较慢，已生成备用题目。', 'AI service is slow, fallback problem generated.'],
  ['出题成功：', 'Generated: '],
  ['已生成新题', 'New problem generated'],
  ['AI 出题失败', 'Generation failed'],
  ['AI 出题失败，请稍后重试', 'Generation failed, please retry later'],
  ['确定删除「', 'Delete "'],
  ['」吗？删除后不可恢复。', '"? This action cannot be undone.'],
  ['已删除：', 'Deleted: '],
  ['删除失败', 'Delete failed'],
  ['删除失败，请稍后重试', 'Delete failed, please retry later'],
  ['该题已在广场中', 'This problem is already shared in square'],
  ['请先通过该题后再分享', 'Pass this problem before sharing'],
  ['确定将「', 'Share "'],
  ['该题', 'this problem'],
  ['」分享到广场吗？', '" to square?'],
  ['分享成功', 'Shared successfully'],
  ['分享失败', 'Share failed'],
  ['分享失败，请稍后重试', 'Share failed, please retry later'],
  ['不能导入自己分享的题目', "You can't import your own shared problem"],
  ['导入成功', 'Imported successfully'],
  ['导入失败', 'Import failed'],
  ['导入失败，请稍后重试', 'Import failed, please retry later'],
  ['你已 Star 过该题', 'You already starred this problem'],
  ['Star 成功', 'Star success'],
  ['Star 失败', 'Star failed'],
  ['Star 失败，请稍后重试', 'Star failed, please retry later'],
  ['确定取消分享「', 'Unshare "'],
  ['」吗？', '"?'],
  ['已取消分享', 'Unshared'],
  ['取消分享失败', 'Unshare failed'],
  ['取消分享失败，请稍后重试', 'Unshare failed, please retry later'],
  ['加载题目中...', 'Loading problem...'],
  ['正在加载题目内容...', 'Loading problem content...'],
  ['题库题', 'Official'],
  ['时间 ', 'Time '],
  ['内存 ', 'Memory '],
  ['暂无题目描述', 'No problem description'],
  ['示例测试用例', 'Sample Test Cases'],
  [' 个', ' items'],
  ['用例 ', 'Case '],
  ['公开', 'Public'],
  ['输入', 'Input'],
  ['输出', 'Output'],
  ['写代码区', 'Code Editor'],
  ['先运行，再提交，快速验证思路与边界条件。', 'Run first, then submit to validate ideas and edge cases quickly.'],
  [' 行', ' lines'],
  [' 字符', ' chars'],
  ['语言', 'Language'],
  ['恢复模板', 'Reset Template'],
  ['运行中...', 'Running...'],
  ['运行代码', 'Run Code'],
  ['提交中...', 'Submitting...'],
  ['提交判题', 'Submit'],
  ['Tab 触发智能补全', 'Tab to trigger completion'],
  ['支持 Python / JavaScript / Java', 'Supports Python / JavaScript / Java'],
  ['拖动下方分割条可自由调节代码区高度', 'Drag the splitter below to resize the editor freely'],
  ['判题详情', 'Judge Details'],
  ['点击“运行代码”或“提交判题”查看结果', 'Click "Run Code" or "Submit" to view results'],
  ['判题执行中，请稍候...', 'Judging, please wait...'],
  ['通过 ', 'Passed '],
  ['耗时 ', 'Time '],
  ['峰值 ', 'Peak '],
  ['输出预览', 'Output Preview'],
  ['期望', 'Expected'],
  ['实际输出', 'Actual Output'],
  ['(无输出)', '(No output)'],
  ['错误信息', 'Error'],
  ['提交成功', 'Submitted Successfully'],
  ['所有测试用例通过，继续保持这个节奏。', 'All test cases passed. Keep the momentum.'],
  ['继续在当前题目', 'Stay on This Problem'],
  ['请先编写代码', 'Please write code first'],
  ['判题失败，请稍后重试', 'Judge failed, please retry later'],
  ['确定恢复当前语言默认模板吗？当前代码会被覆盖。', 'Reset to default template for this language? Current code will be overwritten.'],
  ['定义函数', 'Define function'],
  ['for 循环', 'for loop'],
  ['主入口', 'Entry point'],
  ['主函数', 'Main function'],
  ['题目讨论区', 'Problem Discussion'],
  ['返回', 'Back'],
  ['发布讨论', 'Post Discussion'],
  ['分享你的思路、坑点或优化方向', 'Share ideas, pitfalls, or optimization directions'],
  ['描述你的想法：比如如何拆解问题、为什么会超时、怎么优化...', 'Describe your thoughts: decomposition, timeout reasons, and optimization...'],
  ['支持普通文本，建议分段表达更清晰。', 'Plain text is supported. Paragraphs are recommended for clarity.'],
  ['发布中...', 'Posting...'],
  ['讨论列表', 'Discussion Threads'],
  ['加载讨论中...', 'Loading discussions...'],
  ['还没有讨论内容，来发表第一条观点。', 'No discussion yet. Be the first to share your thoughts.'],
  ['匿名用户', 'Anonymous'],
  ['回复 ', 'Replies '],
  ['用户', 'User'],
  ['添加回复...', 'Add a reply...'],
  ['回复', 'Reply'],
  ['刚刚', 'Just now'],
  ['分钟前', 'm ago'],
  ['小时前', 'h ago'],
  ['确定要删除这条帖子吗？', 'Delete this post?'],
  ['删除评论失败', 'Delete comment failed'],
  ['删除评论失败，请稍后重试', 'Delete comment failed, please retry later'],
  ['确定要删除这条评论吗？', 'Delete this comment?'],
  ['个人设置', 'Settings'],
  ['资料设置', 'Profile Settings'],
  ['更新昵称并保持账号信息一致。', 'Update nickname and keep account information consistent.'],
  ['输入新的用户名', 'Enter new username'],
  ['邮箱', 'Email'],
  ['保存中...', 'Saving...'],
  ['保存资料', 'Save Profile'],
  ['修改密码', 'Change Password'],
  ['建议使用字母+数字的强密码，至少 8 位。', 'Use a strong password with letters and numbers, at least 8 chars.'],
  ['当前密码', 'Current Password'],
  ['输入当前密码', 'Enter current password'],
  ['输入新密码', 'Enter new password'],
  ['再次输入新密码', 'Re-enter new password'],
  ['修改中...', 'Updating...'],
  ['更新密码', 'Update Password'],
  ['注销账号', 'Delete Account'],
  ['通过邮箱验证码确认后，将永久删除当前账号及其关联数据。', 'After email verification, this account and related data will be permanently deleted.'],
  ['注销后不可恢复。你的提交记录、讨论内容以及 AI 私有题将被清理。', 'This action cannot be undone. Submissions, discussions, and AI private problems will be removed.'],
  ['邮箱验证码', 'Email Verification Code'],
  ['输入 6 位验证码', 'Enter 6-digit code'],
  [' 后重发', 's to resend'],
  ['发送中...', 'Sending...'],
  ['注销中...', 'Deleting...'],
  ['确认注销账号', 'Confirm Account Deletion'],
  ['用户名至少需要3个字符', 'Username must be at least 3 characters'],
  ['保存成功', 'Saved successfully'],
  ['保存失败，请稍后重试', 'Save failed, please retry later'],
  ['请填写所有密码字段', 'Please fill all password fields'],
  ['新密码至少需要8个字符', 'New password must be at least 8 characters'],
  ['两次密码输入不一致', 'Passwords do not match'],
  ['密码修改成功', 'Password updated successfully'],
  ['修改失败，请稍后重试', 'Update failed, please retry later'],
  ['注销验证码已发送到注册邮箱', 'Deletion code sent to your registered email'],
  ['发送失败，请稍后重试', 'Send failed, please retry later'],
  ['请输入 6 位数字验证码', 'Please enter a 6-digit numeric code'],
  ['注销后将删除账号及关联数据，且不可恢复。确认继续吗？', 'This will delete your account and related data permanently. Continue?'],
  ['账号已注销，正在退出登录...', 'Account deleted, signing out...'],
  ['注销失败，请稍后重试', 'Deletion failed, please retry later'],
  ['收起', 'Collapse'],
  ['展开', 'Expand'],
  ['AI 导师', 'AI Tutor'],
  ['引导式提示，不直接给完整答案', 'Guided hints, no full direct answer'],
  ['在线', 'Online'],
  ['开始提问', 'Start Asking'],
  ['你可以问思路、边界条件、复杂度、调试方向，我会按步骤引导。', 'Ask about ideas, edge cases, complexity, or debugging. I will guide step by step.'],
  ['输入你的问题，按 Enter 发送，Shift + Enter 换行', 'Type your question, Enter to send, Shift+Enter for newline'],
  ['发送', 'Send'],
  ['发送中...', 'Sending...'],
  ['题目描述和你的代码已加载。你可以先问：当前思路哪里可能有漏洞？边界条件应该补哪些？复杂度是否可优化？', 'Problem and code loaded. You can ask: where is the logic weak? what edge cases are missing? can complexity be optimized?'],
  ['当前没有收到有效内容，请重试一次。', 'No valid content received. Please retry.'],
  ['当前服务暂时不可用，请稍后重试。', 'Service is temporarily unavailable. Please retry later.']
]

const sortedTranslations = [...directTranslations].sort((a, b) => b[0].length - a[0].length)

const toEnglish = (sourceText) => {
  if (!sourceText) return sourceText
  let output = sourceText
  for (const [zhText, enText] of sortedTranslations) {
    if (!zhText || !enText) continue
    if (!output.includes(zhText)) continue
    output = output.split(zhText).join(enText)
  }
  return output
}

const localizeText = (sourceText, lang) => (lang === 'en' ? toEnglish(sourceText) : sourceText)

const localizeTextNode = (textNode, lang) => {
  if (!textNode || textNode.nodeType !== Node.TEXT_NODE) return
  const currentText = textNode.nodeValue || ''
  const originalText = textNodeOriginMap.has(textNode)
    ? textNodeOriginMap.get(textNode)
    : currentText

  if (!textNodeOriginMap.has(textNode)) {
    textNodeOriginMap.set(textNode, originalText)
  }

  const nextText = localizeText(originalText, lang)
  if (nextText !== textNode.nodeValue) {
    textNode.nodeValue = nextText
  }
}

const localizeElementAttributes = (element, lang) => {
  if (!(element instanceof HTMLElement)) return
  for (const attr of TRANSLATABLE_ATTRS) {
    if (!element.hasAttribute(attr)) continue
    const currentValue = element.getAttribute(attr) || ''
    let originalMap = attrOriginMap.get(element)
    if (!originalMap) {
      originalMap = new Map()
      attrOriginMap.set(element, originalMap)
    }
    if (!originalMap.has(attr)) {
      originalMap.set(attr, currentValue)
    }
    const originalValue = originalMap.get(attr) || ''
    const nextValue = localizeText(originalValue, lang)
    if (nextValue !== currentValue) {
      element.setAttribute(attr, nextValue)
    }
  }
}

const localizeSubtree = (root, lang) => {
  if (!root) return

  if (root.nodeType === Node.TEXT_NODE) {
    localizeTextNode(root, lang)
    return
  }

  if (root.nodeType === Node.ELEMENT_NODE) {
    localizeElementAttributes(root, lang)
  }

  const walker = document.createTreeWalker(
    root,
    NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT
  )
  while (walker.nextNode()) {
    const node = walker.currentNode
    if (node.nodeType === Node.TEXT_NODE) {
      localizeTextNode(node, lang)
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      localizeElementAttributes(node, lang)
    }
  }
}

const scheduleRefresh = () => {
  if (refreshScheduled) return
  refreshScheduled = true
  requestAnimationFrame(() => {
    refreshScheduled = false
    if (typeof document === 'undefined') return
    localizeSubtree(document.body, locale.value)
  })
}

export const initDomLocale = () => {
  if (typeof window === 'undefined' || typeof document === 'undefined') return

  if (stopLocaleWatch) {
    stopLocaleWatch()
    stopLocaleWatch = null
  }
  if (mutationObserver) {
    mutationObserver.disconnect()
    mutationObserver = null
  }

  stopLocaleWatch = watch(
    locale,
    () => {
      scheduleRefresh()
    },
    { immediate: true }
  )

  mutationObserver = new MutationObserver(() => {
    scheduleRefresh()
  })

  mutationObserver.observe(document.body, {
    childList: true,
    subtree: true,
    characterData: true,
    attributes: true,
    attributeFilter: TRANSLATABLE_ATTRS
  })
}
