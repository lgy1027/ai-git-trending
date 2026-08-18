<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
    <div class="relative w-full max-w-6xl max-h-[90vh] overflow-hidden rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl animate-fadeIn">
      <!-- 模态框头部 -->
      <div class="sticky top-0 z-10 flex items-center justify-between p-6 bg-slate-900 border-b border-slate-800">
        <h2 class="text-xl font-bold text-white flex items-center">
          <i class="fa fa-line-chart text-primary mr-3"></i>
          技术趋势深度分析
        </h2>
        <div class="flex items-center space-x-3">
          <button class="btn-icon" @click="handleClose">
            <i class="fa fa-times"></i>
          </button>
        </div>
      </div>

      <!-- 模态框内容 -->
      <div class="p-6 overflow-y-auto max-h-[calc(90vh-8rem)]">
        <!-- 时间选择器 -->
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center space-x-2">
            <button
              v-for="window in timeWindows"
              :key="window.value"
              :class="['text-sm px-4 py-2 rounded-lg transition-colors', selectedWindow === window.value ? 'bg-primary text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700']"
              @click="selectedWindow = window.value"
            >
              {{ window.label }}
            </button>
          </div>
          <div class="text-sm text-slate-400">
            显示趋势数据从 {{ formatDate(startDate) }} 至 {{ formatDate(endDate) }}
          </div>
        </div>

        <!-- 顶部 KPI 卡片 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="glass-card p-6 rounded-xl">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-white">热门项目</h3>
              <i class="fa fa-fire text-orange-400"></i>
            </div>
            <div class="flex items-end space-x-3">
              <div class="text-3xl font-bold text-white">{{ topProjectCount }}</div>
              <div class="text-sm text-slate-400 mb-1">个</div>
            </div>
          </div>

          <div class="glass-card p-6 rounded-xl">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-white">活跃贡献者</h3>
              <i class="fa fa-users text-cyan-400"></i>
            </div>
            <div class="flex items-end space-x-3">
              <div class="text-3xl font-bold text-white">{{ totalContributors }}</div>
              <div class="text-sm text-slate-400 mb-1">累计</div>
            </div>
          </div>

          <div class="glass-card p-6 rounded-xl">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-white">编程语言</h3>
              <i class="fa fa-code text-emerald-400"></i>
            </div>
            <div class="flex items-end space-x-3">
              <div class="text-3xl font-bold text-white">{{ languageCount }}</div>
              <div class="text-sm text-slate-400 mb-1">种</div>
            </div>
          </div>
        </div>

        <!-- 双列图表区域 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <!-- 编程语言分布 -->
          <div class="glass-card p-6 rounded-xl">
            <h3 class="text-lg font-semibold text-white mb-6">编程语言分布</h3>
            <div class="h-80">
              <canvas id="languageTrendChart"></canvas>
            </div>
          </div>

          <!-- 技术领域分布 -->
          <div class="glass-card p-6 rounded-xl">
            <h3 class="text-lg font-semibold text-white mb-6">技术领域分布</h3>
            <div class="h-80">
              <canvas id="techDomainChart"></canvas>
            </div>
          </div>
        </div>

        <!-- 热门技术领域深度分析 -->
        <div class="glass-card p-6 rounded-xl">
          <h3 class="text-lg font-semibold text-white mb-6">热门技术领域深度分析</h3>

          <div v-if="techDomainRows.length > 0" class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-slate-800">
                  <th class="text-left py-3 px-4 text-sm font-medium text-slate-400">技术领域</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-slate-400">项目数</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-slate-400">占比</th>
                  <th class="text-left py-3 px-4 text-sm font-medium text-slate-400">活跃度</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in techDomainRows" :key="row.name" class="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                  <td class="py-3 px-4 text-sm font-medium text-white">{{ row.name }}</td>
                  <td class="py-3 px-4 text-sm text-slate-300">{{ row.count }}</td>
                  <td class="py-3 px-4 text-sm text-slate-300">{{ row.percentage }}%</td>
                  <td class="py-3 px-4">
                    <div class="w-full bg-slate-700/50 rounded-full h-2 mb-1">
                      <div
                        class="h-full rounded-full bg-gradient-to-r from-blue-500 to-purple-500"
                        :style="{ width: row.percentage + '%' }"
                      ></div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else class="text-center py-8">
            <div class="w-16 h-16 bg-slate-700/50 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fa fa-table text-slate-400 text-xl"></i>
            </div>
            <p class="text-slate-400">暂无技术领域数据</p>
            <p class="text-slate-500 text-sm mt-2">需要更多天的爬取数据积累</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import type { TrendsData, TechDomainData } from '@/api/reports'
