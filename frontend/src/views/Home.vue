<template>
  <div class="home-container min-h-screen bg-[#071019] text-slate-100">
    <!-- 顶部导航栏 - 技术情报终端 -->
    <header class="sticky top-0 z-40 border-b border-cyan-400/10 bg-[#071019]/95 backdrop-blur-sm">
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
          <router-link to="/" class="terminal-nav active">情报台</router-link>
          <router-link to="/rankings" class="terminal-nav">排行榜</router-link>
          <router-link to="/trend-analysis" class="terminal-nav">趋势图谱</router-link>
          <router-link to="/favorites" class="terminal-nav">收藏</router-link>
        </nav>
      </div>
    </header>

    <!-- 情报终端首屏 -->
    <section class="terminal-shell border-b border-cyan-400/10">
      <div class="mx-auto grid max-w-[1500px] gap-4 px-4 py-5 lg:grid-cols-[1.45fr_0.95fr] lg:px-6">
        <div class="terminal-panel min-h-[360px]">
          <div class="terminal-panel-head">
            <span>LIVE BRIEFING</span>
            <span>{{ currentDateLabel }}</span>
          </div>
          <div class="p-5 lg:p-6">
            <div class="mb-5 flex flex-wrap items-center gap-2">
              <span class="status-chip online">后端在线</span>
              <span class="status-chip">GitHub Trending</span>
              <span class="status-chip">LLM Report</span>
            </div>
            <h2 class="max-w-4xl text-3xl font-semibold leading-tight text-slate-50 md:text-5xl">
              技术情报终端
            </h2>
            <p class="mt-4 max-w-3xl text-sm leading-7 text-slate-400 md:text-base">
              聚合 GitHub 热门项目、语言热度、技术领域和 AI 分析报告，把每日开源变化整理成可扫描、可追踪、可复盘的情报面板。
            </p>

            <div class="mt-8 grid grid-cols-2 gap-3 lg:grid-cols-4">
              <div class="terminal-metric">
                <span>REPORTS</span>
                <strong>{{ statsData.totalReports }}</strong>
              </div>
              <div class="terminal-metric">
                <span>PROJECTS</span>
                <strong>{{ statsData.totalProjects }}</strong>
              </div>
              <div class="terminal-metric">
                <span>WEEKLY NEW</span>
                <strong>{{ statsData.weeklyNew }}</strong>
              </div>
              <div class="terminal-metric">
                <span>AVG CONTRIBUTORS</span>
                <strong>{{ statsData.avgContributors }}</strong>
              </div>
            </div>

            <div class="mt-8 flex flex-wrap gap-3">
              <button class="terminal-action primary" @click="viewTodayTrending">
                查看今日热门
              </button>
              <button class="terminal-action" @click="openTechTrendsModal">
                打开趋势雷达
              </button>
            </div>
          </div>
        </div>

        <aside class="grid gap-4">
          <div class="terminal-panel">
            <div class="terminal-panel-head">
              <span>REPORT QUEUE</span>
              <router-link to="/reports" class="text-cyan-300 hover:text-cyan-200">全部</router-link>
            </div>
            <div class="divide-y divide-slate-800/80">
              <button
                v-for="report in featuredReports.slice(0, 3)"
                :key="report.date"
                class="w-full px-4 py-3 text-left transition-colors hover:bg-cyan-400/5"
                @click="openReportModal(report)"
              >
                <div class="flex items-center justify-between gap-3">
                  <span class="text-sm font-medium text-slate-200">{{ formatDate(report.date) }}</span>
                  <span class="text-[11px] text-slate-500">{{ report.project_count }} projects</span>
                </div>
                <p class="mt-1 line-clamp-1 text-xs text-slate-500">{{ getReportTitle(report) }}</p>
              </button>
              <div v-if="featuredReports.length === 0" class="px-4 py-8 text-center text-sm text-slate-500">
                暂无报告
              </div>
            </div>
          </div>

          <div class="terminal-panel">
            <div class="terminal-panel-head">
              <span>SIGNAL FEED</span>
              <span>{{ timeFilter.toUpperCase() }}</span>
            </div>
            <div class="space-y-3 p-4">
              <div v-for="item in intelligenceFeed" :key="item.label" class="feed-row">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </section>

    <!-- 核心内容区域 -->
    <main class="mx-auto max-w-[1500px] px-4 py-8 lg:px-6">
      <!-- 数据概览 -->
      <section class="mb-12 animate-fadeInUp">
        <div class="terminal-section-title">
          <div>
            <p class="section-kicker">INTELLIGENCE OVERVIEW</p>
            <h3>情报概览</h3>
          </div>
          <button class="terminal-action compact" @click="openTechTrendsModal">
            <i class="fa fa-chart-line mr-1"></i> 打开趋势雷达
          </button>
        </div>
        <StatsChart
          :stats="statsData"
          :languageData="topLanguages"
          :trendData="trendAreasData"
          :emergingAreas="emergingAreas"
          :surgingProjects="surgingProjects"
          :surgingMode="surgingMode"
        />
      </section>

      <!-- 热门项目 -->
      <section id="trending-projects" class="mb-12">
        <div class="terminal-section-title animate-fadeInUp">
          <div>
            <p class="section-kicker">TRENDING REPOSITORIES</p>
            <h3>今日热门项目</h3>
          </div>
          <div class="flex items-center gap-4">
            <div class="relative">
              <select v-model="timeFilter" class="border border-slate-700 bg-slate-950/70 py-2 pl-3 pr-8 text-sm text-slate-300 outline-none transition-colors hover:border-cyan-400/40">
                <option value="today">今日</option>
                <option value="week">本周</option>
                <option value="month">本月</option>
              </select>
              <svg class="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 9l-7 7-7-7"></path>
              </svg>
            </div>
          </div>
        </div>

        <!-- 项目卡片网格 - 响应式布局 -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          <ProjectCard 
            v-for="(project, index) in trendingProjects" 
            :key="project.name"
            :project="project"
            :index="index"
            @click="openProjectModal(project)"
          />
        </div>
        
        <div class="text-center mt-8 animate-fadeInUp">
          <button class="terminal-action">
            查看更多项目 <i class="fa fa-angle-right ml-1"></i>
          </button>
        </div>
      </section>

      <!-- 分析报告 - 按时间展示 -->
      <section class="mb-12">
        <div class="terminal-section-title animate-fadeInUp">
          <div>
            <p class="section-kicker">REPORT ARCHIVE</p>
            <h3>分析报告</h3>
          </div>
          <router-link to="/reports" class="flex items-center gap-1 text-sm text-cyan-300 hover:text-cyan-200">
            查看全部 <i class="fa fa-angle-right"></i>
          </router-link>
        </div>
        
        <div v-if="featuredReports.length > 0" class="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-5">
          <div 
            v-for="(report, index) in featuredReports" 
            :key="report.date"
            class="report-card report-card-compact animate-fadeInUp" 
            :style="{ animationDelay: `${index * 0.1}s` }"
            @click="openReportModal(report)"
            :class="{ 'opacity-50 cursor-not-allowed': isLoading }"
          >
            <div class="p-4">
              <div class="mb-5 flex items-center justify-between gap-3">
                <span class="text-[10px] uppercase tracking-[0.18em] text-cyan-400/75">Daily</span>
                <span class="report-status">已生成</span>
              </div>
              <div class="report-date">
                <strong>{{ formatReportDay(report.date) }}</strong>
                <span>{{ formatReportMonth(report.date) }}</span>
              </div>
              <div class="mt-5 flex items-center justify-between border-t border-slate-800/80 pt-3 text-xs">
                <span class="text-slate-500">{{ report.project_count }} 个项目</span>
                <span class="text-cyan-300">查看</span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="border border-dashed border-slate-800 bg-slate-950/40 py-12 text-center text-slate-500">
          暂无分析报告，完成一次后端项目分析后会在这里按时间展示。
        </div>
        
        <!-- 加载提示 -->
        <div v-if="isLoading" class="fixed inset-0 z-40 flex items-center justify-center bg-black/60">
          <div class="flex flex-col items-center border border-cyan-400/20 bg-slate-950 p-6 shadow-2xl">
            <div class="mb-4 h-12 w-12 animate-spin border-4 border-cyan-400/20 border-t-cyan-300"></div>
            <p class="text-slate-300">加载报告内容中...</p>
          </div>
        </div>
      </section>
    </main>

    <!-- 页脚 -->
    <footer class="border-t border-cyan-400/10 bg-[#071019]">
      <div class="mx-auto flex max-w-[1500px] flex-col gap-3 px-4 py-6 text-xs text-slate-500 md:flex-row md:items-center md:justify-between lg:px-6">
        <span>GITTREND INTEL / OPEN SOURCE SIGNAL WATCH</span>
        <span>© {{ new Date().getFullYear() }} GitTrend Insights</span>
      </div>
    </footer>

    <!-- 项目详情模态框 -->
    <ProjectModal 
      :visible="isProjectModalOpen"
      :project-name="selectedProject?.name"
      @close="closeProjectModal"
    />

    <!-- 报告详情模态框 -->
    <ReportModal 
      :report="selectedReport"
      :theme="theme"
      v-if="isReportModalOpen"
      @close="closeReportModal"
    />

    <!-- 技术趋势分析模态框 -->
    <TechTrendsModal 
      :visible="isTechTrendsModalOpen"
      :trends-data="trendsData"
      @close="closeTechTrendsModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
