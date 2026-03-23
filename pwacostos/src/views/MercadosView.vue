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
          <select v-model="selectedSubcategoria" class="input" @change="onSubcategoriaChange">
            <option value="">Selecciona subcategoría...</option>
            <option v-for="sub in subcategorias" :key="sub.id" :value="sub.id">
              {{ sub.nombre }}
            </option>
          </select>
        </div>

        <!-- Producto -->
        <div v-if="selectedSubcategoria" class="filter-section">
          <label class="filter-label">Producto</label>
          <select v-model="selectedProductoId" class="input" @change="onProductoChange">
            <option value="">Selecciona producto...</option>
            <option v-for="p in productos" :key="p.id" :value="p.id">
              {{ p.nombre }}
            </option>
          </select>
        </div>

        <!-- Formulario de precio (aparece al seleccionar producto) -->
        <div v-if="selectedProducto" class="precio-form">
          <div class="precio-form__header">
            <div class="precio-form__cat-icon" :class="selectedCategoria === 'AGRICOLA' ? 'cat-icon--agricola' : 'cat-icon--pecuario'">
              <Wheat v-if="selectedCategoria === 'AGRICOLA'" :size="14" />
              <Beef v-else :size="14" />
            </div>
            <span class="precio-form__name">{{ selectedProducto.nombre }}</span>
          </div>
          <div class="precio-form__fields">
            <div class="precio-form__field">
              <label>Precio (MXN)</label>
              <input
                ref="precioInput"
                type="number"
                v-model.number="precioValue"
                class="input input--price"
                placeholder="0.00"
                min="0.01"
                step="0.01"
              />
            </div>
            <div class="precio-form__field">
              <label>Unidad</label>
              <select v-model="unidadValue" class="input">
                <option value="">Seleccionar...</option>
                <option v-for="u in unidades" :key="u.id" :value="u.nombre">
                  {{ u.nombre }}
                </option>
              </select>
            </div>
          </div>
          <button
            class="btn btn--primary btn--full"
            :disabled="!canSavePrecio || saving"
            @click="savePrecio"
          >
            <Save :size="18" />
            <span>{{ saving ? 'Guardando...' : 'Guardar precio' }}</span>
          </button>
        </div>

        <!-- Historial de precios registrados -->
        <div v-if="historial.length > 0" class="historial-section">
          <h3 class="historial-title">
            <FileText :size="18" />
            Precios registrados ({{ historial.length }})
          </h3>
          <div class="historial-scroll">
            <div v-for="h in historial" :key="h.id" class="historial-row">
              <div class="historial-row__cat-icon" :class="h.categoria_id === 'AGRICOLA' ? 'cat-icon--agricola' : 'cat-icon--pecuario'">
                <Wheat v-if="h.categoria_id === 'AGRICOLA'" :size="12" />
                <Beef v-else :size="12" />
              </div>
              <div class="historial-row__left">
                <span class="historial-row__name">{{ h.producto_nombre }}</span>
                <span class="historial-row__sub">{{ h.subcategoria_nombre }}</span>
              </div>
              <div class="historial-row__right">
                <span class="historial-row__price">${{ h.precio.toFixed(2) }}</span>
                <span class="historial-row__unit">{{ h.unidad }}</span>
                <span class="historial-row__badge" :class="h.tipo_precio === 'MENUDEO' ? 'badge--blue' : 'badge--orange'">
                  {{ h.tipo_precio === 'MENUDEO' ? 'Men' : 'May' }}
                </span>
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useUiStore } from '@/stores/ui'
import { mercadosService } from '@/services/mercados.service'
import type { Mercado, Categoria, Subcategoria, Producto, Unidad, PrecioHistorialItem } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppToast from '@/components/AppToast.vue'
import {
  Store, Plus, Trash2, ChevronRight, ArrowLeft,
  Wheat, Beef, Save, FileText
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

// ── State: Precio individual ──
const tipoPrecio = ref<'MENUDEO' | 'MAYOREO'>('MENUDEO')
const precioValue = ref<number | null>(null)
const unidadValue = ref('')
const saving = ref(false)
const precioInput = ref<HTMLInputElement | null>(null)

// ── State: Historial ──
const historial = ref<PrecioHistorialItem[]>([])

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
const selectedProducto = computed(() => {
  if (!selectedProductoId.value) return null
  return productos.value.find(p => p.id === selectedProductoId.value) || null
})

const canSavePrecio = computed(() =>
  precioValue.value !== null && precioValue.value > 0 && unidadValue.value !== ''
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
  if (!confirm('¿Eliminar este mercado? Se eliminarán también sus precios.')) return
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
  selectedCategoria.value = ''
  selectedSubcategoria.value = ''
  selectedProductoId.value = ''
  precioValue.value = null
  unidadValue.value = ''
  historial.value = []

  try {
    if (categorias.value.length === 0) {
      categorias.value = await mercadosService.getCategorias()
    }
    historial.value = await mercadosService.getPreciosHistorial(m.id)
  } catch {
    ui.showToast('Error al cargar datos', 'error')
  }
}

function backToMercados() {
  selectedMercado.value = null
}

// ── Filtros ──
async function onCategoriaChange(catId: string) {
  selectedCategoria.value = catId
  selectedSubcategoria.value = ''
  selectedProductoId.value = ''
  subcategorias.value = []
  productos.value = []
  unidades.value = []
  precioValue.value = null
  unidadValue.value = ''
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
  precioValue.value = null
  unidadValue.value = ''
  if (!subId) return
  try {
    const [prods, units] = await Promise.all([
      mercadosService.getProductos(subId),
      mercadosService.getUnidades(subId, tipoPrecio.value)
    ])
    productos.value = prods
    unidades.value = units
  } catch {
    ui.showToast('Error al cargar productos', 'error')
  }
}

function onProductoChange() {
  precioValue.value = null
  unidadValue.value = unidades.value.length === 1 ? unidades.value[0].nombre : ''
  nextTick(() => {
    precioInput.value?.focus()
  })
}

// Recargar unidades al cambiar tipo de precio
watch(tipoPrecio, async () => {
  const subId = selectedSubcategoria.value
  if (!subId) return
  try {
    unidades.value = await mercadosService.getUnidades(subId, tipoPrecio.value)
    // Resetear unidad si ya no está disponible
    const unitNames = unidades.value.map(u => u.nombre)
    if (!unitNames.includes(unidadValue.value)) {
      unidadValue.value = unitNames.length === 1 ? unitNames[0] : ''
    }
  } catch {
    ui.showToast('Error al cargar unidades', 'error')
  }
})

// ── Guardar precio individual ──
async function savePrecio() {
  if (!canSavePrecio.value || !selectedMercado.value || !selectedProductoId.value) return

  saving.value = true
  try {
    const saved = await mercadosService.savePrecioIndividual({
      mercado_id: selectedMercado.value.id,
      tipo_precio: tipoPrecio.value,
      producto_id: selectedProductoId.value as number,
      precio: Math.round(precioValue.value! * 100) / 100,
      unidad: unidadValue.value
    })
    historial.value.unshift(saved)
    ui.showToast(`${saved.producto_nombre} — $${saved.precio.toFixed(2)} guardado`, 'success')

    // Limpiar para el siguiente producto
    precioValue.value = null
    unidadValue.value = unidades.value.length === 1 ? unidades.value[0].nombre : ''
    selectedProductoId.value = ''
  } catch (e: any) {
    const msg = e.response?.data?.detail || 'Error al guardar precio'
    ui.showToast(msg, 'error')
  } finally {
    saving.value = false
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

/* ── Precio Form (individual) ── */
.precio-form {
  background: #fff;
  border: 1.5px solid #e8f5e9;
  border-radius: 14px;
  padding: 1rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.precio-form__header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.precio-form__cat-icon {
  width: 28px;
  height: 28px;
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
.precio-form__name {
  font-weight: 700;
  font-size: 1.05rem;
  color: #1B5E20;
}
.precio-form__fields {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.85rem;
}
.precio-form__field {
  flex: 1;
}
.precio-form__field label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #888;
  margin-bottom: 0.2rem;
}

/* ── Historial de precios ── */
.historial-section {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1.5px solid #e8f5e9;
}
.historial-title {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.75rem;
}
.historial-scroll {
  max-height: 360px;
  overflow-y: auto;
  background: #fff;
  border: 1.5px solid #e8f5e9;
  border-radius: 12px;
}
.historial-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 0.85rem;
  border-bottom: 1px solid #f0f0f0;
  gap: 0.5rem;
}
.historial-row:last-child {
  border-bottom: none;
}
.historial-row__cat-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.historial-row__left {
  display: flex;
  flex-direction: column;
  gap: 0.05rem;
  min-width: 0;
  flex: 1;
}
.historial-row__name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.historial-row__sub {
  font-size: 0.75rem;
  color: #999;
}
.historial-row__right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}
.historial-row__price {
  font-weight: 700;
  color: #1B5E20;
  font-size: 0.9rem;
}
.historial-row__unit {
  color: #888;
  font-size: 0.78rem;
  min-width: 55px;
  text-align: right;
}
.historial-row__badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
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

/* ── Responsive ── */
@media (max-width: 480px) {
  .precio-form__fields {
    flex-direction: column;
  }
  .tipo-precio-toggle {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
