<template>
  <div class="app-layout">
    <AppNavbar />
    <AppSidebar />

    <main class="main-content" @click="closeSidebar">
      <!-- ═══ MIS MERCADOS ═══ -->
      <div v-if="!selectedMercado" class="mercados-section">
        <div class="section-header">
          <Store :size="24" />
          <h1>Mis Mercados</h1>
        </div>

        <!-- Agregar mercado -->
        <div class="add-mercado">
          <input
            v-model="newMercadoNombre"
            type="text"
            placeholder="Nombre del mercado..."
            class="input"
            maxlength="200"
            @input="newMercadoNombre = toUpper(newMercadoNombre)"
            @keyup.enter="addMercado"
          />
          <button class="btn btn--primary" :disabled="!newMercadoNombre.trim() || addingMercado" @click="addMercado">
            <Plus :size="18" />
            <span>Agregar</span>
          </button>
        </div>

        <!-- Lista de mercados -->
        <div v-if="loadingMercados" class="loading-state">
          <div class="spinner"></div>
          <p>Cargando mercados...</p>
        </div>

        <div v-else-if="mercados.length === 0" class="empty-state">
          <Store :size="48" />
          <p>No tienes mercados registrados</p>
          <p class="empty-state__hint">Agrega un mercado para comenzar a capturar precios</p>
        </div>

        <div v-else class="mercados-list">
          <div
            v-for="m in mercados"
            :key="m.id"
            class="mercado-card"
            @click="selectMercado(m)"
          >
            <div class="mercado-card__info">
              <h3>{{ m.nombre }}</h3>
              <span class="mercado-card__date">{{ formatDate(m.created_at) }}</span>
            </div>
            <div class="mercado-card__actions">
              <button class="btn-icon btn-icon--danger" @click.stop="deleteMercado(m.id)" title="Eliminar mercado">
                <Trash2 :size="18" />
              </button>
              <ChevronRight :size="20" class="mercado-card__arrow" />
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ CAPTURA DE PRECIOS ═══ -->
      <div v-else class="captura-section">
        <!-- Header -->
        <div class="captura-header">
          <button class="btn-back" @click="backToMercados">
            <ArrowLeft :size="20" />
            <span>Volver</span>
          </button>
          <div class="captura-header__title">
            <Store :size="20" />
            <h2>{{ selectedMercado.nombre }}</h2>
          </div>
        </div>

        <!-- Toggle Menudeo / Mayoreo -->
        <div class="tipo-precio-toggle">
          <span class="toggle-label">Tipo de precio:</span>
          <div class="toggle-pills">
            <button
              class="toggle-pill"
              :class="{ 'toggle-pill--active': tipoPrecio === 'MENUDEO' }"
              @click="tipoPrecio = 'MENUDEO'"
            >Menudeo</button>
            <button
              class="toggle-pill"
              :class="{ 'toggle-pill--active': tipoPrecio === 'MAYOREO' }"
              @click="tipoPrecio = 'MAYOREO'"
            >Mayoreo</button>
          </div>
        </div>

        <!-- Categoría -->
        <div class="filter-section">
          <label class="filter-label">Categoría</label>
          <p v-if="!selectedCategoria" class="step-hint">1. Selecciona una categoría para comenzar</p>
          <div class="category-tabs">
            <button
              v-for="cat in categorias"
              :key="cat.id"
              class="cat-tab"
              :class="{ 'cat-tab--active': selectedCategoria === cat.id }"
              @click="onCategoriaChange(cat.id)"
            >
              <Wheat v-if="cat.id === 'AGRICOLA'" :size="18" />
              <Beef v-else :size="18" />
              <span>{{ cat.nombre }}</span>
            </button>
          </div>
        </div>

        <!-- Subcategoría -->
        <div v-if="selectedCategoria" class="filter-section">
          <label class="filter-label">Subcategoría</label>
          <p v-if="!selectedSubcategoria" class="step-hint">2. Selecciona una subcategoría</p>
          <select v-model="selectedSubcategoria" class="input" @change="onSubcategoriaChange">
            <option value="">Selecciona subcategoría...</option>
            <option v-for="sub in subcategorias" :key="sub.id" :value="sub.id">
              {{ sub.nombre }}
            </option>
          </select>
        </div>

        <!-- Agregar producto -->
        <div v-if="selectedSubcategoria" class="add-product-section">
          <label class="filter-label">Agregar producto</label>
          <p v-if="!selectedProductoId" class="step-hint">3. Selecciona un producto y presiona <strong>+</strong> para agregarlo</p>
          <div class="add-product-row">
            <select v-model="selectedProductoId" class="input input--grow">
              <option value="">Buscar producto...</option>
              <option
                v-for="p in availableProductos"
                :key="p.id"
                :value="p.id"
              >{{ p.nombre }}</option>
            </select>
            <button
              class="btn btn--primary btn--icon-only"
              :disabled="!selectedProductoId"
              @click="addProduct"
              title="Agregar producto"
            >
              <Plus :size="20" />
            </button>
          </div>
          <!-- Tip: múltiples productos -->
          <div class="multi-product-tip">
            <Info :size="14" />
            <span>Puedes agregar varios productos antes de guardar el reporte</span>
          </div>
        </div>

        <!-- Tabla de captura -->
        <div v-if="capturaItems.length > 0" class="captura-table-section">
          <div class="captura-table-header">
            <h3>
              <ClipboardList :size="18" />
              Productos seleccionados ({{ capturaItems.length }})
            </h3>
          </div>

          <div class="captura-cards">
            <div v-for="(item, idx) in capturaItems" :key="idx" class="captura-card">
              <!-- Icono de categoría -->
              <div class="captura-card__cat-icon" :class="item.categoria_id === 'AGRICOLA' ? 'cat-icon--agricola' : 'cat-icon--pecuario'">
                <Wheat v-if="item.categoria_id === 'AGRICOLA'" :size="12" />
                <Beef v-else :size="12" />
              </div>
              <div class="captura-card__content">
                <div class="captura-card__header">
                  <span class="captura-card__name">{{ item.producto_nombre }}</span>
                  <button class="captura-card__delete" @click="removeProduct(idx)" title="Quitar">
                    <X :size="14" />
                  </button>
                </div>
                <div class="captura-card__fields">
                  <div class="captura-field">
                    <label>Precio (MXN)</label>
                    <input
                      type="number"
                      v-model.number="item.precio"
                      class="input input--price"
                      placeholder="0.00"
                      min="0.01"
                      step="0.01"
                      @blur="validatePrice(item)"
                    />
                  </div>
                  <div class="captura-field">
                    <label>Unidad</label>
                    <select v-model="item.unidad" class="input">
                      <option value="">Seleccionar...</option>
                      <option v-for="u in item.unidades_disponibles" :key="u" :value="u">
                        {{ u }}
                      </option>
                    </select>
                  </div>
                </div>
                <p v-if="item.precio !== null && item.precio <= 0" class="field-error">
                  El precio debe ser mayor a 0
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Resumen y guardar -->
        <div v-if="capturaItems.length > 0" class="captura-footer">
          <div class="captura-summary">
            <span>{{ validItems }} de {{ capturaItems.length }} productos listos</span>
          </div>
          <button
            class="btn btn--primary btn--full"
            :disabled="!canSave || saving"
            @click="saveReporte"
          >
            <Save :size="18" />
            <span>{{ saving ? 'Guardando...' : 'Guardar reporte' }}</span>
          </button>
        </div>

        <!-- Reportes anteriores -->
        <div v-if="reportes.length > 0" class="reportes-section">
          <h3 class="reportes-title">
            <FileText :size="18" />
            Reportes anteriores
          </h3>
          <div
            v-for="r in reportes"
            :key="r.id"
            class="reporte-card"
          >
            <div class="reporte-card__main" @click="toggleReporteDetalle(r.id)">
              <div class="reporte-card__left">
                <span class="reporte-card__tipo" :class="r.tipo_precio === 'MENUDEO' ? 'badge--blue' : 'badge--orange'">
                  {{ r.tipo_precio }}
                </span>
                <div class="reporte-card__meta">
                  <span class="reporte-card__fecha">{{ r.fecha }}</span>
                  <span class="reporte-card__count">{{ r.total_productos }} productos</span>
                </div>
              </div>
              <button class="reporte-card__toggle" :class="{ 'toggle--open': expandedReporte === r.id }">
                <ChevronDown :size="20" />
              </button>
            </div>
            <!-- Detalle expandido -->
            <div v-if="expandedReporte === r.id && reporteDetalle" class="reporte-detalle">
              <div v-for="d in reporteDetalle.items" :key="d.id" class="detalle-row">
                <span class="detalle-row__name">{{ d.producto_nombre }}</span>
                <span class="detalle-row__price">${{ d.precio.toFixed(2) }}</span>
                <span class="detalle-row__unit">{{ d.unidad }}</span>
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
import type { Mercado, Categoria, Subcategoria, Producto, Unidad, CapturaItem, ReporteOut, ReporteDetalleOut } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppToast from '@/components/AppToast.vue'
import {
  Store, Plus, Trash2, ChevronRight, ArrowLeft,
  Wheat, Beef, ClipboardList, X, Save, FileText,
  ChevronDown, Info
} from 'lucide-vue-next'