// import mermaid from 'mermaid';
import { useRouter } from 'vue-router'
import ProjectCard from '@/components/ProjectCard.vue'
import ProjectModal from '@/components/ProjectModal.vue'
import ReportModal from '@/components/ReportModal.vue'
import StatsChart from '@/components/StatsChart.vue'
import TechTrendsModal from '@/components/TechTrendsModal.vue'
import type { Project, Report, Stats, TrendsData, TrendDataItem } from '@/api/reports'
import { getReports, getStats, getTrends, getReportByDate, getTrendData } from '@/api/reports'

const router = useRouter()

// 响应式数据
const theme = ref<'light' | 'dark'>('dark')
const timeFilter = ref('today')

// 监听timeFilter变化，更新项目数据
watch(timeFilter, async () => {
  await refreshData()
})
const statsData = ref<Stats>({
  totalReports: 0,
  totalProjects: 0,
  topLanguage: 'N/A',
  weeklyNew: 0,
  totalForks: '0',
  avgContributors: 0,
  activityScore: 0
})
const trendingProjects = ref<Project[]>([])
const featuredReports = ref<Report[]>([])
const trendsData = ref<TrendsData>({  time_window_days: 30,
  most_frequent_projects: [],
  most_frequent_languages: [],
  programmingLanguages: [],
  surgingProjects: [],
  techDomains: []
})
const trendAreasData = ref<TrendDataItem[]>([]) // 新兴技术领域数据

