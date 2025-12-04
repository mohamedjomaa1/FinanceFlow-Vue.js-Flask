<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="w-full max-w-md">
      <div class="card">
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-blue-600 mb-2">FinanceFlow</h1>
          <p class="text-gray-600">Welcome back! Please login to continue</p>
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input 
              v-model="form.email" 
              type="email" 
              required
              class="input"
              placeholder="you@example.com"
            />
          </div>

          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input 
              v-model="form.password" 
              type="password" 
              required
              class="input"
              placeholder="••••••••"
            />
          </div>

          <div class="flex items-center justify-between mb-6">
            <router-link 
              to="/forgot-password"
              class="text-sm text-blue-600 hover:text-blue-700"
            >
              Forgot password?
            </router-link>
          </div>

          <button 
            type="submit" 
            :disabled="loading"
            class="w-full btn btn-primary"
          >
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>

          <div v-if="error" class="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
            {{ error }}
          </div>
        </form>

        <div class="mt-6 text-center text-sm text-gray-600">
          Don't have an account?
          <router-link to="/register" class="text-blue-600 hover:text-blue-700 font-medium">
            Sign up
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  email: '',
  password: ''
})

const loading = ref(false)
const error = ref(null)

const handleLogin = async () => {
  loading.value = true
  error.value = null

  try {
    await authStore.login(form.value)
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>