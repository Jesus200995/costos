<template>
  <div class="auth-page">
    <div class="auth-bg">
      <div class="auth-bg-shape auth-bg-shape--1"></div>
      <div class="auth-bg-shape auth-bg-shape--2"></div>
      <div class="auth-bg-shape auth-bg-shape--3"></div>
    </div>

    <div class="auth-container" :class="{ 'auth-container--visible': mounted }">
      <div class="auth-logo">
        <div class="auth-logo__icon">
          <UserPlus :size="32" />
        </div>
        <h1 class="auth-logo__title">Crear Cuenta</h1>
        <p class="auth-logo__subtitle">Únete a COSTOS</p>
      </div>

      <form class="auth-form" @submit.prevent="handleRegister" novalidate>
        <div class="form-group" :class="{ 'form-group--error': errors.name, 'form-group--focus': focused === 'name' }">
          <div class="form-input-wrapper">
            <User :size="20" class="form-icon" />
            <input
              v-model="form.name"
              type="text"
              placeholder="Nombre completo"
              autocomplete="name"
              @focus="focused = 'name'"
              @blur="focused = ''"
            />
          </div>
          <Transition name="slide-error">
            <span v-if="errors.name" class="form-error">{{ errors.name }}</span>
          </Transition>
        </div>

        <div class="form-group" :class="{ 'form-group--error': errors.email, 'form-group--focus': focused === 'email' }">
          <div class="form-input-wrapper">
            <Mail :size="20" class="form-icon" />
            <input
              v-model="form.email"
              type="email"
              placeholder="Correo electrónico"
              autocomplete="email"
              @focus="focused = 'email'"
              @blur="focused = ''"
            />
          </div>
          <Transition name="slide-error">
            <span v-if="errors.email" class="form-error">{{ errors.email }}</span>
          </Transition>
        </div>

        <div class="form-group" :class="{ 'form-group--error': errors.password, 'form-group--focus': focused === 'password' }">
          <div class="form-input-wrapper">
            <Lock :size="20" class="form-icon" />
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Contraseña"
              autocomplete="new-password"
              @focus="focused = 'password'"
              @blur="focused = ''"
            />
            <button type="button" class="form-toggle-pass" @click="showPassword = !showPassword" tabindex="-1">
              <EyeOff v-if="showPassword" :size="20" />
              <Eye v-else :size="20" />
            </button>
          </div>
          <Transition name="slide-error">
            <span v-if="errors.password" class="form-error">{{ errors.password }}</span>
          </Transition>
        </div>

        <div class="form-group" :class="{ 'form-group--error': errors.confirmPassword, 'form-group--focus': focused === 'confirm' }">
          <div class="form-input-wrapper">
            <ShieldCheck :size="20" class="form-icon" />
            <input
              v-model="form.confirmPassword"
              :type="showConfirm ? 'text' : 'password'"
              placeholder="Confirmar contraseña"
              autocomplete="new-password"
              @focus="focused = 'confirm'"
              @blur="focused = ''"
            />
            <button type="button" class="form-toggle-pass" @click="showConfirm = !showConfirm" tabindex="-1">
              <EyeOff v-if="showConfirm" :size="20" />
              <Eye v-else :size="20" />
            </button>
          </div>
          <Transition name="slide-error">
            <span v-if="errors.confirmPassword" class="form-error">{{ errors.confirmPassword }}</span>
          </Transition>
        </div>

        <!-- Password strength -->
        <div v-if="form.password" class="password-strength">
          <div class="password-strength__bar">
            <div
              class="password-strength__fill"
              :style="{ width: strengthPercent + '%' }"
              :class="'password-strength__fill--' + strengthLevel"
            ></div>
          </div>
          <span class="password-strength__label" :class="'password-strength__label--' + strengthLevel">
            {{ strengthText }}
          </span>
        </div>

        <Transition name="slide-error">
          <div v-if="serverError" class="form-server-error">
            <AlertCircle :size="18" />
            <span>{{ serverError }}</span>
          </div>
        </Transition>

        <button type="submit" class="btn btn--primary btn--full" :disabled="authStore.loading">
          <Loader2 v-if="authStore.loading" :size="20" class="spin" />
          <UserPlus v-else :size="20" />
          <span>{{ authStore.loading ? 'Creando cuenta...' : 'Registrarse' }}</span>
        </button>
      </form>

      <div class="auth-footer">
        <p>¿Ya tienes cuenta?</p>
        <router-link to="/login" class="auth-link">
          <ArrowLeft :size="16" />
          Iniciar sesión
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import {
  UserPlus, User, Mail, Lock, ShieldCheck,
  Eye, EyeOff, ArrowLeft, Loader2, AlertCircle
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const ui = useUiStore()

const mounted = ref(false)
const focused = ref('')
const showPassword = ref(false)
const showConfirm = ref(false)
const serverError = ref('')

const form = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const errors = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const strengthPercent = computed(() => {
  const p = form.password
  if (!p) return 0
  let score = 0
  if (p.length >= 6) score += 25
  if (p.length >= 10) score += 15
  if (/[A-Z]/.test(p)) score += 20
  if (/[0-9]/.test(p)) score += 20
  if (/[^A-Za-z0-9]/.test(p)) score += 20
  return Math.min(score, 100)
})

const strengthLevel = computed(() => {
  if (strengthPercent.value < 30) return 'weak'
  if (strengthPercent.value < 60) return 'medium'
  if (strengthPercent.value < 85) return 'strong'
  return 'excellent'
})

const strengthText = computed(() => {
  const map: Record<string, string> = {
    weak: 'Débil',
    medium: 'Media',
    strong: 'Fuerte',
    excellent: 'Excelente'
  }
  return map[strengthLevel.value]
})

onMounted(() => {
  setTimeout(() => { mounted.value = true }, 50)
})

function validate(): boolean {
  let valid = true
  errors.name = ''
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''

  if (!form.name.trim()) {
    errors.name = 'El nombre es obligatorio'
    valid = false
  } else if (form.name.trim().length < 2) {
    errors.name = 'Mínimo 2 caracteres'
    valid = false
  }

  if (!form.email.trim()) {
    errors.email = 'El correo es obligatorio'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Correo inválido'
    valid = false
  }

  if (!form.password) {
    errors.password = 'La contraseña es obligatoria'
    valid = false
  } else if (form.password.length < 6) {
    errors.password = 'Mínimo 6 caracteres'
    valid = false
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = 'Confirma tu contraseña'
    valid = false
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Las contraseñas no coinciden'
    valid = false
  }

  return valid
}

async function handleRegister() {
  serverError.value = ''
  if (!validate()) return

  try {
    await authStore.register(form)
    ui.showToast('¡Cuenta creada exitosamente!', 'success')
    router.push('/')
  } catch (err: unknown) {
    const error = err as { response?: { data?: { message?: string } } }
    serverError.value = error.response?.data?.detail || error.response?.data?.message || 'Error al registrarse'
  }
}
</script>
