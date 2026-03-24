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

        <!-- Botón agregar mercado -->
        <button class="btn btn--primary btn--full" @click="showCatalogo = true" style="margin-bottom: 1.25rem;">
          <Search :size="18" />
          <span>Buscar y agregar mercado</span>
        </button>

        <!-- Lista de mercados -->
        <div v-if="loadingMercados" class="loading-state">
          <div class="spinner"></div>
          <p>Cargando mercados...</p>
        </div>

        <div v-else-if="mercados.length === 0" class="empty-state">
          <Store :size="48" />
          <p>No tienes mercados registrados</p>
          <p class="empty-state__hint">Busca un mercado del catálogo para comenzar a capturar precios</p>
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
              <div class="mercado-card__meta">
                <span class="mercado-card__badge" :class="tipoBadgeClass(m.tipo)">{{ formatTipo(m.tipo) }}</span>
                <span class="mercado-card__loc">
                  <MapPin :size="12" />
                  {{ m.municipio }}, {{ m.entidad }}
                </span>
              </div>
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

      <!-- ═══ MODAL CATÁLOGO ═══ -->
      <div v-if="showCatalogo" class="modal-overlay" @click.self="showCatalogo = false">
        <div class="modal-catalogo">
          <div class="modal-header">
            <h2><Search :size="20" /> Buscar Mercado</h2>
            <button class="btn-icon" @click="showCatalogo = false"><X :size="22" /></button>
          </div>

          <!-- Filtros -->
          <div class="catalogo-filtros">
            <div class="filter-row">
              <select v-model="filtroEntidad" class="input" @change="onEntidadChange">
                <option value="">Todos los estados...</option>
                <option v-for="e in entidades" :key="e" :value="e">{{ e }}</option>
              </select>
            </div>
            <div class="filter-row">
              <select v-model="filtroMunicipio" class="input" :disabled="!filtroEntidad" @change="searchCatalogo">
                <option value="">Todos los municipios...</option>
                <option v-for="m in municipiosCat" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            <div class="filter-row">
              <input
                v-model="filtroNombre"
                type="text"
                class="input"
                placeholder="Buscar por nombre..."
                @input="onNombreInput"
              />
            </div>
          </div>

          <!-- Resultados -->
          <div v-if="searchingCatalogo" class="loading-state" style="padding: 2rem;">
            <div class="spinner"></div>
            <p>Buscando mercados...</p>
          </div>

          <div v-else-if="catalogoResults.length === 0 && hasSearched" class="empty-state" style="padding: 2rem;">
            <p>No se encontraron mercados</p>
            <button class="btn btn--outline btn--wrap" style="margin-top: 0.75rem;" @click="showCatalogo = false; showProponer = true">
              <Plus :size="16" />
              <span>Proponer mercado nuevo</span>
            </button>
          </div>

          <div v-else class="catalogo-results">
            <div
              v-for="cm in catalogoResults"
              :key="cm.id"
              class="catalogo-item"
              :class="{ 'catalogo-item--added': isMercadoAdded(cm.id) }"
              @click="addFromCatalogo(cm)"
            >
              <div class="catalogo-item__info">
                <h4>{{ cm.nombre }}</h4>
                <div class="catalogo-item__meta">
                  <span class="catalogo-item__badge" :class="tipoBadgeClass(cm.tipo)">{{ formatTipo(cm.tipo) }}</span>
                  <span>{{ cm.municipio }}, {{ cm.entidad }}</span>
                </div>
                <span v-if="cm.localidad" class="catalogo-item__loc">{{ cm.localidad }}</span>
              </div>
              <div class="catalogo-item__action">
                <span v-if="isMercadoAdded(cm.id)" class="added-label">
                  <CheckCircle :size="16" /> Agregado
                </span>
                <button v-else class="btn btn--primary btn--sm" :disabled="addingId === cm.id">
                  <Plus :size="16" />
                </button>
              </div>
            </div>
          </div>

          <!-- Botón proponer al fondo del modal -->
          <div class="catalogo-footer">
            <button class="btn btn--outline btn--full btn--wrap" @click="showCatalogo = false; showProponer = true">
              <MapPin :size="16" />
              <span>¿No encuentras tu mercado?<br>Proponer uno nuevo</span>
            </button>
          </div>
        </div>
      </div>

      <!-- ═══ MODAL PROPONER MERCADO ═══ -->
      <div v-if="showProponer" class="modal-overlay" @click.self="showProponer = false">
        <div class="modal-catalogo modal-proponer">
          <div class="modal-header">
            <h2><MapPin :size="20" /> Proponer Mercado</h2>
            <button class="btn-icon" @click="showProponer = false"><X :size="22" /></button>
          </div>

          <div class="proponer-form">
            <!-- A. Identificación -->
            <div class="proponer-section">
              <h3 class="proponer-section__title">Identificación</h3>

              <div class="form-group">
                <label class="form-label">Nombre del mercado *</label>
                <input v-model="propForm.nombre_mercado" type="text" class="input" placeholder="Ej: Mercado Municipal Centro" />
              </div>

              <div class="form-group">
                <label class="form-label">Tipo de mercado *</label>
                <select v-model="propForm.tipo_mercado" class="input">
                  <option value="">Seleccionar...</option>
                  <option value="MERCADO_PUBLICO">Mercado público</option>
                  <option value="TIANGUIS">Tianguis</option>
                  <option value="CENTRAL_ABASTO">Central de abasto</option>
                  <option value="OTRO">Otro</option>
                </select>
              </div>

              <div v-if="propForm.tipo_mercado === 'OTRO'" class="form-group">
                <label class="form-label">Especificar tipo</label>
                <input v-model="propForm.tipo_mercado_otro" type="text" class="input" placeholder="Tipo de mercado..." />
              </div>

              <div class="form-group">
                <label class="form-label">Estado *</label>
                <select v-model="propForm.estado" class="input" @change="onPropEntidadChange">
                  <option value="">Seleccionar estado...</option>
                  <option v-for="e in entidades" :key="e" :value="e">{{ e }}</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Municipio *</label>
                <select v-model="propForm.municipio" class="input" :disabled="!propForm.estado">
                  <option value="">Seleccionar municipio...</option>
                  <option v-for="m in propMunicipios" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Localidad / Colonia</label>
                <input v-model="propForm.localidad_colonia" type="text" class="input" placeholder="Ej: Centro, Col. Reforma..." />
              </div>
            </div>

            <!-- B. Ubicación GPS -->
            <div class="proponer-section">
              <h3 class="proponer-section__title">Ubicación GPS</h3>

              <div v-if="gpsStatus === 'success'" class="gps-status gps-status--ok">
                <CheckCircle :size="16" />
                <span>Ubicación capturada</span>
                <span class="gps-coords">{{ propForm.latitud.toFixed(6) }}, {{ propForm.longitud.toFixed(6) }}</span>
              </div>
              <div v-else-if="gpsStatus === 'loading'" class="gps-status gps-status--loading">
                <div class="spinner spinner--sm"></div>
                <span>Obteniendo ubicación...</span>
              </div>
              <div v-else-if="gpsStatus === 'error'" class="gps-status gps-status--error">
                <AlertCircle :size="16" />
                <span>{{ gpsError }}</span>
              </div>

              <div class="gps-buttons">
                <button class="btn btn--outline btn--full btn--wrap" @click="captureGPS" :disabled="gpsStatus === 'loading'">
                  <Navigation :size="16" />
                  <span>{{ gpsStatus === 'success' ? 'Recapturar GPS' : 'Capturar mi ubicación' }}</span>
                </button>
                <button class="btn btn--outline btn--full btn--wrap" @click="toggleMapMode">
                  <MapPin :size="16" />
                  <span>{{ showMapPicker ? 'Ocultar mapa' : 'Colocar en mapa' }}</span>
                </button>
              </div>

              <!-- Mini mapa para ubicación manual -->
              <div v-if="showMapPicker" class="map-picker">
                <div ref="mapContainer" class="map-picker__map"></div>
                <p class="map-picker__hint">Toca el mapa o arrastra el marcador para ubicar el mercado</p>
                <button class="btn btn--primary btn--full" @click="confirmMapLocation" :disabled="propForm.latitud === 0">
                  <CheckCircle :size="16" />
                  <span>Confirmar ubicación</span>
                </button>
              </div>
            </div>

            <!-- C. Operación -->
            <div class="proponer-section">
              <h3 class="proponer-section__title">Operación</h3>

              <div class="form-group">
                <label class="form-label">Días de operación *</label>
                <div class="dias-grid">
                  <label v-for="dia in DIAS_SEMANA" :key="dia" class="dia-check">
                    <input type="checkbox" :value="dia" v-model="propForm.dias_operacion" />
                    <span class="dia-check__label">{{ dia }}</span>
                  </label>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Horario</label>
                <div class="horario-row">
                  <select v-model="horarioDesde" class="input horario-select">
                    <option value="">Desde...</option>
                    <option v-for="h in HORAS" :key="'d'+h" :value="h">{{ h }}</option>
                  </select>
                  <span class="horario-sep">a</span>
                  <select v-model="horarioHasta" class="input horario-select">
                    <option value="">Hasta...</option>
                    <option v-for="h in HORAS" :key="'h'+h" :value="h">{{ h }}</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Referencia</label>
                <input v-model="propForm.referencia" type="text" class="input" placeholder="EJ: FRENTE A LA IGLESIA..." @input="propForm.referencia = toUpperNoTildes(propForm.referencia)" />
              </div>

              <div class="form-group">
                <label class="form-label">Observaciones</label>
                <textarea v-model="propForm.observaciones" class="input input--textarea" rows="3" placeholder="INFORMACION ADICIONAL..." @input="propForm.observaciones = toUpperNoTildes(propForm.observaciones)"></textarea>
              </div>
            </div>

            <!-- Guardar -->
            <button
              class="btn btn--primary btn--full btn--lg"
              :disabled="!canSubmitPropuesta || submittingProp"
              @click="submitPropuesta"
            >
              <Save :size="18" />
              <span>{{ submittingProp ? 'Enviando...' : 'Enviar propuesta' }}</span>
            </button>

            <p class="proponer-note">
              Tu propuesta será revisada por el equipo. Una vez autorizada, aparecerá en el catálogo de mercados.
            </p>
          </div>
        </div>
      </div>

      <!-- ═══ SECCIÓN: MIS PROPUESTAS ═══ -->
      <div v-if="!selectedMercado && propuestos.length > 0 && !showCatalogo && !showProponer" class="propuestos-section">
        <h3 class="propuestos-title">
          <MapPin :size="18" />
          Mis mercados propuestos ({{ propuestos.length }})
        </h3>
        <div class="propuestos-list">
          <div v-for="p in propuestos" :key="p.id" class="propuesto-card">
            <div class="propuesto-card__info">
              <h4>{{ p.nombre_mercado }}</h4>
              <div class="propuesto-card__meta">
                <span class="propuesto-card__badge" :class="propStatusClass(p.status)">{{ propStatusLabel(p.status) }}</span>
                <span class="propuesto-card__loc">{{ p.municipio }}, {{ p.estado }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ CAPTURA DE PRECIOS ═══ -->
      <div v-if="selectedMercado" class="captura-section">
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
          <div class="captura-header__meta">
            <span class="mercado-card__badge" :class="tipoBadgeClass(selectedMercado.tipo)">{{ formatTipo(selectedMercado.tipo) }}</span>
            <span class="captura-header__loc">
              <MapPin :size="13" />
              {{ selectedMercado.municipio }}, {{ selectedMercado.entidad }}
            </span>
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

        <!-- Formulario de precio -->
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

        <!-- Historial -->
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
import { ref, computed, reactive, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useUiStore } from '@/stores/ui'
import { mercadosService } from '@/services/mercados.service'
import type { Mercado, CatalogoMercado, Categoria, Subcategoria, Producto, Unidad, PrecioHistorialItem, MercadoPropuesto } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppToast from '@/components/AppToast.vue'
import {
  Store, Search, Trash2, ChevronRight, ArrowLeft, MapPin, X, Plus, CheckCircle,
  Wheat, Beef, Save, FileText, Navigation, AlertCircle
} from 'lucide-vue-next'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const ui = useUiStore()

const DIAS_SEMANA = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

const HORAS = (() => {
  const arr: string[] = []
  for (let h = 0; h < 24; h++) {
    const suffix = h < 12 ? 'AM' : 'PM'
    const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h
    for (const m of ['00', '30']) {
      arr.push(`${h12}:${m} ${suffix}`)
    }
  }
  return arr
})()

const ESTADO_COORDS: Record<string, [number, number]> = {
  'AGUASCALIENTES': [21.88, -102.30], 'BAJA CALIFORNIA': [30.84, -115.97],
  'BAJA CALIFORNIA SUR': [24.82, -111.80], 'CAMPECHE': [19.83, -90.52],
  'CHIAPAS': [16.75, -93.12], 'CHIHUAHUA': [28.64, -106.09],
  'CIUDAD DE MEXICO': [19.43, -99.13], 'COAHUILA': [26.34, -102.07],
  'COAHUILA DE ZARAGOZA': [26.34, -102.07], 'COLIMA': [19.24, -103.73],
  'DURANGO': [24.02, -104.66], 'GUANAJUATO': [21.01, -101.26],
  'GUERRERO': [17.55, -99.51], 'HIDALGO': [20.10, -98.73],
  'JALISCO': [20.66, -103.35], 'MEXICO': [19.36, -99.59],
  'ESTADO DE MEXICO': [19.36, -99.59], 'MICHOACAN': [19.70, -101.18],
  'MICHOACAN DE OCAMPO': [19.70, -101.18], 'MORELOS': [18.92, -99.23],
  'NAYARIT': [21.50, -104.89], 'NUEVO LEON': [25.67, -100.31],
  'OAXACA': [17.06, -96.73], 'PUEBLA': [19.04, -98.20],
  'QUERETARO': [20.59, -100.39], 'QUINTANA ROO': [20.50, -87.46],
  'SAN LUIS POTOSI': [22.15, -100.98], 'SINALOA': [24.79, -107.39],
  'SONORA': [29.09, -110.96], 'TABASCO': [17.99, -92.92],
  'TAMAULIPAS': [23.74, -99.14], 'TLAXCALA': [19.32, -98.24],
  'VERACRUZ': [19.17, -96.13], 'VERACRUZ DE IGNACIO DE LA LLAVE': [19.17, -96.13],
  'YUCATAN': [20.97, -89.62], 'ZACATECAS': [22.77, -102.57],
}

// ── State: Mercados ──
const mercados = ref<Mercado[]>([])
const selectedMercado = ref<Mercado | null>(null)
const loadingMercados = ref(false)

// ── State: Catálogo búsqueda ──
const showCatalogo = ref(false)
const entidades = ref<string[]>([])
const municipiosCat = ref<string[]>([])
const filtroEntidad = ref('')
const filtroMunicipio = ref('')
const filtroNombre = ref('')
const catalogoResults = ref<CatalogoMercado[]>([])
const searchingCatalogo = ref(false)
const hasSearched = ref(false)
const addingId = ref<number | null>(null)
let searchTimeout: ReturnType<typeof setTimeout> | null = null

// ── State: Proponer mercado ──
const showProponer = ref(false)
const propMunicipios = ref<string[]>([])
const gpsStatus = ref<'idle' | 'loading' | 'success' | 'error'>('idle')
const gpsError = ref('')
const submittingProp = ref(false)
const propuestos = ref<MercadoPropuesto[]>([])
const showMapPicker = ref(false)
const mapContainer = ref<HTMLElement | null>(null)
const horarioDesde = ref('')
const horarioHasta = ref('')
let leafletMap: L.Map | null = null
let leafletMarker: L.Marker | null = null
const propForm = reactive({
  nombre_mercado: '',
  tipo_mercado: '',
  tipo_mercado_otro: '',
  estado: '',
  municipio: '',
  localidad_colonia: '',
  latitud: 0,
  longitud: 0,
  dias_operacion: [] as string[],
  horario: '',
  referencia: '',
  observaciones: '',
})

// ── State: Catálogos productos ──
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
function formatTipo(tipo: string): string {
  if (tipo === 'MERCADO_PUBLICO') return 'Mercado Público'
  if (tipo === 'CENTRAL_ABASTO') return 'Central de Abasto'
  if (tipo === 'TIANGUIS') return 'Tianguis'
  return tipo
}

function tipoBadgeClass(tipo: string): string {
  if (tipo === 'MERCADO_PUBLICO') return 'badge--green'
  if (tipo === 'CENTRAL_ABASTO') return 'badge--purple'
  return 'badge--teal'
}

function closeSidebar() {
  if (ui.sidebarOpen) ui.closeSidebar()
}

function isMercadoAdded(_catalogoId: number): boolean {
  return false
}

// ── Proponer mercado ──
function propStatusLabel(status: string): string {
  if (status === 'pendiente_autorizacion') return 'Pendiente'
  if (status === 'autorizado') return 'Autorizado'
  if (status === 'rechazado') return 'Rechazado'
  return status
}

function propStatusClass(status: string): string {
  if (status === 'pendiente_autorizacion') return 'badge--orange'
  if (status === 'autorizado') return 'badge--green'
  if (status === 'rechazado') return 'badge--red'
  return 'badge--teal'
}

const canSubmitPropuesta = computed(() =>
  propForm.nombre_mercado.trim().length >= 4 &&
  propForm.tipo_mercado !== '' &&
  propForm.estado !== '' &&
  propForm.municipio !== '' &&
  propForm.dias_operacion.length > 0 &&
  gpsStatus.value === 'success' &&
  propForm.latitud !== 0 && propForm.longitud !== 0
)

async function onPropEntidadChange() {
  propForm.municipio = ''
  propMunicipios.value = []
  if (propForm.estado) {
    try {
      propMunicipios.value = await mercadosService.getCatalogoMunicipios(propForm.estado)
    } catch { /* silent */ }
  }
}

function captureGPS() {
  if (!navigator.geolocation) {
    gpsStatus.value = 'error'
    gpsError.value = 'Tu dispositivo no soporta geolocalización'
    return
  }
  gpsStatus.value = 'loading'
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      propForm.latitud = pos.coords.latitude
      propForm.longitud = pos.coords.longitude
      gpsStatus.value = 'success'
    },
    (err) => {
      gpsStatus.value = 'error'
      if (err.code === 1) gpsError.value = 'Permiso de ubicación denegado'
      else if (err.code === 2) gpsError.value = 'Ubicación no disponible'
      else gpsError.value = 'No se pudo obtener la ubicación'
    },
    { enableHighAccuracy: true, timeout: 15000 }
  )
}

