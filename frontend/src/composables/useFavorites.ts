import { ref } from 'vue'
import api, { type Project } from '@/api/reports'

const CLIENT_ID_KEY = 'gittrend:client_id'
const FAVORITES_CACHE_KEY = 'gittrend:favorites_cache'

// 模块级单例：所有 useFavorites() 调用共享同一份状态
const clientId = ref<string>('')
const favorites = ref<Project[]>([])
let syncPromise: Promise<void> | null = null

function generateClientId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

function ensureClientId(): string {
  if (clientId.value) return clientId.value
  let stored = localStorage.getItem(CLIENT_ID_KEY)
  if (!stored || stored.length < 8) {
    stored = generateClientId()
    localStorage.setItem(CLIENT_ID_KEY, stored)
  }
  clientId.value = stored
  return stored
}

function readCache(): Project[] {
  try {
    const raw = localStorage.getItem(FAVORITES_CACHE_KEY)
    if (!raw) return []
    const arr = JSON.parse(raw)
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
}

function writeCache(items: Project[]) {
  try {
    localStorage.setItem(FAVORITES_CACHE_KEY, JSON.stringify(items))
  } catch {
    // localStorage 被禁用或容量超限，忽略
  }
}

function upsertLocal(project: Project) {
  const idx = favorites.value.findIndex((p) => p.name === project.name)
  if (idx >= 0) {
    favorites.value.splice(idx, 1, project)
  } else {
    favorites.value.unshift(project)
  }
  writeCache(favorites.value)
}

function removeLocal(projectName: string) {
  favorites.value = favorites.value.filter((p) => p.name !== projectName)
  writeCache(favorites.value)
}

async function syncFromServer(): Promise<void> {
  const id = ensureClientId()
  try {
    const res = await api.get<{ data: { items?: Project[] } }>('/api/favorites', {
      params: { client_id: id },
    })
    const items = res.data?.data?.items ?? []
    favorites.value = items
    writeCache(items)
  } catch (e) {
    console.warn('favorites: failed to sync from server, using local cache', e)
  }
}

function ensureLoaded(): Promise<void> {
  if (syncPromise) return syncPromise
  if (favorites.value.length === 0) {
    favorites.value = readCache()
  }
  syncPromise = syncFromServer().finally(() => {
    syncPromise = null
  })
  return syncPromise
}

async function toggleFavorite(project: Project): Promise<boolean> {
  const id = ensureClientId()
  const wasFavorited = favorites.value.some((p) => p.name === project.name)
  // 乐观更新：本地立即响应
  if (wasFavorited) {
    removeLocal(project.name)
  } else {
    upsertLocal(project)
  }
  try {
    if (wasFavorited) {
      await api.delete('/api/favorites', { data: { client_id: id, project_name: project.name } })
      return false
    } else {
      await api.post('/api/favorites', { client_id: id, project_name: project.name })
      return true
    }
  } catch (e) {
    // 回滚到操作前状态
    if (wasFavorited) {
      upsertLocal(project)
    } else {
      removeLocal(project.name)
    }
    throw e
  }
}

export function useFavorites() {
  const isFavorite = (projectName: string) =>
    favorites.value.some((p) => p.name === projectName)

  return {
    favorites,
    isFavorite,
    toggleFavorite,
    ensureLoaded,
  }
}