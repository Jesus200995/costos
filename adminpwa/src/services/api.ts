import axios from 'axios'

const API_URL = import.meta.env.PROD 
  ? 'https://apicostos.sembrandodatos.com/api'
  : 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para agregar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token && config.params) {
    config.params.token = token
  }
  return config
})

export default api
