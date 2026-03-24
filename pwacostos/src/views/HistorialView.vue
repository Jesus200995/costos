<template>
  <div class="app-layout">
    <AppNavbar />
    <AppSidebar />

    <main class="main-content" @click="closeSidebar">
      <div class="historial-page">
        <div class="section-header">
          <ClipboardList :size="24" />
          <h1>Historial de Precios</h1>
        </div>

        <!-- Filtros -->
        <div class="filtros-card">
          <div class="filtros-row">
            <div class="filtro-group">
              <label class="filtro-label">Desde</label>
              <input v-model="fechaDesde" type="date" class="input input--sm" @change="loadHistorial" />
            </div>
            <div class="filtro-group">
              <label class="filtro-label">Hasta</label>
              <input v-model="fechaHasta" type="date" class="input input--sm" @change="loadHistorial" />
            </div>
          </div>
          <div class="filtros-row">
            <div class="filtro-group filtro-group--full">
              <label class="filtro-label">Mercado</label>
              <select v-model="filtroMercado" class="input input--sm" @change="applyFilters">
                <option value="">Todos los mercados</option>
                <option v-for="m in mercadosUnicos" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
          </div>
          <div class="filtros-row">
            <div class="filtro-group filtro-group--full">
              <label class="filtro-label">Tipo</label>
              <div class="toggle-pills toggle-pills--sm">
                <button class="toggle-pill toggle-pill--sm" :class="{ 'toggle-pill--active': filtroTipo === '' }" @click="filtroTipo = ''; applyFilters()">Todos</button>
                <button class="toggle-pill toggle-pill--sm" :class="{ 'toggle-pill--active': filtroTipo === 'MENUDEO' }" @click="filtroTipo = 'MENUDEO'; applyFilters()">Menudeo</button>
                <button class="toggle-pill toggle-pill--sm" :class="{ 'toggle-pill--active': filtroTipo === 'MAYOREO' }" @click="filtroTipo = 'MAYOREO'; applyFilters()">Mayoreo</button>
              </div>
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
                <div class="hist-item__cat" :class="h.categoria_id === 'AGRICOLA' ? 'cat--agricola' : 'cat--pecuario'">
                  <Wheat v-if="h.categoria_id === 'AGRICOLA'" :size="12" />
                  <Beef v-else :size="12" />
                </div>
                <div class="hist-item__info">
                  <span class="hist-item__product">{{ h.producto_nombre }}</span>
                  <span class="hist-item__sub">{{ h.subcategoria_nombre }}</span>
                  <span class="hist-item__market">
                    <Store :size="11" /> {{ h.mercado_nombre }}
                  </span>
                </div>
                <div class="hist-item__right">
                  <span class="hist-item__price">${{ h.precio.toFixed(2) }}</span>
                  <span class="hist-item__unit">{{ h.unidad }}</span>
                  <span class="hist-item__badge" :class="h.tipo_precio === 'MENUDEO' ? 'badge--blue' : 'badge--orange'">
                    {{ h.tipo_precio === 'MENUDEO' ? 'Men' : 'May' }}
                  </span>
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
.historial-page {
  max-width: 640px;
  margin: 0 auto;
  padding: 1rem 1rem 2rem;
}
.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  color: #1B5E20;
}
.section-header h1 {
  font-size: 1.35rem;
  font-weight: 700;
  margin: 0;
}

/* ── Filtros ── */
.filtros-card {
  background: #fafafa;
  border: 1.5px solid #e8e8e8;
  border-radius: 14px;
  padding: 0.75rem;
  margin-bottom: 1rem;
  overflow: hidden;
}
.filtros-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  min-width: 0;
}
.filtros-row:last-of-type {
  margin-bottom: 0;
}
.filtro-group {
  flex: 1;
  min-width: 0;
}
.filtro-group--full {
  flex: 1;
}
.filtro-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #888;
  margin-bottom: 0.2rem;
}
.input--sm {
  padding: 0.45rem 0.6rem;
  font-size: 0.85rem;
}
.toggle-pills--sm {
  display: flex;
  gap: 0.25rem;
}
.toggle-pill--sm {
  padding: 0.35rem 0.6rem;
  font-size: 0.78rem;
}
.btn-clear {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 0.5rem;
  padding: 0.3rem 0.6rem;
  border: none;
  background: #ffebee;
  color: #c62828;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

/* ── Resumen ── */
.resumen-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.5rem;
  font-size: 0.8rem;
  color: #777;
  margin-bottom: 0.75rem;
}
.resumen-sep {
  color: #ddd;
}

