import api from './api'
import type {
  Categoria, Subcategoria, Producto, Unidad,
  Mercado, ReporteOut, ReporteDetalleOut, DetalleItem
} from '@/types'

export const mercadosService = {
  // Catálogos
  async getCategorias(): Promise<Categoria[]> {
    const { data } = await api.get<Categoria[]>('/mercados/categorias')
    return data
  },

  async getSubcategorias(categoria_id: string): Promise<Subcategoria[]> {
    const { data } = await api.get<Subcategoria[]>('/mercados/subcategorias', {
      params: { categoria_id }
    })
    return data
  },

  async getProductos(subcategoria_id: string): Promise<Producto[]> {
    const { data } = await api.get<Producto[]>('/mercados/productos', {
      params: { subcategoria_id }
    })
    return data
  },

  async getUnidades(subcategoria_id: string): Promise<Unidad[]> {
    const { data } = await api.get<Unidad[]>('/mercados/unidades', {
      params: { subcategoria_id }
    })
    return data
  },

  // Mercados del usuario
  async getMercados(): Promise<Mercado[]> {
    const { data } = await api.get<Mercado[]>('/mercados/')
    return data
  },

  async createMercado(nombre: string): Promise<Mercado> {
    const { data } = await api.post<Mercado>('/mercados/', { nombre })
    return data
  },

  async deleteMercado(id: number): Promise<void> {
    await api.delete(`/mercados/${id}`)
  },

  // Reportes
  async createReporte(payload: { mercado_id: number; tipo_precio: string; items: DetalleItem[] }): Promise<ReporteOut> {
    const { data } = await api.post<ReporteOut>('/mercados/reportes', payload)
    return data
  },

  async getReportes(mercado_id?: number): Promise<ReporteOut[]> {
    const { data } = await api.get<ReporteOut[]>('/mercados/reportes', {
      params: mercado_id ? { mercado_id } : {}
    })
    return data
  },

  async getReporte(id: number): Promise<ReporteDetalleOut> {
    const { data } = await api.get<ReporteDetalleOut>(`/mercados/reportes/${id}`)
    return data
  }
}
