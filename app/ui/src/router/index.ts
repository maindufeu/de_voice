import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import Call from '../views/Call.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: Call,
    meta: {
      title: 'Voice Analytics',
    }
  },
  // Add more routes here as needed
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Update page title based on route
router.beforeEach((to, from, next) => {
  document.title = to.meta.title as string || 'Voice Analytics';
  next();
});

export default router;