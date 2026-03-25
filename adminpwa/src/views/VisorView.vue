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
          <MapIcon :size="18" />
          <span>Visor de Mapa</span>
        </router-link>
        <router-link to="/registros-precios" class="nav-item" :class="{ active: $route.path === '/registros-precios' }">
          <ClipboardList :size="18" />
          <span>Registros Precios</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ userInitials }}</div>
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
          <h1 class="top-bar__title"><MapIcon :size="22" /> Monitoreo de Precios</h1>
          <p class="top-bar__desc">Mapa nacional con mercados, reportes y analítica por estado</p>
        </div>
        <div class="top-bar__actions">
          <span class="last-update" v-if="lastUpdate">
            <Clock :size="14" /> {{ lastUpdate }}
          </span>
          <button class="btn-refresh" @click="loadAll" :disabled="loading">
            <RefreshCw :size="16" :class="{ spinning: loading }" /> Refrescar
          </button>
        </div>
      </div>

      <!-- Three-column layout -->
      <div class="monitor-grid">
        <!-- LEFT: Filters -->
        <div class="panel panel-filters">
          <h3 class="panel-title"><Filter :size="16" /> Filtros</h3>

          <!-- Período -->
          <div class="filter-group">
            <label>Período</label>
            <div class="filter-row">
              <input type="date" v-model="filtros.fecha_desde" class="f-input" />
              <input type="date" v-model="filtros.fecha_hasta" class="f-input" />
            </div>
          </div>

          <!-- Categoría -->
          <div class="filter-group">
            <label>Categoría</label>
            <select v-model="filtros.categoria_id" class="f-select" @change="onCategoriaChange">
              <option value="">Todas</option>
              <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
            </select>
          </div>

          <!-- Subcategoría -->
          <div class="filter-group">
            <label>Subcategoría</label>
            <select v-model="filtros.subcategoria_id" class="f-select" @change="onSubcategoriaChange">
              <option value="">Todas</option>
              <option v-for="s in filteredSubcategorias" :key="s.id" :value="s.id">{{ s.nombre }}</option>
            </select>
          </div>

          <!-- Producto -->
          <div class="filter-group">
            <label>Producto</label>
            <select v-model="filtros.producto_id" class="f-select" @change="applyFilters">
              <option value="">Todos</option>
              <option v-for="p in filteredProductos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
            </select>
          </div>

          <!-- Tipo precio -->
          <div class="filter-group">
            <label>Tipo de precio</label>
            <select v-model="filtros.tipo_precio" class="f-select" @change="applyFilters">
              <option value="">Ambos</option>
              <option value="MENUDEO">Menudeo</option>
              <option value="MAYOREO">Mayoreo</option>
            </select>
          </div>

          <!-- Capas -->
          <h3 class="panel-title" style="margin-top:1rem"><MapPin :size="16" /> Capas</h3>
          <label class="layer-toggle">
            <input type="checkbox" v-model="capas.denue" @change="toggleLayers" />
            <span class="layer-dot" style="background:#9ca3af"></span> Mercados DENUE
          </label>
          <label class="layer-toggle">
            <input type="checkbox" v-model="capas.reportados" @change="toggleLayers" />
            <span class="layer-dot" style="background:#22c55e"></span> Con reporte
          </label>
          <label class="layer-toggle">
            <input type="checkbox" v-model="capas.propuestos" @change="toggleLayers" />
            <span class="layer-dot" style="background:#f59e0b"></span> Propuestos
          </label>

          <button class="btn-apply" @click="applyFilters" :disabled="loading">
            <Search :size="15" /> Aplicar filtros
          </button>
        </div>

        <!-- CENTER: Map -->
        <div class="panel panel-map">
          <div ref="mapContainer" class="map-container"></div>
          <!-- Popup overlay -->
          <div v-if="selectedMercado" class="map-popup-overlay" @click.self="selectedMercado = null">
            <div class="map-popup">
              <div class="popup-header">
                <h4>{{ selectedMercado.mercado_nombre || selectedMercado.nombre }}</h4>
                <button @click="selectedMercado = null" class="popup-close">&times;</button>
              </div>
              <div class="popup-meta">
                <span><MapPin :size="13" /> {{ selectedMercado.entidad }}, {{ selectedMercado.municipio }}</span>
                <span v-if="selectedMercado.tipo_mercado">{{ selectedMercado.tipo_mercado }}</span>
              </div>
              <div v-if="popupPrecios.length" class="popup-precios">
                <table>
                  <thead><tr><th>Producto</th><th>Precio</th><th>Unidad</th><th>Tipo</th><th>Fecha</th></tr></thead>
                  <tbody>
                    <tr v-for="pr in popupPrecios" :key="pr.id">
                      <td>{{ pr.producto }}</td>
                      <td class="price">${{ pr.precio.toFixed(2) }}</td>
                      <td>{{ pr.unidad }}</td>
                      <td><span class="badge" :class="pr.tipo_precio === 'MENUDEO' ? 'badge-men' : 'badge-may'">{{ pr.tipo_precio }}</span></td>
                      <td>{{ pr.fecha }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-else class="popup-empty">Sin precios registrados</div>
            </div>
          </div>
        </div>

        <!-- RIGHT: Analytics -->
        <div class="panel panel-analytics">
          <h3 class="panel-title"><BarChart3 :size="16" /> Analítica por Estado</h3>

          <!-- KPIs -->
          <div class="kpis-grid">
            <div class="kpi-card">
              <div class="kpi-label">Promedio Nacional</div>
              <div class="kpi-value">${{ kpis.promedio_nacional?.toFixed(2) || '—' }}</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">Total Reportes</div>
              <div class="kpi-value">{{ kpis.total_reportes || 0 }}</div>
            </div>
            <div class="kpi-card kpi-max">
              <div class="kpi-label">Máximo</div>
              <div class="kpi-value" v-if="kpis.estado_max">${{ kpis.estado_max.maximo.toFixed(2) }}</div>
              <div class="kpi-sub" v-if="kpis.estado_max">{{ kpis.estado_max.estado }}</div>
              <div class="kpi-value" v-else>—</div>
            </div>
            <div class="kpi-card kpi-min">
              <div class="kpi-label">Mínimo</div>
              <div class="kpi-value" v-if="kpis.estado_min">${{ kpis.estado_min.minimo.toFixed(2) }}</div>
              <div class="kpi-sub" v-if="kpis.estado_min">{{ kpis.estado_min.estado }}</div>
              <div class="kpi-value" v-else>—</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">Cobertura</div>
              <div class="kpi-value">{{ kpis.cobertura || '0/0' }}</div>
            </div>
          </div>

          <!-- Chart -->
          <div class="chart-wrap" v-if="estadosData.length">
            <Bar :data="chartData" :options="chartOptions" />
          </div>
          <div v-else class="chart-empty">
            <BarChart3 :size="40" />
            <p>Selecciona filtros y aplica para ver la gráfica</p>
          </div>

          <!-- Ranking table -->
          <div class="ranking" v-if="estadosData.length">
            <h4>Ranking por Estado</h4>
            <table class="ranking-table">
              <thead><tr><th>#</th><th>Estado</th><th>Promedio</th><th>Min</th><th>Max</th><th>Rep.</th></tr></thead>
              <tbody>
                <tr v-for="(e, i) in estadosData" :key="e.estado">
                  <td>{{ i + 1 }}</td>
                  <td>{{ e.estado }}</td>
                  <td class="price">${{ e.promedio.toFixed(2) }}</td>
                  <td>${{ e.minimo.toFixed(2) }}</td>
                  <td>${{ e.maximo.toFixed(2) }}</td>
                  <td>{{ e.num_reportes }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Layers, LayoutDashboard, Users, LogOut, Store, ClipboardList,
  Map as MapIcon, MapPin, Filter, Search, RefreshCw, Clock, BarChart3
} from 'lucide-vue-next'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  Title, Tooltip, Legend
} from 'chart.js'
import api from '@/services/api'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const router = useRouter()
const auth = useAuthStore()

