<template>
  <header class="navbar">
    <button class="navbar__burger" @click="ui.toggleSidebar()" aria-label="Menú">
      <span class="burger-line" :class="{ 'burger-line--open': ui.sidebarOpen }"></span>
      <span class="burger-line" :class="{ 'burger-line--open': ui.sidebarOpen }"></span>
      <span class="burger-line" :class="{ 'burger-line--open': ui.sidebarOpen }"></span>
    </button>
    <div class="navbar__brand">
      <Wheat :size="22" />
      <span>COSTOS</span>
    </div>

    <!-- Indicador de conexión -->
    <div class="navbar__conn" :class="isOnline ? 'navbar__conn--on' : 'navbar__conn--off'">
      <span class="conn-dot"></span>
      <span class="conn-label">{{ isOnline ? 'En línea' : 'Sin conexión' }}</span>
      <span v-if="pendingCount > 0" class="conn-badge">{{ pendingCount }}</span>
    </div>

    <button class="navbar__action" @click="$emit('search')" aria-label="Buscar">
      <Bell :size="22" />
    </button>
  </header>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
import { Wheat, Bell } from 'lucide-vue-next'
import { useOnlineStatus, usePendingCount } from '@/services/offline'

defineEmits<{ search: [] }>()

const ui = useUiStore()
const { isOnline } = useOnlineStatus()
const { pendingCount } = usePendingCount()
</script>

<style scoped>
.navbar__conn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: .75rem;
  font-weight: 600;
  letter-spacing: .02em;
  transition: background .3s, color .3s;
  user-select: none;
}
.navbar__conn--on {
  background: rgba(34, 197, 94, .18);
  color: #22c55e;
}
.navbar__conn--off {
  background: rgba(239, 68, 68, .18);
  color: #ef4444;
}
.conn-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.navbar__conn--on .conn-dot { background: #22c55e; box-shadow: 0 0 6px #22c55e88; }
.navbar__conn--off .conn-dot { background: #ef4444; animation: blink-dot 1.2s infinite; }
@keyframes blink-dot { 0%,100%{opacity:1} 50%{opacity:.3} }
.conn-label { white-space: nowrap; }
.conn-badge {
  background: #ef4444;
  color: #fff;
  font-size: .65rem;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
}
</style>
