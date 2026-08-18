<template>
  <div class="terminal-page">
    <!-- 导航栏 -->
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

        <router-link to="/" class="terminal-action">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          返回首页
        </router-link>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="terminal-main">
      <div class="max-w-4xl mx-auto">
        <!-- 项目介绍 -->
        <section class="terminal-panel p-6 mb-6">
          <div class="terminal-panel-head">
            <span>ABOUT PROJECT</span>
            <span>INFO</span>
          </div>
          <div class="p-6">
            <h2 class="text-2xl font-semibold text-slate-100 mb-4">关于 GitTrend Intel</h2>

            <p class="text-slate-400 text-lg leading-relaxed mb-6">
              GitHub Trending Reporter 是一个自动化分析 GitHub Trending 的机器人，为您每日精选、总结并生成技术洞察报告。
            </p>

            <h3 class="text-lg font-semibold text-slate-200 mb-4">项目特色</h3>
            <ul class="text-slate-400 space-y-3">
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-cyan-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                </svg>
                <span><strong class="text-slate-200">智能分析</strong> - 利用大语言模型深度分析热门项目，生成技术洞察</span>
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-cyan-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"></path>
                </svg>
                <span><strong class="text-slate-200">现代界面</strong> - Vue 3 + TypeScript + Tailwind CSS 构建的响应式界面</span>
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-cyan-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                <span><strong class="text-slate-200">实时数据</strong> - 每日自动抓取和分析最新的GitHub热门项目</span>
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-cyan-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
                <span><strong class="text-slate-200">数据可视</strong> - 提供项目统计和趋势分析功能</span>
              </li>
              <li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-cyan-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path>
                </svg>
                <span><strong class="text-slate-200">本地存储</strong> - 所有数据本地化存储，保护您的隐私</span>
              </li>
            </ul>
          </div>
        </section>

        <!-- 技术栈 -->
        <section class="terminal-panel p-6 mb-6">
          <div class="terminal-panel-head">
            <span>TECH STACK</span>
            <span>DETAILS</span>
          </div>
          <div class="p-6">
            <h3 class="text-lg font-semibold text-slate-200 mb-4">技术栈</h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 class="text-sm font-medium text-cyan-400 mb-4">前端技术</h4>
                <div class="space-y-3">
                  <div class="flex items-center gap-3">
                    <div class="w-3 h-3 bg-green-500 rounded"></div>
                    <span class="text-slate-300">Vue 3 + Composition API</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="w-3 h-3 bg-blue-500 rounded"></div>
                    <span class="text-slate-300">TypeScript</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="w-3 h-3 bg-cyan-500 rounded"></div>
                    <span class="text-slate-300">Tailwind CSS</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="w-3 h-3 bg-orange-500 rounded"></div>
                    <span class="text-slate-300">Vite</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 class="text-sm font-medium text-cyan-400 mb-4">后端技术</h4>
                <div class="space-y-3">
                  <div class="flex items-center gap-3">
                    <div class="w-3 h-3 bg-yellow-500 rounded"></div>
                    <span class="text-slate-300">Python 3.x</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="w-3 h-3 bg-red-500 rounded"></div>
                    <span class="text-slate-300">Flask</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="w-3 h-3 bg-slate-500 rounded"></div>
                    <span class="text-slate-300">SQLite</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="w-3 h-3 bg-purple-500 rounded"></div>
                    <span class="text-slate-300">OpenAI API</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 开源信息 -->
        <section class="terminal-panel p-6">
          <div class="terminal-panel-head">
            <span>OPEN SOURCE</span>
            <span>CONTRIBUTION</span>
          </div>
          <div class="p-6">
            <h3 class="text-lg font-semibold text-slate-200 mb-4">开源贡献</h3>

            <p class="text-slate-400 mb-6">
              这是一个开源项目，欢迎大家参与贡献！
            </p>

            <div class="flex flex-col sm:flex-row gap-4">
              <a
                href="https://github.com/lgy1027/ai-git-trending"
                target="_blank"
                class="terminal-action"
              >
                <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                查看源码
              </a>
              <a
                href="https://github.com/lgy1027/ai-git-trending/issues"
                target="_blank"
                class="terminal-action"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
                报告问题
              </a>
              <a
                href="https://github.com/lgy1027/ai-git-trending/fork"
                target="_blank"
                class="terminal-action primary"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2"></path>
                </svg>
                Fork 项目
              </a>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// About 页面逻辑
</script>