// 加载状态
const isLoading = ref(false)

// 模态框状态
const isProjectModalOpen = ref(false)
const isReportModalOpen = ref(false)
const isTechTrendsModalOpen = ref(false)
const selectedProject = ref<Project | null>(null)
const selectedReport = ref<Report>({
  date: '',
  project_count: 0
})

const currentDateLabel = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    weekday: 'short'
  })
})

const intelligenceFeed = computed(() => [
  {
    label: '最新报告',
    value: featuredReports.value[0]?.date || '待生成'
  },
  {
    label: '高频语言',
    value: topLanguages.value[0]?.name || statsData.value.topLanguage || 'N/A'
  },
  {
    label: '项目样本',
    value: `${trendingProjects.value.length || statsData.value.totalProjects || 0} repos`
  },
  {
    label: surgingMode.value === 'hot' ? '热度样本' : '增长样本',
    value: `${surgingProjects.value.length} signals`
  }
])

// 计算属性 - 热门编程语言
const topLanguages = computed(() => {
  // 只使用从API获取的真实语言数据
  if (trendsData.value && trendsData.value.most_frequent_languages && trendsData.value.most_frequent_languages.length > 0) {
    const total = trendsData.value.most_frequent_languages.reduce((sum, [, count]) => sum + count, 0)
    
    // 为语言分配颜色类
    const colorClasses = [
      'bg-gradient-to-r from-blue-500 to-blue-600',
      'bg-gradient-to-r from-yellow-500 to-yellow-600',
      'bg-gradient-to-r from-green-500 to-green-600',
      'bg-gradient-to-r from-cyan-500 to-cyan-600',
      'bg-gradient-to-r from-orange-500 to-orange-600',
      'bg-gradient-to-r from-purple-500 to-purple-600',
      'bg-gradient-to-r from-pink-500 to-pink-600',
      'bg-gradient-to-r from-red-500 to-red-600'
    ]
    
    return trendsData.value.most_frequent_languages
      .slice(0, 5) // 只显示前5种语言
      .map(([name, count], index) => ({
        name,
        count,
        percentage: Math.round((count / total) * 100),
        colorClass: colorClasses[index % colorClasses.length]
      }))
  }
  
  // 如果没有真实数据，返回空数组
  return []
})

