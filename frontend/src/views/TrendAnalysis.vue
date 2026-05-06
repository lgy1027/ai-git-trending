<template>
  <div class="terminal-page">
    <!-- 顶部导航栏 - 技术情报终端 -->
    <header class="terminal-header">
      <div class="mx-auto flex max-w-[1500px] items-center justify-between px-4 py-3 lg:px-6">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center border border-cyan-400/30 bg-cyan-400/10 text-cyan-300">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
            </svg>
          </div>
          <div>
            <h1 class="text-sm font-semibold tracking-[0.28em] text-slate-100">GITTREND INTEL</h1>
            <p class="text-[10px] uppercase tracking-[0.26em] text-cyan-400/70">TECH INTELLIGENCE TERMINAL</p>
          </div>
        </div>

        <nav class="hidden items-center gap-1 md:flex">
          <router-link to="/" class="terminal-nav">情报台</router-link>
          <router-link to="/rankings" class="terminal-nav">排行榜</router-link>
          <router-link to="/trend-analysis" class="terminal-nav active">趋势图谱</router-link>
          <router-link to="/favorites" class="terminal-nav">收藏</router-link>
        </nav>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="terminal-main">
      <!-- 页面标题 -->
      <div class="mb-8">
        <p class="section-kicker">TREND ANALYSIS</p>
        <h2 class="text-3xl font-semibold text-slate-100">技术趋势分析</h2>
        <p class="mt-2 text-slate-400 max-w-2xl">
          探索技术发展趋势，发现新兴项目和热门技术领域
        </p>
      </div>

      <!-- 筛选选项 -->
      <div class="mb-8 flex flex-wrap gap-4">
        <div class="flex gap-2">
          <button
            v-for="period in timePeriods"
            :key="period.value"
            @click="selectedPeriod = period.value"
            :class="[
              'terminal-action',
              selectedPeriod === period.value ? 'primary' : ''
            ]"
          >
            {{ period.label }}
          </button>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="terminal-loading">
        <div class="spinner"></div>
      </div>

      <!-- 数据展示 -->
      <div v-else class="space-y-6">
        <!-- 编程语言分布图 -->
        <div class="terminal-panel p-6">
          <div class="terminal-panel-head">
            <span>LANGUAGE DISTRIBUTION</span>
            <span>TOP 8</span>
          </div>
          <div class="h-80">
            <canvas ref="languageChartRef"></canvas>
          </div>
        </div>

        <!-- 技术领域分布 -->
        <div class="terminal-panel p-6">
          <div class="terminal-panel-head">
            <span>TECH DOMAINS</span>
            <span>ALL</span>
          </div>
          <div class="h-80">
            <canvas ref="domainChartRef"></canvas>
          </div>
        </div>

        <!-- 项目趋势 -->
        <div class="terminal-panel p-6">
          <div class="terminal-panel-head">
            <span>PROJECT TREND</span>
            <span>LAST 7 DAYS</span>
          </div>
          <div class="h-80">
            <canvas ref="trendChartRef"></canvas>
          </div>
        </div>

        <!-- 趋势项目列表 -->
        <div class="terminal-panel p-6">
          <div class="terminal-panel-head">
            <span>EMERGING PROJECTS</span>
            <span>{{ trendingProjects.length }} ITEMS</span>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
            <ProjectCard
              v-for="(project, index) in trendingProjects"
              :key="project.name"
              :project="project"
              :index="index"
              @click="viewProjectDetails(project)"
            />
          </div>
          <div v-if="trendingProjects.length === 0" class="text-center py-8 text-slate-500">
            暂无项目数据
          </div>
        </div>
      </div>
    </main>

    <!-- 项目详情模态框 -->
    <ProjectModal
      :visible="showProjectModal"
      :project-name="selectedProjectName"
      @close="showProjectModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { getProjectsByDate, getLanguageDistribution, getTechDomains, getProjectTrend, type Project } from '@/api/reports'
import ProjectCard from '@/components/ProjectCard.vue'
import ProjectModal from '@/components/ProjectModal.vue'
import Chart from 'chart.js/auto'

const loading = ref(false)
const selectedPeriod = ref('monthly')
const trendingProjects = ref<Project[]>([])
const showProjectModal = ref(false)
const selectedProjectName = ref('')

// Chart refs
const languageChartRef = ref<HTMLCanvasElement | null>(null)
const domainChartRef = ref<HTMLCanvasElement | null>(null)
const trendChartRef = ref<HTMLCanvasElement | null>(null)