const ui = useUiStore()

// ── State: Mercados ──
const mercados = ref<Mercado[]>([])
const selectedMercado = ref<Mercado | null>(null)
const newMercadoNombre = ref('')
const loadingMercados = ref(false)
const addingMercado = ref(false)

// ── State: Catálogos ──
const categorias = ref<Categoria[]>([])
const subcategorias = ref<Subcategoria[]>([])
const productos = ref<Producto[]>([])
const unidades = ref<Unidad[]>([])
const selectedCategoria = ref('')
const selectedSubcategoria = ref('')
const selectedProductoId = ref<number | ''>('')

// ── State: Captura ──
const tipoPrecio = ref<'MENUDEO' | 'MAYOREO'>('MENUDEO')
const capturaItems = ref<CapturaItem[]>([])
const saving = ref(false)

// ── State: Reportes ──
const reportes = ref<ReporteOut[]>([])
const expandedReporte = ref<number | null>(null)
const reporteDetalle = ref<ReporteDetalleOut | null>(null)

// ── Helpers ──
function toUpper(v: string): string {
  return v.toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' })
}

function closeSidebar() {
  if (ui.sidebarOpen) ui.closeSidebar()
}

// ── Computed ──
const availableProductos = computed(() => {
  const addedIds = new Set(capturaItems.value.map(i => i.producto_id))
  return productos.value.filter(p => !addedIds.has(p.id))
})

