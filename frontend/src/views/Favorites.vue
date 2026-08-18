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
          <router-link to="/favorites" class="terminal-nav active">收藏</router-link>
          <span class="mx-2 hidden h-4 w-px bg-slate-800 md:inline-block"></span>
          <router-link to="/contact" class="terminal-nav">联系我们</router-link>
        </nav>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="terminal-main">
      <!-- 页面标题 -->
      <div class="mb-8">
        <p class="section-kicker">FAVORITES</p>
        <h2 class="text-3xl font-semibold text-slate-100">我的收藏</h2>
        <p class="mt-2 text-slate-400">
          管理和浏览你收藏的 GitHub 开源项目
        </p>
      </div>

      <!-- 搜索栏 -->
      <div class="mb-6">
        <div class="relative max-w-2xl">
          <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索收藏的项目..."
            class="w-full pl-12 pr-4 py-3 terminal-search"
          >
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="terminal-loading">
        <div class="spinner"></div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="filteredProjects.length === 0" class="terminal-empty py-20">
        <svg class="w-16 h-16 text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
        </svg>
        <h3 v-if="searchQuery" class="text-lg font-medium text-slate-400 mb-2">没有匹配的项目</h3>
        <h3 v-else class="text-lg font-medium text-slate-400 mb-2">暂无收藏</h3>
        <p v-if="!searchQuery" class="text-slate-500 mb-6">在项目卡片右上角点击 ❤️ 即可收藏感兴趣的项目</p>
        <p v-else class="text-slate-500 mb-6">试试其他关键词</p>
        <router-link v-if="!searchQuery" to="/" class="terminal-action primary">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
          </svg>
          去首页发现项目
        </router-link>
      </div>

      <!-- 已加载内容 -->
      <div v-else>
        <!-- 统计信息 -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div class="terminal-metric">
            <span>收藏总数</span>
            <strong>{{ favorites.length }}</strong>
          </div>
          <div class="terminal-metric">
            <span>语言种类</span>
            <strong>{{ uniqueLanguages }}</strong>
          </div>
          <div class="terminal-metric">
            <span>热门语言</span>
            <strong>{{ topLanguage || '-' }}</strong>
          </div>
          <div class="terminal-metric">
            <span>总星标数</span>
            <strong>{{ totalStars }}</strong>
          </div>
        </div>

        <!-- 项目列表 -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <div
            v-for="project in filteredProjects"
            :key="project.name"
            class="terminal-panel relative overflow-hidden group"
          >
            <!-- 取消收藏按钮（hover 时右上角显示） -->
            <button
              type="button"
              class="absolute top-3 right-3 z-10 w-7 h-7 flex items-center justify-center rounded-full bg-slate-900/70 border border-slate-700/80 opacity-0 group-hover:opacity-100 hover:!opacity-100 hover:border-rose-500/60 hover:bg-rose-500/15 transition-all"
              title="移除收藏"
              aria-label="移除收藏"
              @click.stop="onRemoveFavorite(project.name)"
            >
              <svg class="w-3.5 h-3.5 text-slate-300 group-hover:text-rose-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>

            <!-- 项目内容 -->
            <div class="p-5 cursor-pointer" @click="viewProjectDetails(project.name)">
              <div class="mb-3 pr-8">
                <h3 class="font-semibold text-slate-200 text-lg mb-2 line-clamp-1">
                  {{ getProjectDisplayName(project.name) }}
                </h3>
                <p class="text-slate-400 text-sm line-clamp-2 leading-relaxed">
                  {{ project.description || '暂无描述' }}
                </p>
              </div>

              <!-- 项目标签 -->
              <div class="flex items-center justify-between">
                <span
                  v-if="project.language"
                  class="px-2 py-1 text-xs rounded border border-slate-700 text-slate-400"
                >
                  {{ project.language }}
                </span>
                <span
                  v-else
                  class="px-2 py-1 text-xs rounded border border-slate-700 text-slate-500"
                >
                  未知
                </span>

                <div class="flex items-center text-sm text-slate-500">
                  <svg class="w-4 h-4 mr-1 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                  </svg>
                  {{ formatNumber(project.stars) }}
                </div>
              </div>

              <!-- 更新时间 -->
              <div class="mt-4 pt-4 border-t border-slate-800">
                <div class="text-xs text-slate-500">
                  收藏于 {{ formatDate(project.summary_date) }}
                </div>
              </div>
            </div>
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
import { computed, onMounted, ref } from 'vue'
import ProjectModal from '@/components/ProjectModal.vue'
import { useFavorites } from '@/composables/useFavorites'

const loading = ref(true)
const searchQuery = ref('')
const showProjectModal = ref(false)
const selectedProjectName = ref('')

const { favorites, ensureLoaded, toggleFavorite } = useFavorites()

onMounted(async () => {
  try {
    await ensureLoaded()
  } finally {
    loading.value = false
  }
})

async function onRemoveFavorite(projectName: string) {
  const project = favorites.value.find((p) => p.name === projectName)
  if (!project) return
  try {
    await toggleFavorite(project)
  } catch (e) {
    console.error('移除收藏失败:', e)
  }
}

function viewProjectDetails(projectName: string) {
  selectedProjectName.value = projectName
  showProjectModal.value = true
}

function getProjectDisplayName(name: string): string {
  const parts = name.split('/')
  return parts.length > 1 ? parts[1] ?? name : name
}

function formatNumber(num: number | undefined): string {
  if (!num || num === 0) return '0'
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr || dateStr === 'N/A') return '未知'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
  } catch {
    return '未知'
  }
}

const filteredProjects = computed(() => {
  let result = favorites.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(
      (project) =>
        project.name.toLowerCase().includes(query) ||
        project.description?.toLowerCase().includes(query) ||
        project.language?.toLowerCase().includes(query),
    )
  }
  return result
})

const uniqueLanguages = computed(() => {
  const languages = new Set(favorites.value.map((p) => p.language).filter((lang) => lang))
  return languages.size
})

const topLanguage = computed(() => {
  const counts: Record<string, number> = {}
  favorites.value.forEach((p) => {
    if (p.language) {
      counts[p.language] = (counts[p.language] || 0) + 1
    }
  })
  let max = 0
  let top = ''
  for (const [lang, c] of Object.entries(counts)) {
    if (c > max) {
      max = c
      top = lang
    }
  }
  return top
})

const totalStars = computed(() => {
  return formatNumber(favorites.value.reduce((sum, p) => sum + (p.stars || 0), 0))
})
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>