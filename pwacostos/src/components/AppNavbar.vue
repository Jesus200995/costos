<template>
  <header class="navbar">
    <button class="navbar__burger" @click="ui.toggleSidebar()" aria-label="Menú">
      <span class="burger-line" :class="{ 'burger-line--open': ui.sidebarOpen }"></span>
      <span class="burger-line" :class="{ 'burger-line--open': ui.sidebarOpen }"></span>
      <span class="burger-line" :class="{ 'burger-line--open': ui.sidebarOpen }"></span>
    </button>
    <div class="navbar__brand">
      <DollarSign :size="22" />
      <span>CostApp</span>
    </div>
    <button class="navbar__action" @click="$emit('search')" aria-label="Buscar">
      <Bell :size="22" />
    </button>
  </header>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
import { DollarSign, Bell } from 'lucide-vue-next'

defineEmits<{ search: [] }>()

const ui = useUiStore()
</script>
