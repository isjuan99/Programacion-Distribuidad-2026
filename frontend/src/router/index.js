import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  // Public
  { path: '/', name: 'Home', component: () => import('../pages/HomePage.vue') },
  { path: '/shop', name: 'Shop', component: () => import('../pages/ShopPage.vue') },
  { path: '/product/:id', name: 'Product', component: () => import('../pages/ProductPage.vue') },
  { path: '/cart', name: 'Cart', component: () => import('../pages/CartPage.vue') },
  { path: '/contact', name: 'Contact', component: () => import('../pages/ContactPage.vue') },
  { path: '/terms', name: 'Terms', component: () => import('../pages/TermsPage.vue') },
  { path: '/privacy', name: 'Privacy', component: () => import('../pages/PrivacyPage.vue') },
  { path: '/shipping', name: 'Shipping', component: () => import('../pages/ShippingPage.vue') },
  { path: '/order/success/:orderId', name: 'OrderSuccess', component: () => import('../pages/OrderSuccessPage.vue') },

  // Auth
  { path: '/login', name: 'Login', component: () => import('../pages/LoginPage.vue'), meta: { guestOnly: true } },
  { path: '/register', name: 'Register', component: () => import('../pages/RegisterPage.vue'), meta: { guestOnly: true } },
  { path: '/forgot-password', name: 'ForgotPassword', component: () => import('../pages/ForgotPasswordPage.vue'), meta: { guestOnly: true } },
  { path: '/reset-password', name: 'ResetPassword', component: () => import('../pages/ForgotPasswordPage.vue') },
  { path: '/verify-email', name: 'VerifyEmail', component: () => import('../pages/VerifyEmailPage.vue') },

  // Protected
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('../pages/CheckoutPage.vue'),
  },
  {
    path: '/account',
    name: 'Account',
    component: () => import('../pages/AccountPage.vue'),
    meta: { requiresAuth: true },
  },

  // Admin
  {
    path: '/admin',
    redirect: '/admin/dashboard',
    meta: { requiresAdmin: true },
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('../pages/admin/AdminDashboard.vue') },
      { path: 'products', name: 'AdminProducts', component: () => import('../pages/admin/AdminProducts.vue') },
      { path: 'orders', name: 'AdminOrders', component: () => import('../pages/admin/AdminOrders.vue') },
      { path: 'customers', name: 'AdminCustomers', component: () => import('../pages/admin/AdminCustomers.vue') },
      { path: 'inventory', name: 'AdminInventory', component: () => import('../pages/admin/AdminInventory.vue') },
      { path: 'categories', name: 'AdminCategories', component: () => import('../pages/admin/AdminCategories.vue') },
      { path: 'brands', name: 'AdminBrands', component: () => import('../pages/admin/AdminBrands.vue') },
      { path: 'coupons', name: 'AdminCoupons', component: () => import('../pages/admin/AdminCoupons.vue') },
      { path: 'reviews', name: 'AdminReviews', component: () => import('../pages/admin/AdminReviews.vue') },
      { path: 'reports', name: 'AdminReports', component: () => import('../pages/admin/AdminReports.vue') },
      { path: 'settings', name: 'AdminSettings', component: () => import('../pages/admin/AdminSettings.vue') },
      { path: 'returns', name: 'AdminReturns', component: () => import('../pages/admin/AdminReturns.vue') },
    ],
  },
  { path: '/admin/login', name: 'AdminLogin', component: () => import('../pages/admin/AdminLoginPage.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  // Admin panel requires logging in explicitly via /admin/login
  if (to.meta.requiresAdmin && !auth.isAdminSession) {
    return next('/admin/login')
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return next('/')
  }
  next()
})

export default router