function toUpperNoTildes(str: string): string {
  return str.toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
}

function destroyMap() {
  if (leafletMap) {
    leafletMap.remove()
    leafletMap = null
    leafletMarker = null
  }
}

function initPropMap() {
  if (!mapContainer.value) return
  destroyMap()

  let center: L.LatLngExpression = [23.63, -102.55]
  let zoom = 5

  if (propForm.estado) {
    const key = propForm.estado.toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    const coords = ESTADO_COORDS[key]
    if (coords) { center = coords; zoom = 9 }
  }

  if (propForm.latitud !== 0 && propForm.longitud !== 0) {
    center = [propForm.latitud, propForm.longitud]
    zoom = 15
  }

  leafletMap = L.map(mapContainer.value, { center, zoom, zoomControl: true, attributionControl: false })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
  }).addTo(leafletMap)

  const markerIcon = L.divIcon({
    className: 'prop-map-marker',
    html: '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="42" viewBox="0 0 32 42"><path d="M16 0C7.16 0 0 7.16 0 16c0 12 16 26 16 26s16-14 16-26C32 7.16 24.84 0 16 0z" fill="#1B5E20"/><circle cx="16" cy="16" r="7" fill="#fff"/></svg>',
    iconSize: [32, 42],
    iconAnchor: [16, 42],
  })

  leafletMarker = L.marker(center, { draggable: true, icon: markerIcon }).addTo(leafletMap)

  leafletMarker.on('dragend', () => {
    const pos = leafletMarker!.getLatLng()
    propForm.latitud = pos.lat
    propForm.longitud = pos.lng
    gpsStatus.value = 'success'
  })

  leafletMap.on('click', (e: L.LeafletMouseEvent) => {
    leafletMarker!.setLatLng(e.latlng)
    propForm.latitud = e.latlng.lat
    propForm.longitud = e.latlng.lng
    gpsStatus.value = 'success'
  })
}