// ── State ──
const mapContainer = ref<HTMLElement | null>(null)
let map: mapboxgl.Map | null = null
const loading = ref(false)
const lastUpdate = ref('')

const filtros = reactive({
  categoria_id: '',
  subcategoria_id: '',
  producto_id: '' as string | number,
  tipo_precio: '',
  unidad: '',
  fecha_desde: '',
  fecha_hasta: ''
})

const capas = reactive({ denue: true, reportados: true, propuestos: true })

// Catalogs
const categorias = ref<any[]>([])
const subcategorias = ref<any[]>([])
const productos = ref<any[]>([])

// Data
const denueMarkers = ref<any[]>([])
const reportadosMarkers = ref<any[]>([])
const propuestosMarkers = ref<any[]>([])
const estadosData = ref<any[]>([])
const kpis = ref<any>({})

// Popup
const selectedMercado = ref<any>(null)
const popupPrecios = ref<any[]>([])

// Map markers references
let mapMarkers: mapboxgl.Marker[] = []

// ── Computed ──
const filteredSubcategorias = computed(() =>
  filtros.categoria_id
    ? subcategorias.value.filter(s => s.categoria_id === filtros.categoria_id)
    : subcategorias.value
)
const filteredProductos = computed(() =>
  filtros.subcategoria_id
    ? productos.value.filter(p => p.subcategoria_id === filtros.subcategoria_id)
    : productos.value
)

