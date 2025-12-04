<template>
  <div id="app" class="min-h-screen">
    <Navbar v-if="isAuthenticated" />
    <main :class="{ 'ml-64': isAuthenticated }">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/Navbar.vue'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
</script>