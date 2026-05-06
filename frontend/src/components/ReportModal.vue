<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-2 backdrop-blur-sm sm:p-4 animate-fadeIn" @click="handleOverlayClick">
      <div 
        class="report-reader max-h-[95vh] w-full max-w-6xl overflow-hidden flex flex-col animate-fadeInUp shadow-2xl"
        @click.stop
      >
        <!-- 模态框头部 -->
        <header class="relative border-b border-slate-800 bg-slate-950/90 p-4 lg:p-5">
          <div class="flex justify-between items-center">
              <div class="flex items-center space-x-3 lg:space-x-4 flex-1 min-w-0">
                <div class="flex h-10 w-10 flex-shrink-0 items-center justify-center border border-cyan-400/30 bg-cyan-400/10 text-cyan-300 lg:h-11 lg:w-11">
                  <svg class="h-5 w-5 lg:h-6 lg:w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
                <div class="min-w-0 flex-1">
                  <p class="mb-1 text-[10px] uppercase tracking-[0.22em] text-cyan-400/80">INTELLIGENCE REPORT</p>
                  <h3 class="truncate text-lg font-semibold text-slate-100 lg:text-2xl">
                    GitHub 热门项目报告
                  </h3>
                  <p class="mt-1 truncate text-xs text-slate-500 lg:text-sm">
                    {{ formatDate(report.date) }}
                  </p>
                </div>
              </div>
            
            <div class="flex items-center space-x-2 lg:space-x-3 flex-shrink-0">
              <!-- 关闭按钮 -->
              <button
                @click="$emit('close')"
                class="reader-icon-button hover:bg-red-500/10 hover:border-red-500/30 hover:text-red-300"
                title="关闭"
              >
                <svg class="w-4 h-4 lg:w-5 lg:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
          
          <!-- 进度条 -->
          <div class="absolute bottom-0 left-0 h-0.5 w-full bg-slate-800">
            <div 
              class="h-full bg-cyan-300 transition-all duration-300 ease-out"
              :style="{ width: scrollProgress + '%' }"
            ></div>
          </div>
        </header>

        <!-- 模态框内容 -->
        <main 
          ref="contentContainer"
          class="flex-grow overflow-y-auto relative"
          @scroll="updateScrollProgress"
        >
          <div v-if="loading" class="h-full flex flex-col items-center justify-center py-20">
            <div class="relative mb-8">
              <div class="w-16 h-16 border-4 border-blue-500/30 rounded-full animate-spin"></div>
              <div class="absolute top-0 left-0 w-16 h-16 border-4 border-transparent border-t-blue-500 rounded-full animate-spin"></div>
            </div>
            <h4 class="text-lg font-medium text-slate-300 mb-2">加载中</h4>
            <p class="text-slate-400">正在解析报告内容...</p>
          </div>
          
          <div v-else class="p-4 lg:p-6">
            <!-- 报告统计信息 -->
            <div class="mb-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
              <div class="reader-stat">
                <div class="stat-value">{{ report.project_count }}</div>
                <div class="stat-label">项目数量</div>
              </div>
              <div class="reader-stat">
                <div class="stat-value">{{ wordCount.toLocaleString() }}</div>
                <div class="stat-label">字数统计</div>
              </div>
              <div class="reader-stat">
                <div class="stat-value">{{ readingTime }}</div>
                <div class="stat-label">阅读时间</div>
              </div>
              <div class="reader-stat">
                <div class="stat-value">{{ formatDate(report.date).split(' ')[0] }}</div>
                <div class="stat-label">发布日期</div>
              </div>
            </div>
            

            
            <!-- Markdown 内容 -->
            <div 
              ref="markdownContainer"
              class="markdown-content prose prose-invert max-w-none border border-slate-800 bg-slate-950/55 p-4 text-sm lg:p-6 lg:text-base"
              v-html="renderedContent"
            ></div>
          </div>
          
          <!-- 返回顶部按钮 - 移至左下角避免与导出按钮重叠 -->
          <!-- <button 
            v-show="showBackToTop"
            @click="scrollToTop"
            class="fixed bottom-8 left-8 btn-primary w-12 h-12 rounded-full shadow-lg animate-bounce-gentle z-10"
            title="返回顶部"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12"></path>
            </svg>
          </button> -->
        </main>

        <!-- 模态框底部 -->
        <footer class="border-t border-slate-800 bg-slate-950/90 p-4 lg:p-5">
          <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center space-y-4 lg:space-y-0">
            <div class="flex flex-wrap items-center gap-4 lg:gap-6 text-xs lg:text-sm text-slate-400">
              <div class="flex items-center space-x-1 lg:space-x-2">
                <svg class="w-3 h-3 lg:w-4 lg:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                </svg>
                <span>{{ report.project_count }} 个项目</span>
              </div>
              <div class="flex items-center space-x-1 lg:space-x-2">
                <svg class="w-3 h-3 lg:w-4 lg:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                </svg>
                <span>{{ wordCount.toLocaleString() }} 字</span>
              </div>
              <div class="flex items-center space-x-1 lg:space-x-2">
                <svg class="w-3 h-3 lg:w-4 lg:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>{{ readingTime }}</span>
              </div>
            </div>
            
            <div class="flex flex-wrap gap-2 lg:gap-3 w-full lg:w-auto">
              <button
                @click="copyToClipboard"
                :class="['reader-action flex-1 lg:flex-none text-xs lg:text-sm transition-colors duration-300', isCopying ? 'bg-green-600/20 border-green-500/50 text-green-200' : '']"
                title="复制到剪贴板"
                :disabled="isCopying"
              >
                <svg class="w-3 h-3 lg:w-4 lg:h-4 mr-1 lg:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
                {{ isCopying ? '已复制!' : '复制' }}
              </button>
              
              <div class="relative" ref="exportDropdown">
                <button
                  @click="showExportMenu = !showExportMenu"
                  class="reader-action primary flex-1 lg:flex-none text-xs lg:text-sm"
                  title="导出报告"
                >
                  <svg class="w-3 h-3 lg:w-4 lg:h-4 mr-1 lg:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  导出
                  <svg class="w-3 h-3 lg:w-4 lg:h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                  </svg>
                </button>
                
                <!-- 导出菜单 -->
                <div v-if="showExportMenu" class="absolute bottom-full right-0 mb-2 w-48 border border-slate-700 bg-slate-950 py-2 shadow-xl">
                  <button @click="exportReport('md')" class="export-menu-item">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    Markdown 格式
                  </button>
                  <button @click="exportReport('html')" class="export-menu-item">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
                    </svg>
                    HTML 格式
                  </button>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import type { Report } from '../api/reports'