const userInitials = computed(() => {
  if (!auth.user) return '?'
  const n = auth.user.nombre?.charAt(0) || ''
  const ap = auth.user.apellido_paterno?.charAt(0) || ''
  return (n + ap).toUpperCase()
})

// ── Chart data ──
const chartData = computed(() => ({
  labels: estadosData.value.map(e => e.estado?.substring(0, 15) || 'N/A'),
  datasets: [{
    label: 'Promedio',
    data: estadosData.value.map(e => e.promedio),
    backgroundColor: '#6366f1',
    borderRadius: 4,
  }, {
    label: 'Mínimo',
    data: estadosData.value.map(e => e.minimo),
    backgroundColor: '#22c55e',
    borderRadius: 4,
  }, {
    label: 'Máximo',
    data: estadosData.value.map(e => e.maximo),
    backgroundColor: '#ef4444',
    borderRadius: 4,
  }]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y' as const,
  plugins: {
    legend: { position: 'top' as const, labels: { font: { size: 11 } } },
    tooltip: {
      callbacks: {
        label: (ctx: any) => `${ctx.dataset.label}: $${ctx.parsed.x?.toFixed(2)}`
      }
    }
  },
  scales: {
    x: { ticks: { callback: (v: any) => `$${v}` } },
    y: { ticks: { font: { size: 10 } } }
  }
}

// ── Methods ──
function handleLogout() {
  auth.logout()
  router.push('/login')
}

async function loadCatalogos() {
  try {
    const { data } = await api.get('/admin/registros-precios/filtros', { params: {} })
    categorias.value = data.categorias || []
    subcategorias.value = data.subcategorias || []
    productos.value = data.productos || []
  } catch { /* silent */ }
}

function onCategoriaChange() {
  filtros.subcategoria_id = ''
  filtros.producto_id = ''
}

function onSubcategoriaChange() {
  filtros.producto_id = ''
}

async function loadMercados() {
  try {
    const { data } = await api.get('/admin/monitoreo/mercados', { params: {} })
    denueMarkers.value = data.denue || []
    propuestosMarkers.value = data.propuestos || []
  } catch (e) {
    console.error('Error loading mercados:', e)
  }
}

async function loadPreciosMercados() {
  const params: any = {}
  if (filtros.producto_id) params.producto_id = filtros.producto_id
  if (filtros.subcategoria_id) params.subcategoria_id = filtros.subcategoria_id
  if (filtros.categoria_id) params.categoria_id = filtros.categoria_id
  if (filtros.tipo_precio) params.tipo_precio = filtros.tipo_precio
  if (filtros.unidad) params.unidad = filtros.unidad
  if (filtros.fecha_desde) params.fecha_desde = filtros.fecha_desde
  if (filtros.fecha_hasta) params.fecha_hasta = filtros.fecha_hasta

  try {
    const { data } = await api.get('/admin/monitoreo/precios-mercados', { params })
    reportadosMarkers.value = data
  } catch (e) {
    console.error('Error loading precios-mercados:', e)
  }
}

async function loadPreciosEstado() {
  const params: any = {}
  if (filtros.producto_id) params.producto_id = filtros.producto_id
  if (filtros.subcategoria_id) params.subcategoria_id = filtros.subcategoria_id
  if (filtros.categoria_id) params.categoria_id = filtros.categoria_id
  if (filtros.tipo_precio) params.tipo_precio = filtros.tipo_precio
  if (filtros.unidad) params.unidad = filtros.unidad
  if (filtros.fecha_desde) params.fecha_desde = filtros.fecha_desde
  if (filtros.fecha_hasta) params.fecha_hasta = filtros.fecha_hasta

  try {
    const { data } = await api.get('/admin/monitoreo/precios-estado', { params })
    estadosData.value = data.estados || []
    kpis.value = data.kpis || {}
  } catch (e) {
    console.error('Error loading precios-estado:', e)
  }
}

async function loadMercadoPrecios(mercadoId: number) {
  const params: any = {}
  if (filtros.producto_id) params.producto_id = filtros.producto_id
  try {
    const { data } = await api.get(`/admin/monitoreo/mercado/${mercadoId}/precios`, { params })
    selectedMercado.value = { ...selectedMercado.value, ...data.mercado }
    popupPrecios.value = data.precios || []
  } catch {
    popupPrecios.value = []
  }
}

async function loadAll() {
  loading.value = true
  await Promise.all([loadMercados(), loadPreciosMercados(), loadPreciosEstado()])
  renderMarkers()
  lastUpdate.value = new Date().toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })
  loading.value = false
}

