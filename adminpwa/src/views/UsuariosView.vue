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
          <span>Usuarios</span>
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
          <h1>Gestión de usuarios</h1>
          <p>Administra los usuarios del sistema</p>
        </div>
        <div class="header-stats">
          <div class="stat-mini">
            <span class="stat-mini__value">{{ usuarios.length }}</span>
            <span class="stat-mini__label">Total</span>
          </div>
          <div class="stat-mini stat-mini--success">
            <span class="stat-mini__value">{{ activeCount }}</span>
            <span class="stat-mini__label">Activos</span>
          </div>
          <div class="stat-mini stat-mini--danger">
            <span class="stat-mini__value">{{ inactiveCount }}</span>
            <span class="stat-mini__label">Inactivos</span>
          </div>
        </div>
      </header>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando usuarios...</p>
      </div>

      <!-- Users Table -->
      <div v-else class="users-table-container">
        <div class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th>Nombre completo</th>
                <th class="hide-mobile">CURP</th>
                <th class="hide-mobile">Correo</th>
                <th>Rol</th>
                <th>Estatus</th>
                <th class="text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in usuarios" :key="u.id">
                <td>
                  <div class="user-cell">
                    <div class="user-cell__avatar">
                      {{ getInitials(u) }}
                    </div>
                    <div class="user-cell__info">
                      <span class="user-cell__name">{{ u.nombre }} {{ u.apellido_paterno }}</span>
                      <span class="user-cell__sub">{{ u.apellido_materno }}</span>
                    </div>
                  </div>
                </td>
                <td class="hide-mobile">{{ u.curp }}</td>
                <td class="hide-mobile">{{ u.correo }}</td>
                <td>
                  <select 
                    :value="u.rol" 
                    class="select-mini"
                    :class="u.rol === 'administrador' ? 'select-mini--primary' : 'select-mini--default'"
                    :disabled="u.id === auth.user?.id"
                    @change="updateRol(u.id, ($event.target as HTMLSelectElement).value)"
                  >
                    <option value="usuario">Usuario</option>
                    <option value="administrador">Admin</option>
                  </select>
                </td>
                <td>
                  <button 
                    class="badge-btn"
                    :class="u.estatus === 'activo' ? 'badge-btn--success' : 'badge-btn--danger'"
                    :disabled="u.id === auth.user?.id"
                    @click="toggleEstatus(u)"
                  >
                    {{ u.estatus }}
                    <RefreshCw v-if="u.id !== auth.user?.id" :size="12" />
                  </button>
                </td>
                <td class="text-right">
                  <button 
                    v-if="u.id !== auth.user?.id"
                    class="btn-action btn-action--danger" 
                    @click="confirmDelete(u)"
                    title="Eliminar usuario"
                  >
                    <Trash2 :size="16" />
                  </button>
                  <span v-else class="text-muted">Tú</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Toast -->
      <div v-if="toast.show" class="toast" :class="`toast--${toast.type}`">
        {{ toast.message }}
      </div>

      <!-- Delete Modal -->
      <div v-if="showDeleteModal" class="modal-overlay" @click="showDeleteModal = false">
        <div class="modal" @click.stop>
          <div class="modal-header">
            <AlertTriangle :size="24" class="modal-icon--danger" />
            <h3>Confirmar eliminación</h3>
          </div>
          <p class="modal-body">
            ¿Estás seguro de eliminar a <strong>{{ userToDelete?.nombre }} {{ userToDelete?.apellido_paterno }}</strong>?
            Esta acción no se puede deshacer.
          </p>
          <div class="modal-actions">
            <button class="btn btn--secondary" @click="showDeleteModal = false">Cancelar</button>
            <button class="btn btn--danger" @click="deleteUser" :disabled="deleting">
              {{ deleting ? 'Eliminando...' : 'Eliminar' }}
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/auth.service'
import type { AdminUser } from '@/types'
import {
  Shield, LayoutDashboard, Users, LogOut, Trash2, RefreshCw, AlertTriangle
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const usuarios = ref<AdminUser[]>([])
const loading = ref(true)
const showDeleteModal = ref(false)
const userToDelete = ref<AdminUser | null>(null)
const deleting = ref(false)

const toast = reactive({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error'
})

const activeCount = computed(() => usuarios.value.filter(u => u.estatus === 'activo').length)
const inactiveCount = computed(() => usuarios.value.filter(u => u.estatus === 'inactivo').length)

const userInitials = computed(() => {
  if (!auth.user) return '?'
  const n = auth.user.nombre?.charAt(0) || ''
  const ap = auth.user.apellido_paterno?.charAt(0) || ''
  return (n + ap).toUpperCase()
})

function getInitials(u: AdminUser): string {
  const n = u.nombre?.charAt(0) || ''
  const ap = u.apellido_paterno?.charAt(0) || ''
  return (n + ap).toUpperCase()
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
    usuarios.value = await authService.getUsuarios(auth.token!)
  } catch (e: any) {
    showToast(e.response?.data?.detail || 'Error al cargar usuarios', 'error')
  } finally {
    loading.value = false
  }
}