function toggleMapMode() {
  showMapPicker.value = !showMapPicker.value
  if (showMapPicker.value) {
    nextTick(() => initPropMap())
  } else {
    destroyMap()
  }
}

function confirmMapLocation() {
  if (propForm.latitud !== 0 && propForm.longitud !== 0) {
    gpsStatus.value = 'success'
  }
  showMapPicker.value = false
  destroyMap()
}

function resetPropForm() {
  propForm.nombre_mercado = ''
  propForm.tipo_mercado = ''
  propForm.tipo_mercado_otro = ''
  propForm.estado = ''
  propForm.municipio = ''
  propForm.localidad_colonia = ''
  propForm.latitud = 0
  propForm.longitud = 0
  propForm.dias_operacion = []
  propForm.horario = ''
  propForm.referencia = ''
  propForm.observaciones = ''
  gpsStatus.value = 'idle'
  gpsError.value = ''
  propMunicipios.value = []
  horarioDesde.value = ''
  horarioHasta.value = ''
  showMapPicker.value = false
  destroyMap()
}

async function submitPropuesta() {
  if (!canSubmitPropuesta.value) return
  submittingProp.value = true
  try {
    const created = await mercadosService.proponerMercado({
      nombre_mercado: propForm.nombre_mercado.trim(),
      tipo_mercado: propForm.tipo_mercado,
      tipo_mercado_otro: propForm.tipo_mercado === 'OTRO' ? propForm.tipo_mercado_otro : undefined,
      estado: propForm.estado,
      municipio: propForm.municipio,
      localidad_colonia: propForm.localidad_colonia || undefined,
      latitud: propForm.latitud,
      longitud: propForm.longitud,
      dias_operacion: propForm.dias_operacion,
      horario: horarioDesde.value && horarioHasta.value ? `${horarioDesde.value} - ${horarioHasta.value}` : undefined,
      referencia: propForm.referencia || undefined,
      observaciones: propForm.observaciones || undefined,
    })
    propuestos.value.unshift(created)
    ui.showToast('Propuesta enviada correctamente', 'success')
    showProponer.value = false
    resetPropForm()
  } catch (e: any) {
    const msg = e.response?.data?.detail || 'Error al enviar propuesta'
    ui.showToast(msg, 'error')
  } finally {
    submittingProp.value = false
  }
}

