import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// Bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Axios configuration
import axios from 'axios'

// Set base URL for API
axios.defaults.baseURL = 'http://localhost:5000/api'

// Enable credentials for session-based auth
axios.defaults.withCredentials = true

// Handle authentication errors
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('user')
      store.dispatch('auth/logout')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)

// Make axios available globally
app.config.globalProperties.$http = axios

app.use(store).use(router).mount('#app')
