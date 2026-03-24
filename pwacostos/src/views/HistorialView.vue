<template>
  <div class="app-layout">
    <AppNavbar />
    <AppSidebar />

    <main class="main-content" @click="closeSidebar">
      <div class="historial-page">
        <!-- Header fijo -->
        <div class="historial-top">
          <div class="section-header">
            <ClipboardList :size="24" />
            <div>
              <h1>Historial de Precios</h1>
              <p class="section-subtitle">Selecciona fechas y filtros para consultar tus capturas</p>
            </div>
          </div>

          <!-- Filtros -->
          <div class="filtros-card">
            <div class="filtros-fechas">
              <div class="filtro-group">
                <label class="filtro-label">
                  <Calendar :size="12" /> Desde
                </label>
                <div class="date-wrapper">
                  <input v-model="fechaDesde" type="date" class="input input--date" @change="loadHistorial" />
                </div>
              </div>
              <div class="filtro-group">
                <label class="filtro-label">
                  <Calendar :size="12" /> Hasta
                </label>
                <div class="date-wrapper">
                  <input v-model="fechaHasta" type="date" class="input input--date" @change="loadHistorial" />
                </div>
              </div>
            </div>
            <div class="filtro-group">
              <label class="filtro-label">Mercado</label>
              <select v-model="filtroMercado" class="input input--select" @change="applyFilters">
                <option value="">Todos los mercados</option>
                <option v-for="m in mercadosUnicos" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            <div class="filtro-group">
              <label class="filtro-label">Tipo</label>
              <div class="toggle-pills">
                <button class="toggle-pill" :class="{ 'toggle-pill--active': filtroTipo === '' }" @click="filtroTipo = ''; applyFilters()">Todos</button>
                <button class="toggle-pill" :class="{ 'toggle-pill--active': filtroTipo === 'MENUDEO' }" @click="filtroTipo = 'MENUDEO'; applyFilters()">Menudeo</button>
                <button class="toggle-pill" :class="{ 'toggle-pill--active': filtroTipo === 'MAYOREO' }" @click="filtroTipo = 'MAYOREO'; applyFilters()">Mayoreo</button>
              </div>
            </div>
            <button v-if="fechaDesde || fechaHasta || filtroMercado || filtroTipo" class="btn-clear" @click="clearFilters">
              <X :size="14" /> Limpiar filtros
            </button>
          </div>

          <!-- Stats resumen -->
          <div v-if="!loading && historialFiltrado.length > 0" class="resumen-bar">
            <span class="resumen-item"><strong>{{ historialFiltrado.length }}</strong> registros</span>
            <span class="resumen-sep">·</span>
            <span class="resumen-item"><strong>{{ mercadosCount }}</strong> mercados</span>
            <span class="resumen-sep">·</span>
            <span class="resumen-item"><strong>{{ productosCount }}</strong> productos</span>
          </div>
        </div>

        <!-- Contenedor scrollable de resultados -->
        <div class="historial-results">
          <!-- Loading -->
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>Cargando historial...</p>
          </div>

          <!-- Empty -->
          <div v-else-if="historialFiltrado.length === 0" class="empty-state">
            <ClipboardList :size="48" />
            <p>{{ historial.length === 0 ? 'No hay precios registrados' : 'Sin resultados con estos filtros' }}</p>
            <p class="empty-state__hint">{{ historial.length === 0 ? 'Captura precios en la sección de Mercados' : 'Prueba cambiando los filtros' }}</p>
          </div>

          <!-- Lista agrupada por fecha -->
          <div v-else class="historial-groups">
          <div v-for="group in groupedByDate" :key="group.fecha" class="historial-group">
            <div class="group-date">
              <Calendar :size="14" />
              <span>{{ formatFecha(group.fecha) }}</span>
              <span class="group-count">{{ group.items.length }}</span>
            </div>
            <div class="group-items">
              <div v-for="h in group.items" :key="h.id" class="hist-item">
                <div class="hist-item__top">
                  <div class="hist-item__cat" :class="h.categoria_id === 'AGRICOLA' ? 'cat--agricola' : 'cat--pecuario'">
                    <Wheat v-if="h.categoria_id === 'AGRICOLA'" :size="13" />
                    <Beef v-else :size="13" />
                  </div>
                  <div class="hist-item__info">
                    <span class="hist-item__product">{{ h.producto_nombre }}</span>
                    <span class="hist-item__sub">{{ h.subcategoria_nombre }}</span>
                  </div>
                  <div class="hist-item__price-wrap">
                    <span class="hist-item__price">${{ h.precio.toFixed(2) }}</span>
                    <span class="hist-item__unit">{{ h.unidad }}</span>
                  </div>
                </div>
                <div class="hist-item__bottom">
                  <span class="hist-item__market">
                    <Store :size="11" /> {{ h.mercado_nombre }}
                  </span>
                  <span class="hist-item__badge" :class="h.tipo_precio === 'MENUDEO' ? 'badge--blue' : 'badge--orange'">
                    {{ h.tipo_precio === 'MENUDEO' ? 'Men' : 'May' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          </div>
        </div>
      </div>
    </main>

    <AppToast />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import { mercadosService } from '@/services/mercados.service'
import type { HistorialGeneralItem } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppToast from '@/components/AppToast.vue'
import { ClipboardList, Calendar, Wheat, Beef, Store, X } from 'lucide-vue-next'

const ui = useUiStore()

const loading = ref(false)
const historial = ref<HistorialGeneralItem[]>([])
const fechaDesde = ref('')
const fechaHasta = ref('')
const filtroMercado = ref('')
const filtroTipo = ref('')

function closeSidebar() {
  if (ui.sidebarOpen) ui.closeSidebar()
}

async function loadHistorial() {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (fechaDesde.value) params.fecha_desde = fechaDesde.value
    if (fechaHasta.value) params.fecha_hasta = fechaHasta.value
    historial.value = await mercadosService.getHistorialGeneral(params)
  } catch {
    ui.showToast('Error al cargar historial', 'error')
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  // reactive filtering via computed, no need to reload
}

function clearFilters() {
  fechaDesde.value = ''
  fechaHasta.value = ''
  filtroMercado.value = ''
  filtroTipo.value = ''
  loadHistorial()
}

const mercadosUnicos = computed(() => {
  const set = new Set(historial.value.map(h => h.mercado_nombre))
  return Array.from(set).sort()
})

const historialFiltrado = computed(() => {
  let items = historial.value
  if (filtroMercado.value) {
    items = items.filter(h => h.mercado_nombre === filtroMercado.value)
  }
  if (filtroTipo.value) {
    items = items.filter(h => h.tipo_precio === filtroTipo.value)
  }
  return items
})

const mercadosCount = computed(() => new Set(historialFiltrado.value.map(h => h.mercado_nombre)).size)
const productosCount = computed(() => new Set(historialFiltrado.value.map(h => h.producto_nombre)).size)

interface DateGroup {
  fecha: string
  items: HistorialGeneralItem[]
}

const groupedByDate = computed<DateGroup[]>(() => {
  const map = new Map<string, HistorialGeneralItem[]>()
  for (const h of historialFiltrado.value) {
    const list = map.get(h.fecha) || []
    list.push(h)
    map.set(h.fecha, list)
  }
  return Array.from(map.entries())
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([fecha, items]) => ({ fecha, items }))
})

function formatFecha(fecha: string): string {
  const d = new Date(fecha + 'T12:00:00')
  return d.toLocaleDateString('es-MX', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
}

onMounted(() => {
  loadHistorial()
})
</script>

<style scoped>
/* ── Layout de página ── */
.main-content {
  padding-top: 60px;
  height: 100vh;
  background: #fafafa;
  overflow: hidden;
}
.historial-page {
  max-width: 640px;
  margin: 0 auto;
  padding: 0.85rem 1rem 0;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  overflow: hidden;
}

/* ── Header + filtros (siempre visible) ── */
.historial-top {
  flex-shrink: 0;
}
.section-header {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  color: #1B5E20;
}
.section-header h1 {
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.2;
}
.section-subtitle {
  font-size: 0.78rem;
  color: #888;
  font-weight: 400;
  margin: 0.15rem 0 0;
}

/* ── Filtros ── */
.filtros-card {
  background: #fff;
  border: 1.5px solid #c8e6c9;
  border-radius: 14px;
  padding: 0.85rem;
  margin-bottom: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  box-shadow: 0 1px 4px rgba(27,94,32,0.06);
}
.filtros-fechas {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}
.filtro-group {
  min-width: 0;
}
.filtro-label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #1B5E20;
  margin-bottom: 0.25rem;
}

/* ── Inputs & Date ── */
.input {
  width: 100%;
  padding: 0.5rem 0.65rem;
  border: 1.5px solid #c8e6c9;
  border-radius: 10px;
  font-size: 0.85rem;
  color: #333;
  background: #f9fdf9;
  transition: border-color 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
  min-width: 0;
  -webkit-appearance: none;
  appearance: none;
}
.input:focus {
  border-color: #1B5E20;
  outline: none;
  box-shadow: 0 0 0 2px rgba(27,94,32,0.1);
}
.date-wrapper {
  position: relative;
}
.input--date {
  padding: 0.5rem 0.65rem;
  font-size: 0.84rem;
  min-height: 38px;
  color-scheme: light;
}
.input--date::-webkit-calendar-picker-indicator {
  opacity: 0.6;
  cursor: pointer;
}
.input--select {
  padding: 0.5rem 0.65rem;
  font-size: 0.84rem;
  min-height: 38px;
  background: #f9fdf9 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%231B5E20' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E") no-repeat right 0.55rem center;
  padding-right: 1.9rem;
}

/* ── Toggle pills ── */
.toggle-pills {
  display: flex;
  gap: 0.3rem;
}
.toggle-pill {
  flex: 1;
  padding: 0.4rem 0.45rem;
  border: 1.5px solid #c8e6c9;
  border-radius: 8px;
  background: #fff;
  font-size: 0.8rem;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.15s;
  text-align: center;
  white-space: nowrap;
}
.toggle-pill--active {
  background: #1B5E20;
  color: #fff;
  border-color: #1B5E20;
}

.btn-clear {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.3rem 0.55rem;
  border: none;
  background: #ffebee;
  color: #c62828;
  border-radius: 8px;
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  align-self: flex-start;
}

/* ── Resumen ── */
.resumen-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.4rem 0.5rem;
  font-size: 0.78rem;
  color: #1B5E20;
  margin-bottom: 0.45rem;
  flex-wrap: wrap;
  background: #e8f5e9;
  border-radius: 8px;
  font-weight: 500;
}
.resumen-sep {
  color: #a5d6a7;
}

