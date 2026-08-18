<template>
  <transition name="modal">
    <div 
      v-if="visible" 
      class="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4"
      @click="handleBackdropClick"
    >
      <div
        ref="modalContent"
        class="bg-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col animate-fadeIn"
        @click.stop
      >
        <!-- 模态框头部 -->
        <div class="p-6 border-b border-white/10 flex justify-between items-center">
          <div class="flex items-center flex-1 min-w-0">
            <i class="fa fa-github text-primary mr-3 text-xl"></i>
            <div class="min-w-0 flex-1">
              <h3 class="text-xl font-bold text-white truncate">{{ projectName }}</h3>
              <p class="text-slate-400 text-sm truncate">{{ project?.url }}</p>
            </div>
            <a
              :href="projectName ? `https://github.com/${projectName}` : '#'"
              target="_blank"
              class="btn-secondary inline-flex items-center gap-2 ml-4"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              在 GitHub 查看
            </a>
          </div>
          <button
            @click="$emit('close')"
            class="p-2 rounded-full hover:bg-white/10 transition-colors flex-shrink-0 ml-4"
          >
            <i class="fa fa-times text-xl text-slate-400"></i>
          </button>
        </div>

        <!-- 模态框内容 -->
        <div class="flex-grow overflow-y-auto">
          <div v-if="loading" class="h-full flex flex-col items-center justify-center py-12">
            <div class="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
            <p class="text-slate-400">加载项目详情中...</p>
          </div>

          <div v-else-if="project" class="p-6">
            <!-- 项目描述 -->
            <div class="mb-6">
              <h4 class="text-lg font-semibold text-white mb-3 flex items-center">
                <i class="fa fa-info-circle text-primary mr-2"></i>
                项目描述
              </h4>
              <p class="text-slate-300 leading-relaxed bg-slate-900/50 p-4 rounded-lg">
                {{ project.description || '暂无描述' }}
              </p>
            </div>

            <!-- 技术信息 -->
            <div class="mb-6">
              <h4 class="text-lg font-semibold text-white mb-3 flex items-center">
                <i class="fa fa-code text-primary mr-2"></i>
                技术信息
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="tech-info-item">
                  <span class="label">主要语言</span>
                  <span 
                    class="value language-tag"
                    :class="getLanguageClass(project.language)"
                  >
                    {{ project.language || '未知' }}
                  </span>
                </div>
                <div class="tech-info-item">
                  <span class="label">创建时间</span>
                  <span class="value">{{ formatFullDate(project.created_at) }}</span>
                </div>
                <div class="tech-info-item">
                  <span class="label">最后更新</span>
                  <span class="value">{{ formatFullDate(project.updated_at) }}</span>
                </div>
                <div class="tech-info-item">
                  <span class="label">开放问题</span>
                  <span class="value">{{ formatNumber(project.open_issues) }}</span>
                </div>
              </div>
            </div>

            <!-- 统计数据 -->
            <div class="mb-6">
              <h4 class="text-lg font-semibold text-white mb-3 flex items-center">
                <i class="fa fa-bar-chart text-primary mr-2"></i>
                项目统计
              </h4>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="stat-card">
                  <div class="stat-icon bg-yellow-500/20">
                    <i class="fa fa-star text-yellow-400"></i>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ formatNumber(project.stars) }}</div>
                    <div class="stat-label">Stars</div>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-icon bg-blue-500/20">
                    <i class="fa fa-code-fork text-blue-400"></i>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ formatNumber(project.forks) }}</div>
                    <div class="stat-label">Forks</div>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-icon bg-green-500/20">
                    <i class="fa fa-users text-green-400"></i>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ formatNumber(project.contributor_count) }}</div>
                    <div class="stat-label">贡献者</div>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-icon bg-purple-500/20">
                    <i class="fa fa-eye text-purple-400"></i>
                  </div>
                  <div class="stat-content">
                    <div class="stat-value">{{ formatNumber(project.watchers) }}</div>
                    <div class="stat-label">关注者</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- AI 深度分析 -->
            <div class="mb-6">
              <button
                @click="toggleAnalysis"
                :class="['analysis-toggle w-full', analysisExpanded ? 'expanded' : '']"
                :disabled="analysisLoading"
              >
                <div class="flex items-center justify-between">
                  <div class="flex items-center">
                    <i class="fa fa-robot text-primary mr-2"></i>
                    <span class="text-lg font-semibold text-white">AI 深度分析</span>
                    <span v-if="analysisLoaded && !analysisHasContent" class="ml-3 text-xs text-slate-400">
                      暂无分析报告
                    </span>
                  </div>
                  <i
                    :class="['fa text-slate-400 transition-transform duration-300', analysisExpanded ? 'fa-chevron-up' : 'fa-chevron-down']"
                  ></i>
                </div>
              </button>

              <div v-if="analysisExpanded" class="mt-4">
                <div v-if="analysisLoading" class="flex flex-col items-center justify-center py-8">
                  <div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mb-3"></div>
                  <p class="text-slate-400 text-sm">正在加载分析报告...</p>
                </div>

                <div v-else-if="analysisError" class="text-center py-6">
                  <i class="fa fa-exclamation-circle text-red-400 text-2xl mb-2"></i>
                  <p class="text-slate-400 text-sm">{{ analysisError }}</p>
                </div>

                <div
                  v-else-if="analysisHasContent"
                  ref="analysisContainer"
                  class="markdown-content prose prose-invert max-w-none border border-slate-700 bg-slate-900/50 p-4 rounded-lg text-sm"
                  v-html="renderedAnalysis"
                ></div>

                <div v-else class="text-center py-6 text-slate-500 text-sm">
                  <i class="fa fa-file-text-o text-2xl mb-2 block"></i>
                  该项目暂无 AI 分析报告
                </div>
              </div>
            </div>
          </div>

          <div v-else class="h-full flex flex-col items-center justify-center py-12">
            <i class="fa fa-exclamation-triangle text-red-400 text-4xl mb-4"></i>
            <p class="text-slate-400">加载项目详情失败</p>
          </div>
        </div>

        <!-- 模态框底部 -->
        <div class="p-6 border-t border-white/10 flex justify-between items-center">
          <div class="text-slate-400 text-sm">
            分析时间：{{ project?.summary_date ? formatFullDate(project.summary_date) : '未知' }}
          </div>
          <div class="flex space-x-3">
            <a 
              v-if="project?.url" 
              :href="project.url" 
              target="_blank" 
              rel="noopener noreferrer"
              class="px-4 py-2 bg-primary rounded-lg hover:bg-primary/80 transition-colors flex items-center"
            >
              <i class="fa fa-external-link mr-2"></i>
              访问项目
            </a>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import type { Project } from '@/api/reports'
import { getProjectAnalysis, getProjectDetails } from '@/api/reports'
import { enhanceMarkdownDisplay, renderMarkdown } from '@/utils/markdown-simple'

interface Props {
  visible: boolean
  projectName?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

const modalContent = ref<HTMLElement>()
const analysisContainer = ref<HTMLElement>()
const loading = ref(false)
const project = ref<Project | null>(null)

// AI 分析区域状态
const analysisExpanded = ref(false)
const analysisLoading = ref(false)
const analysisLoaded = ref(false)
const analysisHasContent = ref(false)
const analysisError = ref('')
const renderedAnalysis = ref('')

const projectDisplayName = computed(() => {
  if (!props.projectName) return ''
  const parts = props.projectName.split('/')
  return parts.length > 1 ? parts[1] : props.projectName
})

watch(() => props.visible, async (visible) => {
  if (visible && props.projectName) {
    resetAnalysisState()
    await loadProjectDetails()
  }
})

// 监听项目名变化，重置分析状态
watch(() => props.projectName, () => {
  resetAnalysisState()
})

const loadProjectDetails = async () => {
  if (!props.projectName) return

  loading.value = true
  try {
    // 修改为使用查询参数，而不是路径参数，以更好地处理包含特殊字符的项目名称
    project.value = await getProjectDetails(props.projectName)
  } catch (error) {
    console.error('Failed to load project details:', error)
    project.value = null
  } finally {
    loading.value = false
  }
}

function resetAnalysisState() {
  analysisExpanded.value = false
  analysisLoading.value = false
  analysisLoaded.value = false
  analysisHasContent.value = false
  analysisError.value = ''
  renderedAnalysis.value = ''
}

async function toggleAnalysis() {
  if (analysisLoading.value) return
  analysisExpanded.value = !analysisExpanded.value
  // 首次展开时按需加载
  if (analysisExpanded.value && !analysisLoaded.value) {
    await loadAnalysis()
  }
}

async function loadAnalysis() {
  if (!props.projectName) return
  analysisLoading.value = true
  analysisError.value = ''
  try {
    const result = await getProjectAnalysis(props.projectName)
    analysisHasContent.value = result.has_analysis
    if (result.has_analysis) {
      renderedAnalysis.value = await renderMarkdown(result.content)
      await nextTick()
      if (analysisContainer.value) {
        enhanceMarkdownDisplay(analysisContainer.value)
      }
    }
    analysisLoaded.value = true
  } catch (error) {
    console.error('加载 AI 分析失败:', error)
    analysisError.value = error instanceof Error ? error.message : '加载失败，请重试'
    analysisLoaded.value = true
  } finally {
    analysisLoading.value = false
  }
}

const handleBackdropClick = (event: MouseEvent) => {
  if (event.target === event.currentTarget) {
    emit('close')
  }
}

const formatNumber = (num: number | string): string => {
  if (typeof num === 'string') return num
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

const formatFullDate = (dateStr: string): string => {
  if (!dateStr || dateStr === 'N/A') return '未知'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch {
    return '未知'
  }
}

const getLanguageClass = (language: string): string => {
  const languageColors: Record<string, string> = {
    'JavaScript': 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
    'TypeScript': 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
    'Python': 'bg-green-500/20 text-green-400 border border-green-500/30',
    'Java': 'bg-orange-500/20 text-orange-400 border border-orange-500/30',
    'Go': 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30',
    'Rust': 'bg-red-500/20 text-red-400 border border-red-500/30',
    'C++': 'bg-purple-500/20 text-purple-400 border border-purple-500/30',
    'C': 'bg-gray-500/20 text-gray-400 border border-gray-500/30',
    'PHP': 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30',
    'Ruby': 'bg-red-600/20 text-red-400 border border-red-600/30',
    'Swift': 'bg-orange-600/20 text-orange-400 border border-orange-600/30',
    'Kotlin': 'bg-purple-600/20 text-purple-400 border border-purple-600/30'
  }
  
  return languageColors[language] || 'bg-slate-500/20 text-slate-400 border border-slate-500/30'
}
</script>

<style scoped>
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

.tech-info-item {
  @apply bg-slate-900/50 p-3 rounded-lg flex justify-between items-center;
}

.tech-info-item .label {
  @apply text-slate-400 text-sm;
}

.tech-info-item .value {
  @apply text-white font-medium;
}

.language-tag {
  @apply px-2 py-1 rounded-full text-xs font-medium;
}

.stat-card {
  @apply bg-slate-900/50 p-4 rounded-lg flex items-center space-x-3 hover:bg-slate-900/70 transition-colors;
}

.stat-icon {
  @apply w-10 h-10 rounded-lg flex items-center justify-center;
}

.stat-content {
  @apply flex-1;
}

.stat-value {
  @apply text-lg font-bold text-white;
}

.stat-label {
  @apply text-slate-400 text-xs;
}

.analysis-toggle {
  @apply bg-slate-900/50 hover:bg-slate-900/70 border border-slate-700/80 rounded-lg px-4 py-3 transition-colors duration-300;
}

.analysis-toggle:disabled {
  @apply opacity-60 cursor-not-allowed;
}

.analysis-toggle.expanded {
  @apply border-primary/40 bg-slate-900/80;
}

.analysis-toggle:focus {
  @apply outline-none ring-2 ring-primary/30;
}

.analysis-toggle:focus:not(:focus-visible) {
  @apply ring-0;
}

.analysis-toggle :deep(.fa-chevron-up) {
  transform: translateY(0);
}

.analysis-toggle :deep(.fa-chevron-down) {
  transform: translateY(0);
}

.markdown-content :deep(h1) {
  @apply text-xl font-semibold text-slate-100 border-b border-slate-700 pb-2 mb-3;
}

.markdown-content :deep(h2) {
  @apply text-base font-semibold text-slate-200 mt-5 mb-3;
}

.markdown-content :deep(h3) {
  @apply text-sm font-semibold text-slate-200 mt-4 mb-2;
}

.markdown-content :deep(p) {
  @apply text-slate-300 leading-relaxed my-2;
}

.markdown-content :deep(ul) {
  @apply list-disc list-inside text-slate-300 my-2 space-y-1;
}

.markdown-content :deep(ol) {
  @apply list-decimal list-inside text-slate-300 my-2 space-y-1;
}

.markdown-content :deep(li) {
  @apply text-slate-300;
}

.markdown-content :deep(blockquote) {
  @apply border-l-4 border-primary/50 bg-slate-900/60 px-4 py-2 my-3 text-slate-300 italic rounded-r;
}

.markdown-content :deep(strong) {
  @apply text-slate-100 font-semibold;
}

.markdown-content :deep(a) {
  @apply text-primary hover:text-primary/80 underline;
}

.markdown-content :deep(code) {
  @apply bg-slate-800 text-cyan-300 px-1.5 py-0.5 rounded text-xs;
}

.markdown-content :deep(pre) {
  @apply bg-slate-950 border border-slate-800 rounded p-3 overflow-x-auto my-3;
}

.markdown-content :deep(pre code) {
  @apply bg-transparent text-slate-200 p-0;
}

.markdown-content :deep(hr) {
  @apply border-slate-700 my-4;
}

.markdown-content :deep(table) {
  @apply w-full border-collapse my-3 text-slate-300;
}

.markdown-content :deep(th) {
  @apply bg-slate-800 text-slate-100 px-3 py-2 border border-slate-700 text-left;
}

.markdown-content :deep(td) {
  @apply px-3 py-2 border border-slate-700;
}
</style>
