<template>
  <div class="app-layout">
    <AppNavbar />
    <AppSidebar />

    <main class="main-content" @click="closeSidebar">
      <div class="home-header" :class="{ 'home-header--visible': mounted }">
        <div class="home-welcome">
          <h1 class="home-welcome__title">
            Hola, <span>{{ authStore.user?.name?.split(' ')[0] || 'Usuario' }}</span> 👋
          </h1>
          <p class="home-welcome__subtitle">Gestión de cultivos y productos</p>
        </div>
        <div class="home-avatar" @click.stop="showProfileModal = true">
          <span>{{ initials }}</span>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="stats-grid" :class="{ 'stats-grid--visible': mounted }">
        <div class="stat-card stat-card--primary">
          <div class="stat-card__icon">
            <MapPin :size="22" />
          </div>
          <div class="stat-card__info">
            <span class="stat-card__value">0</span>
            <span class="stat-card__label">Lugares</span>
          </div>
        </div>
        <div class="stat-card stat-card--accent">
          <div class="stat-card__icon">
            <Receipt :size="22" />
          </div>
          <div class="stat-card__info">
            <span class="stat-card__value">0</span>
            <span class="stat-card__label">Registros</span>
          </div>
        </div>
        <div class="stat-card stat-card--success">
          <div class="stat-card__icon">
            <TrendingDown :size="22" />
          </div>
          <div class="stat-card__info">
            <span class="stat-card__value">$0</span>
            <span class="stat-card__label">Ahorro</span>
          </div>
        </div>
        <div class="stat-card stat-card--warning">
          <div class="stat-card__icon">
            <Wallet :size="22" />
          </div>
          <div class="stat-card__info">
            <span class="stat-card__value">$0</span>
            <span class="stat-card__label">Total</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <section class="home-section" :class="{ 'home-section--visible': mounted }">
        <h2 class="home-section__title">
          <Zap :size="20" />
          Acciones rápidas
        </h2>
        <div class="quick-actions">
          <button class="quick-action" @click="ui.showToast('Próximamente: Agregar lugar', 'info')">
            <div class="quick-action__icon quick-action__icon--blue">
              <Plus :size="24" />
            </div>
            <span>Nuevo Lugar</span>
          </button>
          <button class="quick-action" @click="ui.showToast('Próximamente: Registrar costo', 'info')">
            <div class="quick-action__icon quick-action__icon--green">
              <DollarSign :size="24" />
            </div>
            <span>Nuevo Costo</span>
          </button>
          <button class="quick-action" @click="ui.showToast('Próximamente: Ver reportes', 'info')">
            <div class="quick-action__icon quick-action__icon--purple">
              <BarChart3 :size="24" />
            </div>
            <span>Reportes</span>
          </button>
          <button class="quick-action" @click="ui.showToast('Próximamente: Exportar', 'info')">
            <div class="quick-action__icon quick-action__icon--orange">
              <Download :size="24" />
            </div>
            <span>Exportar</span>
          </button>
        </div>
      </section>

      <!-- Recent Activity (placeholder) -->
      <section class="home-section home-section--last" :class="{ 'home-section--visible': mounted }">
        <h2 class="home-section__title">
          <Clock :size="20" />
          Actividad reciente
        </h2>
        <div class="empty-state">
          <div class="empty-state__icon">
            <Inbox :size="48" />
          </div>
          <p class="empty-state__text">Aún no hay registros</p>
          <p class="empty-state__hint">Comienza agregando un lugar y registrando costos</p>
        </div>
      </section>
    </main>

    <!-- Profile Modal -->
    <AppModal :show="showProfileModal" @close="showProfileModal = false">
      <template #header>
        <UserCircle :size="24" />
        <span>Mi Perfil</span>
      </template>
      <template #body>
        <div class="profile-modal">
          <div class="profile-modal__avatar">
            <span>{{ initials }}</span>
          </div>
          <h3>{{ authStore.user?.name }}</h3>
          <p>{{ authStore.user?.email }}</p>
        </div>
      </template>
      <template #footer>
        <button class="btn btn--danger btn--full" @click="handleLogout">
          <LogOut :size="18" />
          <span>Cerrar Sesión</span>
        </button>
      </template>
    </AppModal>

    <AppToast />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppModal from '@/components/AppModal.vue'
import AppToast from '@/components/AppToast.vue'
import {
  MapPin, Receipt, TrendingDown, Wallet, Zap, Plus,
  DollarSign, BarChart3, Download, Clock, Inbox,
  UserCircle, LogOut
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const ui = useUiStore()

const mounted = ref(false)
const showProfileModal = ref(false)

const initials = computed(() => {
  const name = authStore.user?.name || 'U'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
})

function closeSidebar() {
  if (ui.sidebarOpen) ui.closeSidebar()
}

function handleLogout() {
  showProfileModal.value = false
  authStore.logout()
  ui.showToast('Sesión cerrada', 'info')
  router.push('/login')
}

onMounted(() => {
  setTimeout(() => { mounted.value = true }, 100)
})
</script>
