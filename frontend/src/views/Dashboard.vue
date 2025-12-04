<template>
  <div class="p-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
      <p class="text-gray-600 mt-1">Welcome back, {{ user?.name || 'User' }}!</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">Total Income</p>
            <p class="text-2xl font-bold text-green-600">${{ formatNumber(stats.income) }}</p>
          </div>
          <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">Total Expenses</p>
            <p class="text-2xl font-bold text-red-600">${{ formatNumber(stats.expenses) }}</p>
          </div>
          <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
            </svg>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">Balance</p>
            <p class="text-2xl font-bold" :class="stats.balance >= 0 ? 'text-blue-600' : 'text-red-600'">
              ${{ formatNumber(stats.balance) }}
            </p>
          </div>
          <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Spending by Category</h2>
        <Pie v-if="chartData.pie" :data="chartData.pie" :options="chartOptions.pie" />
        <p v-else class="text-gray-500 text-center py-8">No expense data available</p>
      </div>

      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Budget Overview</h2>
        <div v-if="budgets.length > 0" class="space-y-4">
          <div v-for="budget in budgets" :key="budget.id" class="border-b pb-4 last:border-0">
            <div class="flex justify-between mb-2">
              <span class="font-medium">{{ budget.category }}</span>
              <span class="text-sm text-gray-600">
                ${{ formatNumber(budget.spent) }} / ${{ formatNumber(budget.limit) }}
              </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="h-2 rounded-full transition-all"
                :class="budget.percentage > 90 ? 'bg-red-500' : budget.percentage > 70 ? 'bg-yellow-500' : 'bg-green-500'"
                :style="{ width: Math.min(budget.percentage, 100) + '%' }"
              ></div>
            </div>
            <p class="text-xs text-gray-500 mt-1">{{ budget.percentage.toFixed(0) }}% used</p>
          </div>
        </div>
        <p v-else class="text-gray-500 text-center py-8">No budgets set for this month</p>
      </div>
    </div>

    <!-- Recent Transactions -->
    <div class="card">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold">Recent Transactions</h2>
        <router-link to="/transactions" class="text-sm text-blue-600 hover:text-blue-700">
          View all →
        </router-link>
      </div>
      
      <div v-if="recentTransactions.length > 0" class="space-y-3">
        <div 
          v-for="transaction in recentTransactions" 
          :key="transaction.id"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center gap-3">
            <div 
              class="w-10 h-10 rounded-full flex items-center justify-center"
              :class="transaction.type === 'income' ? 'bg-green-100' : 'bg-red-100'"
            >
              <span :class="transaction.type === 'income' ? 'text-green-600' : 'text-red-600'">
                {{ transaction.type === 'income' ? '↑' : '↓' }}
              </span>
            </div>
            <div>
              <p class="font-medium">{{ transaction.category }}</p>
              <p class="text-sm text-gray-500">{{ formatDate(transaction.date) }}</p>
            </div>
          </div>
          <span 
            class="font-semibold"
            :class="transaction.type === 'income' ? 'text-green-600' : 'text-red-600'"
          >
            {{ transaction.type === 'income' ? '+' : '-' }}${{ formatNumber(transaction.amount) }}
          </span>
        </div>
      </div>
      <p v-else class="text-gray-500 text-center py-8">No transactions yet</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { format } from 'date-fns'

ChartJS.register(ArcElement, Tooltip, Legend)

const authStore = useAuthStore()
const user = computed(() => authStore.currentUser)

const stats = ref({
  income: 0,
  expenses: 0,
  balance: 0,
  categories: []
})

const budgets = ref([])
const recentTransactions = ref([])

const chartData = ref({
  pie: null
})

const chartOptions = {
  pie: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom'
      }
    }
  }
}

const formatNumber = (num) => {
  return Number(num).toFixed(2)
}

const formatDate = (date) => {
  return format(new Date(date), 'MMM dd, yyyy')
}

const loadData = async () => {
  try {
    // Load stats
    const statsRes = await api.getStats()
    stats.value = statsRes.data

    // Prepare pie chart data
    if (stats.value.categories && stats.value.categories.length > 0) {
      chartData.value.pie = {
        labels: stats.value.categories.map(c => c.category),
        datasets: [{
          data: stats.value.categories.map(c => c.amount),
          backgroundColor: [
            '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
            '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
          ]
        }]
      }
    }

    // Load budgets
    const currentMonth = format(new Date(), 'yyyy-MM')
    const budgetsRes = await api.getBudgets({ month: currentMonth })
    budgets.value = budgetsRes.data.budgets

    // Load recent transactions
    const transactionsRes = await api.getTransactions({ limit: 5 })
    recentTransactions.value = transactionsRes.data.transactions
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>