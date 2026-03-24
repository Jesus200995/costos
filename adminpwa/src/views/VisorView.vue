<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo">
          <Layers :size="30" />
        </div>
        <div class="sidebar-brand">
          <span class="sidebar-brand__title">COSTOS</span>
          <span class="sidebar-brand__sub">Panel Admin</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="sidebar-nav-label">Menú</div>
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <LayoutDashboard :size="18" />
          <span>Dashboard</span>
        </router-link>

        <router-link to="/usuarios" class="nav-item" :class="{ active: $route.path === '/usuarios' }">
          <Users :size="18" />
          <span>Administradores</span>
        </router-link>

        <router-link to="/usuarios-pwa" class="nav-item" :class="{ active: $route.path === '/usuarios-pwa' }">
          <Users :size="18" />
          <span>Usuarios</span>
        </router-link>

        <router-link to="/propuestas" class="nav-item" :class="{ active: $route.path === '/propuestas' }">
          <Store :size="18" />
          <span>Propuestas Mercados</span>
        </router-link>

        <router-link to="/visor" class="nav-item" :class="{ active: $route.path === '/visor' }">
          <Map :size="18" />
          <span>Visor de Mapa</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">
            {{ userInitials }}
          </div>
          <div class="user-details">
            <span class="user-name">{{ auth.user?.nombre }}</span>
            <span class="user-role">{{ auth.user?.rol }}</span>
          </div>
        </div>
        <button class="btn-logout" @click="handleLogout">
          <LogOut :size="18" />
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Top Bar -->
      <div class="top-bar">
        <div class="top-bar__info">
          <h1 class="top-bar__title"><Map :size="22" /> Visor de Mapa</h1>
          <p class="top-bar__desc">Mapa interactivo satelital para visualización y análisis territorial</p>
        </div>
      </div>

      <!-- Map Container -->
      <div class="map-card">
        <div ref="mapContainer" class="map-container"></div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Layers, LayoutDashboard, Users, LogOut, Map, Store
} from 'lucide-vue-next'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

const router = useRouter()
const auth = useAuthStore()

const mapContainer = ref<HTMLElement | null>(null)
let map: mapboxgl.Map | null = null

const userInitials = computed(() => {
  if (!auth.user) return '?'
  const n = auth.user.nombre?.charAt(0) || ''
  const ap = auth.user.apellido_paterno?.charAt(0) || ''
  return (n + ap).toUpperCase()
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(async () => {
  await nextTick()
  if (!mapContainer.value) return

  mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || ''

  map = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [-102.5528, 23.6345],
    zoom: 4.8,
    attributionControl: false,
    projection: 'mercator'
  })

  map.addControl(new mapboxgl.NavigationControl(), 'top-right')
  map.addControl(new mapboxgl.FullscreenControl(), 'top-right')
  map.addControl(new mapboxgl.AttributionControl({ compact: true }), 'bottom-left')

  map.on('load', () => {
    map?.resize()
  })
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<style scoped>
/* ═══════════════════════════════════════════
   Layout
   ═══════════════════════════════════════════ */
.dashboard-layout { display: flex; min-height: 100vh; }

/* ── Sidebar ── */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  display: flex; flex-direction: column; position: fixed; height: 100vh; z-index: 100;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
  box-shadow: 4px 0 24px rgba(15, 23, 42, 0.35);
}

.sidebar-header { display: flex; align-items: center; gap: 0.75rem; padding: 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: #fff; }
.sidebar-logo { width: 44px; height: 44px; background: linear-gradient(135deg,#4f46e5,#6366f1); border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.sidebar-brand { display: flex; flex-direction: column; line-height: 1.15; }
.sidebar-brand__title { font-weight: 800; font-size: 1.15rem; letter-spacing: 0.04em; }
.sidebar-brand__sub { font-size: 0.68rem; font-weight: 500; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.02em; }

.sidebar-nav { flex: 1; padding: 0.75rem 0.65rem; }
.sidebar-nav-label { font-size: 0.7rem; font-weight: 600; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.05em; padding: 0.5rem 0.85rem 0.35rem; }

.nav-item { display: flex; align-items: center; gap: 0.65rem; padding: 0.55rem 0.85rem; border-radius: 8px; color: rgba(255,255,255,0.75); text-decoration: none; font-weight: 500; font-size: 0.88rem; transition: all 0.2s cubic-bezier(.4,0,.2,1); margin-bottom: 2px; }
.nav-item:hover { background: rgba(255,255,255,0.08); color: #fff; }
.nav-item.active { background: rgba(99,102,241,0.25); color: #fff; font-weight: 600; }

.sidebar-footer { padding: 0.85rem; border-top: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; }
.user-info { display: flex; align-items: center; gap: 0.65rem; }
.user-avatar { width: 34px; height: 34px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 600; font-size: 0.78rem; }
.user-details { display: flex; flex-direction: column; }
.user-name { font-weight: 600; font-size: 0.82rem; color: #fff; }
.user-role { font-size: 0.7rem; color: rgba(255,255,255,0.5); text-transform: capitalize; }
.btn-logout { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border: none; border-radius: 8px; background: transparent; color: rgba(255,255,255,0.5); cursor: pointer; transition: all 0.15s; }
.btn-logout:hover { background: rgba(255,255,255,0.1); color: #fff; }

/* ── Main Content ── */
.main-content { flex: 1; margin-left: 260px; padding: 0.75rem 2rem 2rem; background: #f8fafc; min-height: 100vh; display: flex; flex-direction: column; }

/* ── Top Bar ── */
.top-bar { display: flex; align-items: center; justify-content: space-between; background: linear-gradient(135deg,#4f46e5,#6366f1); border-radius: 14px; padding: 1.15rem 1.5rem; margin-bottom: 1.25rem; box-shadow: 0 4px 20px rgba(79,70,229,0.18); flex-shrink: 0; }
.top-bar__title { font-size: 1.35rem; font-weight: 700; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.top-bar__desc { font-size: 0.85rem; color: rgba(255,255,255,0.75); margin: 0.15rem 0 0; }

/* ═══════════════════════════════════════════
   Map
   ═══════════════════════════════════════════ */
.map-card {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  overflow: hidden;
  min-height: 500px;
  position: relative;
}

.map-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
}

/* Mapbox overrides */
:deep(.mapboxgl-ctrl-top-right) {
  top: 12px;
  right: 12px;
}

:deep(.mapboxgl-ctrl-group) {
  border-radius: 10px !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important;
  overflow: hidden;
}

:deep(.mapboxgl-ctrl-group button) {
  width: 36px !important;
  height: 36px !important;
}

:deep(.mapboxgl-ctrl-fullscreen) {
  margin-top: 8px;
}

/* ═══════════════════════════════════════════
   Responsive
   ═══════════════════════════════════════════ */
@media (max-width: 900px) {
  .sidebar { width: 68px; }
  .sidebar-brand, .nav-item span, .user-details, .sidebar-nav-label { display: none; }
  .sidebar-header { justify-content: center; padding: 1rem 0.5rem; }
  .sidebar-logo { width: 36px; height: 36px; }
  .nav-item { justify-content: center; padding: 0.6rem 0.5rem; }
  .sidebar-footer { flex-direction: column; gap: 0.5rem; }
  .user-info { display: none; }
  .main-content { margin-left: 68px; }
}

@media (max-width: 600px) {
  .main-content { padding: 0.75rem 1rem 1.5rem; }
}
</style>
