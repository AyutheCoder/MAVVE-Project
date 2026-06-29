import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Dashboard ───────────────────────────────────────────
export const fetchDashboardStats = () =>
  api.get('/api/dashboard/stats').then((r) => r.data)

export const fetchRTOTrend = () =>
  api.get('/api/dashboard/rto-trend').then((r) => r.data)

export const fetchAgentPerformance = () =>
  api.get('/api/dashboard/agent-performance').then((r) => r.data)

export const fetchLanguageDistribution = () =>
  api.get('/api/dashboard/language-distribution').then((r) => r.data)

// ── Orders ──────────────────────────────────────────────
export const fetchOrders = (params) =>
  api.get('/api/orders', { params }).then((r) => r.data)

export const fetchOrder = (orderId) =>
  api.get(`/api/orders/${orderId}`).then((r) => r.data)

export const interceptOrder = (orderId) =>
  api.post('/api/orders/intercept', null, { params: { order_id: orderId } }).then((r) => r.data)

// ── Health ──────────────────────────────────────────────
export const fetchHealth = () =>
  api.get('/health').then((r) => r.data)

export default api