import { copyReport, getRateLimitStatus } from '../api/reports'
import { renderMarkdown, enhanceMarkdownDisplay } from '../utils/markdown-simple'

// Props
const props = defineProps<{
  report: Report
  theme: 'light' | 'dark' // Add theme prop
}>()

// Emits
const emit = defineEmits<{
  close: []
}>()

// 响应式数据
const loading = ref(false)
const markdownContainer = ref<HTMLElement>()
const isCopying = ref(false)
const contentContainer = ref<HTMLElement>()
const exportDropdown = ref<HTMLElement>()
const showExportMenu = ref(false)
const scrollProgress = ref(0)
const showBackToTop = ref(false)

// 使用ref存储渲染后的内容
const renderedContent = ref('<p class="text-slate-400">暂无报告内容</p>')

const wordCount = computed(() => {
  if (!props.report.content) return 0
  return props.report.content.replace(/\s/g, '').length
})

const readingTime = computed(() => {
  const wordsPerMinute = 300 // 中文阅读速度
  const minutes = Math.ceil(wordCount.value / wordsPerMinute)
  return minutes + ' 分钟'
})

// 异步渲染Markdown内容
async function updateRenderedContent(content: string) {
  if (!content) {
    renderedContent.value = '<p class="text-slate-400">暂无报告内容</p>'
    return
  }
  try {
    const html = await renderMarkdown(content)
    renderedContent.value = html
  } catch (error) {
    console.error('渲染Markdown内容失败:', error)
    renderedContent.value = `<div class="text-red-500 p-4 border border-red-200 rounded-lg bg-red-50">渲染失败: ${error}</div>`
  }
}

// 监听报告内容变化
watch(() => props.report.content, async (newContent: string | undefined) => {
  await updateRenderedContent(newContent || '')
}, { immediate: true })