/* ── Contenedor scrollable de resultados ── */
.historial-results {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  background: #fff;
  border: 1.5px solid #e0e0e0;
  border-radius: 14px;
  padding: 0.65rem;
  margin-bottom: 0.5rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  -webkit-overflow-scrolling: touch;
}

/* ── Loading / Empty ── */
.loading-state,
.empty-state {
  text-align: center;
  padding: 2.5rem 1rem;
  color: #bbb;
}
.loading-state p,
.empty-state p {
  margin: 0.5rem 0 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #999;
}
.empty-state__hint {
  font-weight: 400 !important;
  font-size: 0.82rem !important;
  color: #bbb !important;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e0e0e0;
  border-top-color: #1B5E20;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  margin: 0 auto 0.5rem;
}
@keyframes spin { to { transform: rotate(360deg) } }

/* ── Groups ── */
.historial-groups {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.group-date {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
  font-weight: 700;
  color: #1B5E20;
  margin-bottom: 0.35rem;
  padding-bottom: 0.25rem;
  border-bottom: 1.5px solid #e8f5e9;
  position: sticky;
  top: 0;
  background: #fff;
  z-index: 1;
  padding-top: 0.1rem;
}
.group-count {
  margin-left: auto;
  background: #e8f5e9;
  color: #1B5E20;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 10px;
}
.group-items {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

/* ── Item (2 filas) ── */
.hist-item {
  display: flex;
  flex-direction: column;
  background: #fafffe;
  border: 1px solid #e8f5e9;
  border-radius: 10px;
  padding: 0.5rem 0.6rem;
  gap: 0.2rem;
}
.hist-item__top {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}
.hist-item__cat {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.cat--agricola {
  background: #e8f5e9;
  color: #2e7d32;
}
.cat--pecuario {
  background: #fff3e0;
  color: #e65100;
}
.hist-item__info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.hist-item__product {
  font-size: 0.84rem;
  font-weight: 700;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.hist-item__sub {
  font-size: 0.7rem;
  color: #999;
}
.hist-item__price-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  flex-shrink: 0;
}
.hist-item__price {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1B5E20;
  white-space: nowrap;
}
.hist-item__unit {
  font-size: 0.66rem;
  color: #999;
}
.hist-item__bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.15rem;
  border-top: 1px solid #f0f0f0;
}
.hist-item__market {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  font-size: 0.72rem;
  color: #1B5E20;
  font-weight: 600;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.hist-item__badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.1rem 0.38rem;
  border-radius: 4px;
  text-transform: uppercase;
  flex-shrink: 0;
}
.badge--blue {
  background: #e3f2fd;
  color: #1565c0;
}
.badge--orange {
  background: #fff3e0;
  color: #e65100;
}

/* ── Responsive 480px ── */
@media (max-width: 480px) {
  .historial-page {
    padding: 0.55rem 0.55rem 0;
  }
  .section-header {
    margin-bottom: 0.5rem;
    gap: 0.35rem;
  }
  .section-header h1 {
    font-size: 1.05rem;
  }
  .section-subtitle {
    font-size: 0.68rem;
  }
  .filtros-card {
    padding: 0.55rem;
    border-radius: 11px;
    gap: 0.4rem;
    margin-bottom: 0.35rem;
  }
  .filtros-fechas {
    gap: 0.35rem;
  }
  .filtro-label {
    font-size: 0.68rem;
  }
  .input--date,
  .input--select {
    padding: 0.4rem 0.5rem;
    font-size: 0.78rem;
    min-height: 34px;
    border-radius: 8px;
  }
  .input--select {
    padding-right: 1.7rem;
  }
  .toggle-pill {
    padding: 0.32rem 0.3rem;
    font-size: 0.72rem;
    border-radius: 7px;
  }
  .btn-clear {
    font-size: 0.68rem;
    padding: 0.25rem 0.4rem;
  }
  .resumen-bar {
    font-size: 0.68rem;
    padding: 0.28rem 0.4rem;
    margin-bottom: 0.3rem;
    border-radius: 6px;
  }
  .historial-results {
    padding: 0.45rem;
    border-radius: 11px;
    margin-bottom: 0.35rem;
  }
  .historial-groups {
    gap: 0.6rem;
  }
  .group-date {
    font-size: 0.74rem;
    gap: 0.2rem;
  }
  .group-count {
    font-size: 0.62rem;
    padding: 0.08rem 0.3rem;
  }
  .group-items {
    gap: 0.2rem;
  }
  .hist-item {
    padding: 0.4rem 0.45rem;
    gap: 0.15rem;
    border-radius: 8px;
  }
  .hist-item__top {
    gap: 0.35rem;
  }
  .hist-item__cat {
    width: 24px;
    height: 24px;
    border-radius: 6px;
  }
  .hist-item__product {
    font-size: 0.76rem;
  }
  .hist-item__sub {
    font-size: 0.64rem;
  }
  .hist-item__price {
    font-size: 0.84rem;
  }
  .hist-item__unit {
    font-size: 0.58rem;
  }
  .hist-item__market {
    font-size: 0.64rem;
  }
  .hist-item__badge {
    font-size: 0.56rem;
    padding: 0.08rem 0.28rem;
  }
  .loading-state,
  .empty-state {
    padding: 1.5rem 0.75rem;
  }
  .empty-state p {
    font-size: 0.8rem;
  }
  .empty-state__hint {
    font-size: 0.7rem !important;
  }
}

/* ── Responsive 360px ── */
@media (max-width: 360px) {
  .historial-page {
    padding: 0.35rem 0.35rem 0;
  }
  .section-header h1 {
    font-size: 0.92rem;
  }
  .section-subtitle {
    font-size: 0.62rem;
  }
  .filtros-card {
    padding: 0.4rem;
    gap: 0.3rem;
  }
  .filtros-fechas {
    grid-template-columns: 1fr;
    gap: 0.2rem;
  }
  .filtro-label {
    font-size: 0.6rem;
  }
  .input--date,
  .input--select {
    padding: 0.35rem 0.4rem;
    font-size: 0.72rem;
    min-height: 32px;
  }
  .toggle-pills {
    gap: 0.15rem;
  }
  .toggle-pill {
    padding: 0.25rem 0.22rem;
    font-size: 0.65rem;
  }
  .resumen-bar {
    font-size: 0.62rem;
  }
  .historial-results {
    padding: 0.35rem;
    border-radius: 9px;
  }
  .group-date {
    font-size: 0.66rem;
  }
  .hist-item {
    padding: 0.35rem 0.38rem;
  }
  .hist-item__cat {
    width: 20px;
    height: 20px;
  }
  .hist-item__product {
    font-size: 0.7rem;
  }
  .hist-item__price {
    font-size: 0.76rem;
  }
  .hist-item__market {
    font-size: 0.58rem;
  }
  .hist-item__badge {
    font-size: 0.52rem;
    padding: 0.06rem 0.2rem;
  }
}
</style>