/* ── Loading / Empty ── */
.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
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
  gap: 1rem;
}
.group-date {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
  font-weight: 700;
  color: #1B5E20;
  margin-bottom: 0.4rem;
  padding-bottom: 0.3rem;
  border-bottom: 1.5px solid #e8f5e9;
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
  gap: 0.35rem;
}

/* ── Item ── */
.hist-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #fff;
  border: 1.5px solid #f0f0f0;
  border-radius: 10px;
  padding: 0.6rem 0.7rem;
}
.hist-item__cat {
  width: 28px;
  height: 28px;
  border-radius: 8px;
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
  font-size: 0.85rem;
  font-weight: 700;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.hist-item__sub {
  font-size: 0.72rem;
  color: #999;
}
.hist-item__market {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  font-size: 0.72rem;
  color: #1B5E20;
  font-weight: 600;
  margin-top: 0.1rem;
}
.hist-item__right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.1rem;
  flex-shrink: 0;
}
.hist-item__price {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1B5E20;
}
.hist-item__unit {
  font-size: 0.7rem;
  color: #999;
}
.hist-item__badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  text-transform: uppercase;
}
.badge--blue {
  background: #e3f2fd;
  color: #1565c0;
}
.badge--orange {
  background: #fff3e0;
  color: #e65100;
}

/* ── Toggle pills ── */
.toggle-pill {
  padding: 0.45rem 0.85rem;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  font-size: 0.82rem;
  font-weight: 600;
  color: #888;
  cursor: pointer;
  transition: all 0.15s;
}
.toggle-pill--active {
  background: #1B5E20;
  color: #fff;
  border-color: #1B5E20;
}

/* ── Inputs ── */
.input {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  font-size: 0.9rem;
  color: #333;
  background: #fff;
  transition: border-color 0.15s;
  box-sizing: border-box;
  max-width: 100%;
  min-width: 0;
}
.input:focus {
  border-color: #1B5E20;
  outline: none;
}

/* ── Nav ── */
.main-content {
  padding-top: 60px;
  min-height: 100vh;
  background: #fafafa;
}

/* ── Responsive ── */
@media (max-width: 400px) {
  .historial-page {
    padding: 0.75rem 0.75rem 2rem;
  }
  .section-header h1 {
    font-size: 1.1rem;
  }
  .filtros-card {
    padding: 0.5rem;
  }
  .filtros-row {
    flex-direction: column;
    gap: 0.35rem;
  }
  .filtro-label {
    font-size: 0.7rem;
  }
  .input--sm {
    padding: 0.4rem 0.5rem;
    font-size: 0.78rem;
  }
  .toggle-pill--sm {
    padding: 0.3rem 0.45rem;
    font-size: 0.72rem;
  }
  .resumen-bar {
    font-size: 0.72rem;
    gap: 0.25rem;
    flex-wrap: wrap;
    justify-content: center;
  }
  .hist-item {
    padding: 0.5rem 0.55rem;
    gap: 0.35rem;
  }
  .hist-item__cat {
    width: 24px;
    height: 24px;
  }
  .hist-item__product {
    font-size: 0.78rem;
  }
  .hist-item__sub,
  .hist-item__market {
    font-size: 0.68rem;
  }
  .hist-item__price {
    font-size: 0.85rem;
  }
  .hist-item__unit {
    font-size: 0.65rem;
  }
  .hist-item__badge {
    font-size: 0.6rem;
  }
  .group-date {
    font-size: 0.75rem;
  }
}

@media (max-width: 340px) {
  .section-header h1 {
    font-size: 1rem;
  }
  .toggle-pills--sm {
    flex-wrap: wrap;
  }
  .hist-item__product {
    font-size: 0.72rem;
  }
  .hist-item__price {
    font-size: 0.78rem;
  }
}
</style>