// 更新热门趋势项目数据
function updateTrendingProjects() {
  if (trendsData.value && trendsData.value.most_frequent_projects && trendsData.value.most_frequent_projects.length > 0) {
    // 直接使用后端返回的完整项目数据
    trendingProjects.value = trendsData.value.most_frequent_projects.slice(0, 12).map(project => ({
      name: project.name,
      url: project.url || `https://github.com/${project.name}`,
      description: project.description,
      language: project.language,
      stars: project.stars || project.avg_stars || 0,
      forks: project.forks || 0,
      contributor_count: project.contributor_count || 0,
      created_at: project.created_at || new Date().toISOString(),
      updated_at: project.updated_at || new Date().toISOString(),
      open_issues: project.open_issues || 0,
      watchers: project.watchers || 0,
      summary_date: project.created_at ? new Date(project.created_at).toISOString().split('T')[0] : new Date().toISOString().split('T')[0]
    }))
  } else {
    // 如果没有真实数据，返回空数组
    trendingProjects.value = []
  }
}

// 计算属性 - 新兴技术领域
const emergingAreas = computed(() => {
  // 只使用从API获取的真实新兴技术领域数据
  if (trendAreasData.value && trendAreasData.value.length > 0) {
    // 为不同的技术领域分配图标和背景色
    const techIcons = ['IconEcosystem', 'IconTooling', 'IconCommunity', 'IconDocumentation']
    const bgClasses = ['bg-purple-500/20', 'bg-blue-500/20', 'bg-green-500/20', 'bg-pink-500/20']
    
    // 进一步映射到相应的days参数
    const areaNameMap: Record<string, string> = {
      '新项目': '生成式AI',
      '活跃项目': 'WebAssembly',
      '热门项目': '边缘计算',
      '趋势项目': '低代码平台'
    }
    
    return trendAreasData.value.slice(0, 4).map((item, index) => ({
      name: areaNameMap[item.label] || item.label,
      growth: item.change,
      bgClass: bgClasses[index % bgClasses.length],
      icon: techIcons[index % techIcons.length]
    }))
  }
  
  // 如果没有真实数据，返回空数组
  return []
})

