import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Importa la carpeta router
import './style.css'
import { registerSW } from 'virtual:pwa-register'


const app = createApp(App)

app.use(router) // Le decimos a Vue que use el router
app.mount('#app')



registerSW({
    onOfflineReady() {
        console.log('PWA lista para usar offline')
    },
    onNeedRefresh() {
        console.log('Nueva versión disponible')
    }
})