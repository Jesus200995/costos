<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <Shield :size="22" />
        <span>COSTOS</span>
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
          <span>Usuarios PWA</span>
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
      <header class="content-header">
        <div>
          <h1>Usuarios PWA</h1>
          <p>Usuarios registrados en la aplicación COSTOS</p>
        </div>
        <div class="header-stats">
          <div class="stat-mini">
            <span class="stat-mini__value">{{ filteredUsers.length }}</span>
            <span class="stat-mini__label">Mostrados</span>
          </div>
          <div class="stat-mini stat-mini--primary">
            <span class="stat-mini__value">{{ usuarios.length }}</span>
            <span class="stat-mini__label">Total</span>
          </div>
        </div>
      </header>

      <!-- Search & Filters -->
      <div class="filters-bar">
        <div class="search-box">
          <Search :size="18" class="search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por nombre, correo, CURP, teléfono..."
            class="search-input"
          />
          <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">
            <X :size="16" />
          </button>
        </div>
        <div class="filter-group">
          <select v-model="filterTipo" class="filter-select">
            <option value="">Todos los tipos</option>
            <option value="REPRESENTANTE_CAC">Representante CAC</option>
            <option value="COM_COMERCIALIZACION">Com. Comercialización</option>
            <option value="OFICINAS">Oficinas</option>
          </select>
          <select v-model="filterEstado" class="filter-select">
            <option value="">Todos los estados</option>
            <option v-for="edo in estadosUnicos" :key="edo" :value="edo">{{ edo }}</option>
          </select>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando usuarios...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredUsers.length === 0" class="empty-state">
        <Users :size="48" />
        <h3>No se encontraron usuarios</h3>
        <p v-if="searchQuery || filterTipo || filterEstado">Intenta con otros filtros de búsqueda</p>
        <p v-else>Aún no hay usuarios registrados en la PWA</p>
      </div>

      <!-- Users Table -->
      <div v-else class="users-table-container">
        <div class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th @click="sortBy('name')" class="sortable">
                  Nombre
                  <ChevronDown v-if="sortField === 'name'" :size="14" :class="{ 'sort-asc': sortDir === 'asc' }" />
                </th>
                <th class="hide-tablet">Correo</th>
                <th class="hide-mobile">CURP</th>
                <th class="hide-mobile">Teléfono</th>
                <th>Tipo</th>
                <th class="hide-tablet">Estado</th>
                <th class="hide-mobile sortable" @click="sortBy('created_at')">
                  Registro
                  <ChevronDown v-if="sortField === 'created_at'" :size="14" :class="{ 'sort-asc': sortDir === 'asc' }" />
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in paginatedUsers" :key="u.id" @click="openDetail(u)" class="row-clickable">
                <td>
                  <div class="user-cell">
                    <div class="user-cell__avatar" :style="{ background: avatarColor(u.name) }">
                      {{ getInitials(u.name) }}
                    </div>
                    <div class="user-cell__info">
                      <span class="user-cell__name">{{ u.name }}</span>
                      <span class="user-cell__sub hide-desktop">{{ u.email }}</span>
                    </div>
                  </div>
                </td>
                <td class="hide-tablet text-ellipsis">{{ u.email }}</td>
                <td class="hide-mobile mono">{{ u.curp || '—' }}</td>
                <td class="hide-mobile">{{ u.telefono || '—' }}</td>
                <td>
                  <span class="badge" :class="badgeClass(u.tipo_capturista)">
                    {{ tipoLabel(u.tipo_capturista) }}
                  </span>
                </td>
                <td class="hide-tablet">{{ u.estado || '—' }}</td>
                <td class="hide-mobile">{{ formatDate(u.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination">
          <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">
            <ChevronLeft :size="16" />
          </button>
          <template v-for="p in visiblePages" :key="p">
            <button
              v-if="p !== '...'"
              class="page-btn" :class="{ active: currentPage === p }"
              @click="currentPage = p as number"
            >{{ p }}</button>
            <span v-else class="page-dots">...</span>
          </template>
          <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">
            <ChevronRight :size="16" />
          </button>
          <span class="page-info">{{ currentPage }} de {{ totalPages }}</span>
        </div>
      </div>

      <!-- Detail Modal -->
      <div v-if="selectedUser" class="modal-overlay" @click="selectedUser = null">
        <div class="modal modal--lg" @click.stop>
          <div class="modal-header">
            <div class="modal-user-header">
              <div class="modal-avatar" :style="{ background: avatarColor(selectedUser.name) }">
                {{ getInitials(selectedUser.name) }}
              </div>
              <div>
                <h3>{{ selectedUser.name }}</h3>
                <p class="modal-subtitle">{{ tipoLabel(selectedUser.tipo_capturista) }}</p>
              </div>
            </div>
            <button class="modal-close" @click="selectedUser = null">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div class="detail-grid">
              <div class="detail-item">
                <label>Correo electrónico</label>
                <span>{{ selectedUser.email }}</span>
              </div>
              <div class="detail-item">
                <label>CURP</label>
                <span class="mono">{{ selectedUser.curp || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>Teléfono</label>
                <span>{{ selectedUser.telefono || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>Tipo de capturista</label>
                <span>{{ tipoLabel(selectedUser.tipo_capturista) }}</span>
              </div>
              <div class="detail-item">
                <label>Estado</label>
                <span>{{ selectedUser.estado || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>Municipio</label>
                <span>{{ selectedUser.municipio || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>Localidad</label>
                <span>{{ selectedUser.localidad || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>Territorio</label>
                <span>{{ selectedUser.territorio || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>CAC ID</label>
                <span class="mono">{{ selectedUser.cac_id || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>CAC Nombre</label>
                <span>{{ selectedUser.cac_nombre || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>Rol comisión</label>
                <span>{{ selectedUser.rol_comision || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>Correo institucional</label>
                <span>{{ selectedUser.correo_institucional || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>Rol interno</label>
                <span>{{ selectedUser.rol_interno || '—' }}</span>
              </div>
              <div class="detail-item">
                <label>Fecha de registro</label>
                <span>{{ formatDateFull(selectedUser.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Toast -->
      <div v-if="toast.show" class="toast" :class="`toast--${toast.type}`">
        {{ toast.message }}
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/auth.service'
import type { PWAUser } from '@/types'
import {
  Shield, LayoutDashboard, Users, LogOut, Search, X,
  ChevronDown, ChevronLeft, ChevronRight
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const usuarios = ref<PWAUser[]>([])
const loading = ref(true)
const searchQuery = ref('')
const filterTipo = ref('')
const filterEstado = ref('')
const sortField = ref<'name' | 'created_at'>('created_at')
const sortDir = ref<'asc' | 'desc'>('desc')
const currentPage = ref(1)
const perPage = 15
const selectedUser = ref<PWAUser | null>(null)

const toast = reactive({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error'
})

const userInitials = computed(() => {
  if (!auth.user) return '?'
  const n = auth.user.nombre?.charAt(0) || ''
  const ap = auth.user.apellido_paterno?.charAt(0) || ''
  return (n + ap).toUpperCase()
})

const estadosUnicos = computed(() => {
  const edos = new Set(usuarios.value.map(u => u.estado).filter(Boolean) as string[])
  return Array.from(edos).sort()
})

const filteredUsers = computed(() => {
  let result = [...usuarios.value]

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(u =>
      u.name?.toLowerCase().includes(q) ||
      u.email?.toLowerCase().includes(q) ||
      u.curp?.toLowerCase().includes(q) ||
      u.telefono?.includes(q) ||
      u.cac_nombre?.toLowerCase().includes(q) ||
      u.territorio?.toLowerCase().includes(q)
    )
  }

  if (filterTipo.value) {
    result = result.filter(u => u.tipo_capturista === filterTipo.value)
  }

  if (filterEstado.value) {
    result = result.filter(u => u.estado === filterEstado.value)
  }

  result.sort((a, b) => {
    const aVal = a[sortField.value] || ''
    const bVal = b[sortField.value] || ''
    const cmp = aVal < bVal ? -1 : aVal > bVal ? 1 : 0
    return sortDir.value === 'asc' ? cmp : -cmp
  })

  return result
})

const totalPages = computed(() => Math.ceil(filteredUsers.value.length / perPage))

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredUsers.value.slice(start, start + perPage)
})

const visiblePages = computed(() => {
  const pages: (number | string)[] = []
  const t = totalPages.value
  const c = currentPage.value
  if (t <= 7) {
    for (let i = 1; i <= t; i++) pages.push(i)
  } else {
    pages.push(1)
    if (c > 3) pages.push('...')
    for (let i = Math.max(2, c - 1); i <= Math.min(t - 1, c + 1); i++) pages.push(i)
    if (c < t - 2) pages.push('...')
    pages.push(t)
  }
  return pages
})

watch([searchQuery, filterTipo, filterEstado], () => {
  currentPage.value = 1
})

function sortBy(field: 'name' | 'created_at') {
  if (sortField.value === field) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDir.value = 'asc'
  }
}

function getInitials(name: string): string {
  if (!name) return '?'
  const parts = name.trim().split(/\s+/)
  return (parts[0]?.charAt(0) || '' + (parts[1]?.charAt(0) || '')).toUpperCase().slice(0, 2)
}

function avatarColor(name: string): string {
  const colors = [
    'linear-gradient(135deg, #bf360c, #e65100)',
    'linear-gradient(135deg, #1565c0, #1976d2)',
    'linear-gradient(135deg, #2e7d32, #388e3c)',
    'linear-gradient(135deg, #6a1b9a, #7b1fa2)',
    'linear-gradient(135deg, #c62828, #d32f2f)',
    'linear-gradient(135deg, #00838f, #0097a7)',
    'linear-gradient(135deg, #4527a0, #512da8)',
    'linear-gradient(135deg, #ad1457, #c2185b)',
  ]
  let hash = 0
  for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

function tipoLabel(tipo: string | null): string {
  const map: Record<string, string> = {
    'REPRESENTANTE_CAC': 'Rep. CAC',
    'COM_COMERCIALIZACION': 'Com. Comercialización',
    'OFICINAS': 'Oficinas',
  }
  return tipo ? (map[tipo] || tipo) : '—'
}

function badgeClass(tipo: string | null): string {
  const map: Record<string, string> = {
    'REPRESENTANTE_CAC': 'badge--orange',
    'COM_COMERCIALIZACION': 'badge--blue',
    'OFICINAS': 'badge--green',
  }
  return tipo ? (map[tipo] || 'badge--default') : 'badge--default'
}

function formatDate(iso: string): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' })
}

function formatDateFull(iso: string): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('es-MX', {
    day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

function openDetail(u: PWAUser) {
  selectedUser.value = u
}

function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

async function loadUsuarios() {
  loading.value = true
  try {
    usuarios.value = await authService.getUsuariosPWA(auth.token!)
  } catch (e: any) {
    showToast(e.response?.data?.detail || 'Error al cargar usuarios', 'error')
  } finally {
    loading.value = false
  }
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  loadUsuarios()
})
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
}

/* ── Sidebar ── */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #bf360c 0%, #8d2f00 100%);
  border-right: none;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  z-index: 100;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
  box-shadow: 4px 0 20px rgba(141, 47, 0, 0.2);
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 1.1rem 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  font-weight: 700;
  font-size: 1.05rem;
  letter-spacing: -0.02em;
}

.sidebar-nav {
  flex: 1;
  padding: 0.75rem 0.65rem;
}

.sidebar-nav-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.55);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.5rem 0.85rem 0.35rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.55rem 0.85rem;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.88rem;
  transition: all 0.15s ease;
  margin-bottom: 2px;
  letter-spacing: -0.01em;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-weight: 600;
}

.sidebar-footer {
  padding: 0.85rem;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.user-avatar {
  width: 34px;
  height: 34px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  font-size: 0.78rem;
  letter-spacing: 0.02em;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  font-size: 0.82rem;
  color: #fff;
  letter-spacing: -0.01em;
}

.user-role {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: capitalize;
}

.btn-logout {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-logout:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

/* ── Main Content ── */
.main-content {
  flex: 1;
  margin-left: 260px;
  padding: 2rem;
  background: #f5f5f5;
  min-height: 100vh;
}

.content-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.content-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 0.25rem;
}

.content-header p {
  color: #757575;
  font-size: 0.95rem;
  margin: 0;
}

.header-stats {
  display: flex;
  gap: 0.75rem;
}

.stat-mini {
  background: #fff;
  border-radius: 10px;
  padding: 0.65rem 1rem;
  text-align: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.stat-mini--primary {
  border-left: 3px solid #bf360c;
}

.stat-mini__value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: #333;
}

.stat-mini__label {
  font-size: 0.75rem;
  color: #888;
}

/* ── Filters ── */
.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 280px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.7rem 2.5rem 0.7rem 2.75rem;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  font-size: 0.9rem;
  background: #fff;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: #bf360c;
  box-shadow: 0 0 0 3px rgba(191, 54, 12, 0.08);
}

.search-input::placeholder {
  color: #bbb;
}

.search-clear {
  position: absolute;
  right: 0.6rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0.2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-clear:hover {
  background: #f0f0f0;
  color: #666;
}

.filter-group {
  display: flex;
  gap: 0.5rem;
}

.filter-select {
  padding: 0.7rem 0.85rem;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  font-size: 0.85rem;
  background: #fff;
  cursor: pointer;
  color: #555;
  transition: border-color 0.2s;
}

.filter-select:focus {
  outline: none;
  border-color: #bf360c;
}

/* ── Loading ── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #888;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e0e0e0;
  border-top-color: #bf360c;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── Empty State ── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #999;
  text-align: center;
}

.empty-state h3 {
  margin: 1rem 0 0.25rem;
  color: #666;
  font-size: 1.2rem;
}

.empty-state p {
  margin: 0;
  font-size: 0.9rem;
}

/* ── Table ── */
.users-table-container {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.table-container {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table thead {
  background: #fafafa;
  border-bottom: 1.5px solid #eee;
}

.table th {
  padding: 0.85rem 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #888;
  white-space: nowrap;
  user-select: none;
}

.table th.sortable {
  cursor: pointer;
  transition: color 0.15s;
}

.table th.sortable:hover {
  color: #bf360c;
}

.sort-asc {
  transform: rotate(180deg);
}

.table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f5f5f5;
  font-size: 0.88rem;
  color: #444;
  vertical-align: middle;
}

.row-clickable {
  cursor: pointer;
  transition: background 0.15s;
}

.row-clickable:hover {
  background: #fafafa;
}

.text-ellipsis {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mono {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 0.82rem;
  letter-spacing: 0.02em;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-cell__avatar {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  font-size: 0.78rem;
  flex-shrink: 0;
}

.user-cell__info {
  display: flex;
  flex-direction: column;
}

.user-cell__name {
  font-weight: 600;
  color: #333;
  font-size: 0.88rem;
}

.user-cell__sub {
  font-size: 0.78rem;
  color: #999;
}

.hide-desktop {
  display: none;
}

/* ── Badges ── */
.badge {
  display: inline-block;
  padding: 0.3rem 0.65rem;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
}

.badge--orange {
  background: #fff3e0;
  color: #e65100;
}

.badge--blue {
  background: #e3f2fd;
  color: #1565c0;
}

.badge--green {
  background: #e8f5e9;
  color: #2e7d32;
}

.badge--default {
  background: #f5f5f5;
  color: #999;
}

/* ── Pagination ── */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  padding: 1rem;
  border-top: 1px solid #f0f0f0;
}

.page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  color: #555;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.page-btn:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #bf360c;
  color: #bf360c;
}

.page-btn.active {
  background: #bf360c;
  border-color: #bf360c;
  color: #fff;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-dots {
  padding: 0 0.25rem;
  color: #999;
}

.page-info {
  margin-left: 0.75rem;
  font-size: 0.82rem;
  color: #999;
}

/* ── Modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background: #fff;
  border-radius: 16px;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  max-height: 90vh;
  overflow-y: auto;
}

.modal--lg {
  max-width: 640px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.modal-user-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.modal-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 1rem;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
}

.modal-subtitle {
  margin: 0.15rem 0 0;
  font-size: 0.82rem;
  color: #888;
}

.modal-close {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0.3rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.modal-close:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 1.25rem 1.5rem 1.5rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.detail-item label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #999;
}

.detail-item span {
  font-size: 0.9rem;
  color: #333;
  word-break: break-word;
}

/* ── Toast ── */
.toast {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.85rem 1.5rem;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  z-index: 1001;
  animation: slideUp 0.3s ease;
}

.toast--success {
  background: #2e7d32;
  color: #fff;
}

.toast--error {
  background: #c62828;
  color: #fff;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* ── Responsive ── */
@media (max-width: 1024px) {
  .hide-tablet {
    display: none !important;
  }
  .hide-desktop {
    display: block;
  }
}

@media (max-width: 900px) {
  .sidebar {
    width: 68px;
  }

  .sidebar-header span,
  .nav-item span,
  .user-details,
  .sidebar-nav-label {
    display: none;
  }

  .sidebar-header {
    justify-content: center;
    padding: 1rem 0.5rem;
  }

  .nav-item {
    justify-content: center;
    padding: 0.6rem 0.5rem;
  }

  .sidebar-footer {
    flex-direction: column;
    gap: 0.5rem;
  }

  .user-info {
    display: none;
  }

  .main-content {
    margin-left: 68px;
  }

  .hide-mobile {
    display: none !important;
  }

  .hide-desktop {
    display: block;
  }
}

@media (max-width: 600px) {
  .main-content {
    padding: 1rem;
  }

  .content-header {
    flex-direction: column;
  }

  .header-stats {
    width: 100%;
    justify-content: space-between;
  }

  .filters-bar {
    flex-direction: column;
  }

  .search-box {
    min-width: unset;
  }

  .filter-group {
    flex-direction: column;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .modal--lg {
    max-width: 100%;
    margin: 0;
    border-radius: 12px;
  }
}
</style>
