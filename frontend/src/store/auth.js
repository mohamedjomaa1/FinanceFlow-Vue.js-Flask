import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('access_token') || null,
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user
  },

  actions: {
    async register(userData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.register(userData)
        this.token = response.data.access_token
        this.user = response.data.user
        localStorage.setItem('access_token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || 'Registration failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async login(credentials) {
      this.loading = true
      this.error = null
      try {
        const response = await api.login(credentials)
        this.token = response.data.access_token
        this.user = response.data.user
        localStorage.setItem('access_token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || 'Login failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchProfile() {
      try {
        const response = await api.getProfile()
        this.user = response.data.user
        localStorage.setItem('user', JSON.stringify(this.user))
      } catch (error) {
        console.error('Failed to fetch profile:', error)
      }
    },

    async updateProfile(data) {
      this.loading = true
      try {
        const response = await api.updateProfile(data)
        this.user = response.data.user
        localStorage.setItem('user', JSON.stringify(this.user))
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || 'Update failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
    }
  }
})