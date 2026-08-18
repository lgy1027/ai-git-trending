<template>
  <div class="terminal-page">
    <!-- 顶部导航栏 -->
    <header class="terminal-header">
      <div class="mx-auto flex max-w-[1500px] items-center justify-between px-4 py-3 lg:px-6">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center border border-cyan-400/30 bg-cyan-400/10 text-cyan-300">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
            </svg>
          </div>
          <div>
            <h1 class="text-sm font-semibold tracking-[0.28em] text-slate-100">GITTREND</h1>
            <p class="text-[10px] uppercase tracking-[0.26em] text-cyan-400/70">GITHUB TRENDING ANALYSIS</p>
          </div>
        </div>

        <nav class="hidden items-center gap-1 md:flex">
          <router-link to="/" class="terminal-nav">首页</router-link>
          <router-link to="/rankings" class="terminal-nav">排行榜</router-link>
          <router-link to="/trend-analysis" class="terminal-nav">趋势图谱</router-link>
          <router-link to="/favorites" class="terminal-nav">收藏</router-link>
          <span class="mx-2 hidden h-4 w-px bg-slate-800 md:inline-block"></span>
          <ContactNavLink />
        </nav>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="terminal-main">
      <!-- 页面标题 -->
      <div class="mb-8">
        <p class="section-kicker">REPORT ARCHIVE</p>
        <h2 class="text-3xl font-semibold text-slate-100">分析报告</h2>
        <p class="mt-2 text-slate-400">
          探索 GitHub 每日热门开源项目分析报告
        </p>
      </div>

      <!-- 搜索筛选 -->
      <div class="mb-8 flex flex-wrap gap-4 items-center">
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
          <input
            v-model="searchQuery"
            @input="filterReports"
            type="text"
            placeholder="搜索报告..."
            class="terminal-search"
          >
        </div>

        <select
          v-model="selectedTimeRange"
          @change="filterReports"
          class="terminal-select"
        >
          <option value="all">全部时间</option>
          <option value="week">本周</option>
          <option value="month">本月</option>
          <option value="quarter">本季度</option>
        </select>

        <button class="terminal-action" @click="refreshAll">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          刷新
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="terminal-loading">
        <div class="spinner"></div>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="terminal-empty">
        <svg class="text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
        </svg>
        <h3 class="text-lg font-medium text-red-400 mb-2">加载失败</h3>
        <p class="text-slate-500 mb-4">{{ error }}</p>
        <button class="terminal-action primary" @click="fetchReports">
          重试
        </button>
      </div>

      <!-- 报告列表 -->
      <div v-else-if="filteredReports.length > 0 || reports.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <div
          v-for="(report, index) in (filteredReports.length > 0 || searchQuery || selectedTimeRange !== 'all' ? filteredReports : reports)"
          :key="report.date"
          class="report-card p-5"
          :style="{ animationDelay: `${index * 0.1}s` }"
          @click="() => openReport(report.date)"
        >
          <!-- 最新标识 -->
          <div v-if="index === 0" class="flex justify-end mb-2">
            <span class="status-chip online">最新</span>
          </div>

          <!-- 日期展示 -->
          <div class="mb-4">
            <div class="text-slate-500 text-sm mb-1">
              {{ formatDateShort(report.date) }}
            </div>
            <div class="text-5xl font-semibold text-slate-100 leading-none">
              {{ formatDay(report.date) }}
            </div>
            <div class="text-slate-400 text-sm mt-1">
              {{ formatDateWeek(report.date) }}
            </div>
          </div>

          <!-- 项目统计 -->
          <div class="border-t border-slate-800 pt-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
                </svg>
                <span class="text-slate-300 text-sm">项目数量</span>
              </div>
              <span class="text-xl font-semibold text-slate-100">{{ report.project_count }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空数据状态 -->
      <div v-else class="terminal-empty">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <h3 class="text-lg font-medium text-slate-400 mb-2">暂无报告</h3>
        <p class="text-slate-500 mb-4">还没有生成任何报告</p>
        <button class="terminal-action primary" @click="fetchReports">
          刷新数据
        </button>
      </div>
    </main>

    <!-- 报告详情模态框 -->
    <div v-if="showModal" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4" @click="closeModal">
      <div class="terminal-panel max-w-5xl w-full max-h-[90vh] overflow-hidden" @click.stop>
        <!-- 模态框头部 -->
        <div class="terminal-panel-head">
          <span>REPORT DETAIL - {{ formatDateShort(currentReport?.date || '') }}</span>
          <button @click="closeModal" class="text-slate-400 hover:text-white transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- 模态框内容 -->
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <div v-if="loadingContent" class="terminal-loading">
            <div class="spinner"></div>
          </div>

          <div v-else-if="reportError" class="terminal-empty">
            <svg class="text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
            <h3 class="text-lg font-medium text-red-400 mb-2">加载失败</h3>
            <p class="text-slate-500 mb-4">{{ reportError }}</p>
            <button class="terminal-action primary" @click="() => loadReportContent(currentReport?.date)">
              重试
            </button>
          </div>

          <div v-else-if="renderedContent" v-html="renderedContent" class="markdown-content"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { reportApi, type Report } from '../api/reports'
import { renderMarkdown } from '../utils/markdown-simple'
import ContactNavLink from '@/components/ContactNavLink.vue'

const reports = ref<Report[]>([])
const filteredReports = ref<Report[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const showModal = ref(false)
const currentReport = ref<Report | null>(null)
const reportContent = ref<string | null>(null)
const renderedContent = ref<string | null>(null)
const loadingContent = ref(false)
const reportError = ref<string | null>(null)

const searchQuery = ref('')
const selectedTimeRange = ref('all')

onMounted(() => {
  fetchReports()
})

async function fetchReports() {
  try {
    loading.value = true
    error.value = null
    const reportsData = await reportApi.getReports()
    reports.value = reportsData || []
    filteredReports.value = reports.value
  } catch (err: any) {
    error.value = err.message || '获取报告列表失败'
  } finally {
    loading.value = false
  }
}

function filterReports() {
  let filtered = [...reports.value]

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(report =>
      report.date.toLowerCase().includes(query) ||
      formatDateShort(report.date).toLowerCase().includes(query)
    )
  }

  if (selectedTimeRange.value !== 'all') {
    const now = new Date()
    const cutoffDate = new Date()

    switch (selectedTimeRange.value) {
      case 'week':
        cutoffDate.setDate(now.getDate() - 7)
        break
      case 'month':
        cutoffDate.setMonth(now.getMonth() - 1)
        break
      case 'quarter':
        cutoffDate.setMonth(now.getMonth() - 3)
        break
    }

    filtered = filtered.filter(report => {
      const reportDate = new Date(report.date)
      return reportDate >= cutoffDate
    })
  }

  filteredReports.value = filtered
}

async function refreshAll() {
  searchQuery.value = ''
  selectedTimeRange.value = 'all'
  await fetchReports()
}

async function loadReportContent(date?: string) {
  if (!date) return

  try {
    loadingContent.value = true
    reportError.value = null
    const report = await reportApi.getReportContent(date)
    reportContent.value = report.content || '暂无内容'

    const html = await renderMarkdown(reportContent.value)
    renderedContent.value = html
  } catch (err: any) {
    reportError.value = err.message || '加载报告内容失败'
    renderedContent.value = null
  } finally {
    loadingContent.value = false
  }
}

async function openReport(date: string) {
  const report = reports.value.find(r => r.date === date)
  if (report) {
    await loadReportContent(date)
    report.content = reportContent.value || ''
    currentReport.value = report
    showModal.value = true
  }
}

function closeModal() {
  showModal.value = false
  currentReport.value = null
  reportContent.value = null
  renderedContent.value = null
  reportError.value = null
  loadingContent.value = false
}

function formatDateShort(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    weekday: 'short'
  })
}

function formatDay(dateStr: string): string {
  const date = new Date(dateStr)
  return date.getDate().toString()
}

function formatDateWeek(dateStr: string): string {
  const date = new Date(dateStr)
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return weekdays[date.getDay()]
}
</script>
