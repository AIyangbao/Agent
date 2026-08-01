import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import BlogList from '../views/BlogList.vue'
import BlogDetail from '../views/BlogDetail.vue'
import EditorPage from '../views/EditorPage.vue'
import AIChat from '../views/AIChat.vue'
import CategoryPage from '../views/CategoryPage.vue'
import AuthPage from '../views/AuthPage.vue'

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/posts', name: 'list', component: BlogList },
  { path: '/posts/:id', name: 'detail', component: BlogDetail },
  { path: '/write', name: 'write', component: EditorPage, meta: { requiresAuth: true } },
  { path: '/ai', name: 'ai', component: AIChat, meta: { requiresAuth: true } },
  { path: '/category', name: 'category', component: CategoryPage },
  { path: '/tags', name: 'tags', component: HomePage },
  { path: '/auth', name: 'auth', component: AuthPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