import { getTechDomains } from '@/api/reports'

Chart.register(...registerables)

interface TechTrendsModalProps {
  visible: boolean
  trendsData?: TrendsData
}

const emit = defineEmits<{
  close: []
}>()

const props = withDefaults(defineProps<TechTrendsModalProps>(), {
  visible: false,
  trendsData: () => ({
    time_window_days: 30,
    most_frequent_projects: [],
    most_frequent_languages: [],
    surgingProjects: []
  })
})

interface TechDomainRow {
  name: string
  count: number
  percentage: number
}

const selectedWindow = ref<string>('30天')
const languageChart = ref<Chart | null>(null)
const techDomainChart = ref<Chart | null>(null)
const techDomains = ref<TechDomainData[]>([])

const timeWindows = [
  { value: '7天', label: '最近7天' },
  { value: '30天', label: '最近30天' },
  { value: '90天', label: '最近90天' },
  { value: '1年', label: '最近1年' }
]

const startDate = computed(() => {
  const today = new Date()
  switch (selectedWindow.value) {
    case '7天': return new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
    case '30天': return new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
    case '90天': return new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000)
    case '1年': return new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000)
    default: return new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
  }
})

const endDate = computed(() => new Date())

// 顶部 KPI：从 trendsData 直接计算
const topProjectCount = computed(() => props.trendsData?.most_frequent_projects?.length ?? 0)

const totalContributors = computed(() => {
  const projects = props.trendsData?.most_frequent_projects ?? []
  return projects.reduce((sum, p) => sum + (p.contributor_count ?? 0), 0)
})

const languageCount = computed(() => props.trendsData?.most_frequent_languages?.length ?? 0)

// 技术领域表格行：仅展示 count > 0 的领域，按 count 倒序，占比基于全量 15 个领域总数
const techDomainRows = computed<TechDomainRow[]>(() => {
  const total = techDomains.value.reduce((sum, d) => sum + d.count, 0)
  if (total === 0) return []
  return techDomains.value
    .filter(d => d.count > 0)
    .sort((a, b) => b.count - a.count)
    .map(d => ({
      name: d.name,
      count: d.count,
      percentage: Math.round((d.count / total) * 100)
    }))
})

watch(() => props.visible, async (newVisible) => {
  if (newVisible) {
    await loadTechDomains()
    await nextTick()
    initCharts()
    document.body.style.overflow = 'hidden'
  } else {
    destroyCharts()
    document.body.style.overflow = ''
  }
})

async function loadTechDomains() {
  try {
    techDomains.value = await getTechDomains({ days: getDaysFromWindow(selectedWindow.value) })
  } catch (e) {
    console.error('加载技术领域失败:', e)
    techDomains.value = []
  }
}

function initCharts() {
  destroyCharts()

  const languageCtx = document.getElementById('languageTrendChart') as HTMLCanvasElement
  if (languageCtx) {
    languageChart.value = new Chart(languageCtx, getLanguageBarConfig())
  }

  const techDomainCtx = document.getElementById('techDomainChart') as HTMLCanvasElement
  if (techDomainCtx) {
    techDomainChart.value = new Chart(techDomainCtx, getTechDomainDoughnutConfig())
  }
}

