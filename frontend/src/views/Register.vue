<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
    <div class="w-full max-w-md">
      <div class="card">
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-blue-600 mb-2">Create Account</h1>
          <p class="text-gray-600">Start managing your finances today</p>
        </div>

        <form @submit.prevent="handleRegister">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
            <input 
              v-model="form.name" 
              type="text" 
              class="input"
              placeholder="John Doe"
            />
          </div>

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

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Phone (Optional)</label>
            <input 
              v-model="form.phone" 
              type="tel" 
              class="input"
              placeholder="+1234567890"
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

          <button 
            type="submit" 
            :disabled="loading"
            class="w-full btn btn-primary"
          >
            {{ loading ? 'Creating account...' : 'Create Account' }}
          </button>

          <div v-if="error" class="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
            {{ error }}
          </div>
        </form>

        <div class="mt-6 text-center text-sm text-gray-600">
          Already have an account?
          <router-link to="/login" class="text-blue-600 hover:text-blue-700 font-medium">
            Login
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
  name: '',
  email: '',
  phone: '',
  password: ''
})

const loading = ref(false)
const error = ref(null)

const handleRegister = async () => {
  loading.value = true
  error.value = null

  try {
    await authStore.register(form.value)
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.error || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>