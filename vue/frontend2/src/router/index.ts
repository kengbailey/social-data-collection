import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import YoutubeDownload from '../views/YoutubeDownload.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/youtubedownload',
      name: 'youtubedownload',
      component: YoutubeDownload
    },
  ]
})

export default router