function destroyCharts() {
  languageChart.value?.destroy()
  languageChart.value = null
  techDomainChart.value?.destroy()
  techDomainChart.value = null
}

// 编程语言分布：条形图（top 10）
function getLanguageBarConfig() {
  const languages = props.trendsData?.most_frequent_languages ?? []
  const top = languages.slice(0, 10)
  const labels = top.map(([name]) => name)
  const data = top.map(([, count]) => count)

  return {
    type: 'bar' as const,
    data: {
      labels,
      datasets: [{
        label: '项目数',
        data,
        backgroundColor: '#6366f1',
        borderColor: '#818cf8',
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y' as const,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          titleColor: '#e2e8f0',
          bodyColor: '#94a3b8',
          padding: 10,
          callbacks: {
            label: (ctx: any) => ` ${ctx.raw} 个项目`
          }
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: { color: 'rgba(100, 116, 139, 0.1)' },
          ticks: { color: '#94a3b8', stepSize: 1 }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#94a3b8' }
        }
      }
    }
  }
}

// 技术领域分布：环形图
function getTechDomainDoughnutConfig() {
  const palette = ['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#3b82f6', '#f43f5e', '#0ea5e9', '#22c55e', '#a855f7']
  const filtered = techDomains.value.filter(d => d.count > 0)
  const labels = filtered.map(d => d.name)
  const data = filtered.map(d => d.count)

  return {
    type: 'doughnut' as const,
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: palette.slice(0, data.length),
        borderColor: 'rgba(15, 23, 42, 0.3)',
        borderWidth: 2,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'right' as const,
          labels: { color: '#94a3b8', padding: 10, font: { size: 11 } }
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          titleColor: '#e2e8f0',
          bodyColor: '#94a3b8',
          padding: 10,
          callbacks: {
            label: (ctx: any) => {
              const total = data.reduce((s, v) => s + v, 0)
              const pct = total > 0 ? Math.round((ctx.raw / total) * 100) : 0
              return ` ${ctx.label}: ${ctx.raw} (${pct}%)`
            }
          }
        }
      }
    }
  }
}

function formatDate(date: Date): string {
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

function getDaysFromWindow(window: string): number {
  switch (window) {
    case '7天': return 7
    case '30天': return 30
    case '90天': return 90
    case '1年': return 365
    default: return 30
  }
}

function handleClose() {
  emit('close')
}

onMounted(() => {
  if (props.visible) {
    loadTechDomains()
    nextTick(() => initCharts())
  }
})
</script>

<style scoped>
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

.glass-card {
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(100, 116, 139, 0.2);
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease forwards;
}

.overflow-y-auto::-webkit-scrollbar { width: 6px; }
.overflow-y-auto::-webkit-scrollbar-track { background: rgba(100, 116, 139, 0.1); border-radius: 3px; }
.overflow-y-auto::-webkit-scrollbar-thumb { background: rgba(100, 116, 139, 0.5); border-radius: 3px; }
.overflow-y-auto::-webkit-scrollbar-thumb:hover { background: rgba(100, 116, 139, 0.7); }

.overflow-x-auto::-webkit-scrollbar { height: 6px; }
.overflow-x-auto::-webkit-scrollbar-track { background: rgba(100, 116, 139, 0.1); border-radius: 3px; }
.overflow-x-auto::-webkit-scrollbar-thumb { background: rgba(100, 116, 139, 0.5); border-radius: 3px; }
.overflow-x-auto::-webkit-scrollbar-thumb:hover { background: rgba(100, 116, 139, 0.7); }

table { border-collapse: collapse; width: 100%; }
th, td { padding: 8px; text-align: left; }

@media (max-width: 768px) {
  .time-windows { overflow-x: auto; padding-bottom: 10px; }
  .grid-cols-2 { grid-template-columns: 1fr; }
  .max-w-6xl { max-width: 100%; }
}
</style>