// 生命周期钩子
onMounted(async () => {
  // 添加事件监听器
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('click', handleOutsideClick)
  
  // 防止背景滚动
  document.body.style.overflow = 'hidden'
  
  // 等待DOM渲染完成后增强Markdown显示效果
  await nextTick()
  if (markdownContainer.value) {
    enhanceMarkdownDisplay(markdownContainer.value)
  }
})

onUnmounted(() => {
  // 清理事件监听器
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('click', handleOutsideClick)
  
  // 恢复背景滚动
  document.body.style.overflow = ''
})

// 事件处理函数
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    emit('close')
  }
}

// 点击背景遮罩层关闭模态框
function handleOverlayClick() {
  emit('close')
}

function handleOutsideClick(e: Event) {
  // 处理导出菜单关闭
  if (showExportMenu.value && exportDropdown.value && !exportDropdown.value.contains(e.target as Node)) {
    showExportMenu.value = false
  }
  
  // 处理点击模态框外部关闭整个模态框
  const targetElement = e.target as HTMLElement
  
  // 获取模态框背景遮罩层
  const modalOverlay = document.querySelector('.fixed.inset-0')
  
  // 获取模态框内容区域
  const modalContent = document.querySelector('.report-reader')
  
  // 当点击的是背景遮罩层，且不是点击在内容区域上时，关闭模态框
  if (modalOverlay && modalContent && 
      (targetElement === modalOverlay || modalOverlay.contains(targetElement)) && 
      !modalContent.contains(targetElement)) {
    emit('close')
  }
}

function updateScrollProgress() {
  if (!contentContainer.value) return
  
  const { scrollTop, scrollHeight, clientHeight } = contentContainer.value
  const progress = (scrollTop / (scrollHeight - clientHeight)) * 100
  scrollProgress.value = Math.min(100, Math.max(0, progress))
  
  // 显示/隐藏返回顶部按钮
  showBackToTop.value = scrollTop > 300
}

function scrollToTop() {
  if (contentContainer.value) {
    contentContainer.value.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }
}


// 工具函数
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
}

