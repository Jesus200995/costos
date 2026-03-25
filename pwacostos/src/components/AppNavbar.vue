<template>
  <div class="navbar-wrapper">
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
      <button class="navbar__action" @click="$emit('search')" aria-label="Buscar">
        <Bell :size="22" />
      </button>
    </header>

    <!-- Barra de conexión de lado a lado -->
    <div class="conn-bar" :class="isOnline ? 'conn-bar--on' : 'conn-bar--off'">
      <span class="conn-dot"></span>
      <span class="conn-label">{{ isOnline ? 'En línea' : 'Sin conexión' }}</span>
      <span v-if="pendingCount > 0" class="conn-badge">{{ pendingCount }} pendiente{{ pendingCount > 1 ? 's' : '' }}</span>
    </div>
  </div>
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
.navbar-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.conn-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 3px 0;
  font-size: .7rem;
  font-weight: 600;
  letter-spacing: .03em;
  transition: background .3s, color .3s;
  user-select: none;
}
.conn-bar--on {
  background: linear-gradient(90deg, #22c55e, #16a34a);
  color: #fff;
}
.conn-bar--off {
  background: linear-gradient(90deg, #ef4444, #dc2626);
  color: #fff;
}
.conn-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #fff;
  flex-shrink: 0;
}
.conn-bar--on .conn-dot { box-shadow: 0 0 6px rgba(255,255,255,.6); }
.conn-bar--off .conn-dot { animation: blink-dot 1.2s infinite; }
@keyframes blink-dot { 0%,100%{opacity:1} 50%{opacity:.3} }
.conn-label { white-space: nowrap; }
.conn-badge {
  background: rgba(255,255,255,.25);
  font-size: .6rem;
  padding: 1px 7px;
  border-radius: 8px;
}
</style>
