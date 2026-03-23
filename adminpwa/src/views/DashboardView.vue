<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <Shield :size="28" />
        <span>Admin COSTOS</span>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <LayoutDashboard :size="20" />
          <span>Dashboard</span>
        </router-link>

        <router-link 
          v-if="auth.isAdmin" 
          to="/usuarios" 
          class="nav-item" 
          :class="{ active: $route.path === '/usuarios' }"
        >
          <Users :size="20" />
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
        <h1>Dashboard</h1>
        <p>Bienvenido, {{ auth.user?.nombre }} {{ auth.user?.apellido_paterno }}</p>
      </header>

      <div class="dashboard-grid">
        <!-- Stats Cards -->
        <div class="stat-card">
          <div class="stat-icon stat-icon--primary">
            <User :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ auth.user?.rol === 'administrador' ? 'Administrador' : 'Usuario' }}</span>
            <span class="stat-label">Tu rol</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon--success">
            <CheckCircle :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value stat-value--success">{{ auth.user?.estatus }}</span>
            <span class="stat-label">Tu estatus</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon--info">
            <Calendar :size="24" />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ formatDate(auth.user?.created_at) }}</span>
            <span class="stat-label">Fecha de registro</span>
          </div>
        </div>
      </div>

      <!-- User Profile Card -->
      <div class="profile-card">
        <h2>
          <UserCircle :size="22" />
          Mi perfil
        </h2>
        <div class="profile-grid">
          <div class="profile-item">
            <label>Nombre completo</label>
            <p>{{ auth.user?.nombre }} {{ auth.user?.apellido_paterno }} {{ auth.user?.apellido_materno }}</p>
          </div>
          <div class="profile-item">
            <label>CURP</label>
            <p>{{ auth.user?.curp }}</p>
          </div>
          <div class="profile-item">
            <label>Correo electrónico</label>
            <p>{{ auth.user?.correo }}</p>
          </div>
          <div class="profile-item">
            <label>Teléfono</label>
            <p>{{ auth.user?.telefono }}</p>
          </div>
        </div>
      </div>

      <!-- Quick Actions for Admin -->
      <div v-if="auth.isAdmin" class="quick-actions">
        <h2>
          <Zap :size="22" />
          Acciones rápidas
        </h2>
        <div class="actions-grid">
          <router-link to="/usuarios" class="action-card">
            <Users :size="32" />
            <span>Gestionar usuarios</span>
          </router-link>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Shield, LayoutDashboard, Users, LogOut, User, CheckCircle,
  Calendar, UserCircle, Zap
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

onMounted(async () => {
  if (!auth.isAuthenticated) {
    await auth.init()
  }
})

const userInitials = computed(() => {
  if (!auth.user) return '?'
  const n = auth.user.nombre?.charAt(0) || ''
  const ap = auth.user.apellido_paterno?.charAt(0) || ''
  return (n + ap).toUpperCase()
})

function formatDate(iso?: string): string {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
}

/* ── Sidebar ── */
.sidebar {
  width: 260px;
  background: #fff;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  z-index: 100;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  color: #1B5E20;
  font-weight: 700;
  font-size: 1.1rem;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0.75rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  color: #616161;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
  margin-bottom: 0.35rem;
}

.nav-item:hover {
  background: #f5f5f5;
  color: #1B5E20;
}

.nav-item.active {
  background: #e8f5e9;
  color: #1B5E20;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #1B5E20, #2E7D32);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 0.9rem;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #333;
}

.user-role {
  font-size: 0.75rem;
  color: #888;
  text-transform: capitalize;
}

.btn-logout {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: #ffebee;
  color: #c62828;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: #ffcdd2;
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
  margin-bottom: 2rem;
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
}

/* ── Stats Grid ── */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon--primary {
  background: #e3f2fd;
  color: #1565c0;
}

.stat-icon--success {
  background: #e8f5e9;
  color: #2e7d32;
}

.stat-icon--info {
  background: #fff3e0;
  color: #e65100;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
  text-transform: capitalize;
}

.stat-value--success {
  color: #2e7d32;
}

.stat-label {
  font-size: 0.85rem;
  color: #888;
}

/* ── Profile Card ── */
.profile-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-bottom: 2rem;
}

.profile-card h2 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1B5E20;
  margin: 0 0 1.25rem;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
}

.profile-item label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: #888;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
}

.profile-item p {
  font-size: 0.95rem;
  color: #333;
  margin: 0;
  word-break: break-word;
}

/* ── Quick Actions ── */
.quick-actions {
  background: #fff;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.quick-actions h2 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1B5E20;
  margin: 0 0 1.25rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1.5rem;
  background: #f5f5f5;
  border-radius: 12px;
  border: 2px solid transparent;
  text-decoration: none;
  color: #616161;
  transition: all 0.2s;
}

.action-card:hover {
  background: #e8f5e9;
  border-color: #1B5E20;
  color: #1B5E20;
}

.action-card span {
  font-weight: 600;
  font-size: 0.9rem;
  text-align: center;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .sidebar {
    width: 70px;
  }

  .sidebar-header span,
  .nav-item span,
  .user-details {
    display: none;
  }

  .sidebar-header {
    justify-content: center;
    padding: 1.25rem 0.5rem;
  }

  .nav-item {
    justify-content: center;
    padding: 0.85rem 0.5rem;
  }

  .sidebar-footer {
    flex-direction: column;
    gap: 0.5rem;
  }

  .user-info {
    display: none;
  }

  .main-content {
    margin-left: 70px;
  }
}

@media (max-width: 600px) {
  .main-content {
    padding: 1rem;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>
