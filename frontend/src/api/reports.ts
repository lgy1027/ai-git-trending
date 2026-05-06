import axios, { AxiosError } from 'axios'

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL

const API_BASE_URL = import.meta.env.DEV
  ? ''
  : (configuredApiBaseUrl !== undefined ? configuredApiBaseUrl : 'http://localhost:5001')

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

type ApiEnvelope<T> = {
  code: number
  message: string
  data: T
}

type ApiErrorPayload = {
  code?: number
  message?: string
  data?: unknown
}

export class ApiRequestError extends Error {
  status?: number
  code?: number
  data?: unknown
  original?: AxiosError<ApiErrorPayload>

  constructor(
    message: string,
    options?: {
      status?: number
      code?: number
      data?: unknown
      original?: AxiosError<ApiErrorPayload>
    },
  ) {
    super(message)
    this.name = 'ApiRequestError'
    this.status = options?.status
    this.code = options?.code
    this.data = options?.data
    this.original = options?.original
  }
}

function createApiError(error: AxiosError<ApiErrorPayload>): ApiRequestError {
  const status = error.response?.status
  const payload = error.response?.data

  if (error.code === 'ECONNREFUSED') {
    return new ApiRequestError('无法连接到后端服务，请确认服务已启动。', { status, original: error })
  }

  if (error.code === 'ECONNABORTED') {
    return new ApiRequestError('请求超时，请稍后重试。', { status, original: error })
  }

  if (payload?.message) {
    return new ApiRequestError(payload.message, {
      status,
      code: payload.code,
      data: payload.data,
      original: error,
    })
  }

  if (status === 404) {
    return new ApiRequestError('请求的资源不存在。', { status, original: error })
  }

  if (status === 429) {
    return new ApiRequestError('请求次数已达上限，请稍后再试。', { status, original: error })
  }

  if (status === 500) {
    return new ApiRequestError('服务端发生错误，请稍后重试。', { status, original: error })
  }

  return new ApiRequestError(error.message || '请求失败', { status, original: error })
}

function unwrap<T>(payload: ApiEnvelope<T> | T): T {
  if (payload && typeof payload === 'object' && 'data' in (payload as ApiEnvelope<T>)) {
    return (payload as ApiEnvelope<T>).data
  }
  return payload as T
}

api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => Promise.reject(error),
)

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorPayload>) => Promise.reject(createApiError(error)),
)

export interface Report {
  date: string
  project_count: number
  content?: string
}

export interface Project {
  name: string
  url: string
  description: string
  language: string
  stars: number
  forks: number
  contributor_count: number
  created_at: string
  updated_at: string
  open_issues: number
  watchers: number
  summary_date?: string | null
  analysis_status?: 'completed' | 'pending'
  trending_date?: string | null
  trending_rank?: number | null
  message?: string
}

export interface Stats {
  totalReports: number
  totalProjects: number
  topLanguage: string
  weeklyNew: number
  totalForks: string
  avgContributors: number
  activityScore: number
  activityBreakdown?: {
    recentlyActive: number
    stable: number
    needsAttention: number
  }
}

export interface LanguageData {
  name: string
  count: number
  percentage?: number
}

export interface TechDomainData {
  name: string
  count: number
  percentage?: number
}

export interface ProjectTrendPoint {
  date: string
  count: number
}

export interface TrendDataItem {
  label: string
  value: number
  change: number
  colorClass: string
}

export interface TrendsData {
  time_window_days: number
  topProjects?: Array<{
    name: string
    url: string
    description: string
    language: string
    count: number
    avg_stars: number
    stars?: number
    forks?: number
    contributor_count?: number
    created_at?: string
    updated_at?: string
    open_issues?: number
    watchers?: number
  }>
  most_frequent_projects: Array<{
    name: string
    url: string
    description: string
    language: string
    count: number
    avg_stars: number
    stars?: number
    forks?: number
    contributor_count?: number
    created_at?: string
    updated_at?: string
    open_issues?: number
    watchers?: number
  }>
  most_frequent_languages: [string, number][]
  programmingLanguages?: [string, number][]
  surgingProjects?: Array<{
    name: string
    url: string
    description: string
    language: string
    star_increase: number
    start_stars: number
    end_stars: number
  }>
  techDomains?: TechDomainData[]
}

function triggerBrowserDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export const reportApi = {
  async getReports(): Promise<Report[]> {
    const response = await api.get<ApiEnvelope<Report[]>>('/api/reports')
    return unwrap(response.data)
  },

  async getReportContent(date: string): Promise<Report> {
    const response = await api.get<ApiEnvelope<Report>>(`/api/report/${date}`)
    return unwrap(response.data)
  },

  async copyReport(date: string): Promise<{ content: string; rate_limit: { limit: number; remaining: number } }> {
    const response = await api.get<ApiEnvelope<{ content: string; rate_limit: { limit: number; remaining: number } }>>(
      `/api/copy/${date}`,
    )
    return unwrap(response.data)
  },

  async downloadReport(date: string, format: 'md' | 'html' = 'md'): Promise<void> {
    const response = await api.get<Blob>(`/api/download/${date}/${format}`, {
      responseType: 'blob',
    })

    const disposition = response.headers['content-disposition']
    const matchedFilename = disposition?.match(/filename="?([^"]+)"?/)
    const filename = matchedFilename?.[1] || `github_trending_${date}.${format}`
    const blob = new Blob([response.data], {
      type: response.headers['content-type'] || 'application/octet-stream',
    })

    triggerBrowserDownload(blob, filename)
  },

  async getRateLimitStatus(): Promise<{ copy: { limit: number; remaining: number }; export: { limit: number; remaining: number } }> {
    const response = await api.get<ApiEnvelope<{ copy: { limit: number; remaining: number }; export: { limit: number; remaining: number } }>>(
      '/api/rate-limit-status',
    )
    return unwrap(response.data)
  },

  async getProjectsByDate(date: string): Promise<Project[]> {
    const response = await api.get<ApiEnvelope<Project[]>>(`/api/projects/${date}`)
    return unwrap(response.data)
  },

  async getProjects(params: {
    date_from?: string
    date_to?: string
    language?: string
    sort_by?: string
    order?: string
    page?: number
    page_size?: number
    search?: string
  }): Promise<{ items: Project[]; total: number; page: number; page_size: number; total_pages: number }> {
    const response = await api.get<ApiEnvelope<{ items: Project[]; total: number; page: number; page_size: number; total_pages: number }>>(
      '/api/projects',
      { params },
    )
    return unwrap(response.data)
  },

  async getProjectDetails(projectName: string): Promise<Project> {
    const response = await api.get<ApiEnvelope<Project>>('/api/project', {
      params: { name: projectName },
    })
    return unwrap(response.data)
  },

  async getStats(): Promise<Stats> {
    const response = await api.get<ApiEnvelope<Stats>>('/api/stats')
    return unwrap(response.data)
  },

  async getTrends(params?: { days?: number }): Promise<TrendsData> {
    const response = await api.get<ApiEnvelope<TrendsData>>('/api/trends', { params })
    return unwrap(response.data)
  },

  async getLanguageDistribution(): Promise<LanguageData[]> {
    const response = await api.get<ApiEnvelope<LanguageData[]>>('/api/language-distribution')
    return unwrap(response.data)
  },

  async getTrendData(params?: { days?: number }): Promise<TrendDataItem[]> {
    const response = await api.get<ApiEnvelope<TrendDataItem[]>>('/api/trend-data', { params })
    return unwrap(response.data)
  },

  async getTechDomains(): Promise<TechDomainData[]> {
    const response = await api.get<ApiEnvelope<TechDomainData[]>>('/api/tech-domains')
    return unwrap(response.data)
  },

  async getProjectTrend(days = 7): Promise<ProjectTrendPoint[]> {
    const response = await api.get<ApiEnvelope<ProjectTrendPoint[]>>('/api/project-trend', {
      params: { days },
    })
    return unwrap(response.data)
  },

  async healthCheck(): Promise<boolean> {
    try {
      await api.get('/api/stats')
      return true
    } catch {
      return false
    }
  },
}

export const getReports = reportApi.getReports
export const getReportByDate = reportApi.getReportContent
export const copyReport = reportApi.copyReport
export const downloadReport = reportApi.downloadReport
export const getRateLimitStatus = reportApi.getRateLimitStatus
export const getProjectsByDate = reportApi.getProjectsByDate
export const getProjects = reportApi.getProjects
export const getProjectDetails = reportApi.getProjectDetails
export const getStats = reportApi.getStats
export const getTrends = reportApi.getTrends
export const getLanguageDistribution = reportApi.getLanguageDistribution
export const getTrendData = reportApi.getTrendData
export const getTechDomains = reportApi.getTechDomains
export const getProjectTrend = reportApi.getProjectTrend
export const healthCheck = reportApi.healthCheck
export const getApiBaseUrl = () => API_BASE_URL

export default api