const validItems = computed(() =>
  capturaItems.value.filter(i => i.precio && i.precio > 0 && i.unidad).length
)

const canSave = computed(() =>
  capturaItems.value.length > 0 && validItems.value === capturaItems.value.length
)

// ── Mercados CRUD ──
async function loadMercados() {
  loadingMercados.value = true
  try {
    mercados.value = await mercadosService.getMercados()
  } catch {
    ui.showToast('Error al cargar mercados', 'error')
  } finally {
    loadingMercados.value = false
  }
}

async function addMercado() {
  const nombre = newMercadoNombre.value.trim()
  if (!nombre) return
  addingMercado.value = true
  try {
    const m = await mercadosService.createMercado(nombre)
    mercados.value.push(m)
    mercados.value.sort((a, b) => a.nombre.localeCompare(b.nombre))
    newMercadoNombre.value = ''
    ui.showToast('Mercado agregado', 'success')
  } catch (e: any) {
    const msg = e.response?.data?.detail || 'Error al agregar mercado'
    ui.showToast(msg, 'error')
  } finally {
    addingMercado.value = false
  }
}

async function deleteMercado(id: number) {
  if (!confirm('¿Eliminar este mercado? Se eliminarán también sus reportes.')) return
  try {
    await mercadosService.deleteMercado(id)
    mercados.value = mercados.value.filter(m => m.id !== id)
    ui.showToast('Mercado eliminado', 'success')
  } catch {
    ui.showToast('Error al eliminar mercado', 'error')
  }
}

