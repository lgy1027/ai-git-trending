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
          <router-link to="/rankings" class="terminal-nav active">排行榜</router-link>
          <router-link to="/trend-analysis" class="terminal-nav">趋势图谱</router-link>
          <router-link to="/favorites" class="terminal-nav">收藏</router-link>
        </nav>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="terminal-main">
      <!-- 页面标题 -->
      <div class="mb-8">
        <p class="section-kicker">LEADERBOARD</p>
        <h2 class="text-3xl font-semibold text-slate-100">项目排行榜</h2>
        <p class="mt-2 text-slate-400 max-w-2xl">
          查看最受欢迎的开源项目，按不同类别和时间段进行排名
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
        <select v-model="selectedCategory" class="terminal-select">
          <option v-for="category in categories" :key="category.name" :value="category.name">
            {{ formatCategoryName(category) }}
          </option>
        </select>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="terminal-loading">
        <div class="spinner"></div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="projects.length === 0" class="terminal-empty">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
        </svg>
        <h3 class="text-lg font-medium text-slate-400 mb-2">暂无排名数据</h3>
        <p class="text-slate-500">请尝试选择其他时间段或分类</p>
      </div>

      <!-- 项目列表 -->
      <div v-else class="space-y-4">
        <div
          v-for="(project, index) in projects"
          :key="project.name"
          class="terminal-panel p-4 flex items-center gap-4"
        >
          <!-- 排名 -->
          <div class="w-10 h-10 rounded-lg bg-cyan-400/10 border border-cyan-400/30 flex items-center justify-center text-cyan-300 font-bold text-lg">
            {{ (currentPage - 1) * pageSize + index + 1 }}
          </div>

          <!-- 项目卡片 -->
          <div class="flex-1 cursor-pointer" @click="viewProjectDetails(project)">
            <ProjectCard :project="project" />
          </div>
        </div>

        <!-- 分页控件 -->
        <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 mt-8">
          <button
            class="terminal-action"
            :disabled="currentPage === 1"
            @click="changePage(currentPage - 1)"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
          </button>

          <template v-for="page in totalPages" :key="page">
            <button
              v-if="page === 1 || page === totalPages || (page >= currentPage - 1 && page <= currentPage + 1)"
              class="terminal-action"
              :class="{ 'primary': currentPage === page }"
              @click="changePage(page)"
            >
              {{ page }}
            </button>
            <span
              v-else-if="page === currentPage - 2 || page === currentPage + 2"
              class="text-slate-500"
            >
              ...
            </span>
          </template>

          <button
            class="terminal-action"
            :disabled="currentPage === totalPages"
            @click="changePage(currentPage + 1)"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
        </div>

        <!-- 总数显示 -->
        <div v-if="totalProjects > 0" class="text-center text-sm text-slate-500 mt-4">
          共 {{ totalProjects }} 个项目，第 {{ currentPage }}/{{ totalPages }} 页
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
import { ref, computed, onMounted, watch } from 'vue'
import { reportApi, type Project } from '@/api/reports'
import ProjectCard from '@/components/ProjectCard.vue'
import ProjectModal from '@/components/ProjectModal.vue'

const loading = ref(false)
const projects = ref<Project[]>([])
const selectedPeriod = ref('daily')
const selectedCategory = ref('all')
const showProjectModal = ref(false)
const selectedProjectName = ref('')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(20)
const totalProjects = ref(0)
const totalPages = computed(() => Math.ceil(totalProjects.value / pageSize.value))

const timePeriods = [
  { label: '今日', value: 'daily' },
  { label: '本周', value: 'weekly' },
  { label: '本月', value: 'monthly' },
  { label: '全年', value: 'yearly' }
]

const categories = ref<{ name: string; count: number }[]>([{ name: 'all', count: 0 }])
const loadingDomains = ref(false)

// 加载技术领域分类
const loadTechDomains = async () => {
  loadingDomains.value = true
  try {
    const domains = await reportApi.getTechDomains()
    if (domains && domains.length > 0) {
      // 过滤掉 count 为 0 的领域，但保留 'all'
      const domainOptions = domains
        .filter(d => d.count > 0)
        .map(d => ({ name: d.name, count: d.count }))
      categories.value = [{ name: 'all', count: domainOptions.reduce((sum, d) => sum + d.count, 0) }, ...domainOptions]
    }
  } catch (error) {
    console.error('加载技术领域失败:', error)
  } finally {
    loadingDomains.value = false
  }
}

// 格式化显示名称
const formatCategoryName = (category: { name: string; count: number }) => {
  if (category.name === 'all') {
    return category.count > 0 ? `全部领域 (${category.count})` : '全部领域'
  }
  return `${category.name} (${category.count})`
}

// 根据选择的时间段计算日期范围
const getDateRange = (period: string): { dateFrom: string; dateTo: string } => {
  const now = new Date()
  const today = now.toISOString().split('T')[0]
  let dateFrom: string
  let dateTo = today

  switch (period) {
    case 'daily':
      dateFrom = today
      break
    case 'weekly':
      const weekAgo = new Date(now)
      weekAgo.setDate(now.getDate() - 7)
      dateFrom = weekAgo.toISOString().split('T')[0]
      break
    case 'monthly':
      const monthAgo = new Date(now)
      monthAgo.setMonth(now.getMonth() - 1)
      dateFrom = monthAgo.toISOString().split('T')[0]
      break
    case 'yearly':
      const yearAgo = new Date(now)
      yearAgo.setFullYear(now.getFullYear() - 1)
      dateFrom = yearAgo.toISOString().split('T')[0]
      break
    default:
      dateFrom = today
  }

  return { dateFrom, dateTo }
}

// 加载项目列表（支持日期范围、技术领域筛选和分页）
const loadProjects = async () => {
  loading.value = true
  try {
    const { dateFrom, dateTo } = getDateRange(selectedPeriod.value)
    const params: any = {
      date_from: dateFrom,
      date_to: dateTo,
      sort_by: 'stars',
      order: 'desc',
      page: currentPage.value,
      page_size: pageSize.value
    }
    // 使用技术领域筛选
    if (selectedCategory.value !== 'all') {
      params.tech_domain = selectedCategory.value
    }
    const response = await reportApi.getProjects(params)
    projects.value = response.items || []
    totalProjects.value = response.total || 0
  } catch (error) {
    console.error('Failed to load projects:', error)
  } finally {
    loading.value = false
  }
}

// 切换页码
const changePage = (page: number) => {
  currentPage.value = page
  loadProjects()
}

// 监听筛选变化，重置到第一页
watch(selectedPeriod, () => {
  currentPage.value = 1
  loadProjects()
})

watch(selectedCategory, () => {
  currentPage.value = 1
  loadProjects()
})

const viewProjectDetails = (project: Project) => {
  selectedProjectName.value = project.name
  showProjectModal.value = true
}

onMounted(() => {
  loadTechDomains()
  loadProjects()
})
</script>

<style scoped>
.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: white;
}

.stat-label {
  font-size: 12px;
  color: slate-400;
}
</style>