async function loadPropuestos() {
  try {
    propuestos.value = await mercadosService.getMercadosPropuestos()
  } catch { /* silent */ }
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

// ── Catálogo búsqueda ──
async function loadEntidades() {
  try {
    entidades.value = await mercadosService.getCatalogoEntidades()
  } catch { /* silent */ }
}

async function onEntidadChange() {
  filtroMunicipio.value = ''
  municipiosCat.value = []
  if (filtroEntidad.value) {
    try {
      municipiosCat.value = await mercadosService.getCatalogoMunicipios(filtroEntidad.value)
    } catch { /* silent */ }
  }
  searchCatalogo()
}

function onNombreInput() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => searchCatalogo(), 350)
}

async function searchCatalogo() {
  const params: Record<string, string> = {}
  if (filtroEntidad.value) params.entidad = filtroEntidad.value
  if (filtroMunicipio.value) params.municipio = filtroMunicipio.value
  if (filtroNombre.value.trim()) params.nombre = filtroNombre.value.trim()

  if (!params.entidad && !params.municipio && !params.nombre) {
    catalogoResults.value = []
    hasSearched.value = false
    return
  }

  searchingCatalogo.value = true
  hasSearched.value = true
  try {
    catalogoResults.value = await mercadosService.searchCatalogo(params)
  } catch {
    ui.showToast('Error al buscar mercados', 'error')
  } finally {
    searchingCatalogo.value = false
  }
}