async function selectMercado(m: Mercado) {
  selectedMercado.value = m
  capturaItems.value = []
  selectedCategoria.value = ''
  selectedSubcategoria.value = ''
  selectedProductoId.value = ''
  reportes.value = []
  expandedReporte.value = null
  reporteDetalle.value = null

  // Load categorias + reportes
  try {
    if (categorias.value.length === 0) {
      categorias.value = await mercadosService.getCategorias()
    }
    reportes.value = await mercadosService.getReportes(m.id)
  } catch {
    ui.showToast('Error al cargar datos', 'error')
  }
}

function backToMercados() {
  selectedMercado.value = null
  capturaItems.value = []
}

// ── Filtros ──
async function onCategoriaChange(catId: string) {
  selectedCategoria.value = catId
  selectedSubcategoria.value = ''
  selectedProductoId.value = ''
  subcategorias.value = []
  productos.value = []
  unidades.value = []
  try {
    subcategorias.value = await mercadosService.getSubcategorias(catId)
  } catch {
    ui.showToast('Error al cargar subcategorías', 'error')
  }
}

async function onSubcategoriaChange() {
  const subId = selectedSubcategoria.value
  selectedProductoId.value = ''
  productos.value = []
  unidades.value = []
  if (!subId) return
  try {
    const [prods, units] = await Promise.all([
      mercadosService.getProductos(subId),
      mercadosService.getUnidades(subId)
    ])
    productos.value = prods
    unidades.value = units
  } catch {
    ui.showToast('Error al cargar productos', 'error')
  }
}

// ── Captura ──
function addProduct() {
  const pid = selectedProductoId.value
  if (!pid) return
  const prod = productos.value.find(p => p.id === pid)
  if (!prod) return

  const unitNames = unidades.value.map(u => u.nombre)

  capturaItems.value.push({
    producto_id: prod.id,
    producto_nombre: prod.nombre,
    subcategoria_id: prod.subcategoria_id,
    categoria_id: selectedCategoria.value,
    precio: null,
    unidad: unitNames.length === 1 ? unitNames[0] : '',
    unidades_disponibles: unitNames
  })
  selectedProductoId.value = ''
}

function removeProduct(idx: number) {
  capturaItems.value.splice(idx, 1)
}

function validatePrice(item: CapturaItem) {
  if (item.precio !== null && item.precio !== 0) {
    item.precio = Math.round(item.precio * 100) / 100
  }
}

async function saveReporte() {
  if (!canSave.value || !selectedMercado.value) return

  // Check duplicates: producto + unidad
  const seen = new Set<string>()
  for (const item of capturaItems.value) {
    const key = `${item.producto_id}-${item.unidad}`
    if (seen.has(key)) {
      ui.showToast(`Producto duplicado con la misma unidad: ${item.producto_nombre}`, 'error')
      return
    }
    seen.add(key)
  }

  saving.value = true
  try {
    await mercadosService.createReporte({
      mercado_id: selectedMercado.value.id,
      tipo_precio: tipoPrecio.value,
      items: capturaItems.value.map(i => ({
        producto_id: i.producto_id,
        precio: i.precio!,
        unidad: i.unidad
      }))
    })
    ui.showToast('Reporte guardado exitosamente', 'success')
    capturaItems.value = []
    reportes.value = await mercadosService.getReportes(selectedMercado.value.id)
  } catch (e: any) {
    const msg = e.response?.data?.detail || 'Error al guardar reporte'
    ui.showToast(msg, 'error')
  } finally {
    saving.value = false
  }
}

