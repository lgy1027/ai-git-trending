import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import { useFavorites } from './composables/useFavorites'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

// 应用启动即加载收藏状态（本地缓存 + 服务端同步），
// 这样在任何页面（包括首页）刷新后收藏标志都能立即可见。
useFavorites().ensureLoaded()
