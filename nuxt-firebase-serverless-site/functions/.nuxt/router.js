import Vue from 'vue'
import Router from 'vue-router'
import { interopDefault } from './utils'
import scrollBehavior from './router.scrollBehavior.js'

const _19d29180 = () => interopDefault(import('../../src/pages/index.vue' /* webpackChunkName: "pages/index" */))
const _390b96d2 = () => interopDefault(import('../../src/pages/login.vue' /* webpackChunkName: "pages/login" */))
const _96523304 = () => interopDefault(import('../../src/pages/profil.vue' /* webpackChunkName: "pages/profil" */))
const _3b736b82 = () => interopDefault(import('../../src/pages/queue.vue' /* webpackChunkName: "pages/queue" */))
const _5f3c6bb6 = () => interopDefault(import('../../src/pages/users.vue' /* webpackChunkName: "pages/users" */))

// TODO: remove in Nuxt 3
const emptyFn = () => {}
const originalPush = Router.prototype.push
Router.prototype.push = function push (location, onComplete = emptyFn, onAbort) {
  return originalPush.call(this, location, onComplete, onAbort)
}

Vue.use(Router)

export const routerOptions = {
  mode: 'history',
  base: decodeURI('/'),
  linkActiveClass: 'nuxt-link-active',
  linkExactActiveClass: 'nuxt-link-exact-active',
  scrollBehavior,

  routes: [{
    path: "/en",
    component: _19d29180,
    name: "index___en"
  }, {
    path: "/login",
    component: _390b96d2,
    name: "login___fr"
  }, {
    path: "/profil",
    component: _96523304,
    name: "profil___fr"
  }, {
    path: "/queue",
    component: _3b736b82,
    name: "queue___fr"
  }, {
    path: "/users",
    component: _5f3c6bb6,
    name: "users___fr"
  }, {
    path: "/en/login",
    component: _390b96d2,
    name: "login___en"
  }, {
    path: "/en/profil",
    component: _96523304,
    name: "profil___en"
  }, {
    path: "/en/queue",
    component: _3b736b82,
    name: "queue___en"
  }, {
    path: "/en/users",
    component: _5f3c6bb6,
    name: "users___en"
  }, {
    path: "/",
    component: _19d29180,
    name: "index___fr"
  }],

  fallback: false
}

export function createRouter () {
  return new Router(routerOptions)
}
