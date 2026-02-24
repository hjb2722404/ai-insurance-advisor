/**
 * AI Insurance Advisor - Main Entry Point
 *
 * This is the main entry point for the uni-app + Vue 3 application.
 * It initializes Pinia store and creates the app instance.
 *
 * @see https://uniapp.dcloud.net.cn/tutorial/
 */

import { createSSRApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

/**
 * Create and initialize the Vue application
 *
 * uni-app uses createSSRApp instead of createApp for SSR compatibility
 * and WeChat Mini Program compatibility.
 *
 * @param app - The Vue app instance
 */
export function createApp(): ReturnType<typeof createSSRApp> {
  const app = createSSRApp(App)

  // Initialize Pinia for state management
  const pinia = createPinia()
  app.use(pinia)

  return app
}

// Create and expose the app instance for uni-app to bootstrap
createApp().mount('#app')