// Chart instances
let languageChart: Chart | null = null
let domainChart: Chart | null = null
let trendChart: Chart | null = null

const timePeriods = [
  { label: '本周', value: 'weekly' },
  { label: '本月', value: 'monthly' },
  { label: '全年', value: 'yearly' }
]

// 图表颜色
const chartColors = [
  '#22d3ee', '#f472b6', '#a78bfa', '#34d399', '#fbbf24',
  '#f87171', '#60a5fa', '#818cf8', '#2dd4bf', '#fb923c'
]

// 加载语言分布图表
const loadLanguageChart = async () => {
  try {
    const data = await getLanguageDistribution()
    if (!languageChartRef.value || data.length === 0) return

    const labels = data.map(d => d.name)
    const values = data.map(d => d.count)

    if (languageChart) languageChart.destroy()

    languageChart = new Chart(languageChartRef.value, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: '项目数量',
          data: values,
          backgroundColor: chartColors.slice(0, labels.length),
          borderColor: 'rgba(34, 211, 238, 0.5)',
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { color: 'rgba(51, 65, 85, 0.3)' },
            ticks: { color: '#94a3b8' }
          },
          y: {
            grid: { color: 'rgba(51, 65, 85, 0.3)' },
            ticks: { color: '#94a3b8' }
          }
        }
      }
    })
  } catch (error) {
    console.error('加载语言分布图表失败:', error)
  }
}

// 加载技术领域分布图表
const loadDomainChart = async () => {
  try {
    const data = await getTechDomains()
    if (!domainChartRef.value || data.length === 0) return

    const labels = data.map(d => d.name)
    const values = data.map(d => d.count)

    if (domainChart) domainChart.destroy()

    domainChart = new Chart(domainChartRef.value, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: '项目数量',
          data: values,
          backgroundColor: chartColors.slice(0, labels.length),
          borderColor: 'rgba(34, 211, 238, 0.5)',
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { color: 'rgba(51, 65, 85, 0.3)' },
            ticks: { color: '#94a3b8' }
          },
          y: {
            grid: { color: 'rgba(51, 65, 85, 0.3)' },
            ticks: { color: '#94a3b8' }
          }
        }
      }
    })
  } catch (error) {
    console.error('加载技术领域图表失败:', error)
  }
}

// 加载项目趋势图表
const loadTrendChart = async () => {
  try {
    const data = await getProjectTrend(7)
    if (!trendChartRef.value || data.length === 0) return

    const labels = data.map(d => {
      const date = new Date(d.date)
      return `${date.getMonth() + 1}/${date.getDate()}`
    })
    const values = data.map(d => d.count)

    if (trendChart) trendChart.destroy()

    trendChart = new Chart(trendChartRef.value, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: '项目数量',
          data: values,
          borderColor: '#22d3ee',
          backgroundColor: 'rgba(34, 211, 238, 0.1)',
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#22d3ee',
          pointBorderColor: '#fff',
          pointRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { color: 'rgba(51, 65, 85, 0.3)' },
            ticks: { color: '#94a3b8' }
          },
          y: {
            grid: { color: 'rgba(51, 65, 85, 0.3)' },
            ticks: { color: '#94a3b8' },
            beginAtZero: true
          }
        }
      }
    })
  } catch (error) {
    console.error('加载趋势图表失败:', error)
  }
}

// 加载所有图表
const loadCharts = async () => {
  await Promise.all([
    loadLanguageChart(),
    loadDomainChart(),
    loadTrendChart()
  ])
}

const renderCharts = async () => {
  await nextTick()
  await loadCharts()
}

const loadTrendingProjects = async () => {
  loading.value = true
  try {
    const date = new Date().toISOString().split('T')[0]
    const data = await getProjectsByDate(date)
    trendingProjects.value = data.slice(0, 6)
  } catch (error) {
    console.error('Failed to load trending projects:', error)
  } finally {
    loading.value = false
  }
}

const viewProjectDetails = (project: Project) => {
  selectedProjectName.value = project.name
  showProjectModal.value = true
}

// 初始化
onMounted(async () => {
  loading.value = true
  try {
    await loadTrendingProjects()
  } finally {
    loading.value = false
  }
  await renderCharts()
})

// 监听时间筛选变化
watch(selectedPeriod, async () => {
  await loadTrendingProjects()
  await renderCharts()
})
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 100%;
  width: 100%;
}
</style>
