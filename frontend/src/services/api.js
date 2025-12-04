import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default {
  // Auth
  register(data) {
    return api.post('/auth/register', data)
  },
  login(data) {
    return api.post('/auth/login', data)
  },
  getProfile() {
    return api.get('/auth/profile')
  },
  updateProfile(data) {
    return api.put('/auth/profile', data)
  },
  forgotPassword(data) {
    return api.post('/auth/forgot-password', data)
  },
  resetPassword(data) {
    return api.post('/auth/reset-password', data)
  },
  changePassword(data) {
    return api.post('/auth/change-password', data)
  },

  // Transactions
  getTransactions(params) {
    return api.get('/transactions', { params })
  },
  getTransaction(id) {
    return api.get(`/transactions/${id}`)
  },
  createTransaction(data) {
    return api.post('/transactions', data)
  },
  updateTransaction(id, data) {
    return api.put(`/transactions/${id}`, data)
  },
  deleteTransaction(id) {
    return api.delete(`/transactions/${id}`)
  },
  getStats(params) {
    return api.get('/transactions/stats', { params })
  },
  exportTransactions(params) {
    return api.get('/transactions/export', { 
      params,
      responseType: 'blob'
    })
  },

  // Budgets
  getBudgets(params) {
    return api.get('/budgets', { params })
  },
  getBudget(id) {
    return api.get(`/budgets/${id}`)
  },
  createBudget(data) {
    return api.post('/budgets', data)
  },
  updateBudget(id, data) {
    return api.put(`/budgets/${id}`, data)
  },
  deleteBudget(id) {
    return api.delete(`/budgets/${id}`)
  },
  getBudgetOverview(params) {
    return api.get('/budgets/overview', { params })
  }
}