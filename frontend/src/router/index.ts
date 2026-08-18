import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Reports from '../views/Reports.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: 'GitTrend Insights - 发现GitHub热门技术趋势'
    }
  },
  {
    path: '/projects/:date',
    name: 'ProjectList',
    component: () => import('../views/ProjectList.vue'),
    meta: {
      title: '项目列表 - GitTrend Insights'
    }
  },
  {
    path: '/rankings',
    name: 'Rankings',
    component: () => import('../views/Rankings.vue'),
    meta: {
      title: '项目排行榜 - GitTrend Insights'
    }
  },
  {
    path: '/trend-analysis',
    name: 'TrendAnalysis',
    component: () => import('../views/TrendAnalysis.vue'),
    meta: {
      title: '技术趋势分析 - GitTrend Insights'
    }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('../views/Favorites.vue'),
    meta: {
      title: '我的收藏项目 - GitTrend Insights'
    }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue'),
    meta: {
      title: '关于我们 - GitTrend Insights'
    }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports,
    meta: {
      title: '报告列表 - GitTrend Insights'
    }
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('../views/Contact.vue'),
    meta: {
      title: '联系我们 - GitTrend Insights'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to) => {
  document.title = to.meta.title as string || 'GitHub Trending Reporter'
})

export default router