async function addFromCatalogo(cm: CatalogoMercado) {
  if (addingId.value) return
  addingId.value = cm.id
  try {
    const m = await mercadosService.addMercado(cm.id)
    mercados.value.push(m)
    mercados.value.sort((a, b) => a.nombre.localeCompare(b.nombre))
    ui.showToast(`${cm.nombre} agregado`, 'success')
    showCatalogo.value = false
  } catch (e: any) {
    const msg = e.response?.data?.detail || 'Error al agregar mercado'
    ui.showToast(msg, 'error')
  } finally {
    addingId.value = null
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

// ── Filtros catálogo productos ──
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

watch(tipoPrecio, async () => {
  const subId = selectedSubcategoria.value
  if (!subId) return
  try {
    unidades.value = await mercadosService.getUnidades(subId, tipoPrecio.value)
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
  loadEntidades()
  loadPropuestos()
})

onBeforeUnmount(() => {
  destroyMap()
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
.input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
.btn--sm {
  padding: 0.4rem 0.65rem;
  font-size: 0.85rem;
  border-radius: 8px;
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
  color: #666;
}
.btn-icon--danger {
  color: #c62828;
}
.btn-icon--danger:hover {
  background: #ffebee;
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
.mercado-card__info {
  min-width: 0;
  flex: 1;
}
.mercado-card__info h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mercado-card__meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.3rem;
  flex-wrap: wrap;
}
.mercado-card__loc {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
  font-size: 0.78rem;
  color: #888;
}
.mercado-card__badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 5px;
}
.mercado-card__actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-shrink: 0;
}
.mercado-card__arrow {
  color: #1B5E20;
}

/* ── Badges ── */
.badge--green {
  background: #e8f5e9;
  color: #1B5E20;
}
.badge--purple {
  background: #f3e5f5;
  color: #7b1fa2;
}
.badge--teal {
  background: #e0f2f1;
  color: #00695c;
}
.badge--blue {
  background: #e3f2fd;
  color: #1565c0;
}
.badge--orange {
  background: #fff3e0;
  color: #e65100;
}

/* ── Modal Catálogo ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-top: env(safe-area-inset-top, 0px);
}
.modal-catalogo {
  background: #fff;
  border-radius: 20px 20px 0 0;
  width: 100%;
  max-width: 640px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.25s ease-out;
}
@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem 0.75rem;
  border-bottom: 1px solid #eee;
}
.modal-header h2 {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1B5E20;
}

.catalogo-filtros {
  padding: 0.75rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border-bottom: 1px solid #eee;
}
.filter-row {
  width: 100%;
}

.catalogo-results {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}
.catalogo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: background 0.15s;
}
.catalogo-item:hover {
  background: #f8fdf8;
}
.catalogo-item--added {
  opacity: 0.55;
  cursor: default;
}
.catalogo-item__info {
  min-width: 0;
  flex: 1;
}
.catalogo-item__info h4 {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 600;
  color: #333;
}
.catalogo-item__meta {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.2rem;
  font-size: 0.78rem;
  color: #888;
  flex-wrap: wrap;
}
.catalogo-item__badge {
  font-size: 0.62rem;
  font-weight: 700;
  padding: 0.12rem 0.4rem;
  border-radius: 4px;
}
.catalogo-item__loc {
  font-size: 0.72rem;
  color: #aaa;
}
.catalogo-item__action {
  flex-shrink: 0;
  margin-left: 0.5rem;
}
.added-label {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  font-size: 0.8rem;
  font-weight: 600;
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
.captura-header__meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.35rem;
  flex-wrap: wrap;
}
.captura-header__loc {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
  font-size: 0.82rem;
  color: #888;
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

/* ── Precio Form ── */
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

/* ── Historial ── */
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

/* ── Responsive ── */
@media (max-width: 480px) {
  .precio-form__fields {
    flex-direction: column;
  }
  .tipo-precio-toggle {
    flex-direction: column;
    align-items: flex-start;
  }
  .modal-catalogo {
    max-height: 90vh;
  }
}

/* ── Botón outline ── */
.btn--outline {
  background: #fff;
  color: #1B5E20;
  border: 1.5px solid #1B5E20;
}
.btn--outline:hover:not(:disabled) {
  background: #e8f5e9;
}
.btn--lg {
  padding: 0.85rem 1.25rem;
  font-size: 1rem;
}

/* ── Catálogo footer ── */
.catalogo-footer {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid #eee;
}

/* ── Modal Proponer ── */
.modal-proponer {
  max-height: 90vh;
}
.proponer-form {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.25rem 1.5rem;
}
.proponer-section {
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f0f0f0;
}
.proponer-section:last-of-type {
  border-bottom: none;
}
.proponer-section__title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1B5E20;
  margin: 0 0 0.75rem;
}
.form-group {
  margin-bottom: 0.75rem;
}
.form-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: #555;
  margin-bottom: 0.25rem;
}
.input--textarea {
  resize: vertical;
  min-height: 60px;
  font-family: inherit;
}

/* ── GPS status ── */
.gps-status {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 0.75rem;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
}
.gps-status--ok {
  background: #e8f5e9;
  color: #1B5E20;
}
.gps-status--loading {
  background: #fff3e0;
  color: #e65100;
}
.gps-status--error {
  background: #ffebee;
  color: #c62828;
}
.gps-coords {
  font-weight: 400;
  font-size: 0.78rem;
  margin-left: auto;
  color: #666;
}
.spinner--sm {
  width: 18px;
  height: 18px;
  border-width: 2px;
}

/* ── GPS buttons & Map picker ── */
.gps-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.6rem;
}
.map-picker {
  margin-top: 0.75rem;
  border: 1.5px solid #c8e6c9;
  border-radius: 12px;
  overflow: hidden;
}
.map-picker__map {
  width: 100%;
  height: 250px;
}
.map-picker__hint {
  font-size: 0.78rem;
  color: #777;
  font-style: italic;
  text-align: center;
  margin: 0.5rem 0.5rem 0;
}
.map-picker .btn {
  margin: 0.5rem;
  width: calc(100% - 1rem);
}
.prop-map-marker {
  background: none !important;
  border: none !important;
}