// ── Reportes ──
async function toggleReporteDetalle(id: number) {
  if (expandedReporte.value === id) {
    expandedReporte.value = null
    reporteDetalle.value = null
    return
  }
  expandedReporte.value = id
  reporteDetalle.value = null
  try {
    reporteDetalle.value = await mercadosService.getReporte(id)
  } catch {
    ui.showToast('Error al cargar detalle', 'error')
  }
}

onMounted(() => {
  loadMercados()
})
</script>

<style scoped>
/* ── Layout ── */
.mercados-section,
.captura-section {
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

/* ── Add Mercado ── */
.add-mercado {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.input {
  width: 100%;
  padding: 0.65rem 0.75rem;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
  background: #fff;
  box-sizing: border-box;
}
.input:focus {
  outline: none;
  border-color: #1B5E20;
}
.input--grow {
  flex: 1;
}
.input--price {
  max-width: 120px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.65rem 1rem;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.btn--primary {
  background: #1B5E20;
  color: #fff;
}
.btn--primary:hover:not(:disabled) {
  background: #2E7D32;
}
.btn--primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn--full {
  width: 100%;
  justify-content: center;
}
.btn--icon-only {
  padding: 0.65rem;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: transparent;
}
.btn-icon--danger {
  color: #c62828;
}
.btn-icon--danger:hover {
  background: #ffebee;
}
.btn-icon--sm {
  width: 28px;
  height: 28px;
}

/* ── Loading / Empty ── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem 1rem;
  color: #888;
}
.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e0e0e0;
  border-top-color: #1B5E20;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 0.75rem;
}
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #888;
}
.empty-state svg {
  color: #ccc;
  margin-bottom: 0.75rem;
}
.empty-state p {
  margin: 0.25rem 0;
}
.empty-state__hint {
  font-size: 0.85rem;
  color: #aaa;
}

/* ── Mercado Cards ── */
.mercados-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mercado-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border: 1.5px solid #e8f5e9;
  border-radius: 12px;
  padding: 0.85rem 1rem;
  cursor: pointer;
  transition: all 0.2s;
}
.mercado-card:hover {
  border-color: #1B5E20;
  box-shadow: 0 2px 8px rgba(27,94,32,0.1);
}
.mercado-card__info h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
}
.mercado-card__date {
  font-size: 0.8rem;
  color: #999;
}
.mercado-card__actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.mercado-card__arrow {
  color: #1B5E20;
}

/* ── Captura Header ── */
.captura-header {
  margin-bottom: 1rem;
}
.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: none;
  border: none;
  color: #1B5E20;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.25rem 0;
  margin-bottom: 0.5rem;
}
.btn-back:hover {
  text-decoration: underline;
}
.captura-header__title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #1B5E20;
}
.captura-header__title h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
}

/* ── Toggle Tipo Precio ── */
.tipo-precio-toggle {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}
.toggle-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #555;
}
.toggle-pills {
  display: flex;
  border-radius: 10px;
  overflow: hidden;
  border: 1.5px solid #e0e0e0;
}
.toggle-pill {
  padding: 0.5rem 1.25rem;
  border: none;
  background: #f5f5f5;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}
.toggle-pill--active {
  background: #1B5E20;
  color: #fff;
}

/* ── Filters ── */
.filter-section {
  margin-bottom: 1rem;
}
.filter-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
  margin-bottom: 0.35rem;
}

/* Hints de paso */
.step-hint {
  font-size: 0.8rem;
  color: #999;
  font-style: italic;
  margin: 0 0 0.5rem;
  padding-left: 0.25rem;
}
.step-hint strong {
  color: #1B5E20;
  font-style: normal;
}

.category-tabs {
  display: flex;
  gap: 0.5rem;
}
.cat-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.6rem 1rem;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  background: #fff;
  font-size: 0.9rem;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}
.cat-tab:hover {
  border-color: #1B5E20;
}
.cat-tab--active {
  background: #e8f5e9;
  border-color: #1B5E20;
  color: #1B5E20;
}