async function applyFilters() {
  loading.value = true
  await Promise.all([loadPreciosMercados(), loadPreciosEstado()])
  renderMarkers()
  lastUpdate.value = new Date().toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })
  loading.value = false
}

// ── Map rendering ──
function clearMarkers() {
  mapMarkers.forEach(m => m.remove())
  mapMarkers = []
}

function renderMarkers() {
  if (!map) return
  clearMarkers()

  // DENUE layer (gray)
  if (capas.denue) {
    denueMarkers.value.forEach(m => {
      if (!m.latitud || !m.longitud) return
      const el = document.createElement('div')
      el.className = 'marker-dot marker-denue'
      const marker = new mapboxgl.Marker({ element: el })
        .setLngLat([m.longitud, m.latitud])
        .addTo(map!)
      mapMarkers.push(marker)
    })
  }

  // Reported layer (green) — on top
  if (capas.reportados) {
    reportadosMarkers.value.forEach(m => {
      if (!m.latitud || !m.longitud) return
      const el = document.createElement('div')
      el.className = 'marker-dot marker-reported'
      el.addEventListener('click', () => {
        selectedMercado.value = m
        popupPrecios.value = []
        loadMercadoPrecios(m.mercado_id)
      })
      const marker = new mapboxgl.Marker({ element: el })
        .setLngLat([m.longitud, m.latitud])
        .addTo(map!)
      mapMarkers.push(marker)
    })
  }

  // Proposed layer (orange)
  if (capas.propuestos) {
    propuestosMarkers.value.forEach(m => {
      if (!m.latitud || !m.longitud) return
      const el = document.createElement('div')
      el.className = 'marker-dot marker-proposed'
      const marker = new mapboxgl.Marker({ element: el })
        .setLngLat([m.longitud, m.latitud])
        .addTo(map!)
      mapMarkers.push(marker)
    })
  }
}

