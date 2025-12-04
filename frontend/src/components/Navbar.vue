<template>
  <nav class="fixed left-0 top-0 h-full w-64 bg-white shadow-lg z-10">
    <div class="p-6">
      <h1 class="text-2xl font-bold text-blue-600">FinanceFlow</h1>
    </div>
    
    <div class="px-4">
      <router-link 
        v-for="item in menuItems" 
        :key="item.path"
        :to="item.path"
        class="flex items-center gap-3 px-4 py-3 mb-2 rounded-lg transition-colors"
        :class="isActive(item.path) ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-50'"
      >
        <component :is="item.icon" class="w-5 h-5" />
        <span class="font-medium">{{ item.label }}</span>
      </router-link>
    </div>

    <div class="absolute bottom-0 w-full p-4 border-t">
      <div class="flex items-center gap-3 px-4 py-3 mb-2">
        <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
          <span class="text-blue-600 font-semibold">{{ userInitials }}</span>
        </div>
        <div class="flex-1">
          <p class="font-medium text-sm">{{ user?.name || user?.email }}</p>
          <router-link to="/profile" class="text-xs text-gray-500 hover:text-blue-600">
            View Profile
          </router-link>
        </div>
      </div>
      <button 
        @click="handleLogout"
        class="w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
      >
        Logout
      </button>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  HomeIcon,
  CreditCardIcon,
  ChartBarIcon,
  DocumentTextIcon,
  UserIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const menuItems = [
  { path: '/dashboard', label: 'Dashboard', icon: HomeIcon },
  { path: '/transactions', label: 'Transactions', icon: CreditCardIcon },
  { path: '/budgets', label: 'Budgets', icon: ChartBarIcon },
  { path: '/reports', label: 'Reports', icon: DocumentTextIcon }
]

const user = computed(() => authStore.currentUser)

const userInitials = computed(() => {
  const name = user.value?.name || user.value?.email || 'U'
  return name.substring(0, 2).toUpperCase()
})

const isActive = (path) => {
  return route.path === path
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>