/* ── Add Product ── */
.add-product-section {
  margin-bottom: 1.25rem;
}
.add-product-row {
  display: flex;
  gap: 0.5rem;
}

/* Tip múltiples productos */
.multi-product-tip {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.65rem;
  padding: 0.5rem 0.75rem;
  background: #fff8e1;
  border-radius: 8px;
  border-left: 3px solid #ffc107;
}
.multi-product-tip svg {
  color: #f9a825;
  flex-shrink: 0;
}
.multi-product-tip span {
  font-size: 0.8rem;
  color: #5d4037;
  line-height: 1.3;
}

/* ── Capture Table ── */
.captura-table-section {
  margin-bottom: 1.25rem;
}
.captura-table-header {
  margin-bottom: 0.75rem;
}
.captura-table-header h3 {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.captura-cards {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.captura-card {
  position: relative;
  background: #fff;
  border: 1.5px solid #e8f5e9;
  border-radius: 14px;
  padding: 0.85rem 0.85rem 0.85rem 2.5rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* Icono de categoría */
.captura-card__cat-icon {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.cat-icon--agricola {
  background: #e8f5e9;
  color: #1B5E20;
}
.cat-icon--pecuario {
  background: #fce4ec;
  color: #d81b60;
}

.captura-card__content {
  width: 100%;
}
.captura-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}
.captura-card__name {
  font-weight: 600;
  font-size: 0.95rem;
  color: #1B5E20;
}
.captura-card__delete {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 50%;
  background: #ffebee;
  color: #c62828;
  cursor: pointer;
  transition: all 0.2s;
}
.captura-card__delete:hover {
  background: #ffcdd2;
}
.captura-card__fields {
  display: flex;
  gap: 0.5rem;
}
.captura-field {
  flex: 1;
}
.captura-field label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #888;
  margin-bottom: 0.2rem;
}

.field-error {
  color: #c62828;
  font-size: 0.78rem;
  margin: 0.25rem 0 0;
}

/* ── Captura Footer ── */
.captura-footer {
  margin-bottom: 1.5rem;
}
.captura-summary {
  text-align: center;
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.5rem;
}

/* ── Reportes ── */
.reportes-section {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1.5px solid #e8f5e9;
}
.reportes-title {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.75rem;
}

.reporte-card {
  background: #fff;
  border: 1.5px solid #e8f5e9;
  border-radius: 12px;
  margin-bottom: 0.65rem;
  overflow: hidden;
  transition: all 0.2s;
}
.reporte-card:hover {
  border-color: #1B5E20;
}

.reporte-card__main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1rem;
  cursor: pointer;
}

.reporte-card__left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.reporte-card__meta {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.reporte-card__tipo {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
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
.reporte-card__fecha {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}
.reporte-card__count {
  font-size: 0.8rem;
  color: #888;
}

.reporte-card__toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: #f5f5f5;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}
.reporte-card__toggle:hover {
  background: #e8f5e9;
  color: #1B5E20;
}
.reporte-card__toggle.toggle--open {
  background: #1B5E20;
  color: #fff;
  transform: rotate(180deg);
}

.reporte-detalle {
  padding: 0.75rem 1rem;
  background: #fafafa;
  border-top: 1px solid #e8f5e9;
}
.detalle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.45rem 0;
  font-size: 0.85rem;
  border-bottom: 1px solid #eee;
}
.detalle-row:last-child {
  border-bottom: none;
}
.detalle-row__name {
  flex: 1;
  color: #333;
}
.detalle-row__price {
  font-weight: 600;
  color: #1B5E20;
  margin: 0 0.75rem;
}
.detalle-row__unit {
  color: #888;
  font-size: 0.8rem;
  min-width: 70px;
  text-align: right;
}

/* ── Responsive ── */
@media (max-width: 480px) {
  .captura-card__fields {
    flex-direction: column;
  }
  .tipo-precio-toggle {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
