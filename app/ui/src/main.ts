import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import './assets/main.css'
import router from './router/index.ts'


const app = createApp(App)
// Use router
app.use(router)
// Mount the app
app.mount('#app')
