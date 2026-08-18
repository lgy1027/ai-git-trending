<template>
  <div
    class="project-card relative bg-slate-900/50 border border-slate-800/50 rounded-lg overflow-hidden cursor-pointer animate-fadeInUp group hover:border-slate-700/80 hover:bg-slate-800/30 transition-all duration-300"
    @click="$emit('click', project)"
    :style="{ animationDelay: `${index * 0.08}s` }"
  >
    <!-- 收藏按钮（绝对定位右上角） -->
    <button
      type="button"
      class="favorite-btn absolute top-3 right-3 z-10 w-8 h-8 flex items-center justify-center rounded-full bg-slate-900/70 border border-slate-700/80 hover:border-slate-600 transition-colors"
      :class="{ 'is-favorite': favorited }"
      :title="favorited ? '取消收藏' : '加入收藏'"
      :aria-label="favorited ? '取消收藏' : '加入收藏'"
      :aria-pressed="favorited"
      @click.stop="onToggleFavorite"
    >
      <svg
        v-if="favorited"
        class="w-4 h-4 text-rose-500"
        fill="currentColor"
        viewBox="0 0 24 24"
      >
        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
      </svg>
      <svg
        v-else
        class="w-4 h-4 text-slate-400"
        fill="none"
        stroke="currentColor"
        stroke-width="1.8"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
      </svg>
    </button>

    <!-- 项目内容 -->
    <div class="p-5">
      <!-- 头部 -->
      <div class="flex items-start justify-between mb-3">
        <div class="flex-1 min-w-0 pr-12">
          <div class="flex items-center gap-2 mb-2">
            <svg class="w-4 h-4 text-slate-500 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            <h3 class="text-base font-medium text-slate-200 truncate group-hover:text-amber-400 transition-colors">{{ projectName }}</h3>
          </div>
          <p class="text-sm text-slate-400 line-clamp-2 leading-relaxed">
            {{ project.description || '暂无描述' }}
          </p>
        </div>
        <span
          v-if="project.language"
          class="flex-shrink-0 px-2 py-0.5 text-[10px] font-light text-slate-400 border border-slate-700 rounded tracking-wide"
        >
          {{ project.language }}
        </span>
      </div>

      <!-- 统计数据 - 杂志风格简洁展示 -->
      <div class="flex items-center gap-6 pt-3 border-t border-slate-800/50">
        <div class="flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
          <span class="text-sm font-light text-slate-300">{{ formatNumber(project.stars) }}</span>
        </div>
        <div class="flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8.75 21V3l8 8m0-8v8m-8 8h16"></path>
          </svg>
          <span class="text-sm font-light text-slate-400">{{ formatNumber(project.forks) }}</span>
        </div>
        <div class="flex-1"></div>
        <span class="text-[10px] text-slate-500 font-light">{{ formatDate(project.created_at) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Project } from '@/api/reports'
import { useFavorites } from '@/composables/useFavorites'

interface Props {
  project: Project
  index?: number
}

const props = withDefaults(defineProps<Props>(), {
  index: 0
})

defineEmits<{
  click: [project: Project]
}>()

const { isFavorite, toggleFavorite } = useFavorites()

const projectName = computed(() => {
  const parts = props.project.name.split('/')
  return parts.length > 1 ? parts[1] : props.project.name
})

const favorited = computed(() => isFavorite(props.project.name))

async function onToggleFavorite() {
  try {
    await toggleFavorite(props.project)
  } catch (e) {
    console.error('toggle favorite failed', e)
  }
}

const formatNumber = (num: number | string): string => {
  if (typeof num === 'string') return num
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

const formatDate = (dateStr: string): string => {
  if (!dateStr || dateStr === 'N/A') return '未知'
  try {
    const date = new Date(dateStr)
    return date.getFullYear().toString()
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
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-card:hover {
  background: rgba(30, 41, 59, 0.8);
}

.project-card:hover .stat-item {
  transform: translateY(-1px);
}

.stat-item {
  transition: transform 0.2s ease;
}

.favorite-btn {
  opacity: 0;
  transform: scale(0.85);
  transition: opacity 0.2s ease, transform 0.2s ease, background-color 0.2s ease;
}

.project-card:hover .favorite-btn,
.favorite-btn:focus-visible,
.favorite-btn.is-favorite {
  opacity: 1;
  transform: scale(1);
}

.favorite-btn:hover {
  background-color: rgba(15, 23, 42, 0.9);
}

.favorite-btn.is-favorite:hover {
  background-color: rgba(244, 63, 94, 0.12);
  border-color: rgba(244, 63, 94, 0.45);
}
</style>