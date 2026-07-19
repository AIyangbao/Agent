import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import BlogList from '../views/BlogList.vue'
import AuthPage from '../views/AuthPage.vue'

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/category', name: 'category', component: HomePage },
  { path: '/tags', name: 'tags', component: HomePage },
  { path: '/posts/:id?', name: 'detail', component: HomePage },
  { path: '/posts', name: 'list', component: BlogList },
  { path: '/auth', name: 'auth', component: AuthPage },
  { path: '/write', name: 'write', component: HomePage, meta: { requiresAuth: true } },
  { path: '/ai', name: 'ai', component: HomePage, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