// 计算属性 - 上升最快项目
const surgingProjects = computed(() => {
  if (trendsData.value && trendsData.value.surgingProjects && trendsData.value.surgingProjects.length > 0) {
    return trendsData.value.surgingProjects.slice(0, 4).map((project, index) => ({
      ...project,
      rank: index + 1
    }))
  }

  return trendingProjects.value.slice(0, 4).map((project, index) => ({
    name: project.name,
    description: project.description,
    language: project.language,
    star_increase: project.stars,
    rank: index + 1
  }))
})

const surgingMode = computed<'surging' | 'hot'>(() => {
  return trendsData.value?.surgingProjects?.length ? 'surging' : 'hot'
})

// 初始化数据
onMounted(async () => {
  await loadInitialData()
  
  // Initialize Mermaid
  // mermaid.initialize({
  //   startOnLoad: false, // We will manually trigger rendering
  //   theme: theme.value === 'dark' ? 'dark' : 'default', // Match app theme
  // });
  // // Run Mermaid to render diagrams
  // mermaid.run();

  // 初始化主题
  applyTheme(theme.value)
  
  // 监听系统主题变化
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (e.matches) {
      setTheme('dark')
    } else {
      setTheme('light')
    }
  })
})

// 加载初始数据
async function loadInitialData() {
  await Promise.all([
    loadStatsData(),
    loadReportCards(),
    loadTrendOverview()
  ])
}

async function loadStatsData() {
  try {
    statsData.value = await getStats()
  } catch (error) {
    console.error('加载统计数据失败:', error)
    statsData.value = { totalReports: 0, totalProjects: 0, topLanguage: 'N/A', weeklyNew: 0, totalForks: '0', avgContributors: 0, activityScore: 0 }
  }
}

async function loadReportCards() {
  try {
    const reports = await getReports()
    featuredReports.value = reports.sort((a, b) => b.date.localeCompare(a.date))
  } catch (error) {
    console.error('加载报告列表失败:', error)
    featuredReports.value = []
  }
}

function getDaysForTimeFilter() {
  switch (timeFilter.value) {
    case 'today':
      return 1
    case 'month':
      return 30
    case 'week':
    default:
      return 7
  }
}

async function loadTrendOverview() {
  try {
    const days = getDaysForTimeFilter()
    const [trendsResponse, trendAreasResponse] = await Promise.all([
      getTrends({ days }),
      getTrendData({ days })
    ])
    trendsData.value = trendsResponse
    trendAreasData.value = trendAreasResponse
    updateTrendingProjects()
  } catch (error) {
    console.error('加载趋势数据失败:', error)
    trendingProjects.value = []
    trendsData.value = { time_window_days: 7, most_frequent_projects: [], most_frequent_languages: [], programmingLanguages: [], surgingProjects: [], techDomains: [] }
    trendAreasData.value = []
  }
}

// 刷新数据
async function refreshData() {
  isLoading.value = true
  try {
    const days = getDaysForTimeFilter()
    const [newTrendsResponse, newTrendAreasResponse] = await Promise.all([
      getTrends({ days }),
      getTrendData({ days })
    ])

    trendsData.value = newTrendsResponse
    trendAreasData.value = newTrendAreasResponse

    // 更新项目数据
    updateTrendingProjects()
  } catch (error) {
    console.error('刷新数据失败:', error)
    // 如果失败，清空项目数据而不是使用模拟数据
    trendingProjects.value = []
  } finally {
    isLoading.value = false
  }
}

// 查看今日热门
function viewTodayTrending() {
  // 设置时间过滤器为今日
  timeFilter.value = 'today'
  // 重新加载数据以确保显示今日热门项目
  loadInitialData().then(() => {
    // 滚动到热门趋势项目区域
    const element = document.querySelector('#trending-projects')
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  })
}

// 主题切换
function toggleTheme() {
  const newTheme = theme.value === 'dark' ? 'light' : 'dark'
  setTheme(newTheme)
}

// 设置主题
function setTheme(newTheme: 'light' | 'dark') {
  theme.value = newTheme
  applyTheme(newTheme)
}

// 应用主题
function applyTheme(newTheme: 'light' | 'dark') {
  if (newTheme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

// 打开项目详情模态框
function openProjectModal(project: Project) {
  selectedProject.value = project
  isProjectModalOpen.value = true
}

// 关闭项目详情模态框
function closeProjectModal() {
  isProjectModalOpen.value = false
  setTimeout(() => {
    selectedProject.value = null
  }, 300)
}

// 打开报告详情模态框
async function openReportModal(report: Report) {
  try {
    // 先显示加载状态
    isLoading.value = true;
    // 获取报告完整内容
    const fullReport = await getReportByDate(report.date);
    selectedReport.value = fullReport;
    isReportModalOpen.value = true;
  } catch (error) {
    console.error('加载报告内容失败:', error);
    // 可以添加错误提示
  } finally {
    isLoading.value = false;
  }
}

// 关闭报告详情模态框
function closeReportModal() {
  isReportModalOpen.value = false
}

// 打开技术趋势分析模态框
function openTechTrendsModal() {
  isTechTrendsModalOpen.value = true
}

// 关闭技术趋势分析模态框
function closeTechTrendsModal() {
  isTechTrendsModalOpen.value = false
}

// 日期格式化
function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function formatReportDay(dateStr: string): string {
  if (!dateStr) return '--'
  const date = new Date(dateStr)
  return String(date.getDate()).padStart(2, '0')
}

function formatReportMonth(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}`
}

function getReportTitle(report: Report): string {
  const content = report.content || ''
  if (!content) return `${formatDate(report.date)} GitHub 趋势分析报告`

  const heading = content
    .split('\n')
    .map(line => line.trim())
    .find(line => line.startsWith('#'))

  return heading?.replace(/^#+\s*/, '') || 'GitHub 热门项目报告'
}
</script>

<style scoped>
.home-container {
  background:
    linear-gradient(rgba(34, 211, 238, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(34, 211, 238, 0.025) 1px, transparent 1px),
    radial-gradient(circle at 18% 8%, rgba(34, 211, 238, 0.08), transparent 28rem),
    #071019;
  background-size: 28px 28px, 28px 28px, auto;
}

.terminal-shell {
  background:
    linear-gradient(180deg, rgba(14, 116, 144, 0.08), transparent 42%),
    rgba(2, 6, 23, 0.26);
}

.terminal-panel,
.report-card {
  border: 1px solid rgba(51, 65, 85, 0.9);
  background: rgba(15, 23, 42, 0.72);
  box-shadow: inset 0 1px 0 rgba(148, 163, 184, 0.06);
}

.terminal-panel {
  position: relative;
}

.terminal-panel::before,
.report-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 1px;
  width: 100%;
  background: linear-gradient(90deg, rgba(34, 211, 238, 0.65), transparent 60%);
  opacity: 0.55;
}

.report-card {
  position: relative;
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

.report-card:hover {
  border-color: rgba(34, 211, 238, 0.38);
  background: rgba(15, 23, 42, 0.9);
  transform: translateY(-2px);
}

.report-card-compact {
  min-height: 10.75rem;
}

.report-status {
  border: 1px solid rgba(34, 197, 94, 0.22);
  background: rgba(34, 197, 94, 0.08);
  padding: 0.18rem 0.4rem;
  font-size: 0.68rem;
  color: #86efac;
}

.report-date strong {
  display: block;
  font-size: 3rem;
  line-height: 1;
  font-weight: 600;
  color: #f8fafc;
}

.report-date span {
  margin-top: 0.35rem;
  display: block;
  font-family: var(--font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace);
  font-size: 0.78rem;
  letter-spacing: 0.16em;
  color: #64748b;
}

.terminal-panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  border-bottom: 1px solid rgba(51, 65, 85, 0.8);
  padding: 0.65rem 1rem;
  font-family: var(--font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace);
  font-size: 0.68rem;
  letter-spacing: 0.18em;
  color: rgba(148, 163, 184, 0.82);
}

.terminal-nav {
  border: 1px solid transparent;
  padding: 0.45rem 0.75rem;
  font-size: 0.78rem;
  color: #94a3b8;
  transition: all 0.2s ease;
}

.terminal-nav:hover,
.terminal-nav.active {
  border-color: rgba(34, 211, 238, 0.22);
  background: rgba(34, 211, 238, 0.06);
  color: #67e8f9;
}

.status-chip {
  border: 1px solid rgba(51, 65, 85, 0.95);
  background: rgba(2, 6, 23, 0.45);
  padding: 0.35rem 0.55rem;
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  color: #94a3b8;
}

.status-chip.online {
  border-color: rgba(34, 197, 94, 0.24);
  color: #86efac;
}

.terminal-metric {
  border: 1px solid rgba(51, 65, 85, 0.8);
  background: rgba(2, 6, 23, 0.36);
  padding: 0.9rem;
}

.terminal-metric span {
  display: block;
  font-family: var(--font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace);
  font-size: 0.64rem;
  letter-spacing: 0.16em;
  color: #64748b;
}

.terminal-metric strong {
  margin-top: 0.55rem;
  display: block;
  font-size: 1.65rem;
  font-weight: 500;
  color: #e2e8f0;
}

.terminal-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(51, 65, 85, 0.95);
  background: rgba(15, 23, 42, 0.75);
  padding: 0.65rem 1rem;
  font-size: 0.84rem;
  color: #cbd5e1;
  transition: all 0.2s ease;
}

.terminal-action.compact {
  padding: 0.5rem 0.8rem;
  font-size: 0.78rem;
}

.terminal-action:hover {
  border-color: rgba(34, 211, 238, 0.38);
  color: #e0f2fe;
}

.terminal-action.primary {
  border-color: rgba(34, 211, 238, 0.36);
  background: rgba(34, 211, 238, 0.12);
  color: #a5f3fc;
}

.feed-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border: 1px solid rgba(51, 65, 85, 0.7);
  background: rgba(2, 6, 23, 0.32);
  padding: 0.75rem;
}

.feed-row span {
  font-size: 0.76rem;
  color: #64748b;
}

.feed-row strong {
  max-width: 12rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.82rem;
  font-weight: 500;
  color: #cbd5e1;
}

.terminal-section-title {
  margin-bottom: 1rem;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  border-bottom: 1px solid rgba(51, 65, 85, 0.7);
  padding-bottom: 0.85rem;
}

.terminal-section-title h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #f8fafc;
}

.section-kicker {
  margin-bottom: 0.25rem;
  font-family: var(--font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace);
  font-size: 0.66rem;
  letter-spacing: 0.2em;
  color: #22d3ee;
}

/* 背景网格图案 */
.bg-grid-pattern {
  background-image: linear-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
}

/* 按钮样式 */
.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.5rem;
  border-radius: 0.5rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: white;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  border-color: rgba(99, 102, 241, 0.5);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.5rem;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.5rem;
  border-radius: 0.5rem;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
}

/* 输入框样式 */
.select-input {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(100, 116, 139, 0.5);
  color: #e2e8f0;
  transition: all 0.2s ease;
}

.select-input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.5s ease forwards;
}

.animate-fadeInUp {
  animation: fadeInUp 0.5s ease forwards;
}

/* 玻璃态卡片样式 */
.glass-card {
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(100, 116, 139, 0.2);
  transition: all 0.3s ease;
}

.glass-card:hover {
  background: rgba(15, 23, 42, 0.6);
  border-color: rgba(100, 116, 139, 0.3);
  transform: translateY(-2px);
}

/* 悬停提升效果 */
.hover-lift {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
}
</style>