function toggleLayers() {
  renderMarkers()
}

// ── Lifecycle ──
onMounted(async () => {
  await nextTick()
  if (!mapContainer.value) return

  mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || ''

  map = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/light-v11',
    center: [-102.5528, 23.6345],
    zoom: 4.8,
    attributionControl: false,
    projection: 'mercator'
  })

  map.addControl(new mapboxgl.NavigationControl(), 'top-right')
  map.addControl(new mapboxgl.FullscreenControl(), 'top-right')

  map.on('load', () => {
    map?.resize()
    loadCatalogos()
    loadAll()
  })
})

onBeforeUnmount(() => {
  clearMarkers()
  if (map) { map.remove(); map = null }
})
</script>

<style scoped>
/* ═══════════════════════════════════════════
   Layout
   ═══════════════════════════════════════════ */
.dashboard-layout { display: flex; min-height: 100vh; }

/* ── Sidebar (same as other views) ── */
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
.sidebar-brand__title { font-weight: 800; font-size: 1.15rem; letter-spacing: 0.04em; color: #fff; }
.sidebar-brand__sub { font-size: 0.68rem; font-weight: 500; color: rgba(255,255,255,0.6); text-transform: uppercase; }
.sidebar-nav { flex: 1; padding: 0.75rem 0.65rem; }
.sidebar-nav-label { font-size: 0.7rem; font-weight: 600; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.05em; padding: 0.5rem 0.85rem 0.35rem; }
.nav-item { display: flex; align-items: center; gap: 0.65rem; padding: 0.55rem 0.85rem; border-radius: 8px; color: rgba(255,255,255,0.75); text-decoration: none; font-weight: 500; font-size: 0.88rem; transition: all 0.2s; margin-bottom: 2px; }
.nav-item:hover { background: rgba(255,255,255,0.08); color: #fff; }
.nav-item.active { background: rgba(99,102,241,0.25); color: #fff; font-weight: 600; }
.sidebar-footer { padding: 0.85rem; border-top: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; }
.user-info { display: flex; align-items: center; gap: 0.65rem; }
.user-avatar { width: 34px; height: 34px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 600; font-size: 0.78rem; }
.user-details { display: flex; flex-direction: column; }
.user-name { font-weight: 600; font-size: 0.82rem; color: #fff; }
.user-role { font-size: 0.7rem; color: rgba(255,255,255,0.5); text-transform: capitalize; }
.btn-logout { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border: none; border-radius: 8px; background: transparent; color: rgba(255,255,255,0.5); cursor: pointer; }
.btn-logout:hover { background: rgba(255,255,255,0.1); color: #fff; }

/* ── Main ── */
.main-content {
  flex: 1; margin-left: 260px; padding: 0.75rem 1rem 1rem;
  background: #f1f5f9; min-height: 100vh; display: flex; flex-direction: column;
}

/* ── Top Bar ── */
.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  background: linear-gradient(135deg,#4f46e5,#6366f1); border-radius: 14px;
  padding: 0.9rem 1.5rem; margin-bottom: 0.75rem; box-shadow: 0 4px 20px rgba(79,70,229,0.18); flex-shrink: 0;
}
.top-bar__title { font-size: 1.2rem; font-weight: 700; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.top-bar__desc { font-size: 0.8rem; color: rgba(255,255,255,0.75); margin: 0.1rem 0 0; }
.top-bar__actions { display: flex; align-items: center; gap: 0.75rem; }
.last-update { font-size: 0.75rem; color: rgba(255,255,255,0.7); display: flex; align-items: center; gap: 4px; }
.btn-refresh {
  display: flex; align-items: center; gap: 5px; background: rgba(255,255,255,0.2);
  color: #fff; border: none; padding: 6px 14px; border-radius: 8px; font-size: 0.78rem;
  font-weight: 600; cursor: pointer; transition: background .15s;
}
.btn-refresh:hover { background: rgba(255,255,255,0.3); }
.btn-refresh:disabled { opacity: 0.6; cursor: not-allowed; }
@keyframes spin { to { transform: rotate(360deg); } }
.spinning { animation: spin .8s linear infinite; }

/* ═══════════════════════════════════════════
   3-column grid
   ═══════════════════════════════════════════ */
.monitor-grid {
  display: grid;
  grid-template-columns: 240px 1fr 300px;
  gap: 0.75rem;
  flex: 1;
  min-height: 0;
}

.panel {
  background: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  overflow: hidden;
}
.panel-title {
  font-size: 0.82rem; font-weight: 700; color: #1e293b; margin: 0;
  padding: 0.75rem 0.85rem 0.5rem; display: flex; align-items: center; gap: 6px;
  border-bottom: 1px solid #f1f5f9;
}

/* ── Left: Filters ── */
.panel-filters {
  overflow-y: auto; padding-bottom: 0.75rem;
}
.filter-group { padding: 0 0.85rem; margin-top: 0.6rem; }
.filter-group label { display: block; font-size: 0.7rem; font-weight: 600; color: #64748b; margin-bottom: 3px; text-transform: uppercase; letter-spacing: .03em; }
.filter-row { display: flex; gap: 4px; }
.f-input, .f-select {
  width: 100%; padding: 5px 8px; border: 1px solid #e2e8f0; border-radius: 6px;
  font-size: 0.78rem; color: #334155; background: #f8fafc;
  transition: border-color .15s;
}
.f-input:focus, .f-select:focus { outline: none; border-color: #6366f1; }
.f-select { appearance: auto; }

.layer-toggle {
  display: flex; align-items: center; gap: 6px; padding: 4px 0.85rem;
  font-size: 0.76rem; color: #475569; cursor: pointer;
}
.layer-toggle input { width: 14px; height: 14px; }
.layer-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

.btn-apply {
  display: flex; align-items: center; justify-content: center; gap: 5px;
  width: calc(100% - 1.7rem); margin: 0.75rem auto 0; padding: 7px;
  background: #6366f1; color: #fff; border: none; border-radius: 8px;
  font-size: 0.78rem; font-weight: 600; cursor: pointer;
}
.btn-apply:hover { background: #4f46e5; }
.btn-apply:disabled { opacity: 0.5; }

/* ── Center: Map ── */
.panel-map { position: relative; min-height: 400px; }
.map-container { position: absolute; top: 0; left: 0; right: 0; bottom: 0; width: 100%; height: 100%; border-radius: 12px; }

/* map markers */
:deep(.marker-dot) {
  width: 10px; height: 10px; border-radius: 50%; border: 1.5px solid #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.3); cursor: pointer;
}
:deep(.marker-denue) { background: #9ca3af; width: 7px; height: 7px; cursor: default; }
:deep(.marker-reported) { background: #22c55e; width: 12px; height: 12px; }
:deep(.marker-proposed) { background: #f59e0b; width: 9px; height: 9px; }

/* Popup overlay */
.map-popup-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.2); display: flex; align-items: flex-start;
  justify-content: center; padding-top: 60px; z-index: 10;
}
.map-popup {
  background: #fff; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  width: 420px; max-height: 70vh; overflow-y: auto;
}
.popup-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.85rem 1rem 0.5rem; border-bottom: 1px solid #f1f5f9;
}
.popup-header h4 { margin: 0; font-size: 0.95rem; color: #1e293b; }
.popup-close { background: none; border: none; font-size: 1.4rem; color: #94a3b8; cursor: pointer; }
.popup-meta { padding: 0.5rem 1rem; font-size: 0.75rem; color: #64748b; display: flex; flex-wrap: wrap; gap: 8px; }
.popup-meta span { display: flex; align-items: center; gap: 3px; }
.popup-precios { padding: 0 0.5rem 0.75rem; }
.popup-precios table { width: 100%; border-collapse: collapse; font-size: 0.75rem; }
.popup-precios th { text-align: left; padding: 4px 6px; color: #64748b; font-weight: 600; border-bottom: 1px solid #e2e8f0; }
.popup-precios td { padding: 4px 6px; border-bottom: 1px solid #f8fafc; }
.popup-empty { padding: 1.5rem; text-align: center; color: #94a3b8; font-size: 0.8rem; }
.price { font-weight: 700; color: #059669; }
.badge { font-size: 0.65rem; padding: 1px 6px; border-radius: 4px; font-weight: 600; }
.badge-men { background: #dbeafe; color: #2563eb; }
.badge-may { background: #fef3c7; color: #92400e; }

/* ── Right: Analytics ── */
.panel-analytics { overflow-y: auto; padding-bottom: 0.75rem; }

.kpis-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 6px;
  padding: 0.5rem 0.75rem;
}
.kpi-card {
  background: #f8fafc; border-radius: 8px; padding: 8px 10px; text-align: center;
}
.kpi-card:first-child { grid-column: 1 / -1; }
.kpi-label { font-size: 0.65rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; }
.kpi-value { font-size: 1.1rem; font-weight: 800; color: #1e293b; margin-top: 2px; }
.kpi-sub { font-size: 0.65rem; color: #64748b; }
.kpi-max .kpi-value { color: #ef4444; }
.kpi-min .kpi-value { color: #22c55e; }

.chart-wrap { height: 300px; padding: 0.5rem 0.75rem; }
.chart-empty {
  padding: 2rem; text-align: center; color: #cbd5e1;
  display: flex; flex-direction: column; align-items: center; gap: 8px;
}
.chart-empty p { font-size: 0.78rem; }

.ranking { padding: 0 0.75rem; }
.ranking h4 { font-size: 0.78rem; font-weight: 700; color: #475569; margin: 0.5rem 0 0.3rem; }
.ranking-table { width: 100%; border-collapse: collapse; font-size: 0.72rem; }
.ranking-table th { text-align: left; padding: 3px 4px; color: #94a3b8; font-weight: 600; border-bottom: 1px solid #e2e8f0; }
.ranking-table td { padding: 3px 4px; border-bottom: 1px solid #f8fafc; }

/* ── Mapbox overrides ── */
:deep(.mapboxgl-ctrl-top-right) { top: 12px; right: 12px; }
:deep(.mapboxgl-ctrl-group) { border-radius: 10px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important; overflow: hidden; }
:deep(.mapboxgl-ctrl-group button) { width: 36px !important; height: 36px !important; }
:deep(.mapboxgl-ctrl-fullscreen) { margin-top: 8px; }

/* ═══════════════════════════════════════════
   Responsive
   ═══════════════════════════════════════════ */
@media (max-width: 1200px) {
  .monitor-grid { grid-template-columns: 200px 1fr 260px; }
}
@media (max-width: 900px) {
  .sidebar { width: 68px; }
  .sidebar-brand, .nav-item span, .user-details, .sidebar-nav-label { display: none; }
  .sidebar-header { justify-content: center; padding: 1rem 0.5rem; }
  .sidebar-logo { width: 36px; height: 36px; }
  .nav-item { justify-content: center; padding: 0.6rem 0.5rem; }
  .sidebar-footer { flex-direction: column; gap: 0.5rem; }
  .user-info { display: none; }
  .main-content { margin-left: 68px; }
  .monitor-grid { grid-template-columns: 1fr; grid-template-rows: auto 400px auto; }
  .panel-filters { display: grid; grid-template-columns: 1fr 1fr 1fr; }
}
</style>
