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

        <router-link 
          v-if="auth.isAdmin" 
          to="/usuarios" 
          class="nav-item" 
          :class="{ active: $route.path === '/usuarios' }"
        >
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