/* ── Horario row ── */
.horario-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.horario-select {
  flex: 1;
  min-width: 0;
}
.horario-sep {
  font-size: 0.85rem;
  font-weight: 600;
  color: #777;
  padding: 0 0.15rem;
}

/* ── Responsive button wrap ── */
.btn--wrap {
  white-space: normal;
  text-align: center;
  line-height: 1.3;
}

/* ── Modal Proponer responsive ── */
.modal-proponer {
  max-height: calc(90vh - env(safe-area-inset-top, 0px));
}

/* ── Días checkboxes ── */
.dias-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.dia-check {
  display: flex;
  align-items: center;
  cursor: pointer;
}
.dia-check input {
  display: none;
}
.dia-check__label {
  padding: 0.4rem 0.65rem;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #666;
  transition: all 0.15s;
  user-select: none;
}
.dia-check input:checked + .dia-check__label {
  background: #1B5E20;
  color: #fff;
  border-color: #1B5E20;
}

.proponer-note {
  text-align: center;
  font-size: 0.78rem;
  color: #999;
  margin-top: 0.75rem;
  line-height: 1.4;
}

/* ── Propuestos section ── */
.propuestos-section {
  max-width: 640px;
  margin: 0 auto;
  padding: 0 1rem 2rem;
}
.propuestos-title {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: #555;
  margin: 0 0 0.5rem;
}
.propuestos-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.propuesto-card {
  display: flex;
  align-items: center;
  background: #fff;
  border: 1.5px solid #fff3e0;
  border-radius: 10px;
  padding: 0.7rem 0.85rem;
}
.propuesto-card__info h4 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}
.propuesto-card__meta {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.2rem;
  flex-wrap: wrap;
}
.propuesto-card__badge {
  font-size: 0.62rem;
  font-weight: 700;
  padding: 0.12rem 0.4rem;
  border-radius: 4px;
}
.propuesto-card__loc {
  font-size: 0.75rem;
  color: #888;
}
.badge--red {
  background: #ffebee;
  color: #c62828;
}
</style>
