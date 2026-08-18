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
          <router-link to="/favorites" class="terminal-nav">收藏</router-link>
          <span class="mx-2 hidden h-4 w-px bg-slate-800 md:inline-block"></span>
          <router-link to="/contact" class="terminal-nav active">联系我们</router-link>
        </nav>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="terminal-main">
      <div class="mx-auto max-w-3xl">
        <section class="terminal-panel p-6">
          <div class="terminal-panel-head">
            <span>CONTACT</span>
            <span>GET IN TOUCH</span>
          </div>

          <div class="px-6 py-8">
            <h2 class="text-2xl font-semibold text-slate-100">联系我们</h2>
            <p class="mt-3 text-sm leading-7 text-slate-400">
              通过下面任意方式都可以找到我们——反馈 Bug、提功能建议、合作、或者单纯想聊聊 GitHub 趋势。
            </p>

            <div class="mt-8 grid grid-cols-1 gap-4 md:grid-cols-2">
              <!-- 微信：hover 显示二维码 -->
              <div class="contact-card group">
                <div class="flex items-start gap-4">
                  <div class="contact-icon">
                    <svg class="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 01.213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.328.328 0 00.167-.054l1.903-1.114a.864.864 0 01.717-.098 10.16 10.16 0 002.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 01-1.162 1.178A1.17 1.17 0 015.785 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 01-1.162 1.178A1.17 1.17 0 0110.599 7.17c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 01.598.082l1.584.926a.272.272 0 00.14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 01-.023-.156.49.49 0 01.201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89c-.135-.01-.27-.027-.407-.032zm-2.328 3.158c.535 0 .969.44.969.982a.976.976 0 01-.969.983.976.976 0 01-.969-.983.976.976 0 01.97-.982zm4.844 0c.535 0 .969.44.969.982a.976.976 0 01-.969.983.976.976 0 01-.969-.983.976.976 0 01.97-.982z"/>
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-base font-semibold text-slate-100">微信</h3>
                    <p class="mt-1 text-sm text-slate-400">
                      扫码加好友，备注「GitTrend」更快通过
                    </p>
                    <p class="mt-2 text-xs text-slate-500 group-hover:text-cyan-300 transition-colors">
                      把鼠标移到这里显示二维码
                    </p>
                  </div>
                </div>

                <!-- hover 显示的二维码 -->
                <div class="qr-popup">
                  <img
                    src="/images/wechat.png"
                    alt="WeChat QR Code"
                    width="240"
                    height="253"
                    class="block h-auto w-60"
                    loading="lazy"
                  />
                </div>
              </div>

              <!-- GitHub Issues -->
              <a
                href="https://github.com/lgy1027/ai-git-trending/issues"
                target="_blank"
                rel="noopener noreferrer"
                class="contact-card hover:border-cyan-400/40"
              >
                <div class="flex items-start gap-4">
                  <div class="contact-icon">
                    <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-base font-semibold text-slate-100">GitHub Issues</h3>
                    <p class="mt-1 text-sm text-slate-400">
                      提交 Bug 报告 / 功能建议，便于公开追踪
                    </p>
                    <p class="mt-2 text-xs text-slate-500 group-hover:text-cyan-300 transition-colors">
                      点击跳转到 GitHub 仓库
                    </p>
                  </div>
                </div>
              </a>
            </div>

            <p class="mt-8 text-xs text-slate-500">
              提示：替换 <code class="bg-slate-800 px-1.5 py-0.5 rounded text-cyan-300">images/wechat.png</code> 即可更新实际二维码。
            </p>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// 联系我们页面 - 静态展示
</script>

<style scoped>
.contact-card {
  position: relative;
  display: block;
  padding: 1.25rem;
  border: 1px solid rgba(51, 65, 85, 0.9);
  border-radius: 0.5rem;
  background: rgba(15, 23, 42, 0.5);
  color: inherit;
  text-decoration: none;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.contact-card:hover {
  border-color: rgba(34, 211, 238, 0.3);
  background: rgba(15, 23, 42, 0.7);
}

.contact-icon {
  width: 2.75rem;
  height: 2.75rem;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  background: rgba(34, 211, 238, 0.08);
  border: 1px solid rgba(34, 211, 238, 0.25);
  color: #67e8f9;
}

.qr-popup {
  position: absolute;
  left: 50%;
  top: calc(100% + 0.5rem);
  transform: translateX(-50%) translateY(-4px);
  padding: 0.75rem;
  background: #0f172a;
  border: 1px solid rgba(34, 211, 238, 0.4);
  border-radius: 0.5rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
  z-index: 10;
}

.contact-card:hover .qr-popup {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
</style>
