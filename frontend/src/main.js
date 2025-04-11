import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { createPinia } from 'pinia';

// import './assets/tailwind.css'
axios.defaults.baseURL = "http://localhost:8080";
axios.defaults.headers.post['Content-Type'] = 'application/json';
const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.config.globalProperties.$axios = axios  // 让 axios 全局可用
app.mount('#app')