async function exportReport(format: 'md' | 'html' = 'md') {
  // 先检查限流状态
  try {
    const status = await getRateLimitStatus()
    if (status.export.remaining <= 0) {
      alert('导出次数已达上限（每天5次），请明天再试')
      return
    }
  } catch (e) {
    console.warn('获取限流状态失败，继续尝试导出')
  }

  if (!props.report.content) return
  
  let content: string
  let mimeType: string
  let extension: string
  
  switch (format) {
    case 'html':
      // 使用简单的字符串拼接避免模板字符串解析问题
      let htmlContent = ''
      htmlContent += '<!DOCTYPE html>\n'
      htmlContent += '<html lang="zh-CN">\n'
      htmlContent += '<head>\n'
      htmlContent += '  <meta charset="UTF-8">\n'
      htmlContent += '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
      htmlContent += '  <title>GitHub 热门项目报告 - ' + props.report.date + '</title>\n'
      htmlContent += '  <style>\n'
      htmlContent += '    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }\n'
      htmlContent += '    h1, h2, h3, h4, h5, h6 { color: #2c3e50; margin-top: 1.5em; margin-bottom: 0.5em; }\n'
      htmlContent += '    p { margin: 1em 0; }\n'
      htmlContent += '    code { background: #f4f4f4; padding: 2px 4px; border-radius: 3px; font-family: "Consolas", "Monaco", monospace; }\n'
      htmlContent += '    pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }\n'
      htmlContent += '    pre code { background: transparent; padding: 0; }\n'
      htmlContent += '    a { color: #3498db; text-decoration: none; }\n'
      htmlContent += '    a:hover { text-decoration: underline; }\n'
      htmlContent += '    blockquote { border-left: 4px solid #ddd; padding-left: 1em; margin: 1em 0; color: #666; }\n'
      htmlContent += '    ul, ol { margin: 1em 0; padding-left: 2em; }\n'
      htmlContent += '    li { margin: 0.5em 0; }\n'
      htmlContent += '    img { max-width: 100%; height: auto; }\n'
      htmlContent += '    table { border-collapse: collapse; width: 100%; margin: 1em 0; }\n'
      htmlContent += '    th, td { padding: 8px 12px; border: 1px solid #ddd; text-align: left; }\n'
      htmlContent += '    th { background-color: #f4f4f4; }\n'
      htmlContent += '  </style>\n'
      htmlContent += '</head>\n'
      htmlContent += '<body>\n'
      htmlContent += renderedContent.value + '\n'
      htmlContent += '</body>\n'
      htmlContent += '</html>'
      
      content = htmlContent
      mimeType = 'text/html'
      extension = 'html'
      break
    default:
      content = props.report.content
      mimeType = 'text/markdown'
      extension = 'md'
  }
  
  const blob = new Blob([content], { type: mimeType + ';charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'github_trending_' + props.report.date + '.' + extension
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  showExportMenu.value = false
  console.log('📥 报告已导出为 ' + format.toUpperCase() + ' 格式')
}

async function copyToClipboard() {
  // 先检查限流状态
  try {
    const status = await getRateLimitStatus()
    if (status.copy.remaining <= 0) {
      alert('复制次数已达上限（每天5次），请明天再试')
      return
    }
  } catch (e) {
    console.warn('获取限流状态失败，继续尝试复制')
  }

  try {
    // 使用带限流的 API 获取内容
    const result = await copyReport(props.report.date)
    await navigator.clipboard.writeText(result.content)
    console.log('📋 内容已复制到剪贴板')

    // 设置复制状态为成功
    isCopying.value = true

    // 2秒后恢复原始状态
    setTimeout(() => {
      isCopying.value = false
    }, 2000)
  } catch (err: any) {
    console.error('复制失败:', err)

    // 处理限流错误
    if (err.response?.status === 429 || err.message?.includes('次数已达上限')) {
      alert(err.message || '复制次数已达上限，请明天再试')
    } else {
      alert('复制失败，请重试')
    }
  }
}

</script>

<style scoped>
  .report-reader {
    position: relative;
    border: 1px solid rgba(51, 65, 85, 0.95);
    background:
      linear-gradient(rgba(34, 211, 238, 0.035) 1px, transparent 1px),
      linear-gradient(90deg, rgba(34, 211, 238, 0.025) 1px, transparent 1px),
      #071019;
    background-size: 28px 28px;
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(148, 163, 184, 0.06);
  }

  .reader-icon-button {
    display: inline-flex;
    height: 2.25rem;
    width: 2.25rem;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(51, 65, 85, 0.9);
    background: rgba(15, 23, 42, 0.62);
    color: #94a3b8;
    transition: all 0.2s ease;
  }

  .reader-stat {
    border: 1px solid rgba(51, 65, 85, 0.84);
    background: rgba(15, 23, 42, 0.72);
    padding: 0.85rem;
    text-align: center;
  }

  .stat-value {
    margin-bottom: 0.3rem;
    overflow-wrap: anywhere;
    font-size: 1.35rem;
    font-weight: 600;
    color: #67e8f9;
  }

  .stat-label {
    font-size: 0.72rem;
    color: #64748b;
  }

  .reader-action {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(51, 65, 85, 0.95);
    background: rgba(15, 23, 42, 0.78);
    padding: 0.55rem 0.85rem;
    color: #cbd5e1;
    transition: all 0.2s ease;
  }

  .reader-action:hover {
    border-color: rgba(34, 211, 238, 0.38);
    color: #e0f2fe;
  }

  .reader-action.primary {
    border-color: rgba(34, 211, 238, 0.36);
    background: rgba(34, 211, 238, 0.12);
    color: #a5f3fc;
  }

  /* 增强markdown样式 */
  .markdown-content :deep(h1),
  .markdown-content :deep(h2),
  .markdown-content :deep(h3),
  .markdown-content :deep(h4),
  .markdown-content :deep(h5),
  .markdown-content :deep(h6) {
    color: #e2e8f0;
    margin-top: 1.5em;
    margin-bottom: 0.75em;
  }
  
  .markdown-content :deep(h1) {
    font-size: 1.8rem;
    border-bottom: 2px solid #475569;
    padding-bottom: 0.3em;
  }
  
  .markdown-content :deep(h2) {
    font-size: 1.5rem;
    border-bottom: 1px solid #475569;
    padding-bottom: 0.3em;
  }
  
  .markdown-content :deep(p) {
    margin: 1em 0;
    line-height: 1.7;
  }
  
  .markdown-content :deep(blockquote) {
    border-left: 4px solid #8b5cf6;
    padding-left: 1em;
    margin: 1em 0;
    color: #94a3b8;
    background-color: rgba(139, 92, 246, 0.1);
    padding: 1em;
    border-radius: 0 0.5rem 0.5rem 0;
  }
  
  .markdown-content :deep(ul),
  .markdown-content :deep(ol) {
    margin: 1em 0;
    padding-left: 2em;
  }
  
  .markdown-content :deep(li) {
    margin: 0.5em 0;
  }
  
  .markdown-content :deep(code) {
    background-color: #334155;
    color: #e2e8f0;
    padding: 0.2em 0.4em;
    border-radius: 0.375rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.875em;
  }
  
  .markdown-content :deep(pre) {
    background-color: #1e293b;
    padding: 1em;
    border-radius: 0.5rem;
    overflow-x: auto;
    margin: 1.5em 0;
  }
  
  .markdown-content :deep(pre code) {
    background-color: transparent;
    padding: 0;
    display: block;
    line-height: 1.5;
  }
  
  .markdown-content :deep(a) {
    color: #8b5cf6;
    text-decoration: none;
    transition: color 0.2s ease;
  }
  
  .markdown-content :deep(a:hover) {
    color: #a78bfa;
    text-decoration: underline;
  }
  
  .markdown-content :deep(table) {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5em 0;
  }
  
  .markdown-content :deep(th) {
    background-color: #334155;
    color: #e2e8f0;
    text-align: left;
    padding: 0.75em;
    border: 1px solid #475569;
  }
  
  .markdown-content :deep(td) {
    padding: 0.75em;
    border: 1px solid #475569;
  }
  
  .markdown-content :deep(tr:nth-child(even)) {
    background-color: #0f172a;
  }
  
  .markdown-content :deep(img) {
    max-width: 100%;
    height: auto;
    border-radius: 0.375rem;
    margin: 1em 0;
  }
  
  /* 代码高亮样式 */
  .markdown-content :deep(.hljs) {
    background: #1e293b;
    color: #e2e8f0;
  }
  
  .markdown-content :deep(.hljs-comment),
  .markdown-content :deep(.hljs-quote) {
    color: #94a3b8;
    font-style: italic;
  }
  
  .markdown-content :deep(.hljs-keyword),
  .markdown-content :deep(.hljs-selector-tag),
  .markdown-content :deep(.hljs-subst) {
    color: #f472b6;
    font-weight: bold;
  }
  
  .markdown-content :deep(.hljs-number),
  .markdown-content :deep(.hljs-literal),
  .markdown-content :deep(.hljs-variable),
  .markdown-content :deep(.hljs-template-variable),
  .markdown-content :deep(.hljs-tag .hljs-attr) {
    color: #fbbf24;
  }
  
  .markdown-content :deep(.hljs-string),
  .markdown-content :deep(.hljs-doctag) {
    color: #4ade80;
  }
  
  .markdown-content :deep(.hljs-title),
  .markdown-content :deep(.hljs-section),
  .markdown-content :deep(.hljs-selector-id) {
    color: #60a5fa;
    font-weight: bold;
  }
  
  .markdown-content :deep(.hljs-subst) {
    font-weight: normal;
  }
  
  .markdown-content :deep(.hljs-type),
  .markdown-content :deep(.hljs-class .hljs-title) {
    color: #60a5fa;
    font-weight: bold;
  }
  
  .markdown-content :deep(.hljs-tag),
  .markdown-content :deep(.hljs-name),
  .markdown-content :deep(.hljs-attribute) {
    color: #93c5fd;
    font-weight: normal;
  }
  
  .markdown-content :deep(.hljs-regexp),
  .markdown-content :deep(.hljs-link) {
    color: #4ade80;
  }
  
  .markdown-content :deep(.hljs-symbol),
  .markdown-content :deep(.hljs-bullet) {
    color: #60a5fa;
  }
  
  .markdown-content :deep(.hljs-built_in),
  .markdown-content :deep(.hljs-builtin-name) {
    color: #f472b6;
  }
  
  .markdown-content :deep(.hljs-meta) {
    color: #94a3b8;
    font-weight: bold;
  }
  
  .markdown-content :deep(.hljs-deletion) {
    background: #ef4444;
    color: #ffffff;
  }
  
  .markdown-content :deep(.hljs-addition) {
    background: #10b981;
    color: #ffffff;
  }
  
  .markdown-content :deep(.hljs-emphasis) {
    font-style: italic;
  }
  
  .markdown-content :deep(.hljs-strong) {
    font-weight: bold;
  }
</style>