async function toggleEstatus(user: AdminUser) {
  const newEstatus = user.estatus === 'activo' ? 'inactivo' : 'activo'
  try {
    const updated = await authService.updateEstatus(user.id, newEstatus, auth.token!)
    const idx = usuarios.value.findIndex(u => u.id === user.id)
    if (idx !== -1) usuarios.value[idx] = updated
    showToast(`Usuario ${newEstatus === 'activo' ? 'activado' : 'desactivado'}`)
  } catch (e: any) {
    showToast(e.response?.data?.detail || 'Error al actualizar estatus', 'error')
  }
}

async function updateRol(userId: number, rol: string) {
  try {
    const updated = await authService.updateRol(userId, rol, auth.token!)
    const idx = usuarios.value.findIndex(u => u.id === userId)
    if (idx !== -1) usuarios.value[idx] = updated
    showToast(`Rol actualizado a ${rol}`)
  } catch (e: any) {
    showToast(e.response?.data?.detail || 'Error al actualizar rol', 'error')
  }
}

function confirmDelete(user: AdminUser) {
  userToDelete.value = user
  showDeleteModal.value = true
}

async function deleteUser() {
  if (!userToDelete.value) return
  deleting.value = true
  try {
    await authService.deleteUsuario(userToDelete.value.id, auth.token!)
    usuarios.value = usuarios.value.filter(u => u.id !== userToDelete.value!.id)
    showToast('Usuario eliminado correctamente')
    showDeleteModal.value = false
  } catch (e: any) {
    showToast(e.response?.data?.detail || 'Error al eliminar usuario', 'error')
  } finally {
    deleting.value = false
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

/* ── Sidebar (Apple-style) ── */
.sidebar {
  width: 260px;
  background: rgba(245, 245, 247, 0.92);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-right: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  z-index: 100;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 1.1rem 1.25rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  color: #1d1d1f;
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
  color: #86868b;
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
  color: #3a3a3c;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.88rem;
  transition: all 0.15s ease;
  margin-bottom: 2px;
  letter-spacing: -0.01em;
}

.nav-item:hover {
  background: rgba(0, 0, 0, 0.04);
  color: #1d1d1f;
}

.nav-item.active {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}

.sidebar-footer {
  padding: 0.85rem;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
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
  background: linear-gradient(135deg, #007aff, #5856d6);
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
  color: #1d1d1f;
  letter-spacing: -0.01em;
}

.user-role {
  font-size: 0.7rem;
  color: #86868b;
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
  color: #86868b;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-logout:hover {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
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

.stat-mini--success {
  border-left: 3px solid #2e7d32;
}

.stat-mini--danger {
  border-left: 3px solid #c62828;
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

/* ── Loading ── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #888;
}

.loading-state .spinner {
  margin-bottom: 1rem;
}

/* ── Table ── */
.users-table-container {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-cell__avatar {
  width: 38px;
  height: 38px;
  background: linear-gradient(135deg, #1B5E20, #2E7D32);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  font-size: 0.8rem;
  flex-shrink: 0;
}

.user-cell__info {
  display: flex;
  flex-direction: column;
}

.user-cell__name {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
}

.user-cell__sub {
  font-size: 0.8rem;
  color: #888;
}

.select-mini {
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  border: 1.5px solid #e0e0e0;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  background: #fff;
  transition: all 0.2s;
}

.select-mini:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.select-mini--primary {
  border-color: #1565c0;
  color: #1565c0;
  background: #e3f2fd;
}

.select-mini--default {
  border-color: #e0e0e0;
  color: #616161;
}

.badge-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.65rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.badge-btn:disabled {
  cursor: default;
}

.badge-btn--success {
  background: #e8f5e9;
  color: #2e7d32;
}

.badge-btn--success:not(:disabled):hover {
  background: #c8e6c9;
}

.badge-btn--danger {
  background: #ffebee;
  color: #c62828;
}

.badge-btn--danger:not(:disabled):hover {
  background: #ffcdd2;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-action--danger {
  background: #fff;
  color: #c62828;
}

.btn-action--danger:hover {
  background: #ffebee;
}

.text-muted {
  color: #bdbdbd;
  font-size: 0.85rem;
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
  padding: 1.5rem;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.modal-icon--danger {
  color: #c62828;
}

.modal-body {
  color: #616161;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.modal-body strong {
  color: #333;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
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
}
</style>
