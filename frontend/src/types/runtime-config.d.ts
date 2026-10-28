export {}

declare global {
  interface Window {
    __APP_CONFIG__?: {
      apiBaseUrl?: string
    }
  }
}
