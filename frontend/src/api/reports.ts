import axios, { AxiosError } from 'axios'

// 根据环境变量或开发/生产环境自动选择API地址
// 开发环境使用相对路径走Vite代理，生产环境使用实际后端地址
const API_BASE_URL = import.meta.env.DEV ? '' : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001')

// 创建axios实例并配置
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.url} - ${response.status}`)
    return response
  },
  (error: AxiosError) => {
    console.error(`❌ API Error: ${error.config?.url}`, error.message)
    
    // 统一错误处理
    if (error.code === 'ECONNREFUSED') {
      throw new Error('无法连接到服务器，请检查后端服务是否启动')
    }
    if (error.response?.status === 404) {
      throw new Error('请求的资源不存在')
    }
    if (error.response?.status === 500) {
      throw new Error('服务器内部错误，请稍后重试')
    }
    if (error.code === 'ECONNABORTED') {
      throw new Error('请求超时，请检查网络连接')
    }
    
    throw new Error(error.message || '请求失败')
  }
)

export interface Report {
  date: string
  project_count: number
  content?: string  // 可选，用于详情页
}

export interface ReportContent {
  mdContent: string
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
  percentage: number
  colorClass: string
}

export interface TrendDataItem {
  label: string
  value: number
  change: number
  colorClass: string
}

export interface TrendsData {
  time_window_days: number
  most_frequent_projects: {
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
  }[]
  most_frequent_languages: [string, number][]
  programmingLanguages: [string, number][]
  surgingProjects: {
    name: string
    url: string
    description: string
    language: string
    star_increase: number
    start_stars: number
    end_stars: number
  }[]
  techDomains: { name: string; count: number; percentage: number }[]
}

export const reportApi = {
  // 获取报告列表
  async getReports(): Promise<Report[]> {
    try {
      const response = await api.get('/api/reports')
      const reports = Array.isArray(response.data)
        ? response.data
        : response.data.data?.items || response.data.data || []
      console.log(`📋 获取到 ${reports.length} 个报告`)
      return reports
    } catch (error) {
      console.error('获取报告列表失败:', error)
      throw error
    }
  },

  // 获取具体报告内容
  async getReportContent(date: string): Promise<Report> {
    try {
      const response = await api.get(`/api/report/${date}`)
      console.log(`📄 获取报告内容: ${date}`)
      return response.data.data || response.data
    } catch (error) {
      console.error(`获取报告内容失败 (${date}):`, error)
      throw error
    }
  },

  // 复制报告内容（带 IP 限流）
  async copyReport(date: string): Promise<{ content: string; rate_limit: { limit: number; remaining: number } }> {
    try {
      const response = await api.get(`/api/copy/${date}`)
      console.log(`📋 复制报告: ${date}`)
      return response.data.data || response.data
    } catch (error: any) {
      if (error.response?.status === 429) {
        throw new Error(error.response.data.message || '复制次数已达上限')
      }
      console.error(`复制报告失败 (${date}):`, error)
      throw error
    }
  },

  // 获取限流状态
  async getRateLimitStatus(): Promise<{ copy: { limit: number; remaining: number }; export: { limit: number; remaining: number } }> {
    try {
      const response = await api.get('/api/rate-limit-status')
      return response.data.data || response.data
    } catch (error) {
      console.error('获取限流状态失败:', error)
      throw error
    }
  },

  // 获取指定日期的项目列表
  async getProjectsByDate(date: string): Promise<Project[]> {
    try {
      const response = await api.get(`/api/projects/${date}`)
      const projects = response.data.data || []
      console.log(`🚀 获取到 ${projects.length} 个项目 (${date})`)
      return projects
    } catch (error) {
      console.error(`获取项目列表失败 (${date}):`, error)
      throw error
    }
  },

  // 获取项目列表（支持日期范围、排序、筛选）
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
    try {
      const response = await api.get('/api/projects', { params })
      console.log(`🚀 获取项目列表:`, params)
      return response.data.data || response.data
    } catch (error) {
      console.error('获取项目列表失败:', error)
      throw error
    }
  },

  // 获取单个项目详情
  async getProjectDetails(projectName: string): Promise<Project> {
    try {
      const response = await api.get('/api/project', {
        params: { name: projectName }
      })
      console.log(`📦 获取项目详情: ${projectName}`)
      return response.data.data || response.data
    } catch (error) {
      console.error(`获取项目详情失败 (${projectName}):`, error)
      throw error
    }
  },

  // 获取统计数据
  async getStats(): Promise<Stats> {
    try {
      const response = await api.get('/api/stats')
      console.log('📊 获取统计数据成功')
      return response.data.data || response.data
    } catch (error) {
      console.error('获取统计数据失败:', error)
      // 不返回默认数据，让调用方处理错误
      throw error
    }
  },

  // 获取趋势数据
  async getTrends(params?: { days?: number }): Promise<TrendsData> {
    try {
      const response = await api.get('/api/trends', { params })
      console.log(`📈 获取趋势数据成功 (时间范围: ${params?.days || 7}天)`)
      return response.data.data || response.data
    } catch (error) {
      console.error('获取趋势数据失败:', error)
      throw error
    }
  },

  // 获取所有技术领域分类
  async getTechDomains(): Promise<{ name: string; count: number }[]> {
    try {
      const response = await api.get('/api/tech-domains')
      return response.data.data || []
    } catch (error) {
      console.error('获取技术领域失败:', error)
      return []
    }
  },

  // 获取项目趋势
  async getProjectTrend(days: number = 7): Promise<{ date: string; count: number }[]> {
    try {
      const response = await api.get('/api/project-trend', { params: { days } })
      return response.data.data || []
    } catch (error) {
      console.error('获取项目趋势失败:', error)
      return []
    }
  },

  // 健康检查
  async healthCheck(): Promise<boolean> {
    try {
      await api.get('/api/stats')
      return true
    } catch {
      return false
    }
  },

  // 获取语言分布数据（从 trends API 获取）
  async getLanguageDistribution(): Promise<LanguageData[]> {
    try {
      const response = await api.get('/api/trends')
      console.log('🌐 获取语言分布数据成功', response.data)
      // 从 trends API 的 programmingLanguages 字段获取
      const data = response.data.data || response.data
      const langData = data?.programmingLanguages || data?.most_frequent_languages || []
      const colorClasses = ['bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-purple-500', 'bg-red-500', 'bg-cyan-500', 'bg-pink-500']
      // 转换为 LanguageData 格式
      return langData.map((item: [string, number], index: number) => ({
        name: item[0],
        count: item[1],
        percentage: Math.round((item[1] / langData.reduce((sum: number, i: [string, number]) => sum + i[1], 0)) * 100),
        colorClass: colorClasses[index % colorClasses.length]
      }))
    } catch (error) {
      console.error('获取语言分布数据失败:', error)
      // 不返回默认数据，让调用方处理错误
      throw error
    }
  },

  // 获取趋势数据
  async getTrendData(): Promise<TrendDataItem[]> {
    try {
      const response = await api.get('/api/trends')
      console.log('📈 获取趋势数据成功', response.data)
      // 从 trends API 的 techDomains 字段获取新兴技术领域数据
      const data = response.data.data || response.data
      const techDomains = data?.techDomains || []
      // 转换为 TrendDataItem 格式
      return techDomains.map((domain: any, index: number) => ({
        label: domain.name,
        value: domain.count,
        change: domain.percentage,
        colorClass: ['text-green-400', 'text-blue-400', 'text-purple-400', 'text-pink-400', 'text-yellow-400'][index % 5]
      }))
    } catch (error) {
      console.error('获取趋势数据失败:', error)
      // 不返回默认数据，让调用方处理错误
      throw error
    }
  }
}

// 导出便利函数
export const getReports = reportApi.getReports
export const getProjectsByDate = reportApi.getProjectsByDate
export const getProjects = reportApi.getProjects
export const getProjectDetails = reportApi.getProjectDetails
export const getReportByDate = reportApi.getReportContent
export const copyReport = reportApi.copyReport
export const getRateLimitStatus = reportApi.getRateLimitStatus
export const getStats = reportApi.getStats
export const getTrends = reportApi.getTrends
export const healthCheck = reportApi.healthCheck
export const getTrendData = reportApi.getTrendData
export const getTechDomains = reportApi.getTechDomains
export const getLanguageDistribution = reportApi.getLanguageDistribution
export const getProjectTrend = reportApi.getProjectTrend

// 导出API基础URL用于调试
export const getApiBaseUrl = () => API_BASE_URL

export default api
