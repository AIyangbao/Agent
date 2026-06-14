import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import BlogList from '../views/BlogList.vue'
import BlogDetail from '../views/BlogDetail.vue'
import AuthPage from '../views/AuthPage.vue'
import EditorPage from '../views/EditorPage.vue'

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/posts', name: 'list', component: BlogList },
  { path: '/posts/:id', name: 'detail', component: BlogDetail, props: true },
  { path: '/auth', name: 'auth', component: AuthPage },
  { path: '/write', name: 'write', component: EditorPage